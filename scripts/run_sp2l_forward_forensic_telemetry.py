"""Research-only SP2L rolling-window forensic telemetry.

This runner only observes MT5 data. It does not place orders, modify orders,
close positions, or send Telegram messages.

It intentionally uses the same rolling acquisition call as the existing
forward runner: copy_rates_from_pos(symbol, M1, 0, 10).
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

try:
    from scripts.sp2l_author_replica_detector import detect
except ModuleNotFoundError:
    from sp2l_author_replica_detector import detect

SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1
WINDOW = 10
P_GAP_PRICE = 1.0
SPIKE_MULTIPLIER = 1.5
MAX_SL_DISTANCE = 10.0
TP_R = 1.0
POLL_SECONDS = float(os.getenv("FORENSIC_POLL_SECONDS", "2"))
DURATION_SECONDS = int(os.getenv("FORENSIC_DURATION_SECONDS", "900"))

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "artifacts" / "forensic" / "runtime"
OUT_DIR.mkdir(parents=True, exist_ok=True)
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
EVENTS = OUT_DIR / f"SP2L_FORWARD_FORENSIC_TELEMETRY_{STAMP}.jsonl"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def mt5_error():
    try:
        return list(mt5.last_error())
    except Exception:
        return None


def scalar(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return str(value)


def terminal_state() -> dict:
    terminal = mt5.terminal_info()
    account = mt5.account_info()
    symbol = mt5.symbol_info(SYMBOL)
    return {
        "terminal_connected": bool(getattr(terminal, "connected", False)) if terminal else None,
        "terminal_trade_allowed": bool(getattr(terminal, "trade_allowed", False)) if terminal else None,
        "terminal_tradeapi_disabled": bool(getattr(terminal, "tradeapi_disabled", False)) if terminal else None,
        "terminal_build": scalar(getattr(terminal, "build", None)) if terminal else None,
        "account_login": scalar(getattr(account, "login", None)) if account else None,
        "account_server": scalar(getattr(account, "server", None)) if account else None,
        "account_trade_mode": scalar(getattr(account, "trade_mode", None)) if account else None,
        "symbol_trade_mode": scalar(getattr(symbol, "trade_mode", None)) if symbol else None,
        "symbol_visible": scalar(getattr(symbol, "visible", None)) if symbol else None,
    }


def bar_snapshot(data) -> dict:
    rows = []
    for index, bar in enumerate(data):
        raw_time = int(bar["time"])
        rows.append({
            "array_index": index,
            "time_raw": raw_time,
            "time_interpreted_utc": datetime.fromtimestamp(
                raw_time, timezone.utc
            ).isoformat(),
            "open": float(bar["open"]),
            "high": float(bar["high"]),
            "low": float(bar["low"]),
            "close": float(bar["close"]),
            "tick_volume": int(bar["tick_volume"]),
            "spread": int(bar["spread"]),
            "real_volume": int(bar["real_volume"]),
        })

    times = [row["time_raw"] for row in rows]
    return {
        "count": len(rows),
        "array_order": "as_returned_by_mt5_copy_rates_from_pos",
        "strictly_increasing": all(
            times[i] < times[i + 1] for i in range(len(times) - 1)
        ),
        "times_raw": times,
        "times_interpreted_utc": [
            row["time_interpreted_utc"] for row in rows
        ],
        "bars": rows,
    }


def tick_snapshot() -> dict:
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        return {"available": False, "last_error": mt5_error()}

    return {
        "available": True,
        "time_raw": scalar(getattr(tick, "time", None)),
        "time_msc": scalar(getattr(tick, "time_msc", None)),
        "bid": float(getattr(tick, "bid", 0.0)),
        "ask": float(getattr(tick, "ask", 0.0)),
        "last": float(getattr(tick, "last", 0.0)),
        "volume": scalar(getattr(tick, "volume", None)),
        "flags": scalar(getattr(tick, "flags", None)),
    }


def write_event(event: dict) -> None:
    with EVENTS.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(event, ensure_ascii=False, separators=(",", ":"))
            + "\n"
        )
    print(json.dumps(event, ensure_ascii=False))


def main() -> None:
    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize failed: {mt5_error()}")

    try:
        account = mt5.account_info()
        if account is None:
            raise RuntimeError(f"account_info failed: {mt5_error()}")
        if int(account.trade_mode) != 0:
            raise RuntimeError(
                f"DEMO-ONLY forensic guard failed: trade_mode={account.trade_mode}"
            )
        if not mt5.symbol_select(SYMBOL, True):
            raise RuntimeError(f"symbol_select failed: {mt5_error()}")

        write_event({
            "event": "FORENSIC_START",
            "ts_utc": utc_now(),
            "mode": "RESEARCH_FORENSIC_TELEMETRY",
            "canonical": False,
            "no_execution": True,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "window": WINDOW,
            "poll_seconds": POLL_SECONDS,
            "duration_seconds": DURATION_SECONDS,
            "detector_config": {
                "pGapPrice": P_GAP_PRICE,
                "spikeMultiplier": SPIKE_MULTIPLIER,
                "maxSlDistance": MAX_SL_DISTANCE,
                "tpR": TP_R,
            },
            "terminal_state": terminal_state(),
            "mt5_last_error": mt5_error(),
            "artifact_path": str(EVENTS.relative_to(ROOT)),
        })

        deadline = time.monotonic() + DURATION_SECONDS
        previous_poll = None
        poll_id = 0

        while time.monotonic() < deadline:
            started = time.monotonic()
            poll_id += 1

            error_before = mt5_error()
            data = mt5.copy_rates_from_pos(
                SYMBOL, TIMEFRAME, 0, WINDOW
            )
            error_after_rates = mt5_error()

            event = {
                "event": "POLL",
                "ts_utc": utc_now(),
                "poll_id": poll_id,
                "elapsed_since_previous_poll_seconds": (
                    None
                    if previous_poll is None
                    else started - previous_poll
                ),
                "copy_rates_call": {
                    "api": "mt5.copy_rates_from_pos",
                    "symbol": SYMBOL,
                    "timeframe": "M1",
                    "start_pos": 0,
                    "count": WINDOW,
                    "returned_none": data is None,
                    "returned_count": 0 if data is None else int(len(data)),
                },
                "mt5_last_error_before": error_before,
                "mt5_last_error_after_rates": error_after_rates,
                "tick": tick_snapshot(),
                "terminal_state": terminal_state(),
            }

            if data is None or len(data) < 6:
                event["data_snapshot"] = None
                event["detector"] = {
                    "status": "INSUFFICIENT_OR_MISSING_DATA",
                    "signal": None,
                }
            else:
                event["data_snapshot"] = bar_snapshot(data)
                signal = detect(
                    data,
                    p_gap_price=P_GAP_PRICE,
                    spike_multiplier=SPIKE_MULTIPLIER,
                    max_sl_distance=MAX_SL_DISTANCE,
                    tp_r=TP_R,
                )
                event["detector"] = {
                    "status": "EVALUATED",
                    "signal": (
                        None
                        if signal is None
                        else {key: scalar(value) for key, value in signal.items()}
                    ),
                }

            event["mt5_last_error_after_detector"] = mt5_error()
            event["poll_elapsed_seconds"] = time.monotonic() - started
            write_event(event)

            previous_poll = started
            remaining = POLL_SECONDS - event["poll_elapsed_seconds"]
            if remaining > 0:
                time.sleep(remaining)

        write_event({
            "event": "FORENSIC_STOP",
            "ts_utc": utc_now(),
            "polls_recorded": poll_id,
            "canonical": False,
            "no_execution": True,
            "artifact_path": str(EVENTS.relative_to(ROOT)),
        })
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
