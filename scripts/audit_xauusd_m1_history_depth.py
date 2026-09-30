"""Audit the actual depth of XAUUSD M1 history exposed by the MT5 terminal.

Research-only utility. It does not run Strategy A and does not infer any
strategy rule. It uses copy_rates_from_pos starting at the newest M1 bar to
measure the oldest bar the terminal currently exposes, then reports internal
gaps and terminal max-bars metadata.

This exists because copy_rates_range can return a misleading successful
response when the requested period predates the available history.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5


def iso(ts: int | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()


def summarize(rates) -> dict:
    if rates is None or len(rates) == 0:
        return {
            "count": 0,
            "first_utc": None,
            "last_utc": None,
            "span_minutes": 0,
            "missing_minutes_inside_span": None,
            "max_gap_minutes": None,
        }
    times = sorted({int(x["time"]) for x in rates})
    diffs = [(b - a) // 60 for a, b in zip(times, times[1:])]
    gaps = [d for d in diffs if d > 1]
    return {
        "count": len(times),
        "first_utc": iso(times[0]),
        "last_utc": iso(times[-1]),
        "span_minutes": (times[-1] - times[0]) // 60,
        "missing_minutes_inside_span": sum(d - 1 for d in gaps),
        "max_gap_minutes": max(gaps) if gaps else 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mt5-path", required=True)
    ap.add_argument("--symbol", default="XAUUSD.ecn")
    ap.add_argument("--count", type=int, default=1_000_000)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    if args.count <= 0:
        raise SystemExit("--count must be positive")

    if not mt5.initialize(path=args.mt5_path):
        print(json.dumps({
            "status": "MT5_INIT_FAILED",
            "error": str(mt5.last_error()),
        }, indent=2))
        return 2

    try:
        symbol = args.symbol
        if not mt5.symbol_select(symbol, True):
            print(json.dumps({
                "status": "SYMBOL_SELECT_FAILED",
                "symbol": symbol,
                "error": str(mt5.last_error()),
            }, indent=2))
            return 2

        info = mt5.symbol_info(symbol)
        terminal = mt5.terminal_info()
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, args.count)
        error = mt5.last_error()
        summary = summarize(rates)

        result = {
            "status": "COMPLETE",
            "mode": "NON_CANONICAL_FORENSIC",
            "experiment": "XAUUSD_M1_HISTORY_DEPTH_AUDIT",
            "symbol": symbol,
            "request": {
                "timeframe": "M1",
                "start_pos": 0,
                "requested_count": args.count,
            },
            "terminal": {
                "name": getattr(terminal, "name", None),
                "build": getattr(terminal, "build", None),
                "connected": getattr(terminal, "connected", None),
                "trade_allowed": getattr(terminal, "trade_allowed", None),
                "maxbars": getattr(terminal, "maxbars", None),
            },
            "symbol_info": {
                "point": getattr(info, "point", None),
                "digits": getattr(info, "digits", None),
                "trade_contract_size": getattr(info, "trade_contract_size", None),
            },
            "history": {
                **summary,
                "last_error": str(error),
            },
            "interpretation_boundary": (
                "This measures history exposed by the connected MT5 terminal only. "
                "It does not establish broker-wide historical availability and "
                "does not infer any strategy signal, outcome, trailing parameter, "
                "ranking, or canonical rule."
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
