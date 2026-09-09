from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .demo_broker import DemoBrokerAdapter, BrokerReceipt
from .models import Order, OrderStatus


class LifecycleAction(str, Enum):
    SUBMIT = "SUBMIT"
    CANCEL = "CANCEL"
    REPLACE = "REPLACE"


@dataclass(frozen=True)
class LifecycleEvent:
    action: LifecycleAction
    order_id: str
    status: OrderStatus
    broker_order_id: str
    price: float | None = None


class DemoOrderLifecycle:
    """Small explicit state machine around a demo broker adapter."""

    def __init__(self, broker: DemoBrokerAdapter) -> None:
        self.broker = broker

    def submit(self, order: Order) -> LifecycleEvent:
        receipt = self.broker.submit(order)
        return self._event(LifecycleAction.SUBMIT, receipt)

    def cancel(self, order_id: str) -> LifecycleEvent:
        receipt = self.broker.cancel(order_id)
        return self._event(LifecycleAction.CANCEL, receipt)

    def replace(self, order_id: str, *, price: float) -> LifecycleEvent:
        receipt = self.broker.replace(order_id, price=price)
        return self._event(LifecycleAction.REPLACE, receipt, price=price)

    @staticmethod
    def _event(action: LifecycleAction, receipt: BrokerReceipt, *, price: float | None = None) -> LifecycleEvent:
        return LifecycleEvent(action, receipt.order_id, receipt.status, receipt.broker_order_id, price)
