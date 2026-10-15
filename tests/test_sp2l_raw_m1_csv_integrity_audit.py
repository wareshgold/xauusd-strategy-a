import csv
import hashlib
import json
from pathlib import Path

from sp2l_raw_m1_csv_integrity_audit import audit_raw_m1_csv


FIELDS = ["timestamp", "open", "high", "low", "close", "tick_volume", "spread", "real_volume"]


def _write_fixture(tmp_path: Path, rows=None):
    csv_path = tmp_path / "sample.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows if rows is not None else [
            {"timestamp": "2026-09-16T22:00:00Z", "open": "10", "high": "12", "low": "9", "close": "11", "tick_volume": "4", "spread": "2", "real_volume": "0"},
            {"timestamp": "2026-09-16T22:01:00Z", "open": "11", "high": "13", "low": "10", "close": "12", "tick_volume": "5", "spread": "2", "real_volume": "0"},
        ])
    manifest = tmp_path / "sample.manifest.json"
    manifest.write_text(json.dumps({
        "artifact": csv_path.name,
        "artifact_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        "returned_bar_count": sum(1 for _ in csv.DictReader(csv_path.open(encoding="utf-8"))),
        "requested_interval_utc": {"start": "2026-09-16T22:00:00Z", "end": "2026-09-16T22:05:00Z"},
        "expected_active_bar_count": 6,
        "session_calendar_historical_applicability": "UNVERIFIED",
    }, indent=2) + "\n", encoding="utf-8")
    return csv_path, manifest


def test_valid_csv_passes_structure_only_and_reports_gap_unclassified(tmp_path):
    csv_path, manifest = _write_fixture(tmp_path, [
        {"timestamp": "2026-09-16T22:00:00Z", "open": "10", "high": "12", "low": "9", "close": "11", "tick_volume": "4", "spread": "2", "real_volume": "0"},
        {"timestamp": "2026-09-16T22:02:00Z", "open": "11", "high": "13", "low": "10", "close": "12", "tick_volume": "5", "spread": "2", "real_volume": "0"},
    ])
    result = audit_raw_m1_csv(csv_path, manifest)
    assert result["status"] == "STRUCTURAL_INTEGRITY_PASS"
    assert result["timestamp_gap_count"] == 1
    assert result["timestamp_gaps"][0]["interpretation"] == "UNCLASSIFIED_TIMESTAMP_GAP"
    assert result["canonical"] is False
    assert result["source_artifacts_modified"] is False
    assert result["warnings"]


def test_crlf_checkout_matches_lf_manifest_without_modifying_source(tmp_path):
    csv_path, manifest = _write_fixture(tmp_path)
    original_lf = csv_path.read_bytes()
    csv_path.write_bytes(original_lf.replace(b"\\n", b"\\r\\n"))

    result = audit_raw_m1_csv(csv_path, manifest)

    assert result["status"] == "STRUCTURAL_INTEGRITY_PASS"
    assert result["csv_sha256"] != result["csv_sha256_lf_normalized"]
    assert result["csv_sha256_lf_normalized"] == json.loads(manifest.read_text(encoding="utf-8"))["artifact_sha256"]
    assert result["line_ending_normalization"] == "CRLF_TO_LF_FOR_MANIFEST_COMPARISON_ONLY"
    assert any("uses CRLF line endings" in warning for warning in result["warnings"])
    assert csv_path.read_bytes() == original_lf.replace(b"\\n", b"\\r\\n")


def test_hash_mismatch_fails_closed(tmp_path):
    csv_path, manifest = _write_fixture(tmp_path)
    csv_path.write_text(csv_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    result = audit_raw_m1_csv(csv_path, manifest)
    assert result["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert any("does not match CSV bytes" in error for error in result["errors"])


def test_duplicate_and_out_of_order_timestamps_fail(tmp_path):
    csv_path, manifest = _write_fixture(tmp_path, [
        {"timestamp": "2026-09-16T22:01:00Z", "open": "10", "high": "12", "low": "9", "close": "11", "tick_volume": "4", "spread": "2", "real_volume": "0"},
        {"timestamp": "2026-09-16T22:01:00Z", "open": "11", "high": "13", "low": "10", "close": "12", "tick_volume": "5", "spread": "2", "real_volume": "0"},
        {"timestamp": "2026-09-16T22:00:00Z", "open": "11", "high": "13", "low": "10", "close": "12", "tick_volume": "5", "spread": "2", "real_volume": "0"},
    ])
    result = audit_raw_m1_csv(csv_path, manifest)
    assert result["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert result["duplicate_timestamp_count"] == 1
    # The equal adjacent pair is counted as a duplicate, not as out-of-order.
    assert result["out_of_order_pair_count"] == 1


def test_invalid_ohlc_fails(tmp_path):
    csv_path, manifest = _write_fixture(tmp_path, [
        {"timestamp": "2026-09-16T22:00:00Z", "open": "10", "high": "8", "low": "9", "close": "11", "tick_volume": "4", "spread": "2", "real_volume": "0"},
    ])
    result = audit_raw_m1_csv(csv_path, manifest)
    assert result["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert any("high is below" in error for error in result["errors"])


def test_empty_csv_fails_closed(tmp_path):
    csv_path, manifest = _write_fixture(tmp_path, [])
    result = audit_raw_m1_csv(csv_path, manifest)
    assert result["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert any("no data rows" in error for error in result["errors"])


def test_non_utc_and_subminute_timestamps_fail(tmp_path):
    csv_path, manifest = _write_fixture(tmp_path, [
        {"timestamp": "2026-09-16T22:00:30Z", "open": "10", "high": "12", "low": "9", "close": "11", "tick_volume": "4", "spread": "2", "real_volume": "0"},
    ])
    result = audit_raw_m1_csv(csv_path, manifest)
    assert result["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert any("minute boundary" in error for error in result["errors"])
