"""Deterministic multi-window historical dataset planning.

Strategy-neutral: plans acquisition windows only; it does not fetch data or
select Strategy A setups.
"""
from __future__ import annotations

from dataclasses import dataclass

from .coverage import CoverageChunk, plan_chunks, validate_chunk_boundaries


@dataclass(frozen=True)
class HistoricalWindow:
    name: str
    start_utc: str
    end_utc: str


@dataclass(frozen=True)
class WindowPlan:
    window: HistoricalWindow
    chunks: tuple[CoverageChunk, ...]


def plan_windows(windows: tuple[HistoricalWindow, ...], *, interval: str, max_points: int = 5000) -> tuple[WindowPlan, ...]:
    """Validate and deterministically expand named, non-overlapping windows."""
    ordered = sorted(windows, key=lambda w: (w.start_utc, w.end_utc, w.name))
    plans: list[WindowPlan] = []
    previous_end = None
    for window in ordered:
        chunks = plan_chunks(window.start_utc, window.end_utc, interval=interval, max_points=max_points)
        validate_chunk_boundaries(chunks, interval=interval)
        if previous_end is not None and window.start_utc <= previous_end:
            raise ValueError("historical windows overlap")
        previous_end = window.end_utc
        plans.append(WindowPlan(window, chunks))
    return tuple(plans)


def flatten_chunks(plans: tuple[WindowPlan, ...]) -> tuple[CoverageChunk, ...]:
    """Return chunks in deterministic window/chunk order."""
    result: list[CoverageChunk] = []
    for plan in plans:
        result.extend(plan.chunks)
    return tuple(result)
