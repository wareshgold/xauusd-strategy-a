#!/usr/bin/env python3
"""Research-only same-bar trailing-stop ambiguity sensitivity for frozen Strategy A V3 trades.

Baseline checks the existing stop/target first, then updates the trail for the next
bar. The alternate scenario assumes a newly tightened stop is crossed on the same
bar when its adverse extreme reaches it. OHLC cannot prove intrabar order or fills.
This diagnostic does not change canonical rules, frozen geometry, or production.
"""
import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_BARS_SHA256 = "b0782e716c7eccbd29ef25e146c088b356f2aadf2ccd5d7ea24e6ac1488aa285"
TRAIL_DISTANCE = 0.40


def ts(value):
    value = value.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError("Timestamp has no timezone: " + value)
    return int(dt.astimezone(timezone.utc).timestamp())


def utc(value):
    return datetime.fromtimestamp(value, timezone.utc).isoformat().replace("+00:00", "Z")


def load_bars(path):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open(newline="", encoding="utf-8-sig") as f:
        rd = csv.DictReader(f)
        if not rd.fieldnames:
            raise ValueError("OHLC CSV has no header")
        cols = {x.strip().lower(): x for x in rd.fieldnames}
        time_col = next((cols[k] for k in ("time_utc_iso", "timestamp_utc", "timestamp",
                                             "datetime", "time", "date") if k in cols), None)
        if not time_col or any(k not in cols for k in ("open", "high", "low", "close")):
            raise ValueError("Timestamp/OHLC columns not recognized: " + repr(rd.fieldnames))
        bars = []
        for line, row in enumerate(rd, 2):
            b = {"time": ts(row[time_col])}
            for k in ("open", "high", "low", "close"):
                b[k] = float(row[cols[k]])
            if b["high"] < max(b["open"], b["close"], b["low"]) or b["low"] > min(b["open"], b["close"], b["high"]):
                raise ValueError("Invalid OHLC at line " + str(line))
            if bars and b["time"] <= bars[-1]["time"]:
                raise ValueError("Timestamps must be strictly increasing; no sorting/deduplication")
            bars.append(b)
    if not bars:
        raise ValueError("No OHLC bars")
    return bars, digest, time_col


def load_trades(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        rd = csv.DictReader(f)
        required = {"strategy", "variant", "direction", "entry_time_utc", "entry_proxy",
                    "sl_initial", "target", "risk_price", "exit_time_utc", "exit_price",
                    "exit_reason", "status", "r_multiple"}
        if not rd.fieldnames or not required.issubset(set(rd.fieldnames)):
            raise ValueError("Trade CSV missing required fields: " + repr(sorted(required)))
        rows = list(rd)
    if not rows:
        raise ValueError("Trade CSV is empty")
    variants = {str(r["variant"]).strip() for r in rows}
    strategies = {str(r["strategy"]).strip().upper() for r in rows}
    if len(variants) != 1 or not next(iter(variants)):
        raise ValueError("Expected one non-empty trade variant: " + repr(sorted(variants)))
    variant = next(iter(variants))
    if "TRAIL" not in variant.upper() or "V3" not in variant.upper():
        raise ValueError("Expected activated-trail V3 variant, got: " + repr(variant))
    if strategies != {"A"}:
        raise ValueError("Expected Strategy A only, got: " + repr(sorted(strategies)))
    return rows


def row(trade, scenario, status, exit_time="", exit_price=None, reason="", r=None, notes=""):
    return {"scenario": scenario, "direction": trade["direction"].upper(),
            "entry_time_utc": trade["entry_time_utc"], "entry_proxy": float(trade["entry_proxy"]),
            "sl_initial": float(trade["sl_initial"]), "target": float(trade["target"]),
            "risk_price": float(trade["risk_price"]), "status": status, "exit_time_utc": exit_time,
            "exit_price": "" if exit_price is None else round(exit_price, 10),
            "exit_reason": reason, "r_multiple": "" if r is None else round(r, 8), "notes": notes}


def simulate(bars, ix, trade, scenario):
    direction = trade["direction"].upper()
    if direction not in ("BUY", "SELL"):
        raise ValueError("Unknown direction: " + direction)
    entry, stop = float(trade["entry_proxy"]), float(trade["sl_initial"])
    target, risk = float(trade["target"]), float(trade["risk_price"])
    if not math.isfinite(risk) or risk <= 0:
        raise ValueError("Invalid risk for " + trade["entry_time_utc"])
    start = ix.get(ts(trade["entry_time_utc"]))
    if start is None:
        return row(trade, scenario, "UNRESOLVED", reason="ENTRY_BAR_NOT_FOUND")
    best, activated, first_activation, ambiguities = entry, False, "", 0
    for i in range(start + 1, len(bars)):
        b = bars[i]
        gap = i > 0 and b["time"] - bars[i - 1]["time"] > 60
        o, h, l = b["open"], b["high"], b["low"]
        if direction == "BUY":
            if gap and o <= stop: px, reason = o, "GAP_STOP_AT_OPEN"
            elif gap and o >= target: px, reason = o, "GAP_TARGET_AT_OPEN"
            elif l <= stop and h >= target: px, reason = stop, "BOTH_TOUCHED_STOP_FIRST"
            elif l <= stop: px, reason = stop, "SL"
            elif h >= target: px, reason = target, "TP"
            else: px = reason = None
        else:
            if gap and o >= stop: px, reason = o, "GAP_STOP_AT_OPEN"
            elif gap and o <= target: px, reason = o, "GAP_TARGET_AT_OPEN"
            elif h >= stop and l <= target: px, reason = stop, "BOTH_TOUCHED_STOP_FIRST"
            elif h >= stop: px, reason = stop, "SL"
            elif l <= target: px, reason = target, "TP"
            else: px = reason = None
        if reason is not None:
            r = (px - entry) / risk if direction == "BUY" else (entry - px) / risk
            return row(trade, scenario, "CLOSED", utc(b["time"]), px, reason, r,
                       "trail_activated=" + str(activated) + "; same_bar_ambiguities=" + str(ambiguities) +
                       "; first_activation_utc=" + first_activation)
        if direction == "BUY":
            best = max(best, h)
            newly = not activated and best >= entry + TRAIL_DISTANCE
            proposed = max(stop, best - TRAIL_DISTANCE) if best >= entry + TRAIL_DISTANCE else stop
            crossed, adverse = proposed > stop and l <= proposed, l
        else:
            best = min(best, l)
            newly = not activated and best <= entry - TRAIL_DISTANCE
            proposed = min(stop, best + TRAIL_DISTANCE) if best <= entry - TRAIL_DISTANCE else stop
            crossed, adverse = proposed < stop and h >= proposed, h
        if newly:
            activated, first_activation = True, utc(b["time"])
        if crossed:
            ambiguities += 1
            if scenario == "IMMEDIATE_NEW_STOP_SAME_BAR":
                r = (proposed - entry) / risk if direction == "BUY" else (entry - proposed) / risk
                return row(trade, scenario, "CLOSED", utc(b["time"]), proposed,
                           "NEW_TRAIL_STOP_CROSSED_SAME_BAR_PROXY", r,
                           "Assumed stop-price fill; intrabar order and actual fill are unknown")
        stop = proposed
    return row(trade, scenario, "UNRESOLVED", reason="OPEN_AT_END_OF_DATA",
               notes="trail_activated=" + str(activated) + "; same_bar_ambiguities=" + str(ambiguities) +
                     "; first_activation_utc=" + first_activation)


def metrics(rows):
    closed = [r for r in rows if r["status"] == "CLOSED"]
    rs = [float(r["r_multiple"]) for r in closed]
    wins, losses, flats = sum(x > 0 for x in rs), sum(x < 0 for x in rs), sum(x == 0 for x in rs)
    gp, gl = sum(x for x in rs if x > 0), -sum(x for x in rs if x < 0)
    return {"trades": len(rows), "closed": len(closed), "unresolved": len(rows) - len(closed),
            "wins": wins, "losses": losses, "flats": flats,
            "win_rate_pct_closed_only": round(100 * wins / len(closed), 4) if closed else None,
            "total_R_closed_only": round(sum(rs), 6),
            "average_R_closed_only": round(sum(rs) / len(rs), 6) if rs else None,
            "gross_profit_R": round(gp, 6), "gross_loss_R": round(gl, 6),
            "profit_factor_gross_R": round(gp / gl, 6) if gl else ("INF" if gp else None),
            "costs": "NOT INCLUDED", "canonical": False}


def write_csv(path, rows, empty_fields=None):
    fields = list(rows[0]) if rows else (empty_fields or ["empty"])
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        wr = csv.DictWriter(f, fieldnames=fields)
        wr.writeheader()
        wr.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bars", required=True, type=Path, help="Frozen raw M1 OHLC CSV")
    ap.add_argument("--trades", required=True, type=Path, help="Frozen activated-trail V3 trade CSV")
    ap.add_argument("--out", required=True, type=Path, help="New or empty output directory")
    ap.add_argument("--expected-sha256", default=EXPECTED_BARS_SHA256)
    args = ap.parse_args()
    if args.out.exists() and not args.out.is_dir():
        raise SystemExit("Output path is not a directory: " + str(args.out))
    if args.out.exists() and any(args.out.iterdir()):
        raise SystemExit("Refusing to overwrite non-empty output directory: " + str(args.out))
    # The previous draft created the output directory after writing CSV files.
    args.out.mkdir(parents=True, exist_ok=True)
    bars, digest, time_col = load_bars(args.bars)
    if args.expected_sha256 and digest.lower() != args.expected_sha256.lower():
        raise SystemExit("Input SHA256 mismatch: expected " + args.expected_sha256 + ", got " + digest)
    trades = load_trades(args.trades)
    ix = {b["time"]: i for i, b in enumerate(bars)}
    baseline, immediate, mismatches, events = [], [], [], []
    for n, trade in enumerate(trades, 1):
        base = simulate(bars, ix, trade, "V3_DEFER_TO_NEXT_BAR")
        alt = simulate(bars, ix, trade, "IMMEDIATE_NEW_STOP_SAME_BAR")
        baseline.append(base)
        immediate.append(alt)
        match = (trade["status"] == base["status"] and trade["exit_reason"] == base["exit_reason"] and
                 trade["exit_time_utc"] == base["exit_time_utc"])
        for key in ("exit_price", "r_multiple"):
            saved, replayed = trade.get(key, ""), base.get(key, "")
            if bool(saved) != bool(replayed):
                match = False
            elif saved and replayed:
                try:
                    if abs(float(saved) - float(replayed)) > 1.1e-7: match = False
                except ValueError:
                    match = False
        if not match:
            mismatches.append({"trade_row": n, "entry_time_utc": trade["entry_time_utc"],
                               "saved_status": trade["status"], "replayed_status": base["status"],
                               "saved_exit_time_utc": trade["exit_time_utc"], "replayed_exit_time_utc": base["exit_time_utc"],
                               "saved_exit_reason": trade["exit_reason"], "replayed_exit_reason": base["exit_reason"],
                               "saved_exit_price": trade["exit_price"], "replayed_exit_price": base["exit_price"],
                               "saved_r": trade["r_multiple"], "replayed_r": base["r_multiple"]})
        direction, entry = trade["direction"].upper(), float(trade["entry_proxy"])
        stop, target = float(trade["sl_initial"]), float(trade["target"])
        start = ix.get(ts(trade["entry_time_utc"]))
        if start is None: continue
        best, activated = entry, False
        for i in range(start + 1, len(bars)):
            b = bars[i]
            gap = i > 0 and b["time"] - bars[i - 1]["time"] > 60
            o, h, l = b["open"], b["high"], b["low"]
            if direction == "BUY":
                if (gap and (o <= stop or o >= target)) or l <= stop or h >= target: break
                best = max(best, h)
                newly = not activated and best >= entry + TRAIL_DISTANCE
                proposed = max(stop, best - TRAIL_DISTANCE) if best >= entry + TRAIL_DISTANCE else stop
                crossed, adverse = proposed > stop and l <= proposed, l
            else:
                if (gap and (o >= stop or o <= target)) or h >= stop or l <= target: break
                best = min(best, l)
                newly = not activated and best <= entry - TRAIL_DISTANCE
                proposed = min(stop, best + TRAIL_DISTANCE) if best <= entry - TRAIL_DISTANCE else stop
                crossed, adverse = proposed < stop and h >= proposed, h
            activated = activated or newly
            if crossed:
                events.append({"trade_row": n, "direction": direction, "entry_time_utc": trade["entry_time_utc"],
                               "ambiguity_bar_utc": utc(b["time"]), "first_activation_bar": newly,
                               "entry_proxy": entry, "old_stop_before_update": round(stop, 10),
                               "new_stop_after_update": round(proposed, 10), "bar_adverse_extreme": round(adverse, 10),
                               "target": target, "interpretation": "OHLC cannot establish whether new stop was crossed after trail update"})
            stop = proposed
    write_csv(args.out / "v3_replay_baseline.csv", baseline)
    write_csv(args.out / "same_bar_stop_sensitivity.csv", immediate)
    event_fields = ["trade_row", "direction", "entry_time_utc", "ambiguity_bar_utc", "first_activation_bar",
                    "entry_proxy", "old_stop_before_update", "new_stop_after_update", "bar_adverse_extreme",
                    "target", "interpretation"]
    write_csv(args.out / "same_bar_ambiguity_events.csv", events, event_fields)
    if mismatches: write_csv(args.out / "baseline_replay_mismatches.csv", mismatches)
    first_events = [e for e in events if e["first_activation_bar"]]
    summary = {
        "status": "OHLC_TRAIL_AMBIGUITY_SENSITIVITY_COMPLETE_NOT_CANONICAL", "research_only": True, "canonical": False,
        "input": {"bars_path": str(args.bars.resolve()), "bars_sha256": digest, "timestamp_column": time_col,
                  "bars": len(bars), "first_bar_utc": utc(bars[0]["time"]), "last_bar_utc": utc(bars[-1]["time"]),
                  "trades_path": str(args.trades.resolve()), "candidate_rows": len(trades),
                  "trade_variant": trades[0]["variant"], "trail_distance_price": TRAIL_DISTANCE},
        "frozen_v3_replay_check": {"rows_matching_saved_v3": len(trades) - len(mismatches),
                                   "rows_mismatching_saved_v3": len(mismatches),
                                   "status": "PASS" if not mismatches else "MISMATCH_REQUIRES_REVIEW"},
        "ambiguity_counts": {"trade_bar_events_all_trail_updates": len(events),
                             "distinct_trade_rows_with_any_event": len({e["trade_row"] for e in events}),
                             "events_on_first_activation_bar": len(first_events),
                             "distinct_trades_with_first_activation_bar_event": len({e["trade_row"] for e in first_events})},
        "scenarios": {"v3_defer_to_next_bar": metrics(baseline), "immediate_new_stop_same_bar_sensitivity": metrics(immediate)},
        "limitations": ["M1 OHLC cannot reveal intrabar high/low order.",
                        "Immediate scenario assumes the newly tightened stop is hit on the same candle if its adverse extreme crosses it.",
                        "Immediate scenario assumes stop-price fill; actual stop execution may differ, especially in fast markets or gaps.",
                        "This is sensitivity analysis, not source-confirmed execution or a canonical rule.",
                        "No spread, slippage, commission, swap, or cash P&L is included.",
                        "No frozen geometry, original V3 output, live runner, or production rule is changed."],
        "artifacts": ["v3_replay_baseline.csv", "same_bar_stop_sensitivity.csv", "same_bar_ambiguity_events.csv"] +
                     (["baseline_replay_mismatches.csv"] if mismatches else [])
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (args.out / "README.md").write_text(
        "# Activated trailing same-bar ambiguity sensitivity\n\n"
        "Research-only, OHLC-proxy, noncanonical. No source or production semantics are inferred.\n\n"
        "- Input SHA256: " + digest + "\n"
        "- Frozen V3 replay check: " + summary["frozen_v3_replay_check"]["status"] + "\n"
        "- Same-bar ambiguity events: " + str(len(events)) + "\n"
        "- Events on first activation bar: " + str(len(first_events)) + "\n\n"
        "The immediate-stop scenario assumes a newly tightened stop is hit on the same candle if the adverse extreme crosses it. "
        "M1 OHLC cannot establish that ordering or actual fill.\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "output": str(args.out.resolve()), "input_sha256": digest,
                      "candidate_rows": len(trades), "baseline_replay_check": summary["frozen_v3_replay_check"],
                      "ambiguity_counts": summary["ambiguity_counts"], "scenarios": summary["scenarios"]}, indent=2))


if __name__ == "__main__":
    main()
