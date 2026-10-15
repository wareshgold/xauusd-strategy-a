"""Deduplicate repeated MT5 history-query failure diagnostics per healthy poll interval.

This suppresses only duplicate telemetry. It does not convert failed queries into
empty history, mark deals as processed, or change lifecycle reconciliation.
"""
from __future__ import annotations


class HistoryQueryFailureLogGate:
    """Log each distinct query failure once until a complete poll succeeds."""

    def __init__(self) -> None:
        self._reported: set[tuple[str, int, str]] = set()

    def should_log(self, query: str, target: int, detail: str) -> bool:
        key = (str(query), int(target), str(detail))
        if key in self._reported:
            return False
        self._reported.add(key)
        return True

    def mark_success(self) -> None:
        """Allow a future recurrence to be logged after a successful poll."""
        self._reported.clear()
