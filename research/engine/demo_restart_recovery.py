from __future__ import annotations

from dataclasses import dataclass

from .demo_order_state_machine import OrderStateMachine
from .demo_recovery_journal import RecoveryJournal, RecoveryJournalEvent
from .models import OrderStatus


@dataclass(frozen=True)
class RecoveredOrder:
    order_id: str
    state: OrderStateMachine


def recover_order(order_id: str, events: tuple[RecoveryJournalEvent, ...]) -> RecoveredOrder:
    state = OrderStateMachine()
    relevant = [event for event in events if event.order_id == order_id]
    for event in relevant:
        mapping = {
            "FILL": "FILL",
            "CANCEL": "CANCEL",
            "EXPIRE": "EXPIRE",
        }
        transition = mapping.get(event.event)
        if transition is None:
            continue
        from .demo_order_state_machine import OrderTransition
        state = state.transition(OrderTransition(transition))
    return RecoveredOrder(order_id, state)
