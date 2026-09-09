from datetime import datetime, timezone

from .demo_broker import InMemoryDemoBroker
from .demo_disconnect import ConnectionState, EmergencyDisconnect
from .demo_event_simulation import DemoEvent, simulate
from .demo_reconciliation import ReconciliationState, reconcile_order
from .models import Order, OrderStatus, OrderType, Side


def order() -> Order:
    return Order(
        order_id="g74-fixture",
        side=Side.BUY,
        order_type=OrderType.LIMIT,
        quantity=1.0,
        created_at=datetime(2026, 9, 9, tzinfo=timezone.utc),
        price=2500.0,
        stop_loss=2490.0,
        take_profit=2520.0,
        setup_id="SYNTHETIC-DEMO",
    )


def test_reconciliation_match_and_mismatch():
    broker = InMemoryDemoBroker()
    broker.submit(order())
    assert reconcile_order(broker, "g74-fixture", OrderStatus.PENDING).state is ReconciliationState.MATCH
    broker.cancel("g74-fixture")
    assert reconcile_order(broker, "g74-fixture", OrderStatus.PENDING).state is ReconciliationState.MISMATCH


def test_reconciliation_unknown_fails_closed_as_unknown():
    broker = InMemoryDemoBroker()
    result = reconcile_order(broker, "missing", OrderStatus.PENDING)
    assert result.state is ReconciliationState.UNKNOWN


def test_event_simulation_preserves_explicit_event():
    event = simulate(DemoEvent.TIMEOUT, "g75", message="simulated timeout")
    assert event.event is DemoEvent.TIMEOUT
    assert event.order_id == "g75"


def test_emergency_disconnect_defaults_closed_and_recovers_explicitly():
    control = EmergencyDisconnect()
    assert control.state is ConnectionState.DISCONNECTED
    assert not control.allow_requests()
    control.connect()
    assert control.allow_requests()
    control.disconnect()
    assert not control.allow_requests()
