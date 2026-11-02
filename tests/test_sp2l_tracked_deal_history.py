from types import SimpleNamespace

import pytest

from scripts.sp2l_tracked_deal_history import (
    DealHistoryQueryError,
    collect_tracked_deals,
)


def test_collects_order_deals_and_linked_position_deals_in_time_order():
    order = SimpleNamespace(ticket=100, symbol="XAUUSD", position_id=200)
    entry = SimpleNamespace(ticket=1, order=100, position_id=200, symbol="XAUUSD", time=10)
    exit_ = SimpleNamespace(ticket=2, order=101, position_id=200, symbol="XAUUSD", time=20)

    def history_orders_get(**kwargs):
        assert kwargs == {"ticket": 100}
        return [order]

    def history_deals_get(**kwargs):
        if "ticket" in kwargs:
            return [entry]
        assert kwargs == {"position": 200}
        return [entry, exit_]

    result = collect_tracked_deals(
        history_deals_get=history_deals_get,
        history_orders_get=history_orders_get,
        symbol="XAUUSD",
        tracked_orders={100},
        tracked_positions=set(),
    )

    assert [deal.ticket for deal in result] == [1, 2]


def test_empty_tuple_is_a_valid_empty_history_result():
    result = collect_tracked_deals(
        history_deals_get=lambda **kwargs: (),
        history_orders_get=lambda **kwargs: (),
        symbol="XAUUSD",
        tracked_orders={100},
        tracked_positions=set(),
    )
    assert result == []


def test_none_history_result_raises_and_includes_mt5_last_error():
    with pytest.raises(DealHistoryQueryError) as caught:
        collect_tracked_deals(
            history_deals_get=lambda **kwargs: None,
            history_orders_get=lambda **kwargs: (),
            symbol="XAUUSD",
            tracked_orders={100},
            tracked_positions=set(),
            last_error=lambda: (-1, "IPC timeout"),
        )

    assert caught.value.query == "history_deals_get(ticket)"
    assert caught.value.target == 100
    assert "MT5 returned None" in caught.value.detail
    assert "IPC timeout" in caught.value.detail


def test_history_query_exception_is_not_treated_as_empty():
    def fail(**kwargs):
        raise TimeoutError("history unavailable")

    with pytest.raises(DealHistoryQueryError, match="TimeoutError: history unavailable"):
        collect_tracked_deals(
            history_deals_get=fail,
            history_orders_get=lambda **kwargs: (),
            symbol="XAUUSD",
            tracked_orders={100},
            tracked_positions=set(),
        )
