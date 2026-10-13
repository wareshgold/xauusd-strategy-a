from scripts.sp2l_v3_entry_geometry_audit import audit_candidates, summarize_rows


def test_buy_and_sell_compare_current_extreme_with_previous_level():
    bars = [
        {"time": 10, "open": 101.0, "high": 103.0, "low": 100.0, "close": 102.0},
        {"time": 70, "open": 101.0, "high": 102.0, "low": 99.0, "close": 100.0},
        {"time": 130, "open": 199.0, "high": 201.0, "low": 198.0, "close": 200.0},
        {"time": 190, "open": 200.0, "high": 202.0, "low": 199.0, "close": 201.0},
    ]
    candidates = [
        ({"direction": "BUY", "trigger_time": 70, "theoretical_entry": 99.0}, 1),
        ({"direction": "SELL", "trigger_time": 190, "theoretical_entry": 202.0}, 3),
    ]

    rows = audit_candidates(bars, candidates)

    assert rows[0]["entry_equals_current_extreme"] is True
    assert rows[0]["previous_candle_level"] == 100.0
    assert rows[0]["entry_minus_previous_level"] == -1.0
    assert rows[0]["previous_level_inside_entry_bar_range"] is True
    assert rows[0]["bar_extends_beyond_previous_level"] is True
    assert rows[0]["previous_bar_time"] == 10
    assert rows[0]["current_bar_time"] == 70
    assert rows[0]["previous_bar_open"] == 101.0
    assert rows[0]["previous_bar_close"] == 102.0
    assert rows[0]["current_bar_open"] == 101.0
    assert rows[0]["current_bar_close"] == 100.0
    assert rows[0]["previous_to_current_seconds"] == 60
    assert rows[0]["bars_are_consecutive_m1"] is True
    assert rows[0]["candidate_trigger_matches_current_bar"] is True

    assert rows[1]["entry_equals_current_extreme"] is True
    assert rows[1]["previous_candle_level"] == 201.0
    assert rows[1]["entry_minus_previous_level"] == 1.0
    assert rows[1]["previous_level_inside_entry_bar_range"] is True
    assert rows[1]["bar_extends_beyond_previous_level"] is True
    assert rows[1]["bars_are_consecutive_m1"] is True


def test_gap_past_previous_level_is_not_claimed_as_an_intrabar_fill():
    bars = [
        {"time": 10, "open": 100.5, "high": 101.0, "low": 100.0, "close": 100.5},
        {"time": 70, "open": 99.2, "high": 99.5, "low": 99.0, "close": 99.3},
    ]
    candidates = [
        ({"direction": "BUY", "trigger_time": 70, "theoretical_entry": 99.0}, 1),
    ]

    row = audit_candidates(bars, candidates)[0]

    assert row["previous_candle_level"] == 100.0
    assert row["previous_level_inside_entry_bar_range"] is False
    assert row["level_outside_entry_bar_range"] is True
    assert row["intrabar_order_resolved"] is False
    assert row["fill_semantics_resolved"] is False
    assert row["canonical_rule_selected"] is False
    assert row["bars_are_consecutive_m1"] is True
    assert row["candidate_trigger_matches_current_bar"] is True


def test_audit_flags_nonconsecutive_bars_and_trigger_timestamp_mismatch():
    bars = [
        {"time": 100, "open": 10.0, "high": 11.0, "low": 9.0, "close": 10.5},
        {"time": 220, "open": 8.5, "high": 9.0, "low": 8.0, "close": 8.5},
    ]
    candidates = [
        ({"direction": "BUY", "trigger_time": 221, "theoretical_entry": 8.0}, 1),
    ]

    row = audit_candidates(bars, candidates)[0]
    summary = summarize_rows([row])

    assert row["previous_to_current_seconds"] == 120
    assert row["bars_are_consecutive_m1"] is False
    assert row["candidate_trigger_matches_current_bar"] is False
    assert row["previous_bar_high"] == 11.0
    assert row["previous_bar_low"] == 9.0
    assert row["current_bar_high"] == 9.0
    assert row["current_bar_low"] == 8.0
    assert summary["overall"]["nonconsecutive_m1_bar_count"] == 1
    assert summary["overall"]["trigger_current_bar_mismatch_count"] == 1


def test_summary_keeps_buy_and_sell_counts_separate_and_research_only():
    bars = [
        {"time": 10, "high": 103.0, "low": 100.0},
        {"time": 70, "high": 102.0, "low": 99.0},
        {"time": 130, "high": 201.0, "low": 198.0},
        {"time": 190, "high": 202.0, "low": 199.0},
    ]
    candidates = [
        ({"direction": "BUY", "trigger_time": 70, "theoretical_entry": 99.0}, 1),
        ({"direction": "SELL", "trigger_time": 190, "theoretical_entry": 202.0}, 3),
    ]
    summary = summarize_rows(audit_candidates(bars, candidates))

    assert summary["candidate_count"] == 2
    assert summary["by_direction"]["BUY"]["count"] == 1
    assert summary["by_direction"]["SELL"]["count"] == 1
    assert summary["intrabar_order_inferred"] is False
    assert summary["fills_simulated"] is False
    assert summary["canonical_rule_selected"] is False
