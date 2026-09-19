#!/usr/bin/env python3
"""Raw MT5 timestamp-basis diagnostic.

Diagnostic only. No timezone conversion, shifting, repair, or dataset writes.
Records raw epoch values and compares numeric relationships only.
"""
from __future__ import annotations

import json
import time as time_module

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1
SERVER_EXPECTED = "OtetGroup-MT5"


def main() -> int:
    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()

        observations = []

        for _ in range(5):
            python_now_before = time_module.time()
            tick = mt5.symbol_info_tick(SYMBOL)
            rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 3)
            python_now_after = time_module.time()

            obs = {
                "python_now_before_epoch": python_now_before,
                "python_now_after_epoch": python_now_after,
                "tick": None,
                "bars": [],
            }

            if tick is not None:
                obs["tick"] = {
                    "raw_epoch": int(tick.time),
                    "raw_time_msc": int(getattr(tick, "time_msc", 0)),
                    "raw_epoch_minus_python_before": int(tick.time) - python_now_before,
                    "raw_epoch_minus_python_after": int(tick.time) - python_now_after,
                }

            if rates is not None:
                for r in rates:
                    raw = int(r["time"])
                    obs["bars"].append({
                        "raw_epoch": raw,
                        "raw_epoch_minus_python_before": raw - python_now_before,
                        "raw_epoch_minus_python_after": raw - python_now_after,
                    })

            observations.append(obs)
            time_module.sleep(0.25)

        result = {
            "account_server": getattr(account, "server", None) if account else None,
            "server_matches_expected": (
                getattr(account, "server", None) == SERVER_EXPECTED
                if account else False
            ),
            "terminal_name": getattr(terminal, "name", None) if terminal else None,
            "terminal_path": getattr(terminal, "path", None) if terminal else None,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "observations": observations,
            "diagnostic": (
                "RAW_EPOCH_ONLY; NUMERIC_COMPARISON_ONLY; "
                "NO_TIMEZONE_INTERPRETATION; DO_NOT_SHIFT_DATA"
            ),
        }

        print(json.dumps(result, indent=2))
        return 0

    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
