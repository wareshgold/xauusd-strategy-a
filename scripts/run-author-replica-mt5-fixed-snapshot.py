"""Research-only fixed-timestamp MT5 snapshot runner.

Purpose: remove rolling-window drift from copy_rates_from() comparisons.
No trading calls are made.

Usage (PowerShell):
  $env:MT5_SNAPSHOT_END_UTC="2026-09-17T10:45:00+00:00"
  python scripts\run-author-replica-mt5-fixed-snapshot.py

The same fixed endpoint should be reused for subsequent replay comparisons.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
BARS = int(os.getenv("MT5_SNAPSHOT_BARS", "10000"))
END_UTC = os.getenv("MT5_SNAPSHOT_END_UTC", "2026-09-17T10:45:00+00:00")
OUT = Path(os.getenv("MT5_SNAPSHOT_OUT", "artifacts/mt5_xauusd_m1_fixed_10000.json"))


def parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def main() -> None:
    end_dt = parse_dt(END_UTC)
    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"symbol_select failed for {SYMBOL}: {mt5.last_error()}")

        rates = mt5.copy_rates_from(SYMBOL, mt5.TIMEFRAME_M1, end_dt, BARS)
        if rates is None:
            raise SystemExit(f"copy_rates_from failed: {mt5.last_error()}")
        if len(rates) != BARS:
            raise SystemExit(f"expected {BARS} bars, got {len(rates)}")

        info = mt5.symbol_info(SYMBOL)
        if info is None:
            raise SystemExit(f"symbol_info failed: {mt5.last_error()}")

        candles = []
        for r in rates:
            candles.append({
                "time": int(r["time"]),
                "time_utc": datetime.fromtimestamp(int(r["time"]), tz=timezone.utc).isoformat(),
                "open": float(r["open"]),
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
                "tick_volume": int(r["tick_volume"]),
                "spread": int(r["spread"]),
                "real_volume": int(r["real_volume"]),
            })

        canonical = json.dumps(candles, separators=(",", ":"), sort_keys=True).encode()
        payload = {
            "research_only": True,
            "source": "MetaTrader5.copy_rates_from",
            "snapshot_end_utc": end_dt.isoformat(),
            "terminal": mt5.terminal_info().name if mt5.terminal_info() else None,
            "server": mt5.account_info().server if mt5.account_info() else None,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "requested_bars": BARS,
            "returned_bars": len(candles),
            "first_utc": candles[0]["time_utc"],
            "last_utc": candles[-1]["time_utc"],
            "symbol_contract": {
                "point": float(info.point),
                "digits": int(info.digits),
                "trade_tick_size": float(info.trade_tick_size),
                "volume_min": float(info.volume_min),
                "volume_step": float(info.volume_step),
                "base_currency": info.currency_base,
                "profit_currency": info.currency_profit,
                "margin_currency": info.currency_margin,
            },
            "candles_sha256": hashlib.sha256(canonical).hexdigest(),
            "candles": candles,
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps({k: v for k, v in payload.items() if k != "candles"}, indent=2))
        print(f"Wrote {OUT}")
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
