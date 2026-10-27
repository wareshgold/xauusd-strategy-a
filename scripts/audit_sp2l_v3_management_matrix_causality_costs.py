#!/usr/bin/env python3
"""Read-only causal replay and spread/commission sensitivity for the SP2L V3 management matrix.

Replays the existing management simulator against the same M1 bars, compares
replayed trade paths with the saved CSV, then estimates P&L after historical
M1 spread proxies and explicit round-turn commission scenarios. Research only.
It does not change canonical rules, input files, or a live runner.
"""
from __future__ import annotations
import argparse, csv, json, math
from collections import defaultdict
from datetime import datetime
from pathlib import Path

def num(row, key, default=None):
    raw = row.get(key)
    if raw is None or str(raw).strip() == "":
        return default
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError(f"Non-finite {key}: {raw}")
    return value

def epoch(raw):
    raw = str(raw or "").strip()
    if not raw:
        return None
    if raw.isdigit() or (raw.startswith("-") and raw[1:].isdigit()):
        return int(raw)
    dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"Timestamp lacks timezone: {raw}")
    return int(dt.timestamp())

def read_bars(path):
    by_time = {}
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        names = {x.strip().lower(): x for x in (reader.fieldnames or [])}
        if "time" not in names and "timestamp" in names:
            names["time"] = names["timestamp"]
        missing = {"time", "open", "high", "low", "close"} - set(names)
        if missing:
            raise ValueError(f"Bars CSV missing columns: {sorted(missing)}")
        spread_key = names.get("spread")
        for line, row in enumerate(reader, 2):
            ts = epoch(row[names["time"]])
            if ts is None:
                raise ValueError(f"Missing bar time at row {line}")
            by_time[ts] = {
                "time": ts,
                "open": float(row[names["open"]]),
                "high": float(row[names["high"]]),
                "low": float(row[names["low"]]),
                "close": float(row[names["close"]]),
                "spread_points": float(row[spread_key]) if spread_key and row.get(spread_key) not in (None, "") else None,
            }
    return sorted(by_time.values(), key=lambda x: x["time"])

def truth(value):
    return str(value or "").strip().lower() in {"true", "1", "yes"}

def replay(bars, idx_by_time, row):
    direction = row["direction"]
    mode = row["scenario"]
    entry = num(row, "entry")
    initial_sl = num(row, "initial_sl")
    tp = num(row, "initial_tp")
    risk = num(row, "risk_price")
    activation_r = num(row, "activation_R")
    distance_r = num(row, "trail_distance_R")
    partial_r = num(row, "partial_tp_R")
    entry_ts = epoch(row.get("entry_time") or row.get("trigger_time"))
    if entry_ts not in idx_by_time:
        return {"missing_entry_bar": True}
    entry_idx = idx_by_time[entry_ts]
    sl = initial_sl
    activated = False
    partial = False
    partial_contribution = 0.0
    part_fraction = 0.5 if mode == "PARTIAL_RUNNER" else 0.0
    runner_fraction = 1.0 - part_fraction
    target = None
    if partial_r is not None:
        target = entry + (partial_r*risk if direction == "BUY" else -partial_r*risk)
    result = {
        "exit_time": None, "exit_price": None, "reason": "OPEN_OR_UNRESOLVED",
        "ambiguous": False, "realized_R": None, "final_sl": sl,
        "trailing_activated": False, "partial_done": False,
    }
    for k in range(entry_idx + 1, len(bars)):
        b = bars[k]
        hi, lo, op = b["high"], b["low"], b["open"]
        hit_sl = lo <= sl if direction == "BUY" else hi >= sl
        hit_tp = (hi >= tp if direction == "BUY" else lo <= tp) if mode == "FIXED_TP" else False
        hit_part = target is not None and not partial and (hi >= target if direction == "BUY" else lo <= target)
        if hit_sl and (hit_tp or hit_part):
            result.update(ambiguous=True, reason="SL_AND_TARGET_SAME_BAR", exit_time=b["time"])
            break
        if hit_sl:
            fill = sl
            if direction == "BUY" and op < sl:
                fill = op
            if direction == "SELL" and op > sl:
                fill = op
            stop_r = (fill-entry)/risk if direction == "BUY" else (entry-fill)/risk
            remaining_fraction = runner_fraction if partial else 1.0
            result.update(exit_price=fill, realized_R=partial_contribution+remaining_fraction*stop_r,
                          exit_time=b["time"], reason="TRAIL_SL" if activated and sl != initial_sl else "SL")
            break
        if hit_tp:
            result.update(exit_price=tp, realized_R=((tp-entry)/risk if direction == "BUY" else (entry-tp)/risk),
                          exit_time=b["time"], reason="TP")
            break
        if hit_part:
            partial_contribution = part_fraction * partial_r
            partial = True
            result["partial_done"] = True
            continue
        if mode in ("RUNNER", "PARTIAL_RUNNER"):
            favorable = hi-entry if direction == "BUY" else entry-lo
            if activation_r is not None and favorable >= activation_r*risk:
                offset = distance_r*risk
                proposed = hi-offset if direction == "BUY" else lo+offset
                if direction == "BUY" and sl < proposed < hi:
                    sl = proposed
                    activated = True
                elif direction == "SELL" and lo < proposed < sl:
                    sl = proposed
                    activated = True
    result["final_sl"] = sl
    result["trailing_activated"] = activated
    result["partial_done"] = partial
    return result

def close_enough(a, b, tol=1e-6):
    if a is None or b is None:
        return a is None and b is None
    return abs(float(a)-float(b)) <= tol * max(1.0, abs(float(a)), abs(float(b)))

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--trades-csv", required=True, type=Path)
    ap.add_argument("--bars-csv", required=True, type=Path)
    ap.add_argument("--output-json", required=True, type=Path)
    ap.add_argument("--point-price", type=float, default=0.01)
    ap.add_argument("--volume-lots", type=float, default=0.01)
    ap.add_argument("--contract-size", type=float, default=100.0)
    ap.add_argument("--commission-per-lot-round-turn", type=float, nargs="+", default=[0.0, 7.0, 14.0],
                    help="explicit sensitivity values in USD per lot round turn; not claimed to be broker actual")
    args = ap.parse_args()
    if args.output_json.exists():
        raise FileExistsError(f"Refusing to overwrite: {args.output_json}")
    if min(args.point_price, args.volume_lots, args.contract_size) <= 0:
        raise ValueError("point, volume and contract size must be positive")
    if any((not math.isfinite(x) or x < 0) for x in args.commission_per_lot_round_turn):
        raise ValueError("commission scenarios must be finite and >= 0")

    bars = read_bars(args.bars_csv)
    by_time = {b["time"]: i for i, b in enumerate(bars)}
    with args.trades_csv.open(newline="", encoding="utf-8-sig") as f:
        trades = list(csv.DictReader(f))
    required = {"scenario","direction","entry","initial_sl","risk_price","entry_time","exit_time",
                "exit_price","final_sl","reason","realized_R","ambiguous"}
    missing = required - set(trades[0] if trades else [])
    if missing:
        raise ValueError(f"Trades CSV missing columns: {sorted(missing)}")

    grouped = defaultdict(list)
    mismatches = []
    missing_entry = 0
    missing_exit = 0
    cost_rows = []
    for line, row in enumerate(trades, 2):
        replayed = replay(bars, by_time, row)
        if replayed.get("missing_entry_bar"):
            missing_entry += 1
            mismatches.append({"csv_row": line, "scenario": row["scenario"], "issue": "entry bar missing"})
            continue
        fields = ["exit_time","exit_price","reason","ambiguous","realized_R","final_sl","trailing_activated","partial_done"]
        diffs = []
        for field in fields:
            stored = row.get(field)
            actual = replayed.get(field)
            if field in ("exit_time",):
                stored = epoch(stored) if stored not in (None, "") else None
                actual = int(actual) if actual is not None else None
                same = stored == actual
            elif field in ("reason",):
                same = str(stored or "") == str(actual or "")
            elif field in ("ambiguous","trailing_activated","partial_done"):
                same = truth(stored) == bool(actual)
            else:
                sv = num(row, field)
                av = actual
                same = close_enough(sv, av)
            if not same:
                diffs.append({"field": field, "stored": stored, "replayed": actual})
        if diffs:
            mismatches.append({"csv_row": line, "scenario": row["scenario"], "trigger_time": row.get("trigger_time"), "diffs": diffs[:8]})

        if truth(row.get("ambiguous")) or num(row, "realized_R") is None:
            continue
        entry_ts = epoch(row.get("entry_time") or row.get("trigger_time"))
        exit_ts = epoch(row.get("exit_time"))
        if exit_ts not in by_time or entry_ts not in by_time:
            missing_exit += int(exit_ts not in by_time)
            continue
        entry_bar, exit_bar = bars[by_time[entry_ts]], bars[by_time[exit_ts]]
        spread_entry, spread_exit = entry_bar["spread_points"], exit_bar["spread_points"]
        # M1 spread is a proxy, not tick-exact fill evidence. For bid-based OHLC,
        # BUY pays spread on entry; SELL pays spread on exit. If a SELL partially
        # closes 50% at target, weight the spread at that partial bar and final exit.
        spread_cost_usd = None
        if spread_entry is not None and spread_exit is not None:
            if row["direction"] == "BUY":
                spread_price_points = spread_entry
            else:
                partial_spread = None
                partial_r = num(row, "partial_tp_R")
                if truth(row.get("partial_done")) and partial_r is not None:
                    target = num(row, "entry") - partial_r * num(row, "risk_price")
                    for b in bars[by_time[entry_ts] + 1:by_time[exit_ts] + 1]:
                        if b["low"] <= target:
                            partial_spread = b["spread_points"]
                            break
                if partial_spread is not None:
                    spread_price_points = 0.5 * partial_spread + 0.5 * spread_exit
                else:
                    spread_price_points = spread_exit
            spread_cost_usd = spread_price_points * args.point_price * args.volume_lots * args.contract_size
        risk = num(row, "risk_price")
        gross_usd = num(row, "realized_R") * risk * args.volume_lots * args.contract_size
        commission_results = {}
        for commission_per_lot in args.commission_per_lot_round_turn:
            commission_usd = commission_per_lot * args.volume_lots
            total_cost = None if spread_cost_usd is None else spread_cost_usd + commission_usd
            commission_results[str(commission_per_lot)] = {
                "commission_usd": commission_usd,
                "spread_cost_usd": spread_cost_usd,
                "total_cost_usd": total_cost,
                "net_usd": None if total_cost is None else gross_usd-total_cost,
            }
        enriched = dict(row)
        enriched["_gross_usd"] = gross_usd
        enriched["_spread_cost_usd"] = spread_cost_usd
        enriched["_commission_results"] = commission_results
        grouped[(row["scenario"], row.get("activation_R",""), row.get("trail_distance_R",""), row.get("partial_tp_R",""))].append(enriched)

    summaries = []
    for key, rows in grouped.items():
        out = {"scenario": key[0], "activation_R": key[1] or None, "trail_distance_R": key[2] or None,
               "partial_tp_R": key[3] or None, "closed_decisive": len(rows)}
        out["gross_net_usd"] = sum(r["_gross_usd"] for r in rows)
        out["spread_cost_usd"] = sum(r["_spread_cost_usd"] for r in rows if r["_spread_cost_usd"] is not None)
        out["spread_missing_count"] = sum(r["_spread_cost_usd"] is None for r in rows)
        out["gross_net_R"] = sum(num(r, "realized_R") for r in rows)
        for commission_per_lot in args.commission_per_lot_round_turn:
            tag = str(commission_per_lot)
            vals = [r["_commission_results"][tag]["net_usd"] for r in rows]
            if any(v is None for v in vals):
                net = None
                cost = None
            else:
                net = sum(vals)
                cost = sum(r["_commission_results"][tag]["total_cost_usd"] for r in rows)
            out[f"net_usd_commission_{tag}_per_lot_rt"] = net
            out[f"total_cost_usd_commission_{tag}_per_lot_rt"] = cost
        summaries.append(out)
    commission_top = {}
    for commission_per_lot in args.commission_per_lot_round_turn:
        field = f"net_usd_commission_{str(commission_per_lot)}_per_lot_rt"
        ranked = sorted((s for s in summaries if s[field] is not None), key=lambda s: s[field], reverse=True)
        commission_top[str(commission_per_lot)] = ranked[:3]

    payload = {
        "status": "COMPLETE",
        "research_only": True,
        "causal_replay": {
            "trade_rows": len(trades),
            "mismatch_count": len(mismatches),
            "mismatch_sample": mismatches[:100],
            "missing_entry_bar_count": missing_entry,
            "missing_exit_bar_count": missing_exit,
            "method": "replay saved M1 management logic; new trailing stop only becomes eligible on following bar; adverse-open stop fill; same-bar stop/target ambiguous",
            "limitation": "M1 OHLC cannot prove tick-level fill order or broker execution",
        },
        "cost_model": {
            "point_price": args.point_price, "volume_lots": args.volume_lots, "contract_size": args.contract_size,
            "spread_proxy": "MT5 M1 spread points; BUY charges entry-bar spread; SELL charges exit-bar spread, or 50/50 partial-target/final-exit spreads for a partial close; multiplied by point*lots*contract size",
            "commission_sensitivity_usd_per_lot_round_turn": args.commission_per_lot_round_turn,
            "commission_is_not_broker_confirmed": True,
            "excludes": ["swap", "slippage", "latency", "spread widening between M1 sampling points"],
            "ambiguous_and_unresolved": "excluded from P&L; not assigned guessed outcomes",
        },
        "input_rows": len(trades), "bars": len(bars), "scenario_count": len(summaries),
        "scenarios": summaries, "top3_by_net_usd_each_commission_assumption": commission_top,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "trade_rows": len(trades),
        "causal_replay_mismatches": len(mismatches),
        "missing_entry_bars": missing_entry,
        "missing_exit_bars": missing_exit,
        "bars_have_spread": any(b["spread_points"] is not None for b in bars),
        "report": str(args.output_json),
        "top3_by_commission_sensitivity": commission_top,
        "mismatch_sample": mismatches[:12],
        "limitations": payload["cost_model"]["excludes"],
    }, indent=2))

if __name__ == "__main__":
    main()
