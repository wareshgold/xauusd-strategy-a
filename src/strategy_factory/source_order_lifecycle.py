"""Source-aligned order/deal lifecycle classification fixtures.

Research-only: this module classifies observed broker records. It does not
infer fills from order state, synthesize missing events, or define execution
semantics beyond explicitly supplied source labels.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OrderLifecycle(str, Enum):
    STARTED = "STARTED"
    PLACED = "PLACED"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    REQUEST_ADD = "REQUEST_ADD"
    REQUEST_MODIFY = "REQUEST_MODIFY"
    REQUEST_CANCEL = "REQUEST_CANCEL"
    UNKNOWN = "UNKNOWN"


class DealEntry(str, Enum):
    IN = "IN"
    OUT = "OUT"
    INOUT = "INOUT"
    OUT_BY = "OUT_BY"
    UNKNOWN = "UNKNOWN"


class EvidenceClass(str, Enum):
    ORDER_STATE_ONLY = "ORDER_STATE_ONLY"
    DEAL_RECORDED = "DEAL_RECORDED"
    PARTIAL_VOLUME_REMAINS = "PARTIAL_VOLUME_REMAINS"
    TERMINAL_ORDER_STATE = "TERMINAL_ORDER_STATE"
    UNRESOLVED = "UNRESOLVED"


TERMINAL_ORDER_STATES = {
    OrderLifecycle.FILLED,
    OrderLifecycle.CANCELED,
    OrderLifecycle.REJECTED,
    OrderLifecycle.EXPIRED,
}


@dataclass(frozen=True)
class OrderObservation:
    ticket: int
    state: str
    volume_initial: float | None = None
    volume_current: float | None = None


@dataclass(frozen=True)
class DealObservation:
    ticket: int
    order_ticket: int
    position_id: int
    entry: str
    volume: float | None = None


@dataclass(frozen=True)
class LifecycleClassification:
    evidence: EvidenceClass
    order_state: OrderLifecycle
    deal_entry: DealEntry | None
    reason: str


def classify_order_state(state: str) -> OrderLifecycle:
    try:
        return OrderLifecycle(state)
    except (ValueError, TypeError):
        return OrderLifecycle.UNKNOWN


def classify_deal_entry(entry: str) -> DealEntry:
    try:
        return DealEntry(entry)
    except (ValueError, TypeError):
        return DealEntry.UNKNOWN


def classify_lifecycle(
    order: OrderObservation | None,
    deal: DealObservation | None,
) -> LifecycleClassification:
    """Classify only the supplied broker observations; never infer absent events."""
    if order is None and deal is None:
        return LifecycleClassification(
            EvidenceClass.UNRESOLVED, OrderLifecycle.UNKNOWN, None,
            "NO_ORDER_OR_DEAL_OBSERVATION",
        )

    order_state = classify_order_state(order.state) if order else OrderLifecycle.UNKNOWN
    deal_entry = classify_deal_entry(deal.entry) if deal else None

    if deal is not None:
        if deal.ticket <= 0 or deal.order_ticket < 0 or deal.position_id < 0:
            return LifecycleClassification(
                EvidenceClass.UNRESOLVED, order_state, deal_entry,
                "INVALID_DEAL_IDENTIFIERS",
            )
        if deal_entry is DealEntry.UNKNOWN:
            return LifecycleClassification(
                EvidenceClass.UNRESOLVED, order_state, deal_entry,
                "UNKNOWN_DEAL_ENTRY_CLASS",
            )
        # A deal record proves a deal event exists, not that the whole order
        # was filled. Order state and deal entry remain separate evidence.
        return LifecycleClassification(
            EvidenceClass.DEAL_RECORDED, order_state, deal_entry,
            "BROKER_DEAL_RECORD_PRESENT_ORDER_COMPLETION_NOT_INFERRED",
        )

    if order is None or order.ticket <= 0:
        return LifecycleClassification(
            EvidenceClass.UNRESOLVED, order_state, None,
            "INVALID_OR_MISSING_ORDER_IDENTIFIERS",
        )

    if order_state is OrderLifecycle.UNKNOWN:
        return LifecycleClassification(
            EvidenceClass.UNRESOLVED, order_state, None,
            "UNKNOWN_ORDER_STATE",
        )

    if order_state is OrderLifecycle.PARTIAL:
        if order.volume_initial is None or order.volume_current is None:
            return LifecycleClassification(
                EvidenceClass.UNRESOLVED, order_state, None,
                "PARTIAL_STATE_WITHOUT_VOLUME_EVIDENCE",
            )
        if order.volume_initial < 0 or order.volume_current < 0:
            return LifecycleClassification(
                EvidenceClass.UNRESOLVED, order_state, None,
                "INVALID_ORDER_VOLUME",
            )
        if order.volume_current > order.volume_initial:
            return LifecycleClassification(
                EvidenceClass.UNRESOLVED, order_state, None,
                "CURRENT_VOLUME_EXCEEDS_INITIAL",
            )
        return LifecycleClassification(
            EvidenceClass.PARTIAL_VOLUME_REMAINS, order_state, None,
            "PARTIAL_ORDER_STATE_RECORDED_NO_SYNTHETIC_FILL_CREATED",
        )

    if order_state in TERMINAL_ORDER_STATES:
        return LifecycleClassification(
            EvidenceClass.TERMINAL_ORDER_STATE, order_state, None,
            "TERMINAL_ORDER_STATE_RECORDED_NOT_A_DEAL_LEDGER",
        )

    return LifecycleClassification(
        EvidenceClass.ORDER_STATE_ONLY, order_state, None,
        "NONTERMINAL_ORDER_STATE_ONLY",
    )
