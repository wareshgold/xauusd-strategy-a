from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .models import Candle


@dataclass(frozen=True)
class BaselineResult:
    candle_count: int
    first_open: float | None
    last_close: float | None
    buy_hold_return: float | None
    buy_hold_max_drawdown: float | None


def price_baseline(candles: Sequence[Candle]) -> BaselineResult:
    """Compute a descriptive long-only price baseline; no signal generation."""
    bars = sorted(candles, key=lambda c: c.timestamp)
    if not bars:
        return BaselineResult(0, None, None, None, None)
    first = bars[0].open
    equity = 1.0
    peak = 1.0
    max_dd = 0.0
    for prev, current in zip(bars, bars[1:]):
        if prev.close <= 0:
            raise ValueError("baseline requires positive prices")
        equity *= current.close / prev.close
        peak = max(peak, equity)
        max_dd = max(max_dd, (peak - equity) / peak)
    final = bars[-1].close
    return BaselineResult(len(bars), first, final, final / first - 1.0, max_dd)


def flat_baseline() -> dict:
    """Explicit null model: zero trades and zero return."""
    return {"tradeCount": 0, "return": 0.0, "maxDrawdown": 0.0}
