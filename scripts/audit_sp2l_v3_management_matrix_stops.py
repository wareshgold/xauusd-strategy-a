"""Read-only forensic audit for management-matrix trade CSVs.

This does not modify matrix artifacts or define canonical Strategy A rules.
Default unit follows the documented XAU pip size of 0.10 price: 10 pips = 1.00.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def _num(row, key):
    raw = row.get(key)
    if raw in (None, ""):
        return None
    value = float(raw)
    return value if math.isfinite(value) else None


def _epoch(raw):
    raw = str(raw or "").strip()
    if not raw:
        return None
    if raw.isdigit() or (raw.startswith("-") and raw[1:].isdigit()):
        return int(raw)
    dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"timestamp lacks timezone: {raw}")
    return int(dt.timestamp())


def load_bars(path):
    by_time = {}
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        names = {x.strip().lower(): x for x in (reader.fieldnames or [])}
        if "time" not in names and "timestamp" in names:
            names["time"] = names["timestamp"]
        for line, row in enumerate(reader, 2):
            ts = _epoch(row.get(names.get("time", "")))
            if ts is None:
                raise ValueError(f"missing timestamp on bar row {line}")
            by_time[ts] = {
                k: float(row[names[k]]) for k in ("open", "high", "low", "close")
                if names.get(k) and row.get(names[k]) not in (None, "")
            }
    return by_time


def audit(trades_path, bars_path, pip_size_price=0.10, min_sl_pips=10.0, tolerance=1e-6):
    if pip_size_price <= 0 or min_sl_pips <= 0:
        raise ValueError("pip_size_price and min_sl_pips must be positive")
    minimum_risk_price = pip_size_price * min_sl_pips
    bars = load_bars(bars_path)
    groups = defaultdict(list)
    stop_issues, r_issues, missing_exit_bars = [], [], []
    total = low_risk = 0
    with Path(trades_path).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"scenario", "direction", "entry", "initial_sl", "risk_price",
                    "exit_time", "exit_price", "final_sl", "reason", "realized_R"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"trade CSV missing columns: {sorted(missing)}")
        for row_no, row in enumerate(reader, 2):
            total += 1
            scenario = row["scenario"]
            risk = _num(row, "risk_price")
            if risk is None or risk <= 0:
                r_issues.append({"row": row_no, "scenario": scenario, "issue": "invalid risk_price", "risk_price": risk})
                continue
            too_tight = risk + tolerance < minimum_risk_price
            low_risk += int(too_tight)
            exit_price = _num(row, "exit_price")
            final_sl = _num(row, "final_sl")
            entry = _num(row, "entry")
            realized = _num(row, "realized_R")
            direction = row["direction"]
            reason = row["reason"]
            partial_done = str(row.get("partial_done", "")).strip().lower() in ("true", "1", "yes")
            partial_r = _num(row, "partial_tp_R")
            if realized is not None and exit_price is not None and entry is not None:
                runner_r = ((exit_price - entry) if direction == "BUY" else (entry - exit_price)) / risk
                expected = (0.5 * partial_r + 0.5 * runner_r) if partial_done and partial_r is not None else runner_r
                if abs(realized - expected) > max(tolerance, abs(expected) * 1e-7):
                    r_issues.append({"row": row_no, "scenario": scenario, "issue": "realized_R mismatch",
                                     "reported_R": realized, "calculated_R": expected, "partial_done": partial_done})
            if reason in ("SL", "TRAIL_SL") and exit_price is not None and final_sl is not None:
                if abs(exit_price - final_sl) > tolerance:
                    ts = _epoch(row.get("exit_time"))
                    bar = bars.get(ts)
                    if bar is None:
                        missing_exit_bars.append({"row": row_no, "scenario": scenario, "exit_time": ts,
                                                  "exit_price": exit_price, "final_sl": final_sl})
                    else:
                        op = bar.get("open")
                        gap_ok = op is not None and abs(exit_price - op) <= tolerance and (
                            (direction == "BUY" and op < final_sl - tolerance) or
                            (direction == "SELL" and op > final_sl + tolerance)
                        )
                        if not gap_ok:
                            stop_issues.append({"row": row_no, "scenario": scenario, "direction": direction,
                                                "reason": reason, "exit_time": ts, "exit_price": exit_price,
                                                "final_sl": final_sl, "bar_open": op, "gap_fill_valid": False})
            groups[scenario].append({
                "risk_price": risk, "too_tight": too_tight, "realized_R": realized,
                "partial_done": partial_done, "exit_time": _epoch(row.get("exit_time")),
                "trigger_time": _epoch(row.get("trigger_time")), "row": row_no,
            })

    scenario_results = []
    for name, rows in sorted(groups.items()):
        closed = [r for r in rows if r["realized_R"] is not None and not r["too_tight"]]
        all_closed = [r for r in rows if r["realized_R"] is not None]
        ordered = sorted(closed, key=lambda r: (r["exit_time"] or 2**63-1, r["trigger_time"] or 2**63-1))
        wins = [r for r in ordered if r["realized_R"] > 0]
        losses = [r for r in ordered if r["realized_R"] < 0]
        net = sum(r["realized_R"] for r in ordered)
        gross_win = sum(r["realized_R"] for r in wins)
        gross_loss = abs(sum(r["realized_R"] for r in losses))
        all_ordered = sorted(all_closed, key=lambda r: (r["exit_time"] or 2**63-1, r["trigger_time"] or 2**63-1))
        all_net = sum(r["realized_R"] for r in all_ordered)
        top = sorted((r["realized_R"] for r in ordered), reverse=True)
        scenario_results.append({
            "scenario": name, "rows": len(rows),
            "below_minimum_sl_count": sum(r["too_tight"] for r in rows),
            "below_minimum_sl_pct": 100 * sum(r["too_tight"] for r in rows) / len(rows) if rows else None,
            "closed_all_risks": len(all_closed), "net_R_all_risks": all_net,
            "closed_after_minimum_sl_filter": len(ordered), "net_R_after_minimum_sl_filter": net,
            "profit_factor_after_minimum_sl_filter": gross_win / gross_loss if gross_loss else None,
            "max_single_win_R_after_filter": max(top) if top else None,
            "top_5_wins_R_after_filter": sum(top[:5]),
            "top_5_share_of_net_pct_after_filter": 100 * sum(top[:5]) / net if net > 0 else None,
        })
    return {
        "status": "COMPLETE", "research_only": True, "canonical": False,
        "trades_csv": str(Path(trades_path)), "bars_csv": str(Path(bars_path)),
        "unit_assumption": {"pip_size_price": pip_size_price, "minimum_sl_pips": min_sl_pips,
                            "minimum_risk_price": minimum_risk_price,
                            "basis": "explicit configurable assumption; verify against the frozen profile"},
        "trades_rows": total, "below_minimum_sl_rows": low_risk,
        "stop_exit_consistency_issue_count": len(stop_issues),
        "realized_R_consistency_issue_count": len(r_issues),
        "missing_exit_bar_count_for_stop_review": len(missing_exit_bars),
        "stop_exit_issues_sample": stop_issues[:100],
        "realized_R_issues_sample": r_issues[:100],
        "missing_exit_bars_sample": missing_exit_bars[:100],
        "scenarios": scenario_results,
        "limitations": [
            "Minimum-SL filtered figures are sensitivity diagnostics, not a fresh backtest.",
            "This audit cannot establish tick-level fill order from M1 OHLC.",
            "Costs, spread, commission, swap and ordinary slippage remain outside this calculation.",
            "No input artifact is modified; outputs are written only to the requested report path."
        ],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--trades-csv", required=True)
    p.add_argument("--bars-csv", required=True)
    p.add_argument("--output-json", required=True)
    p.add_argument("--pip-size-price", type=float, default=0.10)
    p.add_argument("--min-sl-pips", type=float, default=10.0)
    a = p.parse_args()
    report = audit(a.trades_csv, a.bars_csv, a.pip_size_price, a.min_sl_pips)
    out = Path(a.output_json)
    if out.exists():
        raise FileExistsError(f"refusing to overwrite existing report: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(out),
                      "trades_rows": report["trades_rows"],
                      "below_minimum_sl_rows": report["below_minimum_sl_rows"],
                      "stop_exit_consistency_issue_count": report["stop_exit_consistency_issue_count"],
                      "realized_R_consistency_issue_count": report["realized_R_consistency_issue_count"]}, indent=2))
if __name__ == "__main__":
    main()
