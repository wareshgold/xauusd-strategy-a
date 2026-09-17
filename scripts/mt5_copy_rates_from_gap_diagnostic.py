#!/usr/bin/env python3
"""Inspect exact timestamps returned by MT5 copy_rates_from.

Diagnostic only: no timestamp shifting, filling, interpolation, or dataset writes.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone, timedelta

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1


def parse_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp must include UTC offset")
    return dt.astimezone(timezone.utc).replace(second=0, microsecond=0)


def fmt(epoch: int) -> str:
    return datetime.fromtimestamp(int(epoch), tz=timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    args = p.parse_args()
    start, end = parse_utc(args.start), parse_utc(args.end)
    expected = int((end - start).total_seconds() // 60) + 1

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        mt5.symbol_select(SYMBOL, True)
        rates = mt5.copy_rates_from(SYMBOL, TIMEFRAME, end, expected)
        if rates is None:
            print(json.dumps({"status": "FAIL", "reason": "API returned None", "last_error": mt5.last_error()}, indent=2))
            return 1

        epochs = [int(r["time"]) for r in rates]
        requested_epochs = list(range(int(start.timestamp()), int(end.timestamp()) + 60, 60))
        returned_set = set(epochs)
        requested_set = set(requested_epochs)
        in_range = [e for e in epochs if int(start.timestamp()) <= e <= int(end.timestamp())]
        missing_requested = [fmt(e) for e in requested_epochs if e not in returned_set]
        extra_before = [fmt(e) for e in epochs if e < int(start.timestamp())]
        extra_after = [fmt(e) for e in epochs if e > int(end.timestamp())]
        jumps = []
        for a, b in zip(epochs, epochs[1:]):
            if b - a != 60:
                jumps.append({"from": fmt(a), "to": fmt(b), "delta_seconds": b - a})

        result = {
            "requested_interval_utc": {"start": fmt(int(start.timestamp())), "end": fmt(int(end.timestamp()))},
            "expected_requested_bar_count": expected,
            "returned_bar_count": len(epochs),
            "actual_first_utc": fmt(epochs[0]) if epochs else None,
            "actual_last_utc": fmt(epochs[-1]) if epochs else None,
            "returned_inside_requested_interval": len(in_range),
            "missing_requested_bar_count": len(missing_requested),
            "missing_requested_bars_utc": missing_requested,
            "extra_before_requested_interval_count": len(extra_before),
            "extra_before_requested_interval_first_utc": extra_before[0] if extra_before else None,
            "extra_before_requested_interval_last_utc": extra_before[-1] if extra_before else None,
            "extra_after_requested_interval_count": len(extra_after),
            "timestamp_jumps_count": len(jumps),
            "timestamp_jumps": jumps,
            "requested_set_equals_returned_set": requested_set == returned_set,
            "last_error": mt5.last_error(),
            "status": "PASS" if requested_set == returned_set and not jumps else "FAIL",
        }
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "PASS" else 1
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
