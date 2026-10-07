"""Export an immutable M1 MT5 snapshot for SP2L research provenance.

Research-only. This script does not detect signals, replay trades, rank variants,
or generate BUY/SELL decisions. The resulting bytes are the exact dataset
identity that a later research adapter may consume.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5
import numpy as np


def fetch_m1_rates(symbol: str, start: datetime, end: datetime):
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"symbol_select failed: {symbol} {mt5.last_error()}")
    chunks = []
    cur = start.astimezone(timezone.utc)
    end = end.astimezone(timezone.utc)
    while cur < end:
        chunk_end = min(cur + timedelta(days=7), end)
        rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, cur, chunk_end)
        if rates is None or len(rates) == 0:
            raise RuntimeError(
                f"history failed {cur.isoformat()}..{chunk_end.isoformat()}: {mt5.last_error()}"
            )
        chunks.append(rates.copy())
        cur = chunk_end + timedelta(minutes=1)
    bars = np.concatenate(chunks)
    bars.sort(order="time")
    _, idx = np.unique(bars["time"], return_index=True)
    return bars[np.sort(idx)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mt5-path", required=True)
    ap.add_argument("--symbol", default="XAUUSD.ecn")
    ap.add_argument("--start", default="2026-10-05T00:00:00+00:00")
    ap.add_argument("--end", default="2026-10-07T05:30:00+00:00")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    start = datetime.fromisoformat(args.start)
    end = datetime.fromisoformat(args.end)
    if end <= start:
        raise ValueError("--end must be after --start")

    if not mt5.initialize(path=args.mt5_path):
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        bars = fetch_m1_rates(args.symbol, start, end)
    finally:
        mt5.shutdown()

    if len(bars) < 10:
        raise RuntimeError("insufficient M1 history")

    rows = [
        {
            "time": int(b["time"]),
            "open": float(b["open"]),
            "high": float(b["high"]),
            "low": float(b["low"]),
            "close": float(b["close"]),
            "tick_volume": int(b["tick_volume"]),
            "spread": int(b["spread"]),
            "real_volume": int(b["real_volume"]),
        }
        for b in bars
    ]
    payload = {
        "schema_version": 1,
        "research_only": True,
        "symbol": args.symbol,
        "timeframe": "M1",
        "window_utc": {"start": start.isoformat(), "end": end.isoformat()},
        "bars": rows,
    }
    raw = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(raw)
    print(json.dumps({
        "status": "COMPLETE",
        "artifact": str(output.resolve()),
        "symbol": args.symbol,
        "timeframe": "M1",
        "bars": len(rows),
        "byte_size": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }, indent=2))


if __name__ == "__main__":
    main()
