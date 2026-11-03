from scripts.sp2l_history_query_failure_log import HistoryQueryFailureLogGate


def test_logs_same_failure_once_until_success():
    gate = HistoryQueryFailureLogGate()
    assert gate.should_log("history_deals_get(position)", 123, "None")
    assert not gate.should_log("history_deals_get(position)", 123, "None")
    gate.mark_success()
    assert gate.should_log("history_deals_get(position)", 123, "None")


def test_distinct_failure_details_are_logged_independently():
    gate = HistoryQueryFailureLogGate()
    assert gate.should_log("history_orders_get", 10, "None")
    assert gate.should_log("history_orders_get", 10, "timeout")
    assert gate.should_log("history_orders_get", 11, "None")
