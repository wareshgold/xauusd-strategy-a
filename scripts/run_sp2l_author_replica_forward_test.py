"""
Research-only SP2L author-replica forward test for MT5 DEMO.

This runner intentionally reproduces the repository's research implementation
geometry from research/harness/sp2l_author_replica_candidate.ts / v1:
- fixed -4/-3/-2/-1 candle window
- P-Gap price = 1.0
- spike multiplier = 1.5
- origin candle SL
- TP = 1R
- max SL distance = 10.0 price units

It is NOT canonical Strategy A and must never be used for real-money execution.

Execution note:
The research backtest exposes a completed trigger candle and its theoretical
trigger extreme as the entry. In live forward testing that exact historical
price is not knowable after the candle closes, so this runner records the
theoretical entry and executes a MARKET order at the first observed tick after
the completed trigger. This execution difference is explicitly experimental
and must not be promoted to canonical fill semantics.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1
P_GAP_PRICE = 1.0
SPIKE_MULTIPLIER = 1.5
MAX_SL_DISTANCE = 10.0
TP_R = 1.0
VOLUME = 0.01
MAGIC = 26091901
POLL_SECONDS = 2
MAX_OPEN_POSITIONS = 1

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
ARTIFACTS = ROOT / "artifacts" / "forward-test"
RUNTIME.mkdir(parents=True, exist_ok=True)
ARTIFACTS.mkdir(parents=True, exist_ok=True)
EVENTS = ARTIFACTS / "SP2L_AUTHOR_REPLICA_FORWARD_EVENTS.jsonl"
STATE = RUNTIME / "sp2l_author_replica_forward_state.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(event: dict) -> None:
    event = {"ts_utc": utc_now(), **event}
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, separators=(",", ":")) + "\n")
    print(json.dumps(event, indent=2))


def init() -> None:
    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    info = mt5.account_info()
    if info is None:
        raise RuntimeError(f"MT5 account_info failed: {mt5.last_error()}")
    if int(info.trade_mode) != 0:
        raise RuntimeError(
            f"DEMO-ONLY GUARD: account trade_mode={info.trade_mode}; expected DEMO(0)"
        )
    sym = mt5.symbol_info(SYMBOL)
    if sym is None:
        raise RuntimeError(f"Missing symbol {SYMBOL}")
    if not mt5.symbol_select(SYMBOL, True):
        raise RuntimeError(f"symbol_select failed: {mt5.last_error()}")
    if int(sym.trade_mode) not in (1, 2, 4):
        raise RuntimeError(f"Symbol not openable: trade_mode={sym.trade_mode}")
    log_event({
        "event": "START",
        "mode": "RESEARCH_AUTHOR_REPLICA_FORWARD_TEST",
        "canonical": False,
        "account_login": int(info.login),
        "account_server": str(info.server),
        "account_trade_mode": int(info.trade_mode),
        "symbol": SYMBOL,
        "config": {
            "pGapPrice": P_GAP_PRICE,
            "spikeMultiplier": SPIKE_MULTIPLIER,
            "maxSlDistance": MAX_SL_DISTANCE,
            "tpR": TP_R,
            "volume": VOLUME,
        },
    })


def rates(count: int = 10):
    data = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, count)
    if data is None or len(data) < 6:
        return None
    return data


def detect(candles):
    # Use the last FOUR COMPLETED M1 candles. The current forming candle is excluded.
    a, spike, correction, trigger = candles[-5], candles[-4], candles[-3], candles[-2]

    spike_body_buy = float(spike["close"] - spike["open"])
    spike_body_sell = float(spike["open"] - spike["close"])

    buy = (
        trigger["low"] < correction["low"]
        and correction["close"] > spike["close"]
        and correction["open"] > spike["open"]
        and spike["close"] > a["close"]
        and spike["open"] > a["open"]
        and correction["close"] > correction["open"]
        and spike["close"] > spike["open"]
        and a["close"] > a["open"]
        and correction["low"] > a["high"] + P_GAP_PRICE
        and spike_body_buy > SPIKE_MULTIPLIER * (correction["close"] - correction["open"])
        and spike_body_buy > SPIKE_MULTIPLIER * (a["close"] - a["open"])
        and spike_body_buy > SPIKE_MULTIPLIER * (trigger["close"] - trigger["open"])
    )

    sell = (
        trigger["high"] > correction["high"]
        and correction["close"] < spike["close"]
        and correction["open"] < spike["open"]
        and spike["close"] < a["close"]
        and spike["open"] < a["open"]
        and correction["close"] < correction["open"]
        and spike["close"] < spike["open"]
        and a["close"] < a["open"]
        and correction["high"] < a["low"] - P_GAP_PRICE
        and spike_body_sell > SPIKE_MULTIPLIER * (correction["open"] - correction["close"])
        and spike_body_sell > SPIKE_MULTIPLIER * (a["open"] - a["close"])
        and spike_body_sell > SPIKE_MULTIPLIER * (trigger["open"] - trigger["close"])
    )

    if buy == sell:
        return None

    if buy:
        entry = float(trigger["low"])
        sl = float(a["low"])
        risk = entry - sl
        if 0 < risk <= MAX_SL_DISTANCE:
            return {
                "direction": "BUY",
                "trigger_time": int(trigger["time"]),
                "theoretical_entry": entry,
                "sl": sl,
                "risk": risk,
                "tp": entry + TP_R * risk,
            }

    if sell:
        entry = float(trigger["high"])
        sl = float(a["high"])
        risk = sl - entry
        if 0 < risk <= MAX_SL_DISTANCE:
            return {
                "direction": "SELL",
                "trigger_time": int(trigger["time"]),
                "theoretical_entry": entry,
                "sl": sl,
                "risk": risk,
                "tp": entry - TP_R * risk,
            }
    return None


def open_positions():
    return list(mt5.positions_get(symbol=SYMBOL) or [])


def send_market(signal):
    if len(open_positions()) >= MAX_OPEN_POSITIONS:
        return {"ok": False, "reason": "MAX_OPEN_POSITIONS"}

    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        return {"ok": False, "reason": f"NO_TICK:{mt5.last_error()}"}

    direction = signal["direction"]
    price = float(tick.ask if direction == "BUY" else tick.bid)
    sl = float(signal["sl"])
    risk = abs(price - sl)
    if risk <= 0 or risk > MAX_SL_DISTANCE:
        return {"ok": False, "reason": "LIVE_RISK_OUT_OF_RANGE", "price": price, "sl": sl}

    tp = price + TP_R * risk if direction == "BUY" else price - TP_R * risk
    order_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": VOLUME,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 30,
        "magic": MAGIC,
        "comment": "SP2L-FT",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result is None:
        return {"ok": False, "reason": "ORDER_SEND_NONE", "last_error": list(mt5.last_error())}

    return {
        "ok": result.retcode == mt5.TRADE_RETCODE_DONE,
        "retcode": int(result.retcode),
        "order": int(result.order),
        "deal": int(result.deal),
        "comment": str(result.comment),
        "actual_entry": price,
        "actual_sl": sl,
        "actual_tp": tp,
        "theoretical_entry": signal["theoretical_entry"],
    }


def main():
    init()
    seen_trigger = None
    deadline = None
    seconds = os.getenv("FORWARD_TEST_SECONDS")
    if seconds:
        deadline = time.time() + int(seconds)

    try:
        while deadline is None or time.time() < deadline:
            data = rates()
            if data is None:
                time.sleep(POLL_SECONDS)
                continue

            candidate = detect(data)
            if candidate is not None and candidate["trigger_time"] != seen_trigger:
                seen_trigger = candidate["trigger_time"]
                signal_id = f"AUTHOR_REPLICA_FT_{seen_trigger}_{candidate['direction']}"
                log_event({
                    "event": "CANDIDATE",
                    "signal_id": signal_id,
                    "candidate": candidate,
                    "execution_semantics": "MARKET_AFTER_COMPLETED_TRIGGER",
                })
                result = send_market(candidate)
                log_event({
                    "event": "EXECUTION",
                    "signal_id": signal_id,
                    "result": result,
                    "demo_only": True,
                })

            time.sleep(POLL_SECONDS)
    finally:
        mt5.shutdown()
        log_event({"event": "STOP"})


if __name__ == "__main__":
    main()
