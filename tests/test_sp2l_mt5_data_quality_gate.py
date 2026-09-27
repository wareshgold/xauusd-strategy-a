from sp2l_mt5_data_quality_gate import classify_gap, classify_row


def test_weekend_only_gap_passes():
    row = {
        "case_id": "x", "requested_symbol": "EURUSD", "broker_symbol": "EURUSD.ecn",
        "week_start_utc": "2026-01-05", "week_end_utc": "2026-01-12",
        "gap_intervals": [{"missing_minutes": 2880, "calendar_weekend_minutes": 2880, "non_weekend_minutes": 0}],
    }
    assert classify_row(row)["status"] == "PASS"


def test_non_weekend_gap_is_unresolved():
    row = {
        "case_id": "x", "requested_symbol": "XAUUSD", "broker_symbol": "XAUUSD.ecn",
        "week_start_utc": "2026-01-05", "week_end_utc": "2026-01-12",
        "gap_intervals": [{"missing_minutes": 60, "calendar_weekend_minutes": 0, "non_weekend_minutes": 60}],
    }
    result = classify_row(row)
    assert result["status"] == "DATA_QUALITY_UNRESOLVED"
    assert result["unresolved_data_gap_minutes"] == 60


def test_zero_gap():
    result = classify_gap({"missing_minutes": 0, "calendar_weekend_minutes": 0, "non_weekend_minutes": 0})
    assert result.classification == "NO_GAP"
