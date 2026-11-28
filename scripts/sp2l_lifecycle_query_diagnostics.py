"""Small, testable wrapper for MT5 lifecycle snapshot queries."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def query_snapshot_with_diagnostics(
    *,
    operation: Callable[[], Any],
    query: str,
    symbol: str,
    log_failure: Callable[[str, str, str], None],
    mark_success: Callable[[str], None],
    last_error: Callable[[], str],
) -> Any:
    """Return a successful snapshot, or None after exactly one failure report.

    An exception and an MT5 None result are distinct failure modes. In
    particular, an exception must not be re-reported as a second None result.
    """
    try:
        snapshot = operation()
    except Exception as exc:
        log_failure(query, symbol, f"{type(exc).__name__}: {exc}")
        return None

    if snapshot is None:
        log_failure(
            query,
            symbol,
            f"MT5 returned None; last_error={last_error()}",
        )
        return None

    mark_success(query)
    return snapshot
