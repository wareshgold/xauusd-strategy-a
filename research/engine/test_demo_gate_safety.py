from datetime import datetime, timezone

import pytest

from .demo_broker import InMemoryDemoBroker
from .demo_disconnect import EmergencyDisconnect
from .demo_gate_safety import DemoExecutionDecision, DemoGateSafety
from .demo_reconciliation import ReconciliationState, reconcile_order
from .models import Order, OrderStatus, OrderType, Side


def _order() -> Order:
    return Order(
        order_id="g77-fixture",
        side=Side.BUY,
        order_type=OrderType.LIMIT,
        quantity=1.0,
        created_at=datetime(2026, 9, 9, tzinfo=timezone.utc),
        price=2500.0,
        stop_loss=2490.0,
        take_profit=2520.0,
        setup_id="SYNTHETIC-DEMO",
    )


def test_safety_defaults_blocked():
    broker = InMemoryDemoBroker()
    broker.submit(_order())
    result = reconcile_order(broker, "g77-fixture", OrderStatus.PENDING)
    safety = DemoGateSafety(EmergencyDisconnect())
    assert result.state is ReconciliationState.MATCH
    assert safety.decision(result) is DemoExecutionDecision.BLOCK


def test_unknown_or_mismatch_never_allows_execution():
    broker = InMemoryDemoBroker()
    safety = DemoGateSafety(EmergencyDisconnect())
    safety.reset_and_arm()
    unknown = reconcile_order(broker, "missing", OrderStatus.PENDING)
    assert safety.decision(unknown) is DemoExecutionDecision.BLOCK
    broker.submit(_order())
    broker.cancel("g77-fixture")
    mismatch = reconcile_order(broker, "g77-fixture", OrderStatus.PENDING)
    assert safety.decision(mismatch) is DemoExecutionDecision.BLOCK


def test_kill_forces_disconnect_and_requires_explicit_reset():
    broker = InMemoryDemoBroker()
    broker.submit(_order())
    result = reconcile_order(broker, "g77-fixture", OrderStatus.PENDING)
    safety = DemoGateSafety(EmergencyDisconnect())
    safety.reset_and_arm()
    assert safety.decision(result) is DemoExecutionDecision.ALLOW
    safety.kill()
    assert safety.decision(result) is DemoExecutionDecision.BLOCK
    with pytest.raises(RuntimeError):
        safety.arm()
    safety.reset_and_arm()
    assert safety.decision(result) is DemoExecutionDecision.ALLOW
