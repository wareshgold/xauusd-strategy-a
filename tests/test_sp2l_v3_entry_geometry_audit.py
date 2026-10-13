from scripts.sp2l_v3_entry_geometry_audit import audit_candidates, summarize_rows


def test_buy_and_sell_compare_current_extreme_with_previous_level():
    bars = [
        {"time": 10, "high": 103.0, "low": 100.0},
        {"time": 20, "high": 102.0, "low": 99.0},
        {"time": 30, "high": 201.0, "low": 198.0},
        {"time": 40, "high": 202.0, "low": 199.0},
    ]
    candidates = [
        ({"direction": "BUY", "trigger_time": 20, "theoretical_entry": 99.0}, 1),
        ({"direction": "SELL", "trigger_time": 40, "theoretical_entry": 202.0}, 3),
    ]

    rows = audit_candidates(bars, candidates)

    assert rows[0]["entry_equals_current_extreme"] is True
    assert rows[0]["previous_candle_level"] == 100.0
    assert rows[0]["entry_minus_previous_level"] == -1.0
    assert rows[0]["previous_level_inside_entry_bar_range"] is True
    assert rows[0]["bar_extends_beyond_previous_level"] is True

    assert rows[1]["entry_equals_current_extreme"] is True
    assert rows[1]["previous_candle_level"] == 201.0
    assert rows[1]["entry_minus_previous_level"] == 1.0
    assert rows[1]["previous_level_inside_entry_bar_range"] is True
    assert rows[1]["bar_extends_beyond_previous_level"] is True


def test_gap_past_previous_level_is_not_claimed_as_an_intrabar_fill():
    bars = [
        {"time": 10, "high": 101.0, "low": 100.0},
        {"time": 20, "high": 99.5, "low": 99.0},
    ]
    candidates = [
        ({"direction": "BUY", "trigger_time": 20, "theoretical_entry": 99.0}, 1),
    ]

    row = audit_candidates(bars, candidates)[0]

    assert row["previous_candle_level"] == 100.0
    assert row["previous_level_inside_entry_bar_range"] is False
    assert row["level_outside_entry_bar_range"] is True
    assert row["intrabar_order_resolved"] is False
    assert row["fill_semantics_resolved"] is False
    assert row["canonical_rule_selected"] is False


def test_summary_keeps_buy_and_sell_counts_separate_and_research_only():
    bars = [
        {"time": 10, "high": 103.0, "low": 100.0},
        {"time": 20, "high": 102.0, "low": 99.0},
        {"time": 30, "high": 201.0, "low": 198.0},
        {"time": 40, "high": 202.0, "low": 199.0},
    ]
    candidates = [
        ({"direction": "BUY", "trigger_time": 20, "theoretical_entry": 99.0}, 1),
        ({"direction": "SELL", "trigger_time": 40, "theoretical_entry": 202.0}, 3),
    ]
    summary = summarize_rows(audit_candidates(bars, candidates))

    assert summary["candidate_count"] == 2
    assert summary["by_direction"]["BUY"]["count"] == 1
    assert summary["by_direction"]["SELL"]["count"] == 1
    assert summary["intrabar_order_inferred"] is False
    assert summary["fills_simulated"] is False
    assert summary["canonical_rule_selected"] is False
