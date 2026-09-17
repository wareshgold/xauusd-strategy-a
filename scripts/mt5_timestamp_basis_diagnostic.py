#!/usr/bin/env python3
"""Diagnostic for the time basis of MT5 Python bar/tick timestamps.

This does not transform or repair data. It compares raw epoch timestamps with
Python UTC/local representations and terminal tick metadata so we can resolve
whether the acquisition layer is interpreting MT5 timestamps correctly.
"""
from __future__ import annotations

import json
import time as time_module
from datetime import datetime, timezone

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1
SERVER_EXPECTED = "OtetGroup-MT5"


def iso_utc(epoch: int | float) -> str:
    return datetime.fromtimestamp(float(epoch), tz=timezone.utc).isoformat().replace("+00:00", "Z")


def iso_local(epoch: int | float) -> str:
    return datetime.fromtimestamp(float(epoch)).astimezone().isoformat()


def main() -> int:
    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        tick = mt5.symbol_info_tick(SYMBOL)
        rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 3)
        now_epoch = time_module.time()
        result = {
            "python_now_epoch": now_epoch,
            "python_now_utc": iso_utc(now_epoch),
            "python_now_local": iso_local(now_epoch),
            "account_server": getattr(account, "server", None) if account else None,
            "server_matches_expected": getattr(account, "server", None) == SERVER_EXPECTED if account else False,
            "terminal_name": getattr(terminal, "name", None) if terminal else None,
            "terminal_path": getattr(terminal, "path", None) if terminal else None,
            "symbol": SYMBOL,
            "tick": None,
            "bars": [],
            "diagnostic": "COMPARE_EPOCH_TO_CURRENT_CLOCK; DO_NOT_SHIFT_DATA",
        }
        if tick is not None:
            raw = int(tick.time)
            result["tick"] = {
                "raw_epoch": raw,
                "utc_from_raw_epoch": iso_utc(raw),
                "local_from_raw_epoch": iso_local(raw),
                "delta_to_python_now_seconds": raw - now_epoch,
                "time_msc": int(getattr(tick, "time_msc", 0)),
            }
        if rates is not None:
            for r in rates:
                raw = int(r["time"])
                result["bars"].append({
                    "raw_epoch": raw,
                    "utc_from_raw_epoch": iso_utc(raw),
                    "local_from_raw_epoch": iso_local(raw),
                    "delta_to_python_now_seconds": raw - now_epoch,
                    "open": float(r["open"]),
                    "close": float(r["close"]),
                })
        print(json.dumps(result, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
