"""Shared research-only SP2L Author-Replica detector.

This module centralizes the existing research detector so the MT5 backtest and
XAUUSD forward runner cannot silently drift in their signal geometry.

It is NOT canonical Strategy A. The geometry remains research-only.
"""

from __future__ import annotations


def detect(
    candles,
    *,
    p_gap_price: float = 0.0,
    spike_multiplier: float = 1.5,
    max_sl_distance: float = 10.0,
    tp_r: float = 1.0,
):
    """Return the source-aligned research signal for a completed-bar window.

    The caller must provide at least six bars, with the final bar being the
    current/forming bar. The detector intentionally uses [-5],[-4],[-3],[-2].
    This preserves the existing forward/backtest window.\n\n    Source boundary: P-Gap is Pressure Gap; the relevant High/Low pair\n    must be strictly separated. No extra numeric gap threshold is source-confirmed.\n    Positive p_gap_price values are counterfactual sensitivity tests only.
    """
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
        and correction["low"] > a["high"] + p_gap_price
        and spike_body_buy > spike_multiplier * (correction["close"] - correction["open"])
        and spike_body_buy > spike_multiplier * (a["close"] - a["open"])
        and spike_body_buy > spike_multiplier * (trigger["close"] - trigger["open"])
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
        and correction["high"] < a["low"] - p_gap_price
        and spike_body_sell > spike_multiplier * (correction["open"] - correction["close"])
        and spike_body_sell > spike_multiplier * (a["open"] - a["close"])
        and spike_body_sell > spike_multiplier * (trigger["open"] - trigger["close"])
    )

    if buy == sell:
        return None

    if buy:
        entry, sl = float(trigger["low"]), float(spike["low"])
        risk = entry - sl
        if 0 < risk <= max_sl_distance:
            return {
                "direction": "BUY",
                "signal_time": int(trigger["time"]),
                "entry": entry,
                "sl": sl,
                "risk": risk,
                "tp": entry + tp_r * risk,
            }

    if sell:
        entry, sl = float(trigger["high"]), float(spike["high"])
        risk = sl - entry
        if 0 < risk <= max_sl_distance:
            return {
                "direction": "SELL",
                "signal_time": int(trigger["time"]),
                "entry": entry,
                "sl": sl,
                "risk": risk,
                "tp": entry - tp_r * risk,
            }

    return None
