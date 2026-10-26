from strategy_factory.history_query_fixtures import (
    HistoryPollStatus,
    HistoryQueryStatus,
    observe_history_query,
    summarize_history_poll,
)


def test_none_is_query_failure_not_empty_history():
    result = observe_history_query("history_deals_get(position)", 30, None)
    assert result.status is HistoryQueryStatus.QUERY_FAILED
    assert result.issue == "QUERY_RETURNED_NONE"
    summary = summarize_history_poll([result])
    assert summary.status is HistoryPollStatus.QUERY_FAILED_DEFER
    assert summary.observed_row_count is None


def test_exception_is_query_failure_and_defers_whole_poll():
    failed = observe_history_query("history_deals_get(ticket)", 10, RuntimeError("synthetic"))
    empty = observe_history_query("history_orders_get(ticket)", 10, ())
    summary = summarize_history_poll([failed, empty])
    assert summary.status is HistoryPollStatus.QUERY_FAILED_DEFER
    assert summary.failed_queries == 1
    assert summary.observed_row_count is None


def test_empty_tuple_is_a_successful_empty_query_not_a_fill():
    result = observe_history_query("history_deals_get(ticket)", 10, ())
    assert result.status is HistoryQueryStatus.EMPTY_OBSERVED
    assert result.row_count == 0
    summary = summarize_history_poll([result])
    assert summary.status is HistoryPollStatus.EMPTY_OBSERVED
    assert "EMPTY_RESULTS_ARE_NOT_HISTORY_COMPLETENESS" in summary.issues


def test_rows_are_observed_without_claiming_order_fully_filled():
    result = observe_history_query("history_deals_get(ticket)", 10, ({"ticket": 20},))
    summary = summarize_history_poll([result])
    assert result.status is HistoryQueryStatus.ROWS_OBSERVED
    assert summary.status is HistoryPollStatus.OBSERVATIONS_FOUND
    assert summary.observed_row_count == 1
    assert not hasattr(summary, "complete_fill")


def test_delayed_deal_can_appear_on_a_later_poll_without_rewriting_first_poll():
    first = summarize_history_poll([
        observe_history_query("history_deals_get(position)", 30, ())
    ])
    later = summarize_history_poll([
        observe_history_query("history_deals_get(position)", 30, ({"ticket": 21},))
    ])
    assert first.status is HistoryPollStatus.EMPTY_OBSERVED
    assert later.status is HistoryPollStatus.OBSERVATIONS_FOUND
    assert first.observed_row_count == 0
    assert later.observed_row_count == 1


def test_invalid_query_identity_is_unresolved():
    result = observe_history_query("history_deals_get(ticket)", 0, ())
    summary = summarize_history_poll([result])
    assert summary.status is HistoryPollStatus.UNRESOLVED
    assert summary.observed_row_count is None


def test_non_iterable_response_is_unresolved_not_empty():
    result = observe_history_query("history_deals_get(ticket)", 10, 7)
    assert result.status is HistoryQueryStatus.UNRESOLVED


def test_no_queries_is_unresolved_not_empty_history():
    summary = summarize_history_poll([])
    assert summary.status is HistoryPollStatus.UNRESOLVED
    assert summary.observed_row_count is None
