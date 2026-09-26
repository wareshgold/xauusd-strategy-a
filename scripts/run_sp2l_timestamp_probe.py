"""SP2L forensic timestamp probe.

Research-only. No orders, Telegram, detector decisions, or strategy geometry.
Compares wall-clock UTC with the newest M1 bar raw epoch, interpreted UTC,
and MT5 tick epoch. Designed to isolate timestamp/server-time freshness issues.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
POLL_SECONDS = float(os.getenv("SP2L_FORENSIC_PROBE_INTERVAL_SECONDS", "2"))
DURATION_SECONDS = float(os.getenv("SP2L_FORENSIC_PROBE_DURATION_SECONDS", "60"))
COUNT = 10
TERMINAL_PATH = os.getenv(
    "MT5_TERMINAL_PATH",
    r"C:\Program Files\Otet Group MT5 Terminal\terminal64.exe",
)


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat()


def epoch_iso(value):
    if value is None:
        return None
    return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat()


def main():
    if not mt5.initialize(path=TERMINAL_PATH, timeout=10000):
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    if not mt5.symbol_select(SYMBOL, True):
        raise SystemExit(f"symbol_select failed: {mt5.last_error()}")

    start = time.monotonic()
    rows = []
    poll_id = 0

    try:
        while time.monotonic() - start < DURATION_SECONDS:
            poll_id += 1
            wall = datetime.now(timezone.utc)
            rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M1, 0, COUNT)
            after_rates_error = mt5.last_error()
            tick = mt5.symbol_info_tick(SYMBOL)

            newest = None
            if rates is not None and len(rates):
                newest = rates[-1]

            raw_epoch = int(newest["time"]) if newest is not None else None
            tick_epoch = int(tick.time) if tick is not None and tick.time else None

            row = {
                "event": "TIMESTAMP_PROBE",
                "poll_id": poll_id,
                "wall_clock_utc": iso(wall),
                "newest_bar": {
                    "raw_epoch": raw_epoch,
                    "raw_time_utc": epoch_iso(raw_epoch),
                    "interpreted_time_utc": (
                        datetime.fromtimestamp(raw_epoch, tz=timezone.utc).isoformat()
                        if raw_epoch is not None else None
                    ),
                },
                "tick": {
                    "raw_epoch": tick_epoch,
                    "raw_time_utc": epoch_iso(tick_epoch),
                    "bid": getattr(tick, "bid", None) if tick else None,
                    "ask": getattr(tick, "ask", None) if tick else None,
                },
                "delta_seconds": {
                    "wall_minus_bar": (
                        (wall - datetime.fromtimestamp(raw_epoch, tz=timezone.utc)).total_seconds()
                        if raw_epoch is not None else None
                    ),
                    "wall_minus_tick": (
                        (wall - datetime.fromtimestamp(tick_epoch, tz=timezone.utc)).total_seconds()
                        if tick_epoch is not None else None
                    ),
                    "tick_minus_bar": (
                        float(tick_epoch - raw_epoch)
                        if tick_epoch is not None and raw_epoch is not None else None
                    ),
                },
                "rates_returned": int(len(rates)) if rates is not None else 0,
                "mt5_last_error_after_rates": list(after_rates_error),
            }
            rows.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
            time.sleep(POLL_SECONDS)
    finally:
        mt5.shutdown()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path("artifacts/forensic/runtime") / f"SP2L_TIMESTAMP_PROBE_{stamp}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "COMPLETE",
        "rows": len(rows),
        "output": str(out),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
