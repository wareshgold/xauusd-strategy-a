"""Synthetic contract for history-query outcomes; no broker calls or completeness claims."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class HistoryQueryStatus(str, Enum):
    ROWS_OBSERVED = "ROWS_OBSERVED"
    EMPTY_OBSERVED = "EMPTY_OBSERVED"
    QUERY_FAILED = "QUERY_FAILED"
    UNRESOLVED = "UNRESOLVED"


class HistoryPollStatus(str, Enum):
    OBSERVATIONS_FOUND = "OBSERVATIONS_FOUND"
    EMPTY_OBSERVED = "EMPTY_OBSERVED"
    QUERY_FAILED_DEFER = "QUERY_FAILED_DEFER"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class HistoryQueryObservation:
    query: str
    target: int
    status: HistoryQueryStatus
    row_count: int | None
    issue: str | None = None


@dataclass(frozen=True)
class HistoryPollSummary:
    status: HistoryPollStatus
    successful_queries: int
    failed_queries: int
    observed_row_count: int | None
    issues: tuple[str, ...]


def observe_history_query(query: str, target: int, response: object) -> HistoryQueryObservation:
    """Classify a supplied fake query response using the source's None/empty distinction.

    A None response or raised exception means query failure. An empty iterable is
    an observed empty result for this query only, not proof history is complete.
    """
    if not query or target <= 0:
        return HistoryQueryObservation(
            query=query, target=target, status=HistoryQueryStatus.UNRESOLVED,
            row_count=None, issue="INVALID_QUERY_IDENTITY",
        )
    if isinstance(response, BaseException):
        return HistoryQueryObservation(
            query=query, target=target, status=HistoryQueryStatus.QUERY_FAILED,
            row_count=None, issue=f"QUERY_EXCEPTION:{type(response).__name__}",
        )
    if response is None:
        return HistoryQueryObservation(
            query=query, target=target, status=HistoryQueryStatus.QUERY_FAILED,
            row_count=None, issue="QUERY_RETURNED_NONE",
        )
    try:
        rows = tuple(response)  # only the supplied response is materialized
    except TypeError:
        return HistoryQueryObservation(
            query=query, target=target, status=HistoryQueryStatus.UNRESOLVED,
            row_count=None, issue="RESPONSE_NOT_ITERABLE",
        )
    if not rows:
        return HistoryQueryObservation(
            query=query, target=target, status=HistoryQueryStatus.EMPTY_OBSERVED,
            row_count=0,
        )
    return HistoryQueryObservation(
        query=query, target=target, status=HistoryQueryStatus.ROWS_OBSERVED,
        row_count=len(rows),
    )


def summarize_history_poll(
    observations: Iterable[HistoryQueryObservation],
) -> HistoryPollSummary:
    """Fail closed on any failed query; never call an empty poll complete history."""
    rows = tuple(observations)
    if not rows:
        return HistoryPollSummary(
            HistoryPollStatus.UNRESOLVED, 0, 0, None, ("NO_HISTORY_QUERIES_SUPPLIED",)
        )
    invalid = [row for row in rows if row.status is HistoryQueryStatus.UNRESOLVED]
    failed = [row for row in rows if row.status is HistoryQueryStatus.QUERY_FAILED]
    issues = tuple(
        f"{row.query}:{row.target}:{row.issue}"
        for row in rows if row.issue is not None
    )
    if invalid:
        return HistoryPollSummary(
            HistoryPollStatus.UNRESOLVED,
            sum(row.status is not HistoryQueryStatus.QUERY_FAILED for row in rows),
            len(failed), None, issues,
        )
    if failed:
        return HistoryPollSummary(
            HistoryPollStatus.QUERY_FAILED_DEFER,
            len(rows) - len(failed), len(failed), None, issues,
        )
    count = sum(row.row_count or 0 for row in rows)
    if count:
        return HistoryPollSummary(
            HistoryPollStatus.OBSERVATIONS_FOUND, len(rows), 0, count, issues
        )
    return HistoryPollSummary(
        HistoryPollStatus.EMPTY_OBSERVED, len(rows), 0, 0,
        ("EMPTY_RESULTS_ARE_NOT_HISTORY_COMPLETENESS",),
    )
