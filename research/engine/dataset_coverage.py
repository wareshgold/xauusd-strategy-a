"""Strategy-neutral deterministic historical acquisition coverage planner."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class CoverageWindow:
    start_date: str
    end_date: str


def plan_windows(start: date, end: date, *, days_per_window: int = 3) -> tuple[CoverageWindow, ...]:
    if end < start:
        raise ValueError("end date must be >= start date")
    if days_per_window < 1:
        raise ValueError("days_per_window must be >= 1")
    windows: list[CoverageWindow] = []
    cursor = start
    while cursor <= end:
        window_end = min(cursor + timedelta(days=days_per_window - 1), end)
        windows.append(CoverageWindow(cursor.isoformat(), window_end.isoformat()))
        cursor = window_end + timedelta(days=1)
    return tuple(windows)


def validate_non_overlapping(windows: tuple[CoverageWindow, ...]) -> None:
    previous_end: date | None = None
    for window in windows:
        start = date.fromisoformat(window.start_date)
        end = date.fromisoformat(window.end_date)
        if end < start:
            raise ValueError("coverage window end precedes start")
        if previous_end is not None and start <= previous_end:
            raise ValueError("coverage windows overlap")
        previous_end = end
