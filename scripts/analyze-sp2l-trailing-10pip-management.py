#!/usr/bin/env python3
"""
Research-only SP2L trailing management experiment.

Does NOT change Strategy A geometry, source rules, canonical parameters,
or live execution. It compares the frozen baseline against a 10-pip
favorable-move trailing-stop variant using the archived candle-level evidence.

Interpretation frozen for this experiment:
- pip size = 0.10 price units.
- initial Entry/SL/TP are unchanged.
- once price moves favorably by at least 10 pips from entry,
  SL trails 10 pips behind the best observed favorable price.
- TP is extended in 10-pip increments whenever the favorable price
  reaches the current TP; this is a research variant, not canonical.
- M1 OHLC is used.
- If both the active SL and TP are touched in the same candle and
  ordering cannot be established from M1 OHLC, outcome is AMBIGUOUS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PIP_SIZE = 0.10


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pip_distance(price_a: float, price_b: float) -> float:
    return abs(price_a - price_b) / PIP_SIZE


def simulate(mapping, candles_by_index, trail_pips: float):
    entry = float(mapping["entry"])
    initial_sl = float(mapping["sl"])
    initial_tp = float(mapping["tp"])
    direction = mapping["direction"]
    start = int(mapping["outcome_scan_start_index"])

    trail = trail_pips * PIP_SIZE
    current_sl = initial_sl
    current_tp = initial_tp
    best = entry
    trailing_active = False
    tp_extensions = 0
    exit_price = None
    reason = None
    ambiguous = False

    i = start
    max_favorable_pips = 0.0
    min_adverse_pips = 0.0

    while i < len(candles_by_index):
        c = candles_by_index[i]
        high = float(c["high"])
        low = float(c["low"])

        if direction == "BUY":
            best = max(best, high)
            max_favorable_pips = max(max_favorable_pips, (best - entry) / PIP_SIZE)
            min_adverse_pips = min(min_adverse_pips, (low - entry) / PIP_SIZE)

            if not trailing_active and best >= entry + trail:
                trailing_active = True

            if trailing_active:
                candidate_sl = best - trail
                current_sl = max(current_sl, candidate_sl)

            while best >= current_tp:
                current_tp += trail
                tp_extensions += 1

            sl_hit = low <= current_sl
            tp_hit = high >= current_tp

            if sl_hit and tp_hit:
                ambiguous = True
                reason = "SL_AND_TP_SAME_BAR"
                exit_price = None
                break
            if sl_hit:
                reason = "TRAIL_SL" if trailing_active and current_sl > initial_sl else "SL"
                exit_price = current_sl
                break
            if tp_hit:
                reason = "TP"
                exit_price = current_tp
                break

        else:
            best = min(best, low)
            max_favorable_pips = max(max_favorable_pips, (entry - best) / PIP_SIZE)
            min_adverse_pips = min(min_adverse_pips, (entry - high) / PIP_SIZE)

            if not trailing_active and best <= entry - trail:
                trailing_active = True

            if trailing_active:
                candidate_sl = best + trail
                current_sl = min(current_sl, candidate_sl)

            while best <= current_tp:
                current_tp -= trail
                tp_extensions += 1

            sl_hit = high >= current_sl
            tp_hit = low <= current_tp

            if sl_hit and tp_hit:
                ambiguous = True
                reason = "SL_AND_TP_SAME_BAR"
                exit_price = None
                break
            if sl_hit:
                reason = "TRAIL_SL" if trailing_active and current_sl < initial_sl else "SL"
                exit_price = current_sl
                break
            if tp_hit:
                reason = "TP"
                exit_price = current_tp
                break

        i += 1

    if exit_price is None and not ambiguous:
        reason = "OPEN_OR_UNRESOLVED"

    if exit_price is not None:
        if direction == "BUY":
            realized_pips = (exit_price - entry) / PIP_SIZE
        else:
            realized_pips = (entry - exit_price) / PIP_SIZE
    else:
        realized_pips = None

    return {
        "archived_signal_index": mapping["archived_signal_index"],
        "signal_time_utc": mapping["signal_time_utc"],
        "direction": direction,
        "entry": entry,
        "initial_sl": initial_sl,
        "initial_tp": initial_tp,
        "initial_risk_price": abs(entry - initial_sl),
        "initial_risk_pips": pip_distance(entry, initial_sl),
        "trail_pips": trail_pips,
        "final_sl": current_sl,
        "final_tp": current_tp,
        "tp_extensions": tp_extensions,
        "trailing_activated": trailing_active,
        "max_favorable_pips": max_favorable_pips,
        "min_adverse_pips": min_adverse_pips,
        "exit_price": exit_price,
        "reason": reason,
        "ambiguous": ambiguous,
        "realized_pips": realized_pips,
    }


def summarize(rows):
    decisive = [r for r in rows if r["realized_pips"] is not None and not r["ambiguous"]]
    wins = [r for r in decisive if r["realized_pips"] > 0]
    losses = [r for r in decisive if r["realized_pips"] < 0]
    breakeven = [r for r in decisive if r["realized_pips"] == 0]
    gross_profit = sum(r["realized_pips"] for r in wins)
    gross_loss = abs(sum(r["realized_pips"] for r in losses))
    net = sum(r["realized_pips"] for r in decisive)

    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for r in rows:
        if r["realized_pips"] is None:
            continue
        equity += r["realized_pips"]
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)

    pf = gross_profit / gross_loss if gross_loss else None
    return {
        "signals": len(rows),
        "decisive": len(decisive),
        "wins": len(wins),
        "losses": len(losses),
        "breakeven": len(breakeven),
        "ambiguous": sum(1 for r in rows if r["ambiguous"]),
        "open_or_unresolved": sum(1 for r in rows if r["reason"] == "OPEN_OR_UNRESOLVED"),
        "win_rate_decisive_pct": (len(wins) / len(decisive) * 100) if decisive else None,
        "gross_profit_pips": gross_profit,
        "gross_loss_pips_abs": gross_loss,
        "net_pips": net,
        "profit_factor": pf,
        "max_drawdown_pips": max_dd,
        "avg_win_pips": (gross_profit / len(wins)) if wins else None,
        "avg_loss_pips_abs": (gross_loss / len(losses)) if losses else None,
        "avg_tp_extensions": (
            sum(r["tp_extensions"] for r in rows) / len(rows) if rows else None
        ),
        "trailing_activated_count": sum(1 for r in rows if r["trailing_activated"]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--candle-evidence",
        default="artifacts/SP2L_candle_level_evidence_2026-09-14_2026-09-18.json",
    )
    ap.add_argument(
        "--signal-artifact",
        default="artifacts/SP2L_author_replica_2026-09-14_2026-09-18.json",
    )
    ap.add_argument("--trail-pips", type=float, default=10.0)
    ap.add_argument(
        "--output",
        default="artifacts/SP2L_trailing_10pip_management_experiment_2026-09-14_2026-09-18.json",
    )
    args = ap.parse_args()

    candle_path = Path(args.candle_evidence)
    signal_path = Path(args.signal_artifact)
    output_path = Path(args.output)

    evidence = json.loads(candle_path.read_text(encoding="utf-8"))
    signal_artifact = json.loads(signal_path.read_text(encoding="utf-8"))

    candles = evidence["candles"]
    candles_by_index = candles
    mappings = evidence["signal_mappings"]

    rows = []
    for mapping in mappings:
        rows.append(simulate(mapping, candles_by_index, args.trail_pips))

    baseline = {}
    for s in signal_artifact["signals"]:
        if s["outcome"] in ("WIN", "LOSS"):
            move = (
                (float(s["exit_price"]) - float(s["entry"])) / PIP_SIZE
                if s["direction"] == "BUY"
                else (float(s["entry"]) - float(s["exit_price"])) / PIP_SIZE
            )
            baseline.setdefault("rows", []).append(move)

    output = {
        "research_only": True,
        "experiment": "10_PIP_TRAILING_MANAGEMENT",
        "canonicalization_guard": "RESEARCH_ONLY; NO_STRATEGY_RULE_OR_PARAMETER_PROMOTION",
        "interpretation": {
            "pip_size_price_units": PIP_SIZE,
            "trail_pips": args.trail_pips,
            "trail_price_units": args.trail_pips * PIP_SIZE,
            "description": (
                "After favorable movement reaches trail distance, SL trails "
                "10 pips behind the best observed M1 price; TP extends by "
                "10 pips whenever the current TP is reached."
            ),
            "same_bar_policy": "AMBIGUOUS_WHEN_SL_AND_TP_BOTH_TOUCHED",
        },
        "input_hashes": {
            "candle_evidence_sha256": sha256_file(candle_path),
            "signal_artifact_sha256": sha256_file(signal_path),
        },
        "baseline_archived": {
            "signals": len(signal_artifact["signals"]),
            "decisive": sum(
                1 for s in signal_artifact["signals"] if s["outcome"] in ("WIN", "LOSS")
            ),
            "net_pips": sum(baseline.get("rows", [])),
            "max_drawdown_pips": None,
        },
        "trailing_summary": summarize(rows),
        "trades": rows,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": "ANALYZED",
        "output": str(output_path),
        "trail_pips": args.trail_pips,
        "summary": output["trailing_summary"],
        "input_sha256": output["input_hashes"],
    }, indent=2))


if __name__ == "__main__":
    main()
