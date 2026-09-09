from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import OrderStatus


class DemoEvent(str, Enum):
    SUBMIT_ACK = "SUBMIT_ACK"
    FILL = "FILL"
    CANCEL_ACK = "CANCEL_ACK"
    REPLACE_ACK = "REPLACE_ACK"
    REJECT = "REJECT"
    TIMEOUT = "TIMEOUT"
    DISCONNECT = "DISCONNECT"


@dataclass(frozen=True)
class SimulatedEvent:
    event: DemoEvent
    order_id: str
    status: OrderStatus | None = None
    message: str = ""


def simulate(event: DemoEvent, order_id: str, status: OrderStatus | None = None, message: str = "") -> SimulatedEvent:
    return SimulatedEvent(event, order_id, status, message)
