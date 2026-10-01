"""SP2L Strategy A V3 frozen research configuration.

Single source of truth for the V3 XAUUSD research variant.
Trail-10 is a research experiment, not canonical source-confirmed Strategy A.
"""
from __future__ import annotations
from dataclasses import dataclass

VERSION = "SP2L_V3_XAUUSD_TRAIL10_20261001"
SYMBOL_BASE = "XAUUSD"
TIMEFRAME_NAME = "M1"
P_GAP_PRICE = 1.0
SPIKE_MULTIPLIER = 1.5
MAX_SL_DISTANCE = 10.0
TP_R = 1.0
TRAIL_PIPS = 10.0
XAU_PIP_SIZE_PRICE = 0.1
TRAIL_DISTANCE_PRICE = TRAIL_PIPS * XAU_PIP_SIZE_PRICE
ORDER_MODE = "PENDING_LIMIT_RESEARCH"
SL_ANCHOR = "SPIKE_CANDLE_EXTREME_RESEARCH"
PENDING_TTL_MINUTES = 30.0
SESSION_POLICY = "ALL_MARKET_HOURS"
VOLUME = 0.01

@dataclass(frozen=True)
class Candidate:
    direction: str
    trigger_time: int
    theoretical_entry: float
    sl: float
    risk: float
    tp: float
    secondary_entry_2x: float
    symbol: str

def detect(candles, symbol: str):
    if candles is None or len(candles) < 3:
        return None
    before, spike, after = candles[-3], candles[-2], candles[-1]
    ao, ah, al, ac = map(float, (before["open"], before["high"], before["low"], before["close"]))
    bo, bh, bl, bc = map(float, (spike["open"], spike["high"], spike["low"], spike["close"]))
    co, ch, cl, cc = map(float, (after["open"], after["high"], after["low"], after["close"]))
    before_body = abs(ac - ao)
    spike_body = abs(bc - bo)
    after_body = abs(cc - co)
    buy = (
        cc > bc and co > bo and bc > ac and bo > ao and
        cc > co and bc > bo and ac > ao and
        cl > ah + P_GAP_PRICE and
        spike_body > SPIKE_MULTIPLIER * before_body and
        spike_body > SPIKE_MULTIPLIER * after_body
    )
    sell = (
        cc < bc and co < bo and bc < ac and bo < ao and
        cc < co and bc < bo and ac < ao and
        ch < al - P_GAP_PRICE and
        spike_body > SPIKE_MULTIPLIER * before_body and
        spike_body > SPIKE_MULTIPLIER * after_body
    )
    if buy == sell:
        return None
    return {"direction": "BUY" if buy else "SELL",
            "setup_after_time": int(after["time"]), "symbol": symbol}

def find_first_entry(candles, start_index: int, setup: dict):
    direction = setup["direction"]
    for j in range(start_index + 1, len(candles)):
        prev, cur = candles[j - 1], candles[j]
        if direction == "BUY":
            if float(cur["low"]) >= float(prev["low"]):
                continue
            entry = float(cur["low"])
            sl = float(candles[start_index - 2]["low"])
            risk = entry - sl
            if risk <= 0 or risk > MAX_SL_DISTANCE:
                return None
            return {
                "direction":"BUY", "trigger_time":int(cur["time"]),
                "theoretical_entry":entry, "sl":sl, "risk":risk,
                "tp":entry + TP_R*risk,
                "secondary_entry_2x":entry - 0.5*risk, "symbol":setup["symbol"],
            }
        else:
            if float(cur["high"]) <= float(prev["high"]):
                continue
            entry = float(cur["high"])
            sl = float(candles[start_index - 2]["high"])
            risk = sl - entry
            if risk <= 0 or risk > MAX_SL_DISTANCE:
                return None
            return {
                "direction":"SELL", "trigger_time":int(cur["time"]),
                "theoretical_entry":entry, "sl":sl, "risk":risk,
                "tp":entry - TP_R*risk,
                "secondary_entry_2x":entry + 0.5*risk, "symbol":setup["symbol"],
            }
    return None

def find_latest_candidate(candles, symbol: str):
    candidates = []
    for setup_end in range(2, len(candles)-1):
        setup = detect(candles[setup_end-2:setup_end+1], symbol)
        if setup:
            candidate = find_first_entry(candles, setup_end, setup)
            if candidate:
                candidates.append(candidate)
    return max(candidates, key=lambda x:(int(x["trigger_time"]), x["direction"])) if candidates else None

def trail_stop(direction: str, favorable_extreme: float) -> float:
    if direction == "BUY":
        return favorable_extreme - TRAIL_DISTANCE_PRICE
    return favorable_extreme + TRAIL_DISTANCE_PRICE
