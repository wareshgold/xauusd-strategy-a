from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .demo_broker import DemoBrokerAdapter
from .models import OrderStatus


class ReconciliationState(str, Enum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ReconciliationResult:
    order_id: str
    state: ReconciliationState
    local_status: OrderStatus | None
    broker_status: OrderStatus | None
    reason: str


def reconcile_order(broker: DemoBrokerAdapter, order_id: str, expected_status: OrderStatus) -> ReconciliationResult:
    try:
        remote = broker.snapshot(order_id)
    except Exception as exc:
        return ReconciliationResult(order_id, ReconciliationState.UNKNOWN, expected_status, None, str(exc))
    if remote.status is expected_status:
        return ReconciliationResult(order_id, ReconciliationState.MATCH, expected_status, remote.status, "state matches")
    return ReconciliationResult(order_id, ReconciliationState.MISMATCH, expected_status, remote.status, "broker state differs")
