"""Paired order/deal history observation contract for offline research.

This pure function layer combines two already-observed adapter outcomes. It
never queries a provider, infers history completeness, reconciles rows, or
decides whether a position exists.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from scripts.sp2l_read_only_history_adapter_research import (
    HistoryQueryKind,
    HistoryQueryResult,
    HistoryQueryStatus,
)


class HistoryPairStatus(str, Enum):
    BOTH_RESPONSES_VALID = "both_responses_valid"
    AT_LEAST_ONE_QUERY_FAILED = "at_least_one_query_failed"


@dataclass(frozen=True)
class HistoryPairObservation:
    """Preserve independent order/deal outcomes under one lifecycle key."""

    position_identifier: int
    orders: HistoryQueryResult
    deals: HistoryQueryResult
    status: HistoryPairStatus


def pair_history_observations(
    *,
    orders: HistoryQueryResult,
    deals: HistoryQueryResult,
) -> HistoryPairObservation:
    """Validate and pair outcomes without merging or interpreting their rows.

    EMPTY is a valid response, but this pair contract does not claim that either
    empty result proves history completeness or absence of a broker object.
    """
    if not isinstance(orders, HistoryQueryResult):
        raise TypeError("orders must be a HistoryQueryResult")
    if not isinstance(deals, HistoryQueryResult):
        raise TypeError("deals must be a HistoryQueryResult")
    if orders.query_kind is not HistoryQueryKind.ORDERS:
        raise ValueError("orders result must have query_kind=ORDERS")
    if deals.query_kind is not HistoryQueryKind.DEALS:
        raise ValueError("deals result must have query_kind=DEALS")
    if orders.position_identifier != deals.position_identifier:
        raise ValueError("order and deal observations must share position_identifier")

    valid_statuses = {HistoryQueryStatus.EMPTY, HistoryQueryStatus.NON_EMPTY}
    status = (
        HistoryPairStatus.BOTH_RESPONSES_VALID
        if orders.status in valid_statuses and deals.status in valid_statuses
        else HistoryPairStatus.AT_LEAST_ONE_QUERY_FAILED
    )
    return HistoryPairObservation(
        position_identifier=orders.position_identifier,
        orders=orders,
        deals=deals,
        status=status,
    )
