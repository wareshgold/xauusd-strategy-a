#!/usr/bin/env python3
"""Compare MT5 historical retrieval semantics across multiple UTC windows.

Diagnostic only: no timestamp shifting, filling, interpolation, or dataset writes.
Each window is evaluated independently with copy_rates_range and copy_rates_from.
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
        raise ValueError(f"timestamp must include UTC offset: {value}")
    return dt.astimezone(timezone.utc).replace(second=0, microsecond=0)


def fmt(epoch: int) -> str:
    return datetime.fromtimestamp(int(epoch), tz=timezone.utc).isoformat().replace("+00:00", "Z")


def expected_epochs(start: datetime, end: datetime) -> list[int]:
    return list(range(int(start.timestamp()), int(end.timestamp()) + 60, 60))


def summarize(method: str, rates, expected: list[int], start: int, end: int) -> dict:
    if rates is None:
        return {
            "method": method,
            "status": "FAIL",
            "returned_bar_count": None,
            "last_error": mt5.last_error(),
            "reason": "API returned None",
        }

    epochs = [int(r["time"]) for r in rates]
    requested_set = set(expected)
    returned_set = set(epochs)
    in_range = [e for e in epochs if start <= e <= end]
    missing = [fmt(e) for e in expected if e not in returned_set]
    extra_before = [fmt(e) for e in epochs if e < start]
    extra_after = [fmt(e) for e in epochs if e > end]
    jumps = []
    for a, b in zip(epochs, epochs[1:]):
        if b - a != 60:
            jumps.append({"from": fmt(a), "to": fmt(b), "delta_seconds": b - a})

    status = "PASS" if requested_set == returned_set and not jumps else "FAIL"
    return {
        "method": method,
        "status": status,
        "expected_bar_count": len(expected),
        "returned_bar_count": len(epochs),
        "actual_first_utc": fmt(epochs[0]) if epochs else None,
        "actual_last_utc": fmt(epochs[-1]) if epochs else None,
        "returned_inside_requested_interval": len(in_range),
        "missing_requested_bar_count": len(missing),
        "missing_requested_bars_utc": missing,
        "extra_before_requested_interval_count": len(extra_before),
        "extra_before_first_utc": extra_before[0] if extra_before else None,
        "extra_before_last_utc": extra_before[-1] if extra_before else None,
        "extra_after_requested_interval_count": len(extra_after),
        "timestamp_jumps_count": len(jumps),
        "timestamp_jumps": jumps,
        "requested_set_equals_returned_set": requested_set == returned_set,
        "last_error": mt5.last_error(),
    }


def run_window(start: datetime, end: datetime) -> dict:
    expected = expected_epochs(start, end)
    start_epoch, end_epoch = expected[0], expected[-1]

    range_rates = mt5.copy_rates_range(SYMBOL, TIMEFRAME, start, end)
    range_result = summarize("copy_rates_range", range_rates, expected, start_epoch, end_epoch)

    from_rates = mt5.copy_rates_from(SYMBOL, TIMEFRAME, end, len(expected))
    from_result = summarize("copy_rates_from", from_rates, expected, start_epoch, end_epoch)

    return {
        "requested_interval_utc": {"start": fmt(start_epoch), "end": fmt(end_epoch)},
        "expected_bar_count": len(expected),
        "copy_rates_range": range_result,
        "copy_rates_from": from_result,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--window",
        action="append",
        nargs=2,
        metavar=("START", "END"),
        required=True,
        help="UTC window, repeatable; example: --window 2026-09-15T23:00:00Z 2026-09-16T00:00:00Z",
    )
    args = p.parse_args()

    windows = [(parse_utc(a), parse_utc(b)) for a, b in args.window]
    for start, end in windows:
        if end < start:
            raise SystemExit(f"window end precedes start: {start.isoformat()} > {end.isoformat()}")

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"symbol_select failed for {SYMBOL}: {mt5.last_error()}")

        terminal = mt5.terminal_info()
        account = mt5.account_info()
        results = [run_window(start, end) for start, end in windows]
        overall_pass = all(
            result["copy_rates_range"]["status"] == "PASS"
            and result["copy_rates_from"]["status"] == "PASS"
            for result in results
        )

        output = {
            "symbol": SYMBOL,
            "timeframe": "M1",
            "terminal": {
                "name": terminal.name if terminal else None,
                "connected": terminal.connected if terminal else None,
            },
            "account_server": account.server if account else None,
            "windows": results,
            "overall_status": "PASS" if overall_pass else "FAIL",
            "interpretation": "PASS requires exact requested timestamp set and 1-minute continuity for both retrieval methods in every window; no data is modified by this diagnostic.",
        }
        print(json.dumps(output, indent=2))
        return 0 if overall_pass else 1
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
