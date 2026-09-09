from datetime import datetime, timezone

import pytest

from .demo_broker import DemoBrokerError, InMemoryDemoBroker
from .demo_lifecycle import DemoOrderLifecycle, LifecycleAction
from .execution_safety import CURRENT_RESEARCH_STATUS, ExecutionSafety, SafetyState
from .models import Order, OrderStatus, OrderType, Side


def _order() -> Order:
    return Order(
        order_id="fixture-1",
        side=Side.BUY,
        order_type=OrderType.LIMIT,
        quantity=1.0,
        created_at=datetime(2026, 9, 9, tzinfo=timezone.utc),
        price=2500.0,
        stop_loss=2490.0,
        take_profit=2520.0,
        setup_id="SYNTHETIC-DEMO",
    )


def test_demo_submit_cancel_replace_lifecycle():
    broker = InMemoryDemoBroker()
    lifecycle = DemoOrderLifecycle(broker)

    submitted = lifecycle.submit(_order())
    assert submitted.action is LifecycleAction.SUBMIT
    assert submitted.status is OrderStatus.PENDING

    replaced = lifecycle.replace("fixture-1", price=2501.0)
    assert replaced.action is LifecycleAction.REPLACE
    assert replaced.price == 2501.0
    assert broker.snapshot("fixture-1").price == 2501.0

    cancelled = lifecycle.cancel("fixture-1")
    assert cancelled.action is LifecycleAction.CANCEL
    assert cancelled.status is OrderStatus.CANCELLED


def test_demo_rejects_invalid_lifecycle_transitions():
    broker = InMemoryDemoBroker()
    broker.submit(_order())
    broker.cancel("fixture-1")
    with pytest.raises(DemoBrokerError):
        broker.replace("fixture-1", price=2502.0)


def test_kill_switch_defaults_closed():
    safety = ExecutionSafety()
    assert safety.state is SafetyState.KILLED
    assert not safety.allow_execution(CURRENT_RESEARCH_STATUS)


def test_current_research_cannot_arm_demo_execution():
    safety = ExecutionSafety()
    with pytest.raises(RuntimeError):
        safety.arm(CURRENT_RESEARCH_STATUS)
    assert safety.state is SafetyState.BLOCKED
    safety.kill()
    assert safety.state is SafetyState.KILLED
