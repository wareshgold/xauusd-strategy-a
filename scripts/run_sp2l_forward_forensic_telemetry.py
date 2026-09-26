"""Research-only MT5 rolling-window forensic telemetry for SP2L.

This script does NOT place, modify, or close orders and does NOT send Telegram.
It reproduces the existing forward acquisition path:
    mt5.copy_rates_from_pos("XAUUSD.ecn", M1, 0, 10)
and passes the returned array unchanged to the shared research detector.

Purpose:
- prove exactly what the rolling API returned during a future backtest/forward
  discrepancy;
- capture raw bar timestamps, OHLC, array order, detector result, MT5 errors,
  tick bid/ask, poll cadence, and terminal/account state.

No Strategy A geometry, session, fill, SL/TP, or canonical rule is changed.
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


def jsonable(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return str(value)


def mt5_error():
    try:
        return [jsonable(x) for x in mt5.last_error()]
    except Exception:
        return None


def terminal_snapshot():
    terminal = mt5.terminal_info()
    account = mt5.account_info()
    symbol = mt5.symbol_info(SYMBOL)
    return {
        "terminal": {
            "connected": bool(getattr(terminal, "connected", False)) if terminal else None,
            "trade_allowed": bool(getattr(terminal, "trade_allowed", False)) if terminal else None,
            "tradeapi_disabled": bool(getattr(terminal, "tradeapi_disabled", False)) if terminal else None,
            "community_account": bool(getattr(terminal, "community_account", False)) if terminal else None,
            "build": jsonable(getattr(terminal, "build", None)) if terminal else None,
        },
        "account": {
            "login": jsonable(getattr(account, "login", None)) if account else None,
            "server": jsonable(getattr(account, "server", None)) if account else None,
            "trade_mode": jsonable(getattr(account, "trade_mode", None)) if account else None,
        },
        "symbol": {
            "name": jsonable(getattr(symbol, "name", None)) if symbol else None,
            "trade_mode": jsonable(getattr(symbol, "trade_mode", None)) if symbol else None,
            "visible": jsonable(getattr(symbol, "visible", None)) if symbol else None,
        },
    }


def bar_snapshot(data):
    rows = []
    for i, bar in enumerate(data):
        rows.append({
            "array_index": i,
            "time_raw": jsonable(bar["time"]),
            "time_raw_hex": hex(int(bar["time"])) if bar["time"] is not None else None,
            "time_interpreted_utc": datetime.fromtimestamp(
                int(bar["time"]), timezone.utc
            ).isoformat(),
            "open": float(bar["open"]),
            "high": float(bar["high"]),
            "low": float(bar["low"]),
            "close": float(bar["close"]),
            "tick_volume": int(bar["tick_volume"]),
            "spread": int(bar["spread"]),
            "real_volume": int(bar["real_volume"]),
        })
    times = [r["time_raw"] for r in rows]
    return {
        "count": len(rows),
        "array_order": "as_returned_by_mt5_copy_rates_from_pos",
        "times_raw": times,
        "times_interpreted_utc": [r["time_interpreted_utc"] for r in rows],
        "strictly_increasing": all(
            times[i] < times[i + 1] for i in range(len(times) - 1)
        ),
        "bars": rows,
    }


def tick_snapshot():
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        return {
            "available": False,
            "last_error": mt5_error(),
        }
    return {
        "available": True,
        "time_raw": jsonable(getattr(tick, "time", None)),
        "time_msc": jsonable(getattr(tick, "time_msc", None)),
        "bid": float(getattr(tick, "bid", 0.0)),
        "ask": float(getattr(tick, "ask", 0.0)),
        "last": float(getattr(tick, "last", 0.0)),
        "volume": jsonable(getattr(tick, "volume", None)),
        "flags": jsonable(getattr(tick, "flags", None)),
    }


def detector_snapshot(data):
    signal = detect(
        data,
        p_gap_price=P_GAP_PRICE,
        spike_multiplier=SPIKE_MULTIPLIER,
        max_sl_distance=MAX_SL_DISTANCE,
        tp_r=TP_R,
    )
    if signal is None:
        return {
            "signal_present": False,
            "signal": None,
        }
    return {
        "signal_present": True,
        "signal": {
            key: jsonable(value)
            for key, value in signal.items()
        },
    }


def write_event(payload):
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps(payload, ensure_ascii=False))


def resolve_terminal_path():
    env = os.getenv("MT5_TERMINAL_PATH")
    if env:
        return env
    try:
        import mt5_terminal_resolver
    except ModuleNotFoundError:
        try:
            from scripts import mt5_terminal_resolver
        except ModuleNotFoundError:
            return None
    found = mt5_terminal_resolver.find_mt5_terminal()
    return str(found) if found else None


def main():
    path = resolve_terminal_path()
    initialized = mt5.initialize(path=path) if path else mt5.initialize()
    if not initialized:
        raise RuntimeError(f"MT5 initialize failed: {mt5_error()}")

    try:
        info = mt5.account_info()
        if info is None:
            raise RuntimeError(f"MT5 account_info failed: {mt5_error()}")
        if int(info.trade_mode) != 0:
            raise RuntimeError(
                f"DEMO-ONLY forensic guard: account trade_mode={info.trade_mode}; expected DEMO(0)"
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
            "terminal_snapshot": terminal_snapshot(),
            "mt5_last_error": mt5_error(),
            "artifact_path": str(EVENTS.relative_to(ROOT)),
        })

        deadline = time.monotonic() + DURATION_SECONDS
        previous_poll_monotonic = None
        poll_id = 0

        while time.monotonic() < deadline:
            poll_started = time.monotonic()
            poll_id += 1
            error_before = mt5_error()
            data = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, WINDOW)
            error_after_rates = mt5_error()
            tick = tick_snapshot()

            event = {
                "event": "POLL",
                "ts_utc": utc_now(),
                "poll_id": poll_id,
                "elapsed_since_previous_poll_seconds": (
                    None
                    if previous_poll_monotonic is None
                    else poll_started - previous_poll_monotonic
                ),
                "copy_rates_call": {
                    "api": "mt5.copy_rates_from_pos",
                    "symbol": SYMBOL,
                    "timeframe": "M1",
                    "start_pos": 0,
                    "count": WINDOW,
                    "returned_none": data is None,
                    "returned_count": int(len(data)) if data is not None else 0,
                },
                "mt5_last_error_before": error_before,
                "mt5_last_error_after_rates": error_after_rates,
                "tick": tick,
                "terminal_snapshot": terminal_snapshot(),
            }

            if data is None or len(data) < 6:
                event["data_snapshot"] = None
                event["detector"] = {
                    "signal_present": False,
                    "signal": None,
                    "status": "INSUFFICIENT_OR_MISSING_DATA",
                }
            else:
                event["data_snapshot"] = bar_snapshot(data)
                event["detector"] = detector_snapshot(data)
                event["detector"]["status"] = "EVALUATED"

            event["mt5_last_error_after_detector"] = mt5_error()
            event["poll_elapsed_seconds"] = time.monotonic() - poll_started
            write_event(event)

            previous_poll_monotonic = poll_started
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
