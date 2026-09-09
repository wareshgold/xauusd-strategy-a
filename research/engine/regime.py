"""Strategy-neutral regime descriptors for research reporting.

These descriptors are not Strategy A filters and must not select trades.
"""

from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Iterable

from .models import Candle


@dataclass(frozen=True)
class RegimeSlice:
    label: str
    start_index: int
    end_index: int
    bars: int
    mean_range: float
    range_std: float


def rolling_range_regimes(candles: Iterable[Candle], window: int = 50) -> list[RegimeSlice]:
    rows = list(candles)
    if window <= 0:
        raise ValueError("window must be positive")
    out: list[RegimeSlice] = []
    for end in range(window, len(rows) + 1, window):
        chunk = rows[end - window:end]
        ranges = [c.high - c.low for c in chunk]
        avg = mean(ranges)
        sd = pstdev(ranges) if len(ranges) > 1 else 0.0
        label = "HIGH_RANGE" if avg > 0 and sd / avg > 0.75 else "NORMAL_RANGE"
        out.append(RegimeSlice(label, end - window, end - 1, len(chunk), avg, sd))
    return out
