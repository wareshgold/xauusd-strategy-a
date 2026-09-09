from __future__ import annotations

from typing import Iterable

from .models import Candle, Side, Trade


def trade_excursion(trade: Trade, candles: Iterable[Candle]) -> dict:
    """Measure MAE/MFE in price units and R over the trade's observed bars.

    This is descriptive reporting only. It does not alter fills, exits, or
    Strategy A decisions.
    """
    if trade.exit_time is None:
        raise ValueError("trade must be closed")
    bars = [c for c in candles if trade.entry_time <= c.timestamp <= trade.exit_time]
    if not bars:
        return {"maePrice": None, "mfePrice": None, "maeR": None, "mfeR": None}
    if trade.side is Side.BUY:
        adverse = min(c.low for c in bars) - trade.entry_price
        favorable = max(c.high for c in bars) - trade.entry_price
    else:
        adverse = trade.entry_price - max(c.high for c in bars)
        favorable = trade.entry_price - min(c.low for c in bars)
    risk = trade.risk_distance
    return {
        "maePrice": adverse,
        "mfePrice": favorable,
        "maeR": adverse / risk if risk else None,
        "mfeR": favorable / risk if risk else None,
    }
