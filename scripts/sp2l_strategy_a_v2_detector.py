"""Research-only SP2L Strategy A V2 detector.

V2 intentionally isolates a fully specified external-style contract:
- P-Gap threshold = 1.0 price unit
- first post-setup lower-low / higher-high trigger
- SL on candle before Spike
- 1R target
- no EMA/ATR/ADX/trend/session filters
- no second entry

This module is NOT canonical Strategy A.
"""

from __future__ import annotations


P_GAP_PRICE = 1.0
SPIKE_MULTIPLIER = 1.5
MAX_SL_DISTANCE = 10.0
TP_R = 1.0


def _body(candle, direction: str) -> float:
    if direction == "BUY":
        return float(candle["close"] - candle["open"])
    return float(candle["open"] - candle["close"])


def _setup(candles, direction: str) -> bool:
    """Evaluate the three-candle setup ending at candles[-1].

    candles[-3] = before-spike
    candles[-2] = spike
    candles[-1] = after-spike
    """
    before, spike, after = candles[-3], candles[-2], candles[-1]

    if direction == "BUY":
        return (
            float(after["close"]) > float(spike["close"])
            and float(after["open"]) > float(spike["open"])
            and float(spike["close"]) > float(before["close"])
            and float(spike["open"]) > float(before["open"])
            and float(after["close"]) > float(after["open"])
            and float(spike["close"]) > float(spike["open"])
            and float(before["close"]) > float(before["open"])
            and float(after["low"]) > float(before["high"]) + P_GAP_PRICE
            and _body(spike, "BUY") > SPIKE_MULTIPLIER * _body(before, "BUY")
            and _body(spike, "BUY") > SPIKE_MULTIPLIER * _body(after, "BUY")
        )

    return (
        float(after["close"]) < float(spike["close"])
        and float(after["open"]) < float(spike["open"])
        and float(spike["close"]) < float(before["close"])
        and float(spike["open"]) < float(before["open"])
        and float(after["close"]) < float(after["open"])
        and float(spike["close"]) < float(spike["open"])
        and float(before["close"]) < float(before["open"])
        and float(after["high"]) < float(before["low"]) - P_GAP_PRICE
        and _body(spike, "SELL") > SPIKE_MULTIPLIER * _body(before, "SELL")
        and _body(spike, "SELL") > SPIKE_MULTIPLIER * _body(after, "SELL")
    )


def detect_setup(candles):
    """Return a setup at the final candle, or None.

    The returned setup points to the after-spike candle. Entry is found by
    find_first_entry() only after this candle.
    """
    if len(candles) < 3:
        return None

    buy = _setup(candles, "BUY")
    sell = _setup(candles, "SELL")
    if buy == sell:
        return None

    before, spike, after = candles[-3], candles[-2], candles[-1]
    direction = "BUY" if buy else "SELL"

    return {
        "direction": direction,
        "setup_time": int(after["time"]),
        "before_spike_time": int(before["time"]),
        "spike_time": int(spike["time"]),
        "after_spike_time": int(after["time"]),
        "sl": float(before["low"] if direction == "BUY" else before["high"]),
        "spike_body": _body(spike, direction),
    }


def find_first_entry(candles, start_index: int, setup: dict):
    """Return the first trigger after the setup candle.

    BUY trigger: current Low < previous Low.
    SELL trigger: current High > previous High.

    The reference contract rejects the setup immediately if the first
    qualifying trigger creates invalid risk.
    """
    direction = setup["direction"]
    sl = float(setup["sl"])

    for entry_index in range(start_index + 1, len(candles)):
        current = candles[entry_index]
        previous = candles[entry_index - 1]

        if direction == "BUY":
            entry = float(current["low"])
            if not entry < float(previous["low"]):
                continue
            risk = entry - sl
        else:
            entry = float(current["high"])
            if not entry > float(previous["high"]):
                continue
            risk = sl - entry

        if risk <= 0 or risk > MAX_SL_DISTANCE:
            return None

        return {
            **setup,
            "entry_index": int(entry_index),
            "entry_time": int(current["time"]),
            "entry": entry,
            "risk": float(risk),
            "tp": float(entry + TP_R * risk if direction == "BUY" else entry - TP_R * risk),
        }

    return None
