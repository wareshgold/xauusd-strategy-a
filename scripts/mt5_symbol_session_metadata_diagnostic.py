#!/usr/bin/env python3
"""Inspect available MT5 symbol/session metadata APIs without assuming API names.

Diagnostic only. This does not transform timestamps, infer a session rule, or
write market data. Missing Python APIs are reported as UNAVAILABLE rather than
being treated as evidence about market availability.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"


def safe_asdict(value):
    if value is None:
        return None
    if hasattr(value, "_asdict"):
        return value._asdict()
    try:
        return dict(value)
    except Exception:
        return str(value)


def scalarize(value):
    if isinstance(value, (int, float, str, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k): scalarize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [scalarize(v) for v in value]
    return str(value)


def discover_session_api_names() -> list[str]:
    names = []
    for name in dir(mt5):
        lowered = name.lower()
        if "session" in lowered:
            names.append(name)
    return sorted(names)


def probe_method(method_name: str, day: int) -> dict:
    if not hasattr(mt5, method_name):
        return {
            "status": "UNAVAILABLE",
            "method": method_name,
            "reason": "MetaTrader5 Python module does not expose this attribute",
        }

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
        sessions.append({
            "session_index": index,
            "session": scalarize(safe_asdict(value)),
        })

    return {
        "status": "AVAILABLE",
        "method": method_name,
        "sessions": sessions,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--days", default="0,1,2,3,4,5,6", help="MT5 day-of-week integers to inspect")
    args = p.parse_args()

    try:
        days = [int(x.strip()) for x in args.days.split(",") if x.strip()]
    except ValueError as exc:
        raise SystemExit(f"invalid --days: {exc}")
    if any(day < 0 or day > 6 for day in days):
        raise SystemExit("--days values must be integers in [0,6]")

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        selected = mt5.symbol_select(SYMBOL, True)
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        symbol = mt5.symbol_info(SYMBOL)

        available_session_api_names = discover_session_api_names()
        candidate_methods = [
            "symbol_info_session_quote",
            "symbol_info_session_deals",
        ]

        result = {
            "retrieval_timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "symbol": SYMBOL,
            "mt5_python_version": getattr(mt5, "__version__", None),
            "terminal": scalarize(safe_asdict(terminal)),
            "account_server": account.server if account else None,
            "symbol_selected": selected,
            "symbol_info": scalarize(safe_asdict(symbol)),
            "session_related_attributes_exposed_by_python_module": available_session_api_names,
            "candidate_session_methods": {
                name: {
                    "exposed": hasattr(mt5, name),
                }
                for name in candidate_methods
            },
            "day_number_convention": "Diagnostic convention: 0=Sunday through 6=Saturday; no session rule is inferred from this convention.",
            "days": {},
        }

        for day in days:
            result["days"][str(day)] = {
                "quote_sessions": probe_method("symbol_info_session_quote", day),
                "deal_sessions": probe_method("symbol_info_session_deals", day),
            }

        result["last_error"] = mt5.last_error()
        print(json.dumps(result, indent=2, default=str))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
