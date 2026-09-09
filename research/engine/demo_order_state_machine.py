from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import OrderStatus


class OrderTransition(str, Enum):
    SUBMIT = "SUBMIT"
    FILL = "FILL"
    CANCEL = "CANCEL"
    EXPIRE = "EXPIRE"


_ALLOWED: dict[OrderStatus, dict[OrderTransition, OrderStatus]] = {
    OrderStatus.PENDING: {
        OrderTransition.FILL: OrderStatus.FILLED,
        OrderTransition.CANCEL: OrderStatus.CANCELLED,
        OrderTransition.EXPIRE: OrderStatus.EXPIRED,
    },
    OrderStatus.FILLED: {},
    OrderStatus.CANCELLED: {},
    OrderStatus.EXPIRED: {},
}


@dataclass(frozen=True)
class OrderStateMachine:
    status: OrderStatus = OrderStatus.PENDING

    def transition(self, event: OrderTransition) -> OrderStateMachine:
        try:
            next_status = _ALLOWED[self.status][event]
        except KeyError as exc:
            raise ValueError(f"invalid order transition: {self.status} + {event}") from exc
        return OrderStateMachine(next_status)
