"""Deterministic SP2L trigger-semantics research fixtures.

These fixtures intentionally do not encode a canonical Strategy A rule.
They expose candidate semantics for later source validation.
"""

def candle(i, low, high, close=None):
    return {"index": i, "time": i, "open": close if close is not None else (low + high) / 2,
            "high": high, "low": low, "close": close if close is not None else (low + high) / 2}


def t1_immediate_touch():
    # Reference candle Low=100; immediate correction touches exactly 100.
    return [candle(0, 100, 102), candle(1, 104, 110), candle(2, 100, 106)]


def t2_delayed_reach():
    # First correction misses; later candle reaches reference Low.
    return [candle(0, 100, 102), candle(1, 104, 110), candle(2, 103, 107), candle(3, 100, 106)]


def t3_exact_touch():
    return [candle(0, 100, 102), candle(1, 104, 110), candle(2, 100, 106)]


def t4_penetration():
    # Correction penetrates below reference Low.
    return [candle(0, 100, 102), candle(1, 104, 110), candle(2, 99, 106)]


def t5_close_only():
    # Extreme reaches reference but close returns above it; distinguishes close from touch.
    return [candle(0, 100, 102), candle(1, 104, 110), candle(2, 99, 106, 105)]


def t6_multi_candle_correction():
    # Multiple correction candles precede the eventual reach.
    return [candle(0, 100, 102), candle(1, 104, 110), candle(2, 103, 107),
            candle(3, 102, 106), candle(4, 100, 105)]


RESEARCH_FIXTURES = {
    "T1_IMMEDIATE_TOUCH": t1_immediate_touch,
    "T2_DELAYED_REACH": t2_delayed_reach,
    "T3_EXACT_TOUCH": t3_exact_touch,
    "T4_PENETRATION": t4_penetration,
    "T5_CLOSE_ONLY": t5_close_only,
    "T6_MULTI_CANDLE_CORRECTION": t6_multi_candle_correction,
}
