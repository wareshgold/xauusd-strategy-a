from datetime import datetime, timezone

import pytest

from .demo_broker import InMemoryDemoBroker
from .demo_disconnect import EmergencyDisconnect
from .demo_gate_safety import DemoExecutionDecision, DemoGateSafety
from .demo_idempotency import IdempotentDemoSubmitter
from .demo_order_state_machine import OrderStateMachine, OrderTransition
from .demo_reconciliation import ReconciliationState, reconcile_order
from .demo_recovery import RecoveryAction, recover
from .models import Order, OrderStatus, OrderType, Side


def _order(order_id: str = "g80") -> Order:
    return Order(
        order_id=order_id,
        side=Side.BUY,
        order_type=OrderType.LIMIT,
        quantity=1.0,
        created_at=datetime(2026, 9, 9, tzinfo=timezone.utc),
        price=2500.0,
        stop_loss=2490.0,
        take_profit=2520.0,
        setup_id="SYNTHETIC-DEMO",
    )


def test_g80_valid_and_invalid_transitions():
    sm = OrderStateMachine()
    assert sm.transition(OrderTransition.FILL).status is OrderStatus.FILLED
    with pytest.raises(ValueError):
        sm.transition(OrderTransition.CANCEL).transition(OrderTransition.FILL)


def test_g81_duplicate_submit_returns_original_receipt():
    broker = InMemoryDemoBroker()
    submitter = IdempotentDemoSubmitter(broker)
    first = submitter.submit(_order("g81"))
    second = submitter.submit(_order("g81"))
    assert not first.duplicate
    assert second.duplicate
    assert second.receipt == first.receipt


def test_g82_match_continues_when_safety_allows():
    broker = InMemoryDemoBroker()
    broker.submit(_order("g82"))
    result = reconcile_order(broker, "g82", OrderStatus.PENDING)
    safety = DemoGateSafety(EmergencyDisconnect())
    safety.reset_and_arm()
    decision = recover(safety, result)
    assert result.state is ReconciliationState.MATCH
    assert decision.action is RecoveryAction.CONTINUE
    assert decision.execution is DemoExecutionDecision.ALLOW


def test_g82_mismatch_and_unknown_require_review():
    broker = InMemoryDemoBroker()
    safety = DemoGateSafety(EmergencyDisconnect())
    safety.reset_and_arm()
    unknown = reconcile_order(broker, "missing", OrderStatus.PENDING)
    assert recover(safety, unknown).action is RecoveryAction.REQUIRE_REVIEW
    broker.submit(_order("g82-mismatch"))
    broker.cancel("g82-mismatch")
    mismatch = reconcile_order(broker, "g82-mismatch", OrderStatus.PENDING)
    decision = recover(safety, mismatch)
    assert decision.action is RecoveryAction.REQUIRE_REVIEW
    assert decision.execution is DemoExecutionDecision.BLOCK
