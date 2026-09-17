#!/usr/bin/env python3
"""Diagnose MT5 XAUUSD.ecn M1 history/range semantics without transforming data."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1
SERVER_EXPECTED = "OtetGroup-MT5"


def parse_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp must include UTC offset")
    return dt.astimezone(timezone.utc).replace(second=0, microsecond=0)


def ts(value) -> str | None:
    if value is None:
        return None
    return datetime.fromtimestamp(int(value), tz=timezone.utc).isoformat().replace("+00:00", "Z")


def summarize(rates):
    if rates is None:
        return {"returned": None, "error": mt5.last_error()}
    if len(rates) == 0:
        return {"returned": 0, "first": None, "last": None, "error": mt5.last_error()}
    return {
        "returned": int(len(rates)),
        "first": ts(rates[0]["time"]),
        "last": ts(rates[-1]["time"]),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    args = p.parse_args()
    start, end = parse_utc(args.start), parse_utc(args.end)
    if end <= start:
        raise SystemExit("end must be after start")

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        symbol = mt5.symbol_info(SYMBOL)
        selected = mt5.symbol_select(SYMBOL, True)
        rates_range = mt5.copy_rates_range(SYMBOL, TIMEFRAME, start, end)
        rates_from = mt5.copy_rates_from(SYMBOL, TIMEFRAME, end, int((end - start).total_seconds() // 60) + 1)
        rates_pos = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, int((end - start).total_seconds() // 60) + 1)

        result = {
            "requested_interval_utc": {"start": start.isoformat().replace("+00:00", "Z"), "end": end.isoformat().replace("+00:00", "Z")},
            "expected_inclusive_m1_bars": int((end - start).total_seconds() // 60) + 1,
            "terminal": {
                "name": getattr(terminal, "name", None),
                "community_account": getattr(terminal, "community_account", None),
                "trade_allowed": getattr(terminal, "trade_allowed", None),
                "connected": getattr(terminal, "connected", None),
            },
            "account": {"server": getattr(account, "server", None) if account else None},
            "symbol": {
                "name": getattr(symbol, "name", None) if symbol else None,
                "visible": getattr(symbol, "visible", None) if symbol else None,
                "select_result": selected,
                "time": ts(getattr(symbol, "time", None)) if symbol else None,
            },
            "copy_rates_range": summarize(rates_range),
            "copy_rates_from": summarize(rates_from),
            "copy_rates_from_pos": summarize(rates_pos),
            "last_error_after_calls": mt5.last_error(),
        }
        print(json.dumps(result, indent=2, default=str))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
