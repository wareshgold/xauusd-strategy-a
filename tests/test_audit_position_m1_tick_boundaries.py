import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_position_m1_tick_boundaries.py"
spec = importlib.util.spec_from_file_location("boundary_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_position_audit_reports_post_entry_minimum_and_tick_coverage():
    ticks = [
        {"epoch": 1793105765.0, "time_utc": "2026-10-27T12:56:05.000Z", "bid": 4006.10, "ask": 4006.28, "line": 1},
        {"epoch": 1793105766.0, "time_utc": "2026-10-27T12:56:06.000Z", "bid": 4006.06, "ask": 4006.24, "line": 2},
        {"epoch": 1793105821.0, "time_utc": "2026-10-27T12:57:01.000Z", "bid": 4007.00, "ask": 4007.18, "line": 3},
    ]
    bars = [
        {"epoch": 1793105760, "time_utc": "2026-10-27T12:56:00Z", "open": 4006.20, "high": 4007.1, "low": 4005.9, "close": 4006.4, "source_row": 2},
        {"epoch": 1793105820, "time_utc": "2026-10-27T12:57:00Z", "open": 4006.4, "high": 4007.2, "low": 4006.0, "close": 4007.0, "source_row": 3},
    ]
    result = audit.audit(ticks, bars, "2026-10-27T12:56:05.552Z", "2026-10-27T13:01:49Z")
    assert result["minimum_post_entry_bid"]["bid"] == 4006.06
    assert result["minimum_post_entry_bid"]["favorable_move_price"] == 0.05
    assert result["m1_rows_near_position"] == 2
    assert result["m1_bars"][0]["tick_coverage"] == "PRESENT"
    assert result["m1_bars"][1]["tick_coverage"] == "PRESENT"


def test_csv_parsers_accept_mt5_epoch_columns_and_iso_tick_text(tmp_path):
    tick_file = tmp_path / "ticks.txt"
    tick_file.write_text("2026-10-27T12:56:06.140000+00:00 BID=4006.06 ASK=4006.24\n", encoding="utf-8")
    m1_file = tmp_path / "m1.csv"
    m1_file.write_text("time,open,high,low,close\n1793105760,4006.2,4007.1,4005.9,4006.4\n", encoding="utf-8")
    ticks = audit.parse_ticks(tick_file)
    bars = audit.parse_m1(m1_file)
    assert ticks[0]["bid"] == 4006.06
    assert bars[0]["epoch"] == 1793105760


def test_audit_fails_closed_when_m1_csv_does_not_cover_incident_window():
    ticks = [{"epoch": 1793105766.0, "time_utc": "2026-10-27T12:56:06.000Z", "bid": 4006.06, "ask": 4006.24, "line": 1}]
    import pytest
    with pytest.raises(ValueError, match="No M1 bars in the incident window"):
        audit.audit(ticks, [], "2026-10-27T12:56:05.552Z", "2026-10-27T13:01:49Z")
