"""Read-only MT5 timestamp diagnostic for pending-order TTL research.

This script never calls order_send, order_delete, or any position-modification API.
It records host UTC beside raw MT5 tick/order timestamps so an operator can compare
clock domains during an active market. It does not infer or configure an offset.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any


def iso_utc(epoch: int | float | None) -> str | None:
    if not epoch:
        return None
    try:
        return datetime.fromtimestamp(float(epoch), timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return None


def main() -> int:
    try:
        import MetaTrader5 as mt5
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"MetaTrader5 import failed: {exc}"}))
        return 2

    symbol = os.getenv("SP2L_CLOCK_DIAG_SYMBOL", "XAUUSD.ecn")
    magic_text = os.getenv("SP2L_CLOCK_DIAG_MAGIC", "26092201")
    try:
        magic = int(magic_text)
    except ValueError:
        print(json.dumps({"ok": False, "error": "SP2L_CLOCK_DIAG_MAGIC must be an integer"}))
        return 2

    path = os.getenv("MT5_TERMINAL_PATH", "").strip()
    initialized = mt5.initialize(path=path) if path else mt5.initialize()
    if not initialized:
        print(json.dumps({
            "ok": False,
            "error": "MT5 initialize failed",
            "last_error": str(mt5.last_error()),
        }, indent=2))
        return 3

    try:
        samples: list[dict[str, Any]] = []
        for index in range(4):
            host_before = time.time()
            tick = mt5.symbol_info_tick(symbol)
            host_after = time.time()
            raw_tick_time = int(getattr(tick, "time", 0) or 0) if tick else 0
            raw_tick_msc = int(getattr(tick, "time_msc", 0) or 0) if tick else 0
            host_mid = (host_before + host_after) / 2
            samples.append({
                "sample": index + 1,
                "host_utc_before": iso_utc(host_before),
                "host_utc_after": iso_utc(host_after),
                "raw_tick_time": raw_tick_time or None,
                "raw_tick_time_as_utc_if_epoch": iso_utc(raw_tick_time),
                "raw_tick_time_msc": raw_tick_msc or None,
                "tick_minus_host_seconds": round(raw_tick_time - host_mid, 3) if raw_tick_time else None,
                "tick_msc_minus_host_ms": round(raw_tick_msc - host_mid * 1000, 1) if raw_tick_msc else None,
                "bid": getattr(tick, "bid", None) if tick else None,
                "ask": getattr(tick, "ask", None) if tick else None,
            })
            if index < 3:
                time.sleep(5)

        orders = mt5.orders_get(symbol=symbol)
        matching_orders = []
        if orders is not None:
            for order in orders:
                if int(getattr(order, "magic", 0) or 0) != magic:
                    continue
                setup = int(getattr(order, "time_setup", 0) or 0)
                matching_orders.append({
                    "ticket": int(getattr(order, "ticket", 0) or 0),
                    "symbol": str(getattr(order, "symbol", "") or ""),
                    "magic": int(getattr(order, "magic", 0) or 0),
                    "type": int(getattr(order, "type", -1)),
                    "time_setup_raw": setup or None,
                    "time_setup_as_utc_if_epoch": iso_utc(setup),
                    "setup_minus_host_utc_seconds": round(setup - time.time(), 3) if setup else None,
                    "price_open": float(getattr(order, "price_open", 0.0) or 0.0),
                })

        output = {
            "ok": True,
            "diagnostic": "READ_ONLY_NO_ORDER_MUTATIONS",
            "captured_at_utc": datetime.now(timezone.utc).isoformat(),
            "terminal_version": str(mt5.version()),
            "symbol": symbol,
            "magic_filter": magic,
            "samples": samples,
            "matching_active_orders": matching_orders if orders is not None else None,
            "orders_query_ok": orders is not None,
            "interpretation_guard": (
                "Do not set SP2L_PENDING_SERVER_OFFSET_HOURS from this output alone. "
                "Compare multiple fresh samples with a trusted UTC clock and the "
                "terminal-displayed server clock; retain raw values."
            ),
        }
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
