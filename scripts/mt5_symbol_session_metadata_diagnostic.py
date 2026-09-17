#!/usr/bin/env python3
"""Inspect broker-provided MT5 symbol trading/quote session metadata.

Diagnostic only. This does not transform timestamps, infer a session rule, or
write market data. The output is intended to be compared with independently
observed M1 availability gaps before any acquisition policy is defined.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"


def session_dict(value):
    if value is None:
        return None
    data = value._asdict() if hasattr(value, "_asdict") else dict(value)
    out = {}
    for key, item in data.items():
        if isinstance(item, (int, float, str, bool)) or item is None:
            out[key] = item
        else:
            out[key] = str(item)
    return out


def probe(method_name: str, day: int):
    fn = getattr(mt5, method_name)
    sessions = []
    for index in range(32):
        try:
            value = fn(SYMBOL, day, index)
        except Exception as exc:
            sessions.append({"session_index": index, "error": repr(exc)})
            break
        if value is None:
            break
        sessions.append({"session_index": index, "session": session_dict(value)})
    return sessions


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--days", default="0,1,2,3,4,5,6", help="MT5 day-of-week integers to inspect")
    args = p.parse_args()
    days = [int(x.strip()) for x in args.days.split(",") if x.strip()]
    if any(day < 0 or day > 6 for day in days):
        raise SystemExit("--days values must be integers in [0,6]")

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        mt5.symbol_select(SYMBOL, True)
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        symbol = mt5.symbol_info(SYMBOL)
        result = {
            "retrieval_timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "symbol": SYMBOL,
            "terminal": terminal._asdict() if terminal else None,
            "account_server": account.server if account else None,
            "symbol_info": symbol._asdict() if symbol else None,
            "day_number_convention": "MT5 Python symbol session APIs use day-of-week 0=Sunday through 6=Saturday.",
            "days": {},
        }
        for day in days:
            result["days"][str(day)] = {
                "quote_sessions": probe("symbol_info_session_quote", day),
                "deal_sessions": probe("symbol_info_session_deals", day),
            }
        result["last_error"] = mt5.last_error()
        print(json.dumps(result, indent=2, default=str))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
