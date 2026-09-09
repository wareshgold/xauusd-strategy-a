"""Deterministic historical coverage planning and chunk validation.

Strategy-neutral. This module does not inspect or generate Strategy A signals.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


INTERVAL_SECONDS = {"1min": 60, "5min": 300, "15min": 900, "30min": 1800, "1h": 3600}


@dataclass(frozen=True)
class CoverageChunk:
    index: int
    start_utc: str
    end_utc: str


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("coverage boundary must include timezone")
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def plan_chunks(start_utc: str, end_utc: str, *, interval: str, max_points: int = 5000) -> tuple[CoverageChunk, ...]:
    """Split an inclusive UTC interval into deterministic, non-overlapping chunks.

    Each chunk contains at most ``max_points`` candle timestamps when the requested
    interval is regular. The next chunk starts one interval after the previous end.
    """
    if interval not in INTERVAL_SECONDS:
        raise ValueError(f"unsupported interval: {interval}")
    if max_points < 1:
        raise ValueError("max_points must be >= 1")
    start = _parse_utc(start_utc)
    end = _parse_utc(end_utc)
    if start > end:
        raise ValueError("start_utc must be <= end_utc")

    step = timedelta(seconds=INTERVAL_SECONDS[interval])
    span = step * (max_points - 1)
    chunks: list[CoverageChunk] = []
    cursor = start
    index = 0
    while cursor <= end:
        chunk_end = min(cursor + span, end)
        chunks.append(CoverageChunk(index, cursor.isoformat(), chunk_end.isoformat()))
        cursor = chunk_end + step
        index += 1
    return tuple(chunks)


def validate_chunk_boundaries(chunks: tuple[CoverageChunk, ...], *, interval: str) -> None:
    """Reject overlaps, gaps, reversed chunks, or non-contiguous chunk boundaries."""
    if interval not in INTERVAL_SECONDS:
        raise ValueError(f"unsupported interval: {interval}")
    step = timedelta(seconds=INTERVAL_SECONDS[interval])
    for expected_index, chunk in enumerate(chunks):
        if chunk.index != expected_index:
            raise ValueError("chunk indices must be contiguous")
        start = _parse_utc(chunk.start_utc)
        end = _parse_utc(chunk.end_utc)
        if start > end:
            raise ValueError("chunk start must be <= chunk end")
        if expected_index:
            previous = chunks[expected_index - 1]
            previous_end = _parse_utc(previous.end_utc)
            if start != previous_end + step:
                raise ValueError("chunk boundaries are overlapping or non-contiguous")
