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
    """Preserve ambiguous identities; never infer a completed fill from linkage."""
    order_rows, deal_rows, position_rows = tuple(orders), tuple(deals), tuple(positions)

    def counts(values):
        out = {}
        for value in values:
            out[value] = out.get(value, 0) + 1
        return out

    order_counts = counts(row.ticket for row in order_rows)
    deal_counts = counts(row.ticket for row in deal_rows)
    position_counts = counts(row.ticket for row in position_rows)
    deals_by_order = {}
    for index, deal in enumerate(deal_rows):
        deals_by_order.setdefault(deal.order_ticket, []).append((index, deal))

    results, handled_orders, handled_deal_indexes, referenced_positions = [], set(), set(), set()

    def build(order_ticket, position_id, linked, issues):
        status = (
            ReconciliationStatus.DUPLICATE if any(x.startswith("DUPLICATE_") for x in issues)
            else ReconciliationStatus.CONFLICT if any(x.startswith("CONFLICT_") for x in issues)
            else ReconciliationStatus.UNRESOLVED if any(x.startswith("INVALID_") for x in issues)
            else ReconciliationStatus.INCOMPLETE if issues
            else ReconciliationStatus.LINKED
        )
        return Reconciliation(status, order_ticket, position_id,
                              tuple(sorted(deal.ticket for deal in linked)), tuple(issues))

    for order in order_rows:
        if order.ticket in handled_orders:
            continue
        handled_orders.add(order.ticket)
        issues = []
        if order.ticket <= 0:
            issues.append("INVALID_ORDER_TICKET")
        if order.position_id < 0:
            issues.append("INVALID_ORDER_POSITION_ID")
        if order_counts[order.ticket] > 1:
            issues.extend(("DUPLICATE_ORDER_TICKET", "AMBIGUOUS_ORDER_NOT_UNIQUELY_LINKED"))
            results.append(build(order.ticket, None, [], issues))
            continue

        pairs = deals_by_order.get(order.ticket, [])
        linked = [deal for _, deal in pairs]
        handled_deal_indexes.update(index for index, _ in pairs)
        for deal in linked:
            if deal.ticket <= 0 or deal.order_ticket <= 0 or deal.position_id < 0:
                issues.append("INVALID_DEAL_IDENTIFIER")
            if deal_counts[deal.ticket] > 1:
                issues.append("DUPLICATE_DEAL_TICKET")
            if order.position_id and deal.position_id and order.position_id != deal.position_id:
                issues.append("CONFLICT_ORDER_DEAL_POSITION_ID")

        position_ids = {deal.position_id for deal in linked if deal.position_id > 0}
        if order.position_id > 0:
            position_ids.add(order.position_id)
        if len(position_ids) > 1:
            issues.append("CONFLICT_MULTIPLE_POSITION_IDS")
        position_id = next(iter(position_ids)) if len(position_ids) == 1 else None
        if not linked:
            issues.append("NO_LINKED_DEAL_OBSERVED")
        if position_id is not None:
            if position_counts.get(position_id, 0) > 1:
                issues.append("DUPLICATE_POSITION_TICKET")
                referenced_positions.add(position_id)
            elif position_counts.get(position_id, 0) == 0:
                issues.append("POSITION_NOT_PRESENT_IN_SUPPLIED_SNAPSHOT")
            else:
                referenced_positions.add(position_id)
        results.append(build(order.ticket, position_id, linked, issues))

    for index, deal in enumerate(deal_rows):
        if index in handled_deal_indexes:
            continue
        issues = ["ORPHAN_DEAL_NO_UNIQUE_ORDER"]
        if deal.ticket <= 0 or deal.order_ticket <= 0 or deal.position_id < 0:
            issues.append("INVALID_DEAL_IDENTIFIER")
        if deal_counts[deal.ticket] > 1:
            issues.append("DUPLICATE_DEAL_TICKET")
        if deal.position_id > 0:
            if position_counts.get(deal.position_id, 0) > 1:
                issues.append("DUPLICATE_POSITION_TICKET")
                referenced_positions.add(deal.position_id)
            elif position_counts.get(deal.position_id, 0) == 0:
                issues.append("POSITION_NOT_PRESENT_IN_SUPPLIED_SNAPSHOT")
            else:
                referenced_positions.add(deal.position_id)
        results.append(build(deal.order_ticket or None, deal.position_id or None, [deal], issues))

    for position in position_rows:
        if position.ticket in referenced_positions:
            if position_counts[position.ticket] > 1:
                results.append(build(None, position.ticket, [],
                                     ["DUPLICATE_POSITION_TICKET", "AMBIGUOUS_POSITION_IDENTITY"]))
            continue
        issues = []
        if position.ticket <= 0:
            issues.append("INVALID_POSITION_TICKET")
        if position_counts[position.ticket] > 1:
            issues.append("DUPLICATE_POSITION_TICKET")
        issues.append("UNREFERENCED_POSITION_IN_SUPPLIED_SNAPSHOT")
        results.append(build(None, position.ticket, [], issues))
        if position_counts[position.ticket] > 1:
            referenced_positions.add(position.ticket)

    return tuple(results)
