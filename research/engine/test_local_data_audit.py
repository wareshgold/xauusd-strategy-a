import json

import pytest

from research.engine.local_data_audit import audit_file


def payload(rows):
    return {"meta": {"symbol": "XAU/USD", "interval": "1min"}, "values": rows}


def row(ts, o=100, h=101, l=99, c=100.5):
    return {"datetime": ts, "open": str(o), "high": str(h), "low": str(l), "close": str(c)}


def write(tmp_path, obj):
    p = tmp_path / "time_series.json"
    p.write_text(json.dumps(obj), encoding="utf-8")
    return p


def test_clean_newest_first_sample_passes(tmp_path):
    p = write(tmp_path, payload([row("2026-09-09 00:01:00"), row("2026-09-09 00:00:00")]))
    r = audit_file(p)
    assert r.status == "PASS"
    assert r.row_count == 2
    assert r.cadence_mode_seconds == 60
    assert r.missing_bar_count == 0


def test_gap_is_reported_without_fabrication(tmp_path):
    p = write(tmp_path, payload([row("2026-09-09 00:02:00"), row("2026-09-09 00:00:00")]))
    r = audit_file(p)
    assert r.status == "WARN"
    assert r.missing_bar_count == 1
    assert r.row_count == 2


def test_duplicate_blocks(tmp_path):
    p = write(tmp_path, payload([row("2026-09-09 00:00:00"), row("2026-09-09 00:00:00")]))
    r = audit_file(p)
    assert r.status == "BLOCKED"
    assert len(r.duplicate_timestamps) == 1


def test_invalid_ohlc_blocks(tmp_path):
    p = write(tmp_path, payload([row("2026-09-09 00:00:00", o=105, h=101, l=99, c=100)]))
    r = audit_file(p)
    assert r.status == "BLOCKED"
    assert r.invalid_ohlc_rows == [0]


def test_naive_timestamp_requires_timezone(tmp_path):
    p = write(tmp_path, payload([row("2026-09-09 00:00:00")]))
    with pytest.raises(ValueError, match="explicit source timezone"):
        audit_file(p)
