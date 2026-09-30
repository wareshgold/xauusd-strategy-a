"""Audit XAUUSD M1 history depth using bounded MT5 retrieval probes.

Research-only. No Strategy A signal or rule is inferred.

Some MT5 terminals reject a large copy_rates_from_pos request even when
terminal_info.maxbars reports the nominal chart limit. This utility therefore
probes descending request sizes and records the largest successful retrieval,
rather than assuming maxbars is a valid API count.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5


PROBE_COUNTS = [100000, 50000, 20000, 10000, 5000, 2000, 1000, 500, 100]


def iso(ts: int | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()


def summarize(rates) -> dict:
    if rates is None or len(rates) == 0:
        return {"count": 0, "first_utc": None, "last_utc": None,
                "span_minutes": 0, "missing_minutes_inside_span": None,
                "max_gap_minutes": None}
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
    ap.add_argument("--count", type=int, default=100000)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    if args.count <= 0:
        raise SystemExit("--count must be positive")
    if not mt5.initialize(path=args.mt5_path):
        print(json.dumps({"status": "MT5_INIT_FAILED",
                          "error": str(mt5.last_error())}, indent=2))
        return 2

    try:
        symbol = args.symbol
        if not mt5.symbol_select(symbol, True):
            print(json.dumps({"status": "SYMBOL_SELECT_FAILED",
                              "symbol": symbol,
                              "error": str(mt5.last_error())}, indent=2))
            return 2

        info = mt5.symbol_info(symbol)
        terminal = mt5.terminal_info()
        maxbars = getattr(terminal, "maxbars", None)
        candidates = sorted(
            {min(args.count, int(x)) for x in PROBE_COUNTS if int(x) > 0},
            reverse=True,
        )

        probes = []
        successful_rates = None
        successful_count = None

        for count in candidates:
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, count)
            error = str(mt5.last_error())
            row = {
                "requested_count": count,
                "returned_count": 0 if rates is None else len(rates),
                "last_error": error,
                "success": rates is not None and len(rates) > 0,
            }
            probes.append(row)
            if row["success"]:
                successful_rates = rates
                successful_count = count
                break

        summary = summarize(successful_rates)
        result = {
            "status": "COMPLETE" if successful_rates is not None else "NO_RETRIEVABLE_M1",
            "mode": "NON_CANONICAL_FORENSIC",
            "experiment": "XAUUSD_M1_HISTORY_DEPTH_AUDIT",
            "symbol": symbol,
            "request": {
                "requested_count": args.count,
                "probe_counts": candidates,
                "successful_request_count": successful_count,
            },
            "terminal": {
                "name": getattr(terminal, "name", None),
                "build": getattr(terminal, "build", None),
                "connected": getattr(terminal, "connected", None),
                "trade_allowed": getattr(terminal, "trade_allowed", None),
                "maxbars": maxbars,
            },
            "symbol_info": {
                "point": getattr(info, "point", None),
                "digits": getattr(info, "digits", None),
                "trade_contract_size": getattr(info, "trade_contract_size", None),
            },
            "probes": probes,
            "history": summary,
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
