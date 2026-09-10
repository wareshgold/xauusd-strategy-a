from __future__ import annotations

from dataclasses import dataclass

from .demo_recovery_journal import RecoveryJournalEvent
from .demo_restart_recovery import recover_order


@dataclass(frozen=True)
class RecoveryAudit:
    order_id: str
    recovered_status: object
    event_count: int


def audit_recovery(order_id: str, events: tuple[RecoveryJournalEvent, ...]) -> RecoveryAudit:
    state = recover_order(order_id, events)
    return RecoveryAudit(order_id, state.state.status, len(events))
