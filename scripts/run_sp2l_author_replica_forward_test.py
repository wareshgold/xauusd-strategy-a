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

from live_mt5_gateway import Signal, execute_signal

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
                "secondary_entry_2x": entry + 0.5 * (sl - entry),
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
                "secondary_entry_2x": entry + 0.5 * (sl - entry),
            }
    return None


def open_positions():
    return list(mt5.positions_get(symbol=SYMBOL) or [])


def send_market(signal):
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        return {"ok": False, "reason": f"NO_TICK:{mt5.last_error()}"}

    direction = signal["direction"]
    market_price = float(tick.ask if direction == "BUY" else tick.bid)
    payload = Signal(
        direction=direction,
        symbol=SYMBOL,
        entry=float(signal["theoretical_entry"]),
        sl=float(signal["sl"]),
        tp=float(signal["tp"]),
        volume=VOLUME,
        signal_id=signal["signal_id"],
        source="AUTHOR_REPLICA_FORWARD_TEST",
        status="APPROVED",
    )
    result = execute_signal(payload)
    return {**result, "observed_market_price": market_price, "theoretical_entry": signal["theoretical_entry"]}


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
                candidate["signal_id"] = f"AUTHOR_REPLICA_FT_{seen_trigger}_{candidate['direction']}"
                signal_id = f"AUTHOR_REPLICA_FT_{seen_trigger}_{candidate['direction']}"
                log_event({
                    "event": "CANDIDATE",
                    "signal_id": signal_id,
                    "candidate": candidate,
                    "f13_2x": {
                        "status": "SOURCE_CONFIRMED_RELATION_ONLY",
                        "secondary_entry": candidate["secondary_entry_2x"],
                        "formula": "Entry + 0.5 * (StopLoss - Entry)",
                        "execution": "NOT_EXECUTED_UNRESOLVED_LIFECYCLE",
                    },
                    "execution_semantics": "MARKET_AFTER_COMPLETED_TRIGGER",
                })
                result = send_market(candidate)
                log_event({
                    "event": "EXECUTION",
                    "signal_id": signal_id,
                    "result": result,
                    "demo_only": True,
                })

                # Do not retry or move the strategy levels when the theoretical
                # entry has already been crossed. Fill/activation semantics are
                # unresolved; this is recorded as an execution miss for research.
                if result.get("reason") == "INVALID_STOPS_AT_CURRENT_MARKET":
                    market = float(result["observed_market_price"])
                    theoretical = float(result["theoretical_entry"])
                    drift = (
                        market - theoretical
                        if candidate["direction"] == "BUY"
                        else theoretical - market
                    )
                    log_event({
                        "event": "EXECUTION_MISS",
                        "signal_id": signal_id,
                        "direction": candidate["direction"],
                        "theoretical_entry": theoretical,
                        "observed_market_price": market,
                        "entry_drift_in_favor": drift,
                        "reason": "MARKET_MOVED_PAST_THEORETICAL_ENTRY_BEFORE_EXECUTION",
                        "action": "NO_RETRY_NO_LEVEL_MOVE",
                        "canonical": False,
                        "note": "Execution/fill semantics remain unresolved; candidate retained for research audit.",
                    })

            time.sleep(POLL_SECONDS)
    finally:
        mt5.shutdown()
        log_event({"event": "STOP"})


if __name__ == "__main__":
    main()
