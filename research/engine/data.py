from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Iterable, Sequence

from .models import Candle


def _utc(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


def audit_candles(candles: Sequence[Candle], expected_minutes: int = 1) -> dict:
    """Return deterministic integrity diagnostics without modifying input data."""
    ordered = list(candles)
    timestamps = [_utc(c.timestamp) for c in ordered]
    duplicates = sum(n - 1 for n in Counter(timestamps).values() if n > 1)
    non_chronological = sum(1 for a, b in zip(timestamps, timestamps[1:]) if b <= a)
    invalid_ohlc = sum(1 for c in ordered if c.high < c.low or c.open < c.low or c.open > c.high or c.close < c.low or c.close > c.high)
    gaps = []
    expected = timedelta(minutes=expected_minutes)
    for a, b in zip(timestamps, timestamps[1:]):
        delta = b - a
        if delta > expected:
            gaps.append({"from": a.isoformat(), "to": b.isoformat(), "minutes": int(delta.total_seconds() / 60)})
    return {
        "candleCount": len(ordered),
        "firstTimestamp": timestamps[0].isoformat() if timestamps else None,
        "lastTimestamp": timestamps[-1].isoformat() if timestamps else None,
        "duplicateTimestamps": duplicates,
        "nonChronologicalCount": non_chronological,
        "invalidOhlcCount": invalid_ohlc,
        "gapCount": len(gaps),
        "largestGapMinutes": max((g["minutes"] for g in gaps), default=0),
        "gaps": gaps,
        "pass": not duplicates and not non_chronological and not invalid_ohlc,
    }


def aggregate_ohlc(candles: Sequence[Candle], minutes: int) -> list[Candle]:
    """Aggregate lower-timeframe candles into fixed UTC buckets.

    No forward filling is performed. An output bucket is emitted only when it
    contains the exact expected number of source candles, preventing synthetic
    bars across missing-data gaps.
    """
    if minutes <= 0:
        raise ValueError("minutes must be positive")
    source = sorted(candles, key=lambda c: _utc(c.timestamp))
    bucket: list[Candle] = []
    out: list[Candle] = []
    for candle in source:
        ts = _utc(candle.timestamp)
        bucket_start = ts.replace(minute=(ts.minute // minutes) * minutes, second=0, microsecond=0)
        if bucket and _utc(bucket[0].timestamp).replace(minute=(_utc(bucket[0].timestamp).minute // minutes) * minutes, second=0, microsecond=0) != bucket_start:
            if len(bucket) == minutes:
                out.append(_make_aggregate(bucket, bucket_start, minutes))
            bucket = []
        bucket.append(candle)
    if bucket:
        ts = _utc(bucket[0].timestamp)
        bucket_start = ts.replace(minute=(ts.minute // minutes) * minutes, second=0, microsecond=0)
        if len(bucket) == minutes:
            out.append(_make_aggregate(bucket, bucket_start, minutes))
    return out


def _make_aggregate(bucket: Sequence[Candle], timestamp: datetime, minutes: int) -> Candle:
    ordered = sorted(bucket, key=lambda c: _utc(c.timestamp))
    for a, b in zip(ordered, ordered[1:]):
        if _utc(b.timestamp) - _utc(a.timestamp) != timedelta(minutes=1):
            raise ValueError("source bucket contains a timestamp gap")
    return Candle(timestamp, ordered[0].open, max(c.high for c in ordered), min(c.low for c in ordered), ordered[-1].close, ordered[0].symbol, f"{minutes}m")


def dataset_fingerprint(candles: Iterable[Candle], *, provider: str, symbol: str, timeframe: str, timezone_name: str = "UTC", source_version: str = "") -> str:
    rows = []
    for c in sorted(candles, key=lambda x: _utc(x.timestamp)):
        rows.append([_utc(c.timestamp).isoformat(), c.open, c.high, c.low, c.close])
    manifest = {"provider": provider, "symbol": symbol, "timeframe": timeframe, "timezone": timezone_name, "sourceVersion": source_version, "candles": rows}
    payload = json.dumps(manifest, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()
