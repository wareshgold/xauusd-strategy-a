from __future__ import annotations

from datetime import timedelta, timezone
from typing import Sequence

from .data import _utc
from .models import Candle


def aggregate_m1_to_m5(candles: Sequence[Candle]) -> list[Candle]:
    """Aggregate contiguous UTC M1 candles into complete five-minute bars.

    Buckets are anchored to UTC clock boundaries. Partial or gapped buckets are
    omitted; no forward filling or interpolation is performed.
    """
    source = sorted(candles, key=lambda c: _utc(c.timestamp))
    out: list[Candle] = []
    bucket: list[Candle] = []
    bucket_start = None
    for candle in source:
        ts = _utc(candle.timestamp)
        start = ts.replace(minute=(ts.minute // 5) * 5, second=0, microsecond=0)
        if bucket_start is None:
            bucket_start = start
        if start != bucket_start:
            if len(bucket) == 5 and _contiguous_m1(bucket):
                out.append(_make_m5(bucket, bucket_start))
            bucket = []
            bucket_start = start
        bucket.append(candle)
    if bucket_start is not None and len(bucket) == 5 and _contiguous_m1(bucket):
        out.append(_make_m5(bucket, bucket_start))
    return out


def _contiguous_m1(bucket: Sequence[Candle]) -> bool:
    ordered = sorted(bucket, key=lambda c: _utc(c.timestamp))
    if len(ordered) != 5:
        return False
    for a, b in zip(ordered, ordered[1:]):
        if _utc(b.timestamp) - _utc(a.timestamp) != timedelta(minutes=1):
            return False
    return True


def _make_m5(bucket: Sequence[Candle], timestamp) -> Candle:
    ordered = sorted(bucket, key=lambda c: _utc(c.timestamp))
    return Candle(
        timestamp.astimezone(timezone.utc),
        ordered[0].open,
        max(c.high for c in ordered),
        min(c.low for c in ordered),
        ordered[-1].close,
        ordered[0].symbol,
        "5m",
    )
