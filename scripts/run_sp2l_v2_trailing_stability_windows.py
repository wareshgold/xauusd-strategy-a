"""Research-only V2 trailing stability windows.

Runs the exact V2 population/exit engine over non-overlapping time windows.
Trailing remains NON_CANONICAL_FORENSIC. This script does not select or
promote any parameter.

Default windows are the three months immediately preceding the current
3-month reference period:
  2026-03-28..2026-04-28
  2026-04-28..2026-05-28
  2026-05-28..2026-06-28

The comparison set is RR=1 with trailing OFF, 10, 20, 30 and 50 pips.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
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


def run_window(symbol, rates, trails, contract_size, volume):
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
        for start_text, end_text in DEFAULT_WINDOWS:
            start = parse_ts(start_text)
            end = parse_ts(end_text)
            rates = fetch_rates(symbol, start, end)
            population, variants = run_window(
                symbol, rates, DEFAULT_TRAILS, contract_size, args.volume
            )
            windows.append({
                "period": {"start_utc": start.isoformat(), "end_utc": end.isoformat()},
                "bars": int(len(rates)),
                "population_signals": len(population),
                "variants": variants,
            })

        result = {
            "status": "COMPLETE",
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
            "windows": windows,
            "interpretation_boundary": (
                "Pre-baseline stability evidence only. No trailing variant is "
                "selected, ranked, canonicalized, or treated as a production rule."
            ),
        }

        text = json.dumps(result, indent=2)
        if args.output:
            path = Path(args.output)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text + "\n", encoding="utf-8")
        print(text)
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
