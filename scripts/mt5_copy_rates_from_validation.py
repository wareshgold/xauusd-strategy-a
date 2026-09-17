#!/usr/bin/env python3
"""Validate MT5 copy_rates_from for deterministic inclusive M1 interval retrieval.

This is a diagnostic/validation harness only. It does not shift timestamps,
fabricate candles, or write a dataset.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1


def parse_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp must include UTC offset")
    return dt.astimezone(timezone.utc).replace(second=0, microsecond=0)


def utc(ts: int) -> str:
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    args = p.parse_args()
    start = parse_utc(args.start)
    end = parse_utc(args.end)
    if end <= start:
        raise SystemExit("end must be after start")

    expected = int((end - start).total_seconds() // 60) + 1
    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"symbol_select failed: {mt5.last_error()}")

        rates = mt5.copy_rates_from(SYMBOL, TIMEFRAME, end, expected)
        result = {
            "requested_interval_utc": {
                "start": start.isoformat().replace("+00:00", "Z"),
                "end": end.isoformat().replace("+00:00", "Z"),
            },
            "expected_bar_count": expected,
            "method": "copy_rates_from",
            "symbol": SYMBOL,
            "timeframe": "M1",
            "last_error": mt5.last_error(),
        }

        if rates is None:
            result.update({"returned_bar_count": None, "status": "FAIL", "reason": "API returned None"})
            print(json.dumps(result, indent=2))
            return 1

        returned = len(rates)
        first = utc(rates[0]["time"]) if returned else None
        last = utc(rates[-1]["time"]) if returned else None
        timestamps = [int(row["time"]) for row in rates]
        chronological = all(b > a for a, b in zip(timestamps, timestamps[1:]))
        unique = len(set(timestamps)) == len(timestamps)
        contiguous = all(b - a == 60 for a, b in zip(timestamps, timestamps[1:]))
        count_match = returned == expected
        boundary_match = first == start.isoformat().replace("+00:00", "Z") and last == end.isoformat().replace("+00:00", "Z")
        status = "PASS" if all((count_match, boundary_match, chronological, unique, contiguous)) else "FAIL"

        result.update({
            "returned_bar_count": returned,
            "actual_first_utc": first,
            "actual_last_utc": last,
            "count_match": count_match,
            "boundary_match": boundary_match,
            "chronological": chronological,
            "unique_timestamps": unique,
            "one_minute_continuity": contiguous,
            "status": status,
        })
        print(json.dumps(result, indent=2))
        return 0 if status == "PASS" else 1
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
