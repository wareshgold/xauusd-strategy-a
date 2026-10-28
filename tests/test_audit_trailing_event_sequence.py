import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_trailing_event_sequence.py"
spec = importlib.util.spec_from_file_location("trailing_event_sequence_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def fixture(**overrides):
    values = {
        "entry_time_utc": "2026-10-27T12:56:05.552Z",
        "decision_time_utc": "2026-10-27T12:57:00Z",
        "bar_start_utc": "2026-10-27T12:56:00Z",
        "bar_low_time_utc": "2026-10-27T12:56:00.083Z",
        "bar_low": "4005.44",
        "entry_price": "4006.11",
        "direction": "SELL",
        "activation_distance": "0.40",
        "current_sl": "4012.95",
        "trail_distance": "0.40",
        "current_bid": "4006.06",
        "current_ask": "4006.94",
        "min_broker_distance": "0",
    }
    values.update(overrides)
    return audit.audit_bar_event_order(**values)


def test_incident_order_marks_pre_entry_low_and_separates_activation_from_guard():
    result = fixture()
    assert result["research_only"] is True
    assert result["canonical"] is False
    assert result["bar_completed_at_decision"] is True
    assert result["low_observed_before_entry"] is True
    assert result["bar_relation"] == "ENTRY_BAR_LOW_PRE_ENTRY"
    assert result["sell_full_bar_favorable_move"] == "0.67"
    assert result["activation_pass_from_supplied_observation"] is True
    assert result["candidate_sl_from_supplied_low"] == "4005.84"
    assert result["candidate_improves_existing_sl"] is True
    assert result["sell_ask_distance_guard_pass"] is False


def test_low_after_entry_is_labelled_separately_from_pre_entry_contamination():
    result = fixture(bar_low_time_utc="2026-10-27T12:56:30Z", bar_low="4005.71")
    assert result["low_observed_before_entry"] is False
    assert result["bar_relation"] == "ENTRY_BAR_LOW_AT_OR_AFTER_ENTRY"
    assert result["sell_full_bar_favorable_move"] == "0.40"
    assert result["activation_pass_from_supplied_observation"] is True


def test_entire_completed_bar_before_position_entry_is_not_mislabelled_entry_bar():
    result = fixture(
        entry_time_utc="2026-10-27T12:57:05Z",
        decision_time_utc="2026-10-27T12:58:00Z",
        bar_start_utc="2026-10-27T12:56:00Z",
        bar_low_time_utc="2026-10-27T12:56:30Z",
    )
    assert result["bar_relation"] == "BAR_COMPLETED_BEFORE_ENTRY"
    assert result["low_observed_before_entry"] is True


def test_below_threshold_observation_does_not_pass_activation():
    result = fixture(bar_low="4005.90", bar_low_time_utc="2026-10-27T12:56:30Z")
    assert result["sell_full_bar_favorable_move"] == "0.21"
    assert result["activation_pass_from_supplied_observation"] is False


def test_sell_ask_guard_fails_at_exact_equality_boundary():
    result = fixture(
        bar_low="4005.71",
        bar_low_time_utc="2026-10-27T12:56:30Z",
        current_ask="4005.91",
        min_broker_distance="0.20",
    )
    assert result["candidate_sl_from_supplied_low"] == "4006.11"
    assert result["sell_ask_distance_guard_pass"] is False


def test_candidate_that_does_not_improve_existing_sell_sl_is_flagged():
    result = fixture(current_sl="4005.80", current_ask="4000.00")
    assert result["candidate_sl_from_supplied_low"] == "4005.84"
    assert result["candidate_improves_existing_sl"] is False


def test_rejects_decision_before_bar_completion():
    import pytest
    with pytest.raises(ValueError, match="precedes completion"):
        fixture(decision_time_utc="2026-10-27T12:56:59.999Z")


def test_rejects_low_timestamp_outside_bar():
    import pytest
    with pytest.raises(ValueError, match="outside the M1 bar"):
        fixture(bar_low_time_utc="2026-10-27T12:57:00Z")


def test_rejects_buy_until_buy_geometry_is_source_resolved():
    import pytest
    with pytest.raises(ValueError, match="supports SELL only"):
        fixture(direction="BUY")
