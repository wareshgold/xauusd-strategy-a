from scripts.audit_sp2l_history_query_failures import build_report


def _event(query, target, detail="MT5 returned None", ts="2026-11-07T10:00:00+00:00"):
    return {
        "event": "MT5_DEAL_HISTORY_QUERY_FAILED",
        "query": query,
        "target": target,
        "detail": detail,
        "ts_utc": ts,
    }


def test_groups_query_families_and_anonymizes_targets():
    events = [
        _event("history_orders_get", 22),
        _event("history_deals_get(ticket)", 22),
        _event("history_deals_get(position)", 33),
    ]
    deals = [{"ticket": 1, "order": 22, "position_id": 33}]
    orders = [{"ticket": 22}]

    report = build_report(events, deals, orders)

    assert report["event_count"] == 3
    assert report["unique_query_target_pairs"] == 3
    assert report["final_history_target_status"] == {
        "PRESENT_IN_FINAL_DEAL_HISTORY": 1,
        "PRESENT_IN_FINAL_ORDER_HISTORY": 1,
        "PRESENT_IN_FINAL_POSITION_DEALS": 1,
    }
    assert report["failure_rate"] == "UNAVAILABLE_WITHOUT_TOTAL_QUERY_ATTEMPT_DENOMINATOR"
    assert "22" not in str(report)
    assert "33" not in str(report)


def test_repeated_emission_is_counted_without_claiming_total_api_failures():
    events = [
        _event("history_deals_get(ticket)", 22),
        _event("history_deals_get(ticket)", 22),
        _event("history_deals_get(ticket)", 23, "TimeoutError: timed out"),
    ]

    report = build_report(events, [], [])

    assert report["event_count"] == 3
    assert report["unique_failure_signatures"] == 2
    assert report["repeated_signature_emissions"] == 1
    assert report["query_families"]["history_deals_get(ticket)"]["distinct_targets"] == 2


def test_detail_categories_capture_mt5_error_code():
    events = [
        _event("history_orders_get", 22, "MT5 returned None; MT5 last_error=(-10005, 'IPC timeout')"),
        _event("history_orders_get", 23, "TimeoutError: history unavailable"),
    ]

    report = build_report(events, [], [])

    assert report["detail_categories"] == {
        "MT5_LAST_ERROR_-10005": 1,
        "PYTHON_TIMEOUTERROR": 1,
    }
