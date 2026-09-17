#!/usr/bin/env python3
"""Probe repeated MT5 M1 availability around a suspected daily boundary.

Diagnostic only. No timestamp shifting, filling, interpolation, or dataset writes.
The purpose is to determine whether the observed missing interval repeats across
multiple dates and whether both retrieval methods agree on the available bars.
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


def inspect(method: str, start: datetime, end: datetime):
    expected = int((end - start).total_seconds() // 60) + 1
    if method == "copy_rates_range":
        rates = mt5.copy_rates_range(SYMBOL, TIMEFRAME, start, end)
    else:
        rates = mt5.copy_rates_from(SYMBOL, TIMEFRAME, end, expected)

    if rates is None:
        return {"method": method, "status": "FAIL", "reason": "API returned None", "last_error": mt5.last_error()}

    epochs = [int(r["time"]) for r in rates]
    requested = list(range(int(start.timestamp()), int(end.timestamp()) + 60, 60))
    requested_set = set(requested)
    returned_set = set(epochs)
    jumps = []
    for a, b in zip(epochs, epochs[1:]):
        if b - a != 60:
            jumps.append({"from": fmt(a), "to": fmt(b), "delta_seconds": b - a})

    missing = [fmt(e) for e in requested if e not in returned_set]
    extra_before = [fmt(e) for e in epochs if e < int(start.timestamp())]
    extra_after = [fmt(e) for e in epochs if e > int(end.timestamp())]
    exact = requested_set == returned_set and not jumps
    return {
        "method": method,
        "status": "PASS" if exact else "FAIL",
        "expected_bar_count": expected,
        "returned_bar_count": len(epochs),
        "actual_first_utc": fmt(epochs[0]) if epochs else None,
        "actual_last_utc": fmt(epochs[-1]) if epochs else None,
        "returned_inside_requested_interval": sum(int(start.timestamp()) <= e <= int(end.timestamp()) for e in epochs),
        "missing_requested_bar_count": len(missing),
        "missing_requested_bars_utc": missing,
        "extra_before_count": len(extra_before),
        "extra_before_first_utc": extra_before[0] if extra_before else None,
        "extra_before_last_utc": extra_before[-1] if extra_before else None,
        "extra_after_count": len(extra_after),
        "timestamp_jumps_count": len(jumps),
        "timestamp_jumps": jumps,
        "requested_set_equals_returned_set": requested_set == returned_set,
        "last_error": mt5.last_error(),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--date", action="append", required=True, help="UTC date YYYY-MM-DD; may be repeated")
    p.add_argument("--start-hour", type=int, default=22)
    p.add_argument("--end-hour", type=int, default=2)
    args = p.parse_args()

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        mt5.symbol_select(SYMBOL, True)
        results = []
        for date_text in args.date:
            base = datetime.fromisoformat(date_text).replace(tzinfo=timezone.utc)
            start = base + timedelta(hours=args.start_hour)
            end = base + timedelta(days=1, hours=args.end_hour)
            results.append({
                "requested_interval_utc": {"start": start.isoformat().replace("+00:00", "Z"), "end": end.isoformat().replace("+00:00", "Z")},
                "copy_rates_range": inspect("copy_rates_range", start, end),
                "copy_rates_from": inspect("copy_rates_from", start, end),
            })

        print(json.dumps({
            "symbol": SYMBOL,
            "timeframe": "M1",
            "terminal": mt5.terminal_info()._asdict() if mt5.terminal_info() else None,
            "account_server": mt5.account_info().server if mt5.account_info() else None,
            "dates": results,
            "overall_status": "PASS" if all(r["copy_rates_range"]["status"] == "PASS" and r["copy_rates_from"]["status"] == "PASS" for r in results) else "FAIL",
            "interpretation": "Diagnostic only. Repeated FAIL around the same UTC boundary is evidence of a recurring availability/session boundary, but does not by itself establish its cause.",
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
