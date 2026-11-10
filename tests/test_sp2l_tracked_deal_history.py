from types import SimpleNamespace

from scripts.sp2l_tracked_deal_history import collect_tracked_deals


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

    assert calls == [("orders", {"ticket": 100}), ("deals", {"position": 200})]
    assert [deal.ticket for deal in result.deals] == [1, 2]
    assert result.failures == []


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
    assert [item.ticket for item in result.deals] == [2]
    assert result.failures == []


def test_active_order_is_not_sent_to_historical_order_query():
    deal = SimpleNamespace(ticket=1, order=100, position_id=200, symbol="XAUUSD", time=10)

    def forbidden_history_order_query(**kwargs):
        raise AssertionError("active order must not be queried as historical")

    result = collect_tracked_deals(
        history_deals_get=lambda **kwargs: [deal],
        history_orders_get=forbidden_history_order_query,
        symbol="XAUUSD",
        tracked_orders={100},
        tracked_positions={200},
        active_order_ids={100},
    )
    assert [item.ticket for item in result.deals] == [1]
    assert result.failures == []


def test_order_history_failure_does_not_block_known_position_deals():
    deal = SimpleNamespace(ticket=2, order=101, position_id=200, symbol="XAUUSD", time=20)

    result = collect_tracked_deals(
        history_deals_get=lambda **kwargs: [deal],
        history_orders_get=lambda **kwargs: None,
        symbol="XAUUSD",
        tracked_orders={100},
        tracked_positions={200},
        last_error=lambda: (-2, "Terminal: Invalid params"),
    )
    assert [item.ticket for item in result.deals] == [2]
    assert len(result.failures) == 1
    assert result.failures[0].query == "history_orders_get"
    assert result.failures[0].target == 100
    assert "Invalid params" in result.failures[0].detail


def test_order_history_failure_without_known_positions_is_not_empty_success():
    result = collect_tracked_deals(
        history_deals_get=lambda **kwargs: (),
        history_orders_get=lambda **kwargs: None,
        symbol="XAUUSD",
        tracked_orders={100},
        tracked_positions=set(),
    )
    assert result.deals == []
    assert len(result.failures) == 1
    assert result.failures[0].query == "history_orders_get"


def test_position_history_failure_is_reported_without_losing_other_positions():
    deal = SimpleNamespace(ticket=3, order=103, position_id=300, symbol="XAUUSD", time=30)

    def history_deals_get(**kwargs):
        if kwargs == {"position": 200}:
            return None
        if kwargs == {"position": 300}:
            return [deal]
        raise AssertionError(kwargs)

    result = collect_tracked_deals(
        history_deals_get=history_deals_get,
        history_orders_get=lambda **kwargs: (),
        symbol="XAUUSD",
        tracked_orders=set(),
        tracked_positions={200, 300},
    )
    assert [item.ticket for item in result.deals] == [3]
    assert len(result.failures) == 1
    assert result.failures[0].query == "history_deals_get(position)"
    assert result.failures[0].target == 200


def test_empty_order_and_position_histories_are_valid():
    result = collect_tracked_deals(
        history_deals_get=lambda **kwargs: (),
        history_orders_get=lambda **kwargs: (),
        symbol="XAUUSD",
        tracked_orders={100},
        tracked_positions=set(),
    )
    assert result.deals == []
    assert result.failures == []


def test_missing_order_history_function_is_reported():
    result = collect_tracked_deals(
        history_deals_get=lambda **kwargs: (),
        history_orders_get=None,
        symbol="XAUUSD",
        tracked_orders={100},
        tracked_positions=set(),
    )
    assert result.deals == []
    assert len(result.failures) == 1
    assert result.failures[0].detail == "query function unavailable"


def test_history_query_exception_is_not_treated_as_empty():
    def fail(**kwargs):
        raise TimeoutError("history unavailable")

    result = collect_tracked_deals(
        history_deals_get=lambda **kwargs: (),
        history_orders_get=fail,
        symbol="XAUUSD",
        tracked_orders={100},
        tracked_positions=set(),
    )
    assert result.deals == []
    assert len(result.failures) == 1
    assert "TimeoutError: history unavailable" in result.failures[0].detail


def test_active_pending_order_without_position_is_valid_empty_history():
    def forbidden_history_order_query(**kwargs):
        raise AssertionError("active pending order must not be queried as history")

    result = collect_tracked_deals(
        history_deals_get=lambda **kwargs: (),
        history_orders_get=forbidden_history_order_query,
        symbol="XAUUSD",
        tracked_orders={100},
        tracked_positions=set(),
        active_order_ids={100},
    )
    assert result.deals == []
    assert result.failures == []
