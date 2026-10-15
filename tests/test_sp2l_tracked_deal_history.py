from types import SimpleNamespace

import pytest

from scripts.sp2l_tracked_deal_history import (
    DealHistoryQueryError,
    collect_tracked_deals,
)


def test_resolves_orders_then_queries_deals_by_position_not_order_ticket():
    order = SimpleNamespace(ticket=101, symbol="XAUUSD.ecn", position_id=501)
    entry = SimpleNamespace(
        ticket=9001, order=101, position_id=501, symbol="XAUUSD.ecn", time=100, profit=0
    )
    close = SimpleNamespace(
        ticket=9002, order=102, position_id=501, symbol="XAUUSD.ecn", time=200, profit=1.9
    )
    calls = []

    def history_orders_get(**kwargs):
        calls.append(("order", kwargs))
        assert kwargs == {"ticket": 101}
        return (order,)

    def history_deals_get(**kwargs):
        calls.append(("deal", kwargs))
        assert "ticket" not in kwargs
        assert kwargs == {"position": 501}
        return (entry, close)

    deals = collect_tracked_deals(
        history_deals_get=history_deals_get,
        history_orders_get=history_orders_get,
        symbol="XAUUSD.ecn",
        tracked_orders={101},
        tracked_positions=set(),
    )

    assert [deal.ticket for deal in deals] == [9001, 9002]
    assert calls == [
        ("order", {"ticket": 101}),
        ("deal", {"position": 501}),
    ]


def test_tracked_position_can_be_queried_without_order_history():
    close = SimpleNamespace(
        ticket=9002, order=102, position_id=501, symbol="XAUUSD.ecn", time=200
    )
    calls = []

    def history_deals_get(**kwargs):
        calls.append(kwargs)
        return (close,)

    deals = collect_tracked_deals(
        history_deals_get=history_deals_get,
        history_orders_get=None,
        symbol="XAUUSD.ecn",
        tracked_orders=set(),
        tracked_positions={501},
    )

    assert [deal.ticket for deal in deals] == [9002]
    assert calls == [{"position": 501}]


def test_none_history_result_includes_mt5_last_error_and_is_not_empty_history():
    def history_orders_get(**kwargs):
        return None

    error = ("-2", "No history")
    with pytest.raises(DealHistoryQueryError) as raised:
        collect_tracked_deals(
            history_deals_get=lambda **kwargs: (),
            history_orders_get=history_orders_get,
            symbol="XAUUSD.ecn",
            tracked_orders={101},
            tracked_positions=set(),
            last_error=lambda: error,
        )

    assert raised.value.query == "history_orders_get(ticket)"
    assert raised.value.target == 101
    assert "mt5_last_error=" in raised.value.detail
    assert repr(error) in raised.value.detail


def test_empty_order_history_is_valid_and_does_not_query_deals_by_order_ticket():
    calls = []

    def history_orders_get(**kwargs):
        return ()

    def history_deals_get(**kwargs):
        calls.append(kwargs)
        return ()

    deals = collect_tracked_deals(
        history_deals_get=history_deals_get,
        history_orders_get=history_orders_get,
        symbol="XAUUSD.ecn",
        tracked_orders={101},
        tracked_positions=set(),
    )

    assert deals == []
    assert calls == []
