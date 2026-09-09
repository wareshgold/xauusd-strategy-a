from __future__ import annotations

from dataclasses import dataclass

from .demo_broker import BrokerReceipt, DemoBrokerError, DemoBrokerAdapter
from .models import Order


@dataclass(frozen=True)
class IdempotentSubmitResult:
    receipt: BrokerReceipt
    duplicate: bool


class IdempotentDemoSubmitter:
    """Deduplicates retries by immutable client order id."""

    def __init__(self, broker: DemoBrokerAdapter) -> None:
        self.broker = broker
        self._receipts: dict[str, BrokerReceipt] = {}

    def submit(self, order: Order) -> IdempotentSubmitResult:
        cached = self._receipts.get(order.order_id)
        if cached is not None:
            return IdempotentSubmitResult(cached, True)
        try:
            receipt = self.broker.submit(order)
        except DemoBrokerError:
            existing = self._receipts.get(order.order_id)
            if existing is not None:
                return IdempotentSubmitResult(existing, True)
            raise
        self._receipts[order.order_id] = receipt
        return IdempotentSubmitResult(receipt, False)
