from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence

from .models import Candle


@dataclass(frozen=True)
class DatasetSplit:
    name: str
    start: datetime
    end: datetime

    def contains(self, timestamp: datetime) -> bool:
        ts = timestamp if timestamp.tzinfo else timestamp.replace(tzinfo=timezone.utc)
        return self.start <= ts.astimezone(timezone.utc) < self.end


def chronological_splits(candles: Sequence[Candle], development_fraction: float = 0.60, validation_fraction: float = 0.20) -> tuple[DatasetSplit, ...]:
    """Return contiguous DEV/VAL/FRESH_HOLDOUT intervals without shuffling."""
    if not candles:
        raise ValueError("candles must not be empty")
    if not 0 < development_fraction < 1 or not 0 < validation_fraction < 1:
        raise ValueError("fractions must be between 0 and 1")
    if development_fraction + validation_fraction >= 1:
        raise ValueError("DEV + VAL must leave a positive holdout")
    ts = sorted((c.timestamp if c.timestamp.tzinfo else c.timestamp.replace(tzinfo=timezone.utc)).astimezone(timezone.utc) for c in candles)
    first, last = ts[0], ts[-1]
    span = (last - first).total_seconds()
    if span <= 0:
        raise ValueError("candles must span a positive time interval")
    d_end = first + (last - first) * development_fraction
    v_end = first + (last - first) * (development_fraction + validation_fraction)
    return (
        DatasetSplit("DEV", first, d_end),
        DatasetSplit("VAL", d_end, v_end),
        DatasetSplit("FRESH_HOLDOUT", v_end, last + (last - first) / max(len(ts), 1)),
    )


def assign_split(timestamp: datetime, splits: Sequence[DatasetSplit]) -> str | None:
    for split in splits:
        if split.contains(timestamp):
            return split.name
    return None
