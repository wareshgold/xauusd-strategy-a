from types import SimpleNamespace

import pytest

from scripts.sp2l_tracked_deal_history import collect_tracked_deals


def test_collects_sl_exit_by_position_without_host_time_window():
    entry = SimpleNamespace(
        ticket=62593812, order=63407773, position_id=63407773,
        time=1791969426, symbol="XAUUSD.ecn", entry=0, price=4159.75,
    )
    exit_deal = SimpleNamespace(
        ticket=62594573, order=63408767, position_id=63407773,
        time=1791970020, symbol="XAUUSD.ecn", entry=1, price=4154.55,
    )
    unrelated = SimpleNamespace(
        ticket=777, order=888, position_id=888,
        time=1791970030, symbol="XAUUSD.ecn", entry=1, price=1.0,
    )
    order = SimpleNamespace(ticket=63407773, position_id=63407773, symbol="XAUUSD.ecn")
    calls = []

    def deals_get(**kwargs):
        calls.append(("deals", kwargs))
        if kwargs == {"ticket": 63407773}:
            return [entry]
        if kwargs == {"position": 63407773}:
            return [entry, exit_deal, unrelated]
        raise AssertionError(f"unexpected history query: {kwargs}")

    def orders_get(**kwargs):
        calls.append(("orders", kwargs))
        assert kwargs == {"ticket": 63407773}
        return [order]

    result = collect_tracked_deals(
        history_deals_get=deals_get,
        history_orders_get=orders_get,
        symbol="XAUUSD.ecn",
        tracked_orders={63407773},
        tracked_positions=set(),
    )

    assert [deal.ticket for deal in result] == [62593812, 62594573]
    assert ("deals", {"position": 63407773}) in calls
    assert not any("date_from" in kwargs or "date_to" in kwargs for _, kwargs in calls)


def test_collects_known_position_and_deduplicates_deals():
    first = SimpleNamespace(
        ticket=1, order=10, position_id=20, time=100, symbol="XAUUSD.ecn",
    )
    second = SimpleNamespace(
        ticket=2, order=11, position_id=20, time=101, symbol="XAUUSD.ecn",
    )

    def deals_get(**kwargs):
        if kwargs == {"position": 20}:
            return [first, second]
        return []

    result = collect_tracked_deals(
        history_deals_get=deals_get,
        history_orders_get=lambda **kwargs: [],
        symbol="XAUUSD.ecn",
        tracked_orders=set(),
        tracked_positions={20},
    )

    assert [deal.ticket for deal in result] == [1, 2]



def test_none_history_result_raises_instead_of_becoming_empty():
    from scripts.sp2l_tracked_deal_history import DealHistoryQueryError

    with pytest.raises(DealHistoryQueryError, match="MT5 returned None") as exc:
        collect_tracked_deals(
            history_deals_get=lambda **kwargs: None,
            history_orders_get=lambda **kwargs: [],
            symbol="XAUUSD.ecn",
            tracked_orders={123},
            tracked_positions=set(),
        )
    assert exc.value.query == "history_deals_get(ticket)"
    assert exc.value.target == 123


def test_history_exception_is_preserved_as_query_failure():
    from scripts.sp2l_tracked_deal_history import DealHistoryQueryError

    def failed_query(**kwargs):
        raise OSError("terminal IPC unavailable")

    with pytest.raises(DealHistoryQueryError, match="terminal IPC unavailable") as exc:
        collect_tracked_deals(
            history_deals_get=failed_query,
            history_orders_get=lambda **kwargs: [],
            symbol="XAUUSD.ecn",
            tracked_orders={123},
            tracked_positions=set(),
        )
    assert exc.value.query == "history_deals_get(ticket)"


def test_history_query_failure_log_gate_suppresses_repeats_until_success():
    from scripts.sp2l_history_query_failure_log import HistoryQueryFailureLogGate

    gate = HistoryQueryFailureLogGate()
    failure = ("history_deals_get(ticket)", 63440809, "MT5 returned None")

    assert gate.should_log(*failure)
    assert not gate.should_log(*failure)

    gate.mark_success()

    assert gate.should_log(*failure)


def test_history_query_failure_log_gate_keeps_distinct_failures_visible():
    from scripts.sp2l_history_query_failure_log import HistoryQueryFailureLogGate

    gate = HistoryQueryFailureLogGate()

    assert gate.should_log("history_deals_get(ticket)", 10, "MT5 returned None")
    assert gate.should_log("history_deals_get(ticket)", 11, "MT5 returned None")
    assert gate.should_log("history_deals_get(ticket)", 10, "IPC timeout")
    assert not gate.should_log("history_deals_get(ticket)", 10, "IPC timeout")

