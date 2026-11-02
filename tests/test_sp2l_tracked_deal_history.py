from types import SimpleNamespace

import pytest

from scripts.sp2l_tracked_deal_history import (
    DealHistoryQueryError,
    collect_tracked_deals,
)


def test_resolves_order_then_collects_linked_position_deals_in_time_order():
    order = SimpleNamespace(ticket=100, symbol="XAUUSD", position_id=200)
    entry = SimpleNamespace(ticket=1, order=100, position_id=200, symbol="XAUUSD", time=10)
    exit_ = SimpleNamespace(ticket=2, order=101, position_id=200, symbol="XAUUSD", time=20)
    calls = []

    def history_orders_get(**kwargs):
        calls.append(("orders", kwargs))
        assert kwargs == {"ticket": 100}
        return [order]

    def history_deals_get(**kwargs):
        calls.append(("deals", kwargs))
        assert kwargs == {"position": 200}
        return [entry, exit_]

    result = collect_tracked_deals(
        history_deals_get=history_deals_get,
        history_orders_get=history_orders_get,
        symbol="XAUUSD",
        tracked_orders={100},
        tracked_positions=set(),
    )

    assert calls == [
        ("orders", {"ticket": 100}),
        ("deals", {"position": 200}),
    ]
    assert [deal.ticket for deal in result] == [1, 2]


def test_collects_known_position_without_tracked_orders():
    deal = SimpleNamespace(ticket=2, order=101, position_id=200, symbol="XAUUSD", time=20)

    def unexpected_order_lookup(**kwargs):
        raise AssertionError("no order lookup expected")

    result = collect_tracked_deals(
        history_deals_get=lambda **kwargs: [deal] if kwargs == {"position": 200} else None,
        history_orders_get=unexpected_order_lookup,
        symbol="XAUUSD",
        tracked_orders=set(),
        tracked_positions={200},
    )

    assert [item.ticket for item in result] == [2]


def test_empty_order_and_position_histories_are_valid():
    result = collect_tracked_deals(
        history_deals_get=lambda **kwargs: (),
        history_orders_get=lambda **kwargs: (),
        symbol="XAUUSD",
        tracked_orders={100},
        tracked_positions=set(),
    )
    assert result == []


def test_missing_order_history_function_fails_closed():
    with pytest.raises(DealHistoryQueryError, match="query function unavailable"):
        collect_tracked_deals(
            history_deals_get=lambda **kwargs: (),
            history_orders_get=None,
            symbol="XAUUSD",
            tracked_orders={100},
            tracked_positions=set(),
        )


def test_none_order_history_result_raises_and_includes_mt5_last_error():
    with pytest.raises(DealHistoryQueryError) as caught:
        collect_tracked_deals(
            history_deals_get=lambda **kwargs: (),
            history_orders_get=lambda **kwargs: None,
            symbol="XAUUSD",
            tracked_orders={100},
            tracked_positions=set(),
            last_error=lambda: (-1, "IPC timeout"),
        )

    assert caught.value.query == "history_orders_get"
    assert caught.value.target == 100
    assert "MT5 returned None" in caught.value.detail
    assert "IPC timeout" in caught.value.detail


def test_none_position_history_result_raises():
    order = SimpleNamespace(ticket=100, symbol="XAUUSD", position_id=200)

    with pytest.raises(DealHistoryQueryError) as caught:
        collect_tracked_deals(
            history_deals_get=lambda **kwargs: None,
            history_orders_get=lambda **kwargs: [order],
            symbol="XAUUSD",
            tracked_orders={100},
            tracked_positions=set(),
        )

    assert caught.value.query == "history_deals_get(position)"
    assert caught.value.target == 200


def test_history_query_exception_is_not_treated_as_empty():
    def fail(**kwargs):
        raise TimeoutError("history unavailable")

    with pytest.raises(DealHistoryQueryError, match="TimeoutError: history unavailable"):
        collect_tracked_deals(
            history_deals_get=lambda **kwargs: (),
            history_orders_get=fail,
            symbol="XAUUSD",
            tracked_orders={100},
            tracked_positions=set(),
        )
