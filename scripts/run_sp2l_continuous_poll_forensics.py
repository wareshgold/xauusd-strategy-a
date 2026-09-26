"""Research-only continuous MT5 polling forensic capture for SP2L.

This tool does not run the detector, place orders, send Telegram messages, or
change Strategy A geometry. It records every poll iteration plus MT5 acquisition
metadata, raw candle timestamps/OHLC, detector-independent health, and lifecycle
events so a future interval can be classified as proven continuous, a proven
gap, or unresolved from preserved evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1
POLL_SECONDS = 2
BAR_COUNT = 10


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_terminal_path() -> str | None:
    env = os.getenv("MT5_TERMINAL_PATH")
    if env:
        return env
    try:
        import mt5_terminal_resolver
    except ModuleNotFoundError:
        try:
            from scripts import mt5_terminal_resolver  # type: ignore
        except ModuleNotFoundError:
            return None
    found = mt5_terminal_resolver.find_mt5_terminal()
    return str(found) if found else None


def serialize_bar(row) -> dict:
    raw = int(row["time"])
    return {
        "time_raw": raw,
        "time_utc_interpreted": datetime.fromtimestamp(raw, timezone.utc).isoformat(),
        "open": float(row["open"]),
        "high": float(row["high"]),
        "low": float(row["low"]),
        "close": float(row["close"]),
        "tick_volume": int(row["tick_volume"]),
        "spread": int(row["spread"]),
        "real_volume": int(row["real_volume"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=int, default=300)
    parser.add_argument("--poll-seconds", type=float, default=POLL_SECONDS)
    parser.add_argument("--bars", type=int, default=BAR_COUNT)
    parser.add_argument("--output", default=None)
    parser.add_argument("--mt5-path", default=None)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = (
        Path(args.output)
        if args.output
        else root / "artifacts" / "forensic" / "runtime"
        / f"SP2L_CONTINUOUS_POLL_FORENSIC_{stamp}.jsonl"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    init_kwargs = {}
    mt5_path = args.mt5_path or resolve_terminal_path()
    if mt5_path:
        init_kwargs["path"] = mt5_path

    if not mt5.initialize(**init_kwargs):
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    start_wall = time.monotonic()
    deadline = start_wall + args.seconds
    poll_index = 0

    def emit(payload: dict) -> None:
        record = {
            "ts_utc": utc_now(),
            "wall_monotonic": time.monotonic() - start_wall,
            **payload,
        }
        with output.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")

    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        symbol = mt5.symbol_info(SYMBOL)
        selected = mt5.symbol_select(SYMBOL, True)

        emit({
            "event": "FORENSIC_START",
            "research_only": True,
            "canonical": False,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "poll_seconds": args.poll_seconds,
            "bars": args.bars,
            "terminal": {
                "connected": bool(getattr(terminal, "connected", False)) if terminal else None,
                "build": int(getattr(terminal, "build", 0) or 0) if terminal else None,
                "company": str(getattr(terminal, "company", "")) if terminal else None,
                "name": str(getattr(terminal, "name", "")) if terminal else None,
            },
            "account": {
                "trade_mode": int(getattr(account, "trade_mode", -1)) if account else None,
            },
            "symbol_select": bool(selected),
            "strategy_geometry": "NOT_EVALUATED",
        })

        while time.monotonic() < deadline:
            poll_index += 1
            poll_started = time.monotonic()
            data = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, args.bars)
            err = mt5.last_error()

            if data is None:
                emit({
                    "event": "POLL",
                    "poll_index": poll_index,
                    "status": "DATA_ERROR",
                    "mt5_last_error": [int(err[0]), str(err[1])],
                    "returned_count": 0,
                    "bars": [],
                })
            else:
                rows = [serialize_bar(row) for row in data]
                emit({
                    "event": "POLL",
                    "poll_index": poll_index,
                    "status": "DATA_OK",
                    "mt5_last_error": [int(err[0]), str(err[1])],
                    "returned_count": len(rows),
                    "bars": rows,
                    "latest_raw_time": rows[-1]["time_raw"] if rows else None,
                    "oldest_raw_time": rows[0]["time_raw"] if rows else None,
                    "poll_duration_seconds": time.monotonic() - poll_started,
                })

            remaining = deadline - time.monotonic()
            if remaining > 0:
                time.sleep(min(args.poll_seconds, remaining))

        emit({
            "event": "FORENSIC_STOP",
            "reason": "DEADLINE_REACHED",
            "poll_count": poll_index,
        })
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
