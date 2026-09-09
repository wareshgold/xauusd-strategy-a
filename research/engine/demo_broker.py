from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Protocol

from .models import Order, OrderStatus, OrderType, Side


class DemoBrokerError(RuntimeError):
    pass


class BrokerMode(str, Enum):
    DEMO = "DEMO"


@dataclass(frozen=True)
class BrokerReceipt:
    broker_order_id: str
    order_id: str
    status: OrderStatus
    mode: BrokerMode = BrokerMode.DEMO


class DemoBrokerAdapter(Protocol):
    mode: BrokerMode

    def submit(self, order: Order) -> BrokerReceipt: ...
    def cancel(self, order_id: str) -> BrokerReceipt: ...
    def replace(self, order_id: str, *, price: float) -> BrokerReceipt: ...
    def snapshot(self, order_id: str) -> Order: ...


class InMemoryDemoBroker:
    """Deterministic broker-shaped adapter; no network or live venue access."""

    mode = BrokerMode.DEMO

    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}
        self._broker_ids: dict[str, str] = {}

    def submit(self, order: Order) -> BrokerReceipt:
        if order.order_id in self._orders:
            raise DemoBrokerError("order already exists")
        if order.quantity <= 0:
            raise DemoBrokerError("quantity must be positive")
        if order.order_type is not OrderType.MARKET and order.price is None:
            raise DemoBrokerError("priced order requires price")
        stored = replace(order)
        self._orders[order.order_id] = stored
        broker_id = f"DEMO-{order.order_id}"
        self._broker_ids[order.order_id] = broker_id
        return BrokerReceipt(broker_id, order.order_id, stored.status)

    def cancel(self, order_id: str) -> BrokerReceipt:
        order = self._require(order_id)
        if order.status is not OrderStatus.PENDING:
            raise DemoBrokerError("only pending orders can be cancelled")
        order.status = OrderStatus.CANCELLED
        return BrokerReceipt(self._broker_ids[order_id], order_id, order.status)

    def replace(self, order_id: str, *, price: float) -> BrokerReceipt:
        order = self._require(order_id)
        if order.status is not OrderStatus.PENDING:
            raise DemoBrokerError("only pending orders can be replaced")
        if price <= 0:
            raise DemoBrokerError("price must be positive")
        order.price = price
        return BrokerReceipt(self._broker_ids[order_id], order_id, order.status)

    def snapshot(self, order_id: str) -> Order:
        return replace(self._require(order_id), metadata=dict(self._require(order_id).metadata))

    def _require(self, order_id: str) -> Order:
        try:
            return self._orders[order_id]
        except KeyError as exc:
            raise DemoBrokerError("unknown order") from exc
