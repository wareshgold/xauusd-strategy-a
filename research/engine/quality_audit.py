"""Strategy-neutral quality checks for acquired candle batches."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from .models import Candle


@dataclass(frozen=True)
class QualityAudit:
    row_count: int
    duplicate_timestamps: int
    non_monotonic_pairs: int
    cadence_mode_seconds: int | None
    cadence_anomalies: int
    invalid_ohlc_rows: int

    @property
    def passed(self) -> bool:
        return (
            self.row_count > 0
            and self.duplicate_timestamps == 0
            and self.non_monotonic_pairs == 0
            and self.invalid_ohlc_rows == 0
        )


def audit_candles(candles: tuple[Candle, ...], expected_interval_seconds: int) -> QualityAudit:
    timestamps = [c.timestamp for c in candles]
    duplicates = len(timestamps) - len(set(timestamps))
    non_monotonic = sum(1 for a, b in zip(timestamps, timestamps[1:]) if b <= a)
    deltas = [int((b - a).total_seconds()) for a, b in zip(timestamps, timestamps[1:]) if b > a]
    mode = None
    if deltas:
        counts = {d: deltas.count(d) for d in set(deltas)}
        mode = max(counts, key=counts.get)
    cadence_anomalies = sum(1 for d in deltas if d != expected_interval_seconds)
    invalid = sum(
        1 for c in candles
        if c.high < max(c.open, c.close) or c.low > min(c.open, c.close) or c.high < c.low
    )
    return QualityAudit(
        row_count=len(candles),
        duplicate_timestamps=duplicates,
        non_monotonic_pairs=non_monotonic,
        cadence_mode_seconds=mode,
        cadence_anomalies=cadence_anomalies,
        invalid_ohlc_rows=invalid,
    )
