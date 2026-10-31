"""Additional deterministic synthetic fixtures for the raw MT5 M1 integrity gate.

These fixtures exercise structural/data-manifest contracts only. They do not
infer session calendars, missing bars, trading geometry, or execution semantics.
"""
import csv
import hashlib
import json
from pathlib import Path

from sp2l_raw_m1_csv_integrity_audit import audit_raw_m1_csv


FIELDS = ["timestamp", "open", "high", "low", "close", "tick_volume", "spread", "real_volume"]


def _fixture(tmp_path: Path, rows):
    csv_path = tmp_path / "synthetic.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    manifest_path = tmp_path / "synthetic.manifest.json"
    manifest_path.write_text(json.dumps({
        "artifact": csv_path.name,
        "artifact_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        "returned_bar_count": len(rows),
        "requested_interval_utc": {
            "start": "2026-09-16T22:00:00Z",
            "end": "2026-09-16T22:10:00Z",
        },
        "expected_active_bar_count": 11,
        "session_calendar_historical_applicability": "UNVERIFIED",
    }, indent=2) + "\n", encoding="utf-8")
    return csv_path, manifest_path


def _row(timestamp="2026-09-16T22:00:00Z", **overrides):
    row = {
        "timestamp": timestamp,
        "open": "10",
        "high": "12",
        "low": "9",
        "close": "11",
        "tick_volume": "4",
        "spread": "2",
        "real_volume": "0",
    }
    row.update(overrides)
    return row


def test_negative_volume_fails_closed(tmp_path):
    csv_path, manifest = _fixture(tmp_path, [_row(tick_volume="-1")])
    result = audit_raw_m1_csv(csv_path, manifest)
    assert result["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert result["invalid_row_count"] == 1
    assert any("tick_volume must be non-negative" in error for error in result["errors"])


def test_non_finite_ohlc_fails_closed(tmp_path):
    csv_path, manifest = _fixture(tmp_path, [_row(close="NaN")])
    result = audit_raw_m1_csv(csv_path, manifest)
    assert result["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert result["invalid_row_count"] == 1
    assert any("close must be finite and positive" in error for error in result["errors"])


def test_manifest_row_count_mismatch_fails_closed(tmp_path):
    csv_path, manifest = _fixture(tmp_path, [_row()])
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["returned_bar_count"] = 2
    manifest.write_text(json.dumps(data), encoding="utf-8")
    result = audit_raw_m1_csv(csv_path, manifest)
    assert result["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert any("returned_bar_count=2 disagrees with CSV row_count=1" in error for error in result["errors"])


def test_manifest_interval_exclusion_fails_closed(tmp_path):
    csv_path, manifest = _fixture(tmp_path, [_row("2026-09-16T22:11:00Z")])
    result = audit_raw_m1_csv(csv_path, manifest)
    assert result["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert any("falls outside manifest requested interval" in error for error in result["errors"])


def test_same_fixture_audit_is_deterministic(tmp_path):
    csv_path, manifest = _fixture(tmp_path, [
        _row("2026-09-16T22:00:00Z"),
        _row("2026-09-16T22:02:00Z", open="11", high="13", low="10", close="12"),
    ])
    first = audit_raw_m1_csv(csv_path, manifest)
    second = audit_raw_m1_csv(csv_path, manifest)
    assert first == second
    assert first["status"] == "STRUCTURAL_INTEGRITY_PASS"
    assert first["timestamp_gap_count"] == 1
    assert first["timestamp_gaps"][0]["interpretation"] == "UNCLASSIFIED_TIMESTAMP_GAP"
    assert first["canonical"] is False
    assert first["source_artifacts_modified"] is False
