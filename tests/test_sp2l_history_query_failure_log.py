from scripts.sp2l_history_query_failure_log import HistoryQueryFailureLogGate


def test_repeated_identical_failure_is_logged_once_until_success():
    gate = HistoryQueryFailureLogGate()

    assert gate.should_log("history_deals_get(ticket)", 63440809, "MT5 returned None")
    assert not gate.should_log("history_deals_get(ticket)", 63440809, "MT5 returned None")

    gate.mark_success()

    assert gate.should_log("history_deals_get(ticket)", 63440809, "MT5 returned None")


def test_distinct_targets_and_details_remain_visible():
    gate = HistoryQueryFailureLogGate()

    assert gate.should_log("history_deals_get(ticket)", 10, "MT5 returned None")
    assert gate.should_log("history_deals_get(ticket)", 11, "MT5 returned None")
    assert gate.should_log("history_deals_get(ticket)", 10, "IPC timeout")
    assert not gate.should_log("history_deals_get(ticket)", 10, "IPC timeout")


def test_success_clears_all_previously_reported_failures():
    gate = HistoryQueryFailureLogGate()

    assert gate.should_log("history_orders_get", 42, "MT5 returned None")
    gate.mark_success()
    assert gate.should_log("history_orders_get", 42, "MT5 returned None")
