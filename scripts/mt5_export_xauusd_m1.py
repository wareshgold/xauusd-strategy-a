#!/usr/bin/env python3
"""Research-only MT5 data exporter for SP2L replication.

Exports the exact broker-side XAUUSD M1 sample needed to compare the
public author implementation with this project's deterministic replica.

This script DOES NOT place, modify, or close orders.
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import MetaTrader5 as mt5
except ImportError:
    print("ERROR: MetaTrader5 is not installed in this Python environment.")
    print("Install with: python -m pip install MetaTrader5")
    raise SystemExit(2)

SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD")
TIMEFRAME = mt5.TIMEFRAME_M1
COUNT = int(os.getenv("MT5_EXPORT_COUNT", "10000"))
OUT = Path(os.getenv("MT5_EXPORT_OUT", "artifacts/mt5_xauusd_m1_10000.json"))


def fail(message):
    print(f"ERROR: {message}")
    try:
        print("MT5 last_error:", mt5.last_error())
    except Exception:
        pass
    raise SystemExit(1)


if not mt5.initialize():
    fail("mt5.initialize() failed. Open MetaTrader 5 and verify the terminal/account connection.")

try:
    info = mt5.symbol_info(SYMBOL)
    if info is None:
        fail(f"Symbol {SYMBOL!r} was not found in the connected MT5 terminal.")

    if not mt5.symbol_select(SYMBOL, True):
        fail(f"Could not select symbol {SYMBOL!r}.")

    # Match the author's Meta.GetRates default behavior as closely as possible:
    # copy_rates_from(..., datetime.now(UTC)+3h, number_of_data).
    from_date = datetime.now(timezone.utc) + timedelta(hours=3)
    rates = mt5.copy_rates_from(SYMBOL, TIMEFRAME, from_date, COUNT)
    if rates is None or len(rates) == 0:
        fail("MT5 returned no M1 rates.")

    candles = []
    for row in rates:
        ts = int(row["time"])
        candles.append({
            "time": ts,
            "time_utc": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "tick_volume": int(row["tick_volume"]),
            "spread": int(row["spread"]),
            "real_volume": int(row["real_volume"]),
        })

    payload = {
        "schema": "sp2l.mt5.compatibility.v1",
        "research_only": True,
        "source": "MetaTrader5.copy_rates_from",
        "symbol_requested": SYMBOL,
        "symbol": info.name,
        "timeframe": "M1",
        "requested_count": COUNT,
        "returned_count": len(candles),
        "point": float(info.point),
        "digits": int(info.digits),
        "trade_tick_size": float(info.trade_tick_size),
        "volume_min": float(info.volume_min),
        "volume_step": float(info.volume_step),
        "volume_max": float(info.volume_max),
        "currency_base": info.currency_base,
        "currency_profit": info.currency_profit,
        "currency_margin": info.currency_margin,
        "terminal": {
            "name": getattr(mt5.terminal_info(), "name", None),
            "path": getattr(mt5.terminal_info(), "path", None),
        },
        "account": {
            "server": getattr(mt5.account_info(), "server", None),
        },
        "request_reference_time_utc": from_date.isoformat(),
        "first_candle": candles[0] if candles else None,
        "last_candle": candles[-1] if candles else None,
        "candles": candles,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("=== SP2L MT5 COMPATIBILITY EXPORT ===")
    print("Symbol       :", info.name)
    print("Timeframe    : M1")
    print("Requested    :", COUNT)
    print("Returned     :", len(candles))
    print("Point        :", info.point)
    print("Digits       :", info.digits)
    print("Server       :", getattr(mt5.account_info(), "server", None))
    print("First UTC    :", candles[0]["time_utc"] if candles else None)
    print("Last UTC     :", candles[-1]["time_utc"] if candles else None)
    print("Output       :", OUT.resolve())
    print("======================================")
finally:
    mt5.shutdown()
