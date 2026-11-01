import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from strategy_factory.m1_integrity import M1IntegrityError, validate_m1_artifact


START = "2026-10-05T00:00:00Z"
END = "2026-10-05T00:05:00Z"
T0 = int(datetime(2026, 10, 5, tzinfo=timezone.utc).timestamp())


def bar(timestamp, *, open_=4000.0, high=4001.0, low=3999.0, close=4000.5):
    return {
        "time": timestamp,
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "tick_volume": 10,
        "spread": 2,
        "real_volume": 0,
    }


def write_artifact(tmp_path: Path, bars, *, start=START, end=END, symbol="XAUUSD.ecn"):
    payload = {
        "schema_version": 1,
        "research_only": True,
        "symbol": symbol,
        "timeframe": "M1",
        "window_utc": {"start": start, "end": end},
        "bars": bars,
    }
    path = tmp_path / "m1.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def validate(path, *, start=START, end=END, symbol="XAUUSD.ecn"):
    return validate_m1_artifact(
        path,
        expected_symbol=symbol,
        expected_start=start,
        expected_end=end,
    )


def test_m1_integrity_reports_exact_hash_and_gaps_without_filling(tmp_path):
    path = write_artifact(tmp_path, [bar(T0), bar(T0 + 120), bar(T0 + 180)])
    report = validate(path)
    assert report.status == "PASS_WITH_GAPS"
    assert report.bars == 3
    assert report.gap_count == 1
    assert report.missing_minute_slots == 1
    assert report.largest_gap_minutes == 1
    assert report.content_sha256 == hashlib.sha256(path.read_bytes()).hexdigest()


def test_m1_integrity_rejects_duplicate_timestamps(tmp_path):
    path = write_artifact(tmp_path, [bar(T0), bar(T0)])
    with pytest.raises(M1IntegrityError, match="duplicate"):
        validate(path)


def test_m1_integrity_rejects_out_of_order_timestamps(tmp_path):
    path = write_artifact(tmp_path, [bar(T0 + 60), bar(T0)])
    with pytest.raises(M1IntegrityError, match="out-of-order"):
        validate(path)


def test_m1_integrity_rejects_window_mismatch(tmp_path):
    path = write_artifact(tmp_path, [bar(T0)], start="2026-10-04T00:00:00Z")
    with pytest.raises(M1IntegrityError, match="window does not match"):
        validate(path)


def test_m1_integrity_rejects_out_of_window_bar(tmp_path):
    path = write_artifact(tmp_path, [bar(T0 + 360)])
    with pytest.raises(M1IntegrityError, match="outside"):
        validate(path)


def test_m1_integrity_rejects_invalid_ohlc(tmp_path):
    path = write_artifact(tmp_path, [bar(T0, high=3998.0)])
    with pytest.raises(M1IntegrityError, match="high is inconsistent"):
        validate(path)


def test_m1_integrity_rejects_non_finite_price(tmp_path):
    path = write_artifact(tmp_path, [bar(T0, close=float("nan"))])
    with pytest.raises(M1IntegrityError, match="finite"):
        validate(path)


def test_m1_integrity_validates_original_mt5_csv_without_rewriting(tmp_path):
    from datetime import timedelta

    first = datetime(2026, 10, 5, tzinfo=timezone.utc)
    second = first + timedelta(minutes=2)
    rows = [
        "time_epoch_seconds,time_utc_iso,open,high,low,close,tick_volume,spread,real_volume",
        f"{int(first.timestamp())},{first.isoformat()},4000,4001,3999,4000.5,10,2,0",
        f"{int(second.timestamp())},{second.isoformat()},4000.5,4002,4000,4001.5,12,2,0",
    ]
    path = tmp_path / "m1.csv"
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    original = path.read_bytes()

    report = validate_m1_artifact(
        path,
        expected_symbol="XAUUSD.ecn",
        expected_start=first.isoformat(),
        expected_end=second.isoformat(),
    )
    assert report.status == "PASS_WITH_GAPS"
    assert report.bars == 2
    assert report.missing_minute_slots == 1
    assert report.content_sha256 == hashlib.sha256(original).hexdigest()
    assert path.read_bytes() == original


def test_m1_integrity_rejects_csv_epoch_iso_mismatch(tmp_path):
    path = tmp_path / "m1.csv"
    path.write_text(
        "time_epoch_seconds,time_utc_iso,open,high,low,close,tick_volume,spread,real_volume\n"
        "1791158400,2026-10-05T00:01:00+00:00,4000,4001,3999,4000.5,10,2,0\n",
        encoding="utf-8",
    )
    with pytest.raises(M1IntegrityError, match="epoch and ISO timestamps disagree"):
        validate_m1_artifact(
            path,
            expected_symbol="XAUUSD.ecn",
            expected_start="2026-10-05T00:00:00Z",
            expected_end="2026-10-05T00:01:00Z",
        )
