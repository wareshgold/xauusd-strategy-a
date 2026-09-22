"""Deterministic tests for forward-stream audit invariants."""

from scripts.audit_sp2l_multi_symbol_forward_test import audit


def test_clean_candidate_attempt_result_and_lifecycle():
    events = [
        {"event": "CANDIDATE", "symbol": "XAUUSD.ecn", "signal_id": "X:1:BUY",
         "candidate": {"risk": 2.0}, "f13_2x": {"secondary_entry": 9.0}},
        {"event": "ORDER_ATTEMPT", "symbol": "XAUUSD.ecn", "signal_id": "X:1:BUY"},
        {"event": "ORDER_RESULT", "symbol": "XAUUSD.ecn", "signal_id": "X:1:BUY",
         "success": True, "tracked_order": 1001},
        {"event": "TELEGRAM_DEAL_LIFECYCLE", "symbol": "XAUUSD.ecn",
         "deal": 2001, "order": 1001, "entry": 0, "pips_result": None},
        {"event": "TELEGRAM_DEAL_LIFECYCLE", "symbol": "XAUUSD.ecn",
         "deal": 2002, "order": 1001, "entry": 1, "pips_result": 12.0, "net": 4.0},
    ]
    report = audit(events)
    assert report["signals"]["candidate_without_attempt"] == []
    assert report["signals"]["attempt_without_candidate"] == []
    assert report["signals"]["order_result_without_attempt"] == []
    assert report["integrity"]["duplicate_order_result_events"] == 0
    assert report["integrity"]["duplicate_lifecycle_deal_events"] == 0
    assert report["linkage"]["unmatched_lifecycle_orders"] == []
    assert report["lifecycle"]["measured_close_pips"] == 1
    assert report["lifecycle"]["wins"] == 1


def test_orphan_and_duplicate_records_are_exposed():
    events = [
        {"event": "ORDER_RESULT", "symbol": "EURUSD.ecn", "signal_id": "E:2:SELL",
         "success": True, "tracked_order": 2002},
        {"event": "ORDER_RESULT", "symbol": "EURUSD.ecn", "signal_id": "E:2:SELL",
         "success": True, "tracked_order": 2002},
        {"event": "TELEGRAM_DEAL_LIFECYCLE", "symbol": "EURUSD.ecn",
         "deal": 3001, "order": 9999, "entry": 1, "pips_result": -5.0, "net": -2.0},
        {"event": "TELEGRAM_DEAL_LIFECYCLE", "symbol": "EURUSD.ecn",
         "deal": 3001, "order": 9999, "entry": 1, "pips_result": -5.0, "net": -2.0},
    ]
    report = audit(events)
    assert report["signals"]["order_result_without_attempt"] == ["E:2:SELL"]
    assert report["integrity"]["duplicate_order_result_events"] == 1
    assert report["integrity"]["duplicate_lifecycle_deal_events"] == 1
    assert report["linkage"]["unmatched_lifecycle_orders"] == [9999]


def test_pending_order_placement_is_not_conflated_with_fill():
    events = [
        {"event": "CANDIDATE", "symbol": "XAUUSD.ecn", "signal_id": "X:3:SELL"},
        {"event": "ORDER_ATTEMPT", "symbol": "XAUUSD.ecn", "signal_id": "X:3:SELL"},
        {"event": "ORDER_RESULT", "symbol": "XAUUSD.ecn", "signal_id": "X:3:SELL",
         "success": True, "tracked_order": 3003, "tracked_deal": 0},
        {"event": "PENDING_ORDER_LIFECYCLE", "symbol": "XAUUSD.ecn",
         "order": 3003, "state": "PLACED"},
    ]
    report = audit(events)
    assert report["execution"]["accepted_order_placements"] == 1
    assert report["execution"]["immediate_deals_reported"] == 0
    assert report["execution"]["accepted_without_immediate_deal"] == 1
    assert report["pending_order_lifecycle"]["orders_observed"] == 1
    assert report["pending_order_lifecycle"]["states"]["PLACED"] == 1


def test_pending_order_terminal_states_are_auditable():
    events = [
        {"event": "ORDER_RESULT", "symbol": "BTCUSD.ecn", "signal_id": "B:4:BUY",
         "success": True, "tracked_order": 4004, "tracked_deal": 0},
        {"event": "PENDING_ORDER_LIFECYCLE", "symbol": "BTCUSD.ecn",
         "order": 4004, "state": "PLACED"},
        {"event": "PENDING_ORDER_LIFECYCLE", "symbol": "BTCUSD.ecn",
         "order": 4004, "state": "EXPIRED"},
        {"event": "PENDING_ORDER_LIFECYCLE", "symbol": "EURUSD.ecn",
         "order": 5005, "state": "CANCELED"},
    ]
    report = audit(events)
    assert report["pending_order_lifecycle"]["orders_observed"] == 2
    assert report["pending_order_lifecycle"]["states"]["PLACED"] == 1
    assert report["pending_order_lifecycle"]["states"]["EXPIRED"] == 1
    assert report["pending_order_lifecycle"]["states"]["CANCELED"] == 1
    assert report["pending_order_lifecycle"]["orders_with_terminal_cancel_or_expiry"] == 2
