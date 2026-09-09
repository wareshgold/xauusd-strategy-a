from __future__ import annotations

from collections import Counter
from datetime import timedelta
from statistics import mean, median
from typing import Iterable

from .models import Side, Trade


def summarize_trades(trades: Iterable[Trade]) -> dict:
    """Compute strategy-neutral performance statistics from closed trades."""
    rows = [t for t in trades if t.exit_price is not None and t.exit_time is not None]
    rs = [float(t.r_multiple) for t in rows if t.r_multiple is not None]
    wins = [r for r in rs if r > 0]
    losses = [r for r in rs if r < 0]
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for r in rs:
        equity += r
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    durations = [(t.exit_time - t.entry_time).total_seconds() for t in rows]
    long_rs = [float(t.r_multiple) for t in rows if t.side is Side.BUY and t.r_multiple is not None]
    short_rs = [float(t.r_multiple) for t in rows if t.side is Side.SELL and t.r_multiple is not None]
    max_consecutive_losses = 0
    streak = 0
    for r in rs:
        streak = streak + 1 if r < 0 else 0
        max_consecutive_losses = max(max_consecutive_losses, streak)
    return {
        "tradeCount": len(rows),
        "winRate": len(wins) / len(rs) if rs else None,
        "lossRate": len(losses) / len(rs) if rs else None,
        "expectancyR": mean(rs) if rs else None,
        "averageR": mean(rs) if rs else None,
        "medianR": median(rs) if rs else None,
        "profitFactor": gross_profit / gross_loss if gross_loss else (float("inf") if gross_profit else None),
        "maxDrawdownR": max_dd,
        "maxConsecutiveLosses": max_consecutive_losses,
        "averageHoldingSeconds": mean(durations) if durations else None,
        "longTradeCount": len(long_rs),
        "longAverageR": mean(long_rs) if long_rs else None,
        "shortTradeCount": len(short_rs),
        "shortAverageR": mean(short_rs) if short_rs else None,
    }
