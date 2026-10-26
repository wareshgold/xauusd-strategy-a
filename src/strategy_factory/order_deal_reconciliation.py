"""Conservative order/deal/position reconciliation for synthetic research fixtures.

This module links observed records by explicit identifiers only. It reports
conflicts and missing links; it does not infer fills, collapse partial deals,
or claim that a position is fully explained by the supplied history.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class ReconciliationStatus(str, Enum):
    LINKED = "LINKED"
    INCOMPLETE = "INCOMPLETE"
    CONFLICT = "CONFLICT"
    DUPLICATE = "DUPLICATE"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class OrderRecord:
    ticket: int
    position_id: int = 0


@dataclass(frozen=True)
class DealRecord:
    ticket: int
    order_ticket: int
    position_id: int


@dataclass(frozen=True)
class PositionRecord:
    ticket: int


@dataclass(frozen=True)
class Reconciliation:
    status: ReconciliationStatus
    order_ticket: int | None
    position_id: int | None
    deal_tickets: tuple[int, ...]
    issues: tuple[str, ...]


def reconcile_order_deals_positions(
    orders: Iterable[OrderRecord],
    deals: Iterable[DealRecord],
    positions: Iterable[PositionRecord],
) -> tuple[Reconciliation, ...]:
    """Return one result per observed order/deal/position group, preserving IDs.

    No timestamps are invented and no record is dropped to make a group fit.
    Duplicate identifiers, orphan deals, conflicting position IDs, and
    unreferenced positions remain explicit issues.
    """
    order_rows = tuple(orders)
    deal_rows = tuple(deals)
    position_rows = tuple(positions)

    order_counts: dict[int, int] = {}
    for row in order_rows:
        order_counts[row.ticket] = order_counts.get(row.ticket, 0) + 1
    deal_counts: dict[int, int] = {}
    for row in deal_rows:
        deal_counts[row.ticket] = deal_counts.get(row.ticket, 0) + 1
    position_counts: dict[int, int] = {}
    for row in position_rows:
        position_counts[row.ticket] = position_counts.get(row.ticket, 0) + 1

    orders_by_ticket = {r.ticket: r for r in order_rows if order_counts[r.ticket] == 1}
    positions_by_ticket = {r.ticket: r for r in position_rows if position_counts[r.ticket] == 1}
    deals_by_order: dict[int, list[DealRecord]] = {}
    for deal in deal_rows:
        deals_by_order.setdefault(deal.order_ticket, []).append(deal)

    results: list[Reconciliation] = []
    consumed_orders: set[int] = set()
    consumed_deals: set[int] = set()
    consumed_positions: set[int] = set()

    def build(order_ticket: int | None, position_id: int | None,
              linked_deals: list[DealRecord], issues: list[str]) -> Reconciliation:
        status = (
            ReconciliationStatus.DUPLICATE if any(x.startswith("DUPLICATE_") for x in issues)
            else ReconciliationStatus.CONFLICT if any(x.startswith("CONFLICT_") for x in issues)
            else ReconciliationStatus.UNRESOLVED if any(x.startswith("INVALID_") for x in issues)
            else ReconciliationStatus.INCOMPLETE if issues
            else ReconciliationStatus.LINKED
        )
        return Reconciliation(status, order_ticket, position_id,
                              tuple(sorted(d.ticket for d in linked_deals)), tuple(issues))

    for order in order_rows:
        if order.ticket in consumed_orders:
            continue
        consumed_orders.add(order.ticket)
        issues: list[str] = []
        if order.ticket <= 0:
            issues.append("INVALID_ORDER_TICKET")
        if order_counts[order.ticket] > 1:
            issues.append("DUPLICATE_ORDER_TICKET")
        if order.position_id < 0:
            issues.append("INVALID_ORDER_POSITION_ID")
        linked = list(deals_by_order.get(order.ticket, []))
        for deal in linked:
            consumed_deals.add(deal.ticket)
            if deal.ticket <= 0 or deal.order_ticket <= 0 or deal.position_id < 0:
                issues.append("INVALID_DEAL_IDENTIFIER")
            if deal_counts[deal.ticket] > 1:
                issues.append("DUPLICATE_DEAL_TICKET")
            if order.position_id and deal.position_id and order.position_id != deal.position_id:
                issues.append("CONFLICT_ORDER_DEAL_POSITION_ID")
        nonzero_positions = {d.position_id for d in linked if d.position_id > 0}
        if order.position_id > 0:
            nonzero_positions.add(order.position_id)
        if len(nonzero_positions) > 1:
            issues.append("CONFLICT_MULTIPLE_POSITION_IDS")
        position_id = next(iter(nonzero_positions)) if len(nonzero_positions) == 1 else None
        if not linked:
            issues.append("NO_LINKED_DEAL_OBSERVED")
        if position_id is not None:
            if position_id not in positions_by_ticket:
                issues.append("POSITION_NOT_PRESENT_IN_SUPPLIED_SNAPSHOT")
            else:
                consumed_positions.add(position_id)
                if position_counts[position_id] > 1:
                    issues.append("DUPLICATE_POSITION_TICKET")
        results.append(build(order.ticket, position_id, linked, issues))

    for deal in deal_rows:
        if deal.ticket in consumed_deals:
            continue
        issues = ["ORPHAN_DEAL_NO_UNIQUE_ORDER"]
        if deal.ticket <= 0 or deal.order_ticket <= 0 or deal.position_id < 0:
            issues.append("INVALID_DEAL_IDENTIFIER")
        if deal_counts[deal.ticket] > 1:
            issues.append("DUPLICATE_DEAL_TICKET")
        if deal.position_id > 0 and deal.position_id not in positions_by_ticket:
            issues.append("POSITION_NOT_PRESENT_IN_SUPPLIED_SNAPSHOT")
        elif deal.position_id > 0:
            consumed_positions.add(deal.position_id)
        results.append(build(deal.order_ticket or None, deal.position_id or None, [deal], issues))

    for position in position_rows:
        if position.ticket in consumed_positions:
            continue
        issues = []
        if position.ticket <= 0:
            issues.append("INVALID_POSITION_TICKET")
        if position_counts[position.ticket] > 1:
            issues.append("DUPLICATE_POSITION_TICKET")
        issues.append("UNREFERENCED_POSITION_IN_SUPPLIED_SNAPSHOT")
        results.append(build(None, position.ticket, [], issues))

    return tuple(results)
