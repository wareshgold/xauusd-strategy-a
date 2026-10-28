import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_trailing_entry_bar_contamination.py"
spec = importlib.util.spec_from_file_location("trailing_entry_bar_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_incident_fixture_exposes_pre_entry_low_contamination_without_live_actions():
    result = audit.incident_fixture()

    assert result["status"] == "COMPLETE"
    assert result["research_only"] is True
    assert result["canonical"] is False
    assert result["entry_bar"]["low_occurred_before_entry"] is True
    assert result["full_bar_favorable_move"] == "0.67"
    assert result["full_bar_passes_activation_threshold"] is True
    assert result["post_entry_favorable_move"] == "0.05"
    assert result["post_entry_ticks_pass_activation_threshold"] is False
    assert result["entry_bar_contamination_demonstrated"] is True
    assert result["candidate_sl_from_full_bar_low"] == "4005.84"
    assert result["candidate_rejected_by_ask_guard_throughout_following_minute"] is True


def test_audit_rejects_bar_that_does_not_contain_entry_time():
    import pytest

    with pytest.raises(ValueError, match="does not contain the entry timestamp"):
        audit.audit_entry_bar(
            entry_time_utc="2026-10-27T12:56:05.552Z",
            entry_price="4006.11",
            bar_start_utc="2026-10-27T12:55:00Z",
            bar_low="4005.44",
            bar_low_time_utc="2026-10-27T12:55:30Z",
            activation_distance="0.40",
            post_entry_min_bid="4006.06",
            post_entry_min_bid_time_utc="2026-10-27T12:56:06.140Z",
            following_minute_min_ask="4006.94",
        )


def test_audit_rejects_a_claimed_post_entry_minimum_before_entry():
    import pytest

    with pytest.raises(ValueError, match="post-entry minimum is before entry"):
        audit.audit_entry_bar(
            entry_time_utc="2026-10-27T12:56:05.552Z",
            entry_price="4006.11",
            bar_start_utc="2026-10-27T12:56:00Z",
            bar_low="4005.44",
            bar_low_time_utc="2026-10-27T12:56:00.083Z",
            activation_distance="0.40",
            post_entry_min_bid="4006.06",
            post_entry_min_bid_time_utc="2026-10-27T12:56:05.000Z",
            following_minute_min_ask="4006.94",
        )
