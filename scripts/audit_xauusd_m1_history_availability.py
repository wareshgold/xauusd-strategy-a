"""Audit XAUUSD M1 historical availability before stability research.

Research-only utility. It does not run the Strategy A detector and does not
select any trading rule. It compares MT5 history retrieval methods and
reports coverage/gaps for the requested windows.

The audit is intentionally independent of the V2 trailing stability runner so
a history-availability failure cannot be mistaken for strategy evidence.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5


DEFAULT_WINDOWS = [
    ("2026-03-28T00:00:00Z", "2026-04-28T00:00:00Z"),
    ("2026-04-28T00:00:00Z", "2026-05-28T00:00:00Z"),
    ("2026-05-28T00:00:00Z", "2026-06-28T00:00:00Z"),
]


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def iso(ts: int | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()


def summarize_rates(rates) -> dict:
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


def range_probe(symbol: str, start: datetime, end: datetime):
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start, end)
    return rates, mt5.last_error()


def from_probe(symbol: str, end: datetime, expected_count: int):
    rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M1, end, expected_count)
    return rates, mt5.last_error()


def daily_probe(symbol: str, start: datetime, end: datetime) -> list[dict]:
    rows = []
    cursor = start
    while cursor < end:
        chunk_end = min(cursor + timedelta(days=1), end)
        rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, cursor, chunk_end)
        summary = summarize_rates(rates)
        rows.append({
            "start_utc": cursor.isoformat(),
            "end_utc": chunk_end.isoformat(),
            "count": summary["count"],
            "first_utc": summary["first_utc"],
            "last_utc": summary["last_utc"],
            "last_error": str(mt5.last_error()),
        })
        cursor = chunk_end
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mt5-path", required=True)
    ap.add_argument("--symbol", default="XAUUSD.ecn")
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

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
        windows = []

        for start_text, end_text in DEFAULT_WINDOWS:
            start = parse_ts(start_text)
            end = parse_ts(end_text)
            expected_minutes = int((end - start).total_seconds() // 60)

            range_rates, range_error = range_probe(symbol, start, end)
            from_rates, from_error = from_probe(symbol, end, expected_minutes)

            windows.append({
                "period": {
                    "start_utc": start.isoformat(),
                    "end_utc": end.isoformat(),
                    "expected_m1_minutes": expected_minutes,
                },
                "copy_rates_range": {
                    **summarize_rates(range_rates),
                    "last_error": str(range_error),
                },
                "copy_rates_from": {
                    **summarize_rates(from_rates),
                    "last_error": str(from_error),
                },
                "daily_range_probe": daily_probe(symbol, start, end),
            })

        result = {
            "status": "COMPLETE",
            "mode": "NON_CANONICAL_FORENSIC",
            "experiment": "XAUUSD_M1_HISTORY_AVAILABILITY_AUDIT",
            "symbol": symbol,
            "terminal": {
                "name": getattr(terminal, "name", None),
                "build": getattr(terminal, "build", None),
                "connected": getattr(terminal, "connected", None),
                "trade_allowed": getattr(terminal, "trade_allowed", None),
            },
            "symbol_info": {
                "point": getattr(info, "point", None),
                "digits": getattr(info, "digits", None),
                "trade_contract_size": getattr(info, "trade_contract_size", None),
            },
            "windows": windows,
            "interpretation_boundary": (
                "History availability only. No strategy signal, outcome, "
                "trailing parameter, ranking, or canonical rule is inferred."
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
