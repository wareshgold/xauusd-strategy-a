"""Research-only V2 trailing stability windows.

Runs the exact V2 population/exit engine over non-overlapping time windows.
Trailing remains NON_CANONICAL_FORENSIC. This script does not select or
promote any parameter.

The runner now refuses to produce strategy results when MT5 history does not
cover the requested window. This prevents a successful-but-truncated
copy_rates_range response from being interpreted as a zero-signal window.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

from mt5_terminal_resolver import find_mt5_terminal
from run_sp2l_v2_xauusd_3month_rr_trailing_matrix import (
    build_population,
    fetch_rates,
    parse_ts,
    resolve_xauusd,
    simulate,
    summarize,
)


DEFAULT_WINDOWS = [
    ("2026-03-28T00:00:00Z", "2026-04-28T00:00:00Z"),
    ("2026-04-28T00:00:00Z", "2026-05-28T00:00:00Z"),
    ("2026-05-28T00:00:00Z", "2026-06-28T00:00:00Z"),
]
DEFAULT_TRAILS = [0.0, 10.0, 20.0, 30.0, 50.0]
HISTORY_EDGE_TOLERANCE = timedelta(days=3)


def history_coverage(rates, start, end):
    if rates is None or len(rates) == 0:
        return {
            "sufficient": False,
            "reason": "NO_M1_HISTORY",
            "bars": 0,
            "first_utc": None,
            "last_utc": None,
        }

    times = sorted({int(row["time"]) for row in rates})
    first = datetime.fromtimestamp(times[0], tz=timezone.utc)
    last = datetime.fromtimestamp(times[-1], tz=timezone.utc)
    leading = max(0.0, (first - start).total_seconds())
    trailing = max(0.0, (end - last).total_seconds())
    sufficient = (
        first <= start + HISTORY_EDGE_TOLERANCE
        and last >= end - HISTORY_EDGE_TOLERANCE
    )
    reason = "SUFFICIENT_EDGE_COVERAGE" if sufficient else "TRUNCATED_HISTORY"
    return {
        "sufficient": sufficient,
        "reason": reason,
        "bars": int(len(times)),
        "first_utc": first.isoformat(),
        "last_utc": last.isoformat(),
        "leading_uncovered_minutes": int(leading // 60),
        "trailing_uncovered_minutes": int(trailing // 60),
    }


def run_window(rates, trails, contract_size, volume):
    population = build_population(rates)
    variants = []
    for trail_pips in trails:
        rows = []
        for signal in population:
            outcome = simulate(rates, signal, 1.0, trail_pips)
            rows.append({
                **signal,
                "rr": 1.0,
                "trail_pips": trail_pips,
                **outcome,
                "risk_usd": float(signal["risk"]) * contract_size * volume,
                "pnl_usd": (
                    float(outcome["r"]) * float(signal["risk"]) * contract_size * volume
                    if outcome["r"] is not None else None
                ),
                "exit_time": (
                    int(rates[outcome["exit_index"]]["time"])
                    if outcome["exit_index"] is not None else None
                ),
            })
        variants.append({
            "trail_pips": trail_pips,
            "summary": summarize(rows, contract_size, volume),
        })
    return population, variants


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mt5-path", default=None)
    ap.add_argument("--volume", type=float, default=0.01)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    initialized = mt5.initialize(path=str(args.mt5_path)) if args.mt5_path else mt5.initialize()
    if not initialized:
        terminal = None if args.mt5_path else find_mt5_terminal()
        if terminal is None or not mt5.initialize(path=str(terminal)):
            print(json.dumps({"status": "MT5_INIT_FAILED", "error": mt5.last_error()}, indent=2))
            return 2

    try:
        symbol = resolve_xauusd()
        info = mt5.symbol_info(symbol)
        if info is None:
            raise RuntimeError(f"symbol_info failed: {symbol}: {mt5.last_error()}")
        contract_size = float(info.trade_contract_size)

        windows = []
        insufficient = []
        for start_text, end_text in DEFAULT_WINDOWS:
            start = parse_ts(start_text)
            end = parse_ts(end_text)
            rates = fetch_rates(symbol, start, end)
            coverage = history_coverage(rates, start, end)

            window = {
                "period": {
                    "start_utc": start.isoformat(),
                    "end_utc": end.isoformat(),
                },
                "history_coverage": coverage,
            }

            if coverage["sufficient"]:
                population, variants = run_window(
                    rates, DEFAULT_TRAILS, contract_size, args.volume
                )
                window.update({
                    "bars": int(len(rates)),
                    "population_signals": len(population),
                    "variants": variants,
                })
            else:
                window.update({
                    "bars": int(len(rates)),
                    "population_signals": None,
                    "variants": None,
                })
                insufficient.append({
                    "period": window["period"],
                    "reason": coverage["reason"],
                })

            windows.append(window)

        status = "COMPLETE" if not insufficient else "HISTORY_INSUFFICIENT"
        result = {
            "status": status,
            "mode": "NON_CANONICAL_FORENSIC",
            "experiment": "V2_XAUUSD_RR1_TRAILING_PRE_BASELINE_STABILITY_WINDOWS",
            "population_contract": {
                "detector": "sp2l_strategy_a_v2_detector.py",
                "p_gap_price": 1.0,
                "spike_multiplier": 1.5,
                "max_sl_distance": 10.0,
                "session_filter": False,
                "entry_policy": "V2 detector first entry",
                "initial_sl_policy": "V2 detector unchanged",
            },
            "comparison": {
                "rr": 1.0,
                "trail_pips": DEFAULT_TRAILS,
                "volume_lots": args.volume,
                "contract_size": contract_size,
                "usd_pnl_formula": "R * abs(entry-initial_sl) * contract_size * volume",
            },
            "history_policy": {
                "edge_tolerance_days": 3,
                "behavior": (
                    "Do not calculate signals/outcomes for a window unless the "
                    "returned M1 history reaches both requested edges within tolerance."
                ),
            },
            "windows": windows,
            "insufficient_windows": insufficient,
            "interpretation_boundary": (
                "Pre-baseline stability evidence only. No trailing variant is "
                "selected, ranked, canonicalized, or treated as a production rule. "
                "Insufficient history produces no zero-signal strategy evidence."
            ),
        }

        text = json.dumps(result, indent=2)
        if args.output:
            path = Path(args.output)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text + "\n", encoding="utf-8")
        print(text)
        return 0 if not insufficient else 3
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
