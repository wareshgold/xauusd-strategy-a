from types import SimpleNamespace

import pytest

from scripts.sp2l_tracked_deal_history import (
    DealHistoryQueryError,
    collect_tracked_deals,
)


def test_resolves_order_to_position_and_returns_sorted_unique_deals():
    calls = []

    def history_orders_get(**kwargs):
        calls.append(("order", kwargs))
        return [SimpleNamespace(ticket=7, symbol="XAUUSD.ecn", position_id=70)]

    deals = [
        SimpleNamespace(ticket=702, time=20, symbol="XAUUSD.ecn", order=7, position_id=70),
        SimpleNamespace(ticket=701, time=10, symbol="XAUUSD.ecn", order=7, position_id=70),
        SimpleNamespace(ticket=701, time=10, symbol="XAUUSD.ecn", order=7, position_id=70),
        SimpleNamespace(ticket=999, time=5, symbol="EURUSD", order=7, position_id=70),
    ]

    result = collect_tracked_deals(
        history_deals_get=lambda **kwargs: deals,
        history_orders_get=history_orders_get,
        symbol="XAUUSD.ecn",
        tracked_orders={7},
        tracked_positions=set(),
    )

    assert [deal.ticket for deal in result] == [701, 702]
    assert calls == [("order", {"ticket": 7})]


def test_valid_empty_results_are_not_query_failures():
    result = collect_tracked_deals(
        history_deals_get=lambda **kwargs: [],
        history_orders_get=lambda **kwargs: [],
        symbol="XAUUSD.ecn",
        tracked_orders={7},
        tracked_positions={70},
    )
    assert result == []


@pytest.mark.parametrize("failed_result", [None])
def test_none_history_result_fails_closed(failed_result):
    with pytest.raises(DealHistoryQueryError) as exc:
        collect_tracked_deals(
            history_deals_get=lambda **kwargs: failed_result,
            history_orders_get=lambda **kwargs: [],
            symbol="XAUUSD.ecn",
            tracked_orders=set(),
            tracked_positions={70},
        )
    assert exc.value.query == "history_deals_get(position)"
    assert exc.value.target == 70


def test_query_exception_includes_mt5_last_error():
    def fail(**kwargs):
        raise RuntimeError("broker unavailable")

    with pytest.raises(DealHistoryQueryError) as exc:
        collect_tracked_deals(
            history_deals_get=fail,
            history_orders_get=lambda **kwargs: [],
            symbol="XAUUSD.ecn",
            tracked_orders=set(),
            tracked_positions={70},
            last_error=lambda: (-1, "terminal disconnected"),
        )
    assert "broker unavailable" in exc.value.detail
    assert "terminal disconnected" in exc.value.detail


def test_missing_query_function_is_not_treated_as_empty():
    with pytest.raises(DealHistoryQueryError, match="query function unavailable"):
        collect_tracked_deals(
            history_deals_get=None,
            history_orders_get=None,
            symbol="XAUUSD.ecn",
            tracked_orders=set(),
            tracked_positions={70},
        )
