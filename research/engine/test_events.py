from datetime import datetime, timezone

from .events import EventType, ExecutionConfig, IntrabarPolicy, SyntheticExecutionRunner
from .models import Candle, Order, OrderType, Side


def ts(minute: int) -> datetime:
    return datetime(2026, 1, 1, 0, minute, tzinfo=timezone.utc)


def order(price=100.0, stop=99.0, target=102.0):
    return Order("o1", Side.BUY, OrderType.LIMIT, 1.0, ts(0), price, stop, target)


def candle(minute, o, h, l, c):
    return Candle(ts(minute), o, h, l, c)


def test_unresolved_policy_does_not_invent_fill():
    events, trades = SyntheticExecutionRunner().run([candle(1, 101, 103, 98, 102)], [order()])
    assert any(e.event_type is EventType.UNRESOLVED for e in events)
    assert trades == []


def test_ohlc_path_fill_then_target():
    cfg = ExecutionConfig(IntrabarPolicy.OHLC_PATH)
    events, trades = SyntheticExecutionRunner(cfg).run([candle(1, 101, 103, 98, 102)], [order()])
    assert [e.event_type for e in events] == [EventType.BAR, EventType.FILL, EventType.TARGET]
    assert trades[0].exit_price == 102.0
    assert trades[0].exit_reason == "TARGET"


def test_ohlc_path_fill_then_stop():
    cfg = ExecutionConfig(IntrabarPolicy.OHLC_PATH)
    events, trades = SyntheticExecutionRunner(cfg).run([candle(1, 101, 103, 98, 99.5)], [order()])
    assert [e.event_type for e in events] == [EventType.BAR, EventType.FILL, EventType.STOP]
    assert trades[0].exit_price == 99.0


def test_path_order_changes_same_bar_outcome():
    bars = [candle(1, 101, 103, 98, 102)]
    o = order(stop=99.0, target=102.0)
    _, trades_ohlc = SyntheticExecutionRunner(ExecutionConfig(IntrabarPolicy.OHLC_PATH)).run(bars, [o])
    o2 = order(stop=99.0, target=102.0)
    _, trades_olhc = SyntheticExecutionRunner(ExecutionConfig(IntrabarPolicy.OLHC_PATH)).run(bars, [o2])
    assert trades_ohlc[0].exit_reason == "TARGET"
    assert trades_olhc[0].exit_reason == "STOP"


def test_expiry_is_deterministic():
    cfg = ExecutionConfig(IntrabarPolicy.OHLC_PATH, expire_after_bars=1)
    events, trades = SyntheticExecutionRunner(cfg).run(
        [candle(1, 110, 111, 109, 110), candle(2, 110, 111, 109, 110)], [order()]
    )
    assert trades == []
    assert events[-1].event_type is EventType.EXPIRE
