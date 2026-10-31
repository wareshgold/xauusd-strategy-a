from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from scripts.validate_mt5_research_manifest_v1 import evaluate_manifest


def fixture(tmp_path: Path, *, audit: str = "AUDITED_PASS"):
    raw = tmp_path / "raw.csv"
    second_timestamp = "2026-07-01T01:03:00Z" if audit == "AUDITED_UNCLASSIFIED_COVERAGE" else "2026-07-01T01:01:00Z"
    rows = [
        {"timestamp": "2026-07-01T01:00:00Z", "open": "1", "high": "2", "low": "0.5", "close": "1.5", "tick_volume": "10", "spread": "2", "real_volume": "0"},
        {"timestamp": second_timestamp, "open": "1.5", "high": "2", "low": "1", "close": "1.8", "tick_volume": "11", "spread": "2", "real_volume": "0"},
    ]
    with raw.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    digest = hashlib.sha256(raw.read_bytes()).hexdigest()
    discontinuities = []
    if audit == "AUDITED_UNCLASSIFIED_COVERAGE":
        discontinuities = [{
            "from": "2026-07-01T01:00:00Z",
            "to": "2026-07-01T01:03:00Z",
            "interval_minutes": 3.0,
            "kind": "unclassified_gap",
        }]
    manifest = {
        "schema": {"id": "sp2l.mt5-research-evidence", "version": "1.0.0"},
        "dataset_id": "fixture",
        "actual_bar_count": len(rows),
        "actual_first_utc": rows[0]["timestamp"],
        "actual_last_utc": rows[-1]["timestamp"],
        "invalid_row_count": 0,
        "invalid_rows": [],
        "timestamp_discontinuities": discontinuities,
        "discontinuity_count": len(discontinuities),
        "ordering_anomalies": [],
        "unclassified_gaps": discontinuities,
        "audit_status": audit,
        "raw": {"sha256": digest},
    }
    return manifest, raw


def test_contiguous_hash_verified_manifest_is_accepted(tmp_path):
    manifest, raw = fixture(tmp_path)
    result = evaluate_manifest(manifest, raw)
    assert result["status"] == "ACCEPTED"
    assert result["research_replay_eligible"] is True
    assert result["confirmatory_validation_eligible"] is False
    assert result["production_eligible"] is False


def test_unclassified_coverage_is_not_replay_eligible(tmp_path):
    manifest, raw = fixture(tmp_path, audit="AUDITED_UNCLASSIFIED_COVERAGE")
    result = evaluate_manifest(manifest, raw)
    assert result["status"] == "ACCEPTED_WITH_UNCLASSIFIED_COVERAGE"
    assert result["research_replay_eligible"] is False
    assert result["warnings"]


def test_hash_mismatch_is_rejected(tmp_path):
    manifest, raw = fixture(tmp_path)
    manifest["raw"]["sha256"] = "0" * 64
    result = evaluate_manifest(manifest, raw)
    assert result["status"] == "REJECTED"
    assert "RAW_SHA256_MISMATCH" in result["errors"]


def test_legacy_or_unknown_schema_is_rejected(tmp_path):
    manifest, raw = fixture(tmp_path)
    manifest["schema"] = {"id": "legacy", "version": "1"}
    result = evaluate_manifest(manifest, raw)
    assert result["status"] == "REJECTED"
    assert "UNSUPPORTED_OR_MISSING_SCHEMA" in result["errors"]


def test_manifest_count_mismatch_is_rejected(tmp_path):
    manifest, raw = fixture(tmp_path)
    manifest["actual_bar_count"] += 1
    result = evaluate_manifest(manifest, raw)
    assert result["status"] == "REJECTED"
    assert "RAW_ROW_COUNT_MISMATCH" in result["errors"]


def test_manifest_cannot_hide_gap_present_in_raw_csv(tmp_path):
    manifest, raw = fixture(tmp_path, audit="AUDITED_UNCLASSIFIED_COVERAGE")
    manifest["timestamp_discontinuities"] = []
    manifest["discontinuity_count"] = 0
    manifest["unclassified_gaps"] = []
    result = evaluate_manifest(manifest, raw)
    assert result["status"] == "REJECTED"
    assert "RAW_DISCONTINUITIES_DO_NOT_MATCH_MANIFEST" in result["errors"]


def test_invalid_ohlc_in_raw_csv_is_rejected(tmp_path):
    manifest, raw = fixture(tmp_path)
    text = raw.read_text(encoding="utf-8")
    raw.write_text(text.replace(",2,0.5,1.5,", ",0.5,0.5,1.5,", 1), encoding="utf-8")
    manifest["raw"]["sha256"] = hashlib.sha256(raw.read_bytes()).hexdigest()
    result = evaluate_manifest(manifest, raw)
    assert result["status"] == "REJECTED"
    assert "RAW_OHLC_INVALID" in result["errors"]


def _run_cli_fixture(tmp_path: Path, *, audit: str):
    import json
    import subprocess
    import sys

    manifest, raw = fixture(tmp_path, audit=audit)
    manifest_path = tmp_path / "manifest.json"
    report_path = tmp_path / "report.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/validate_mt5_research_manifest_v1.py",
            "--manifest", str(manifest_path),
            "--raw-csv", str(raw),
            "--output", str(report_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert report_path.is_file()
    return completed, json.loads(report_path.read_text(encoding="utf-8"))


def test_cli_report_only_accepts_contiguous_fixture_without_authorizing_confirmatory_use(tmp_path):
    completed, report = _run_cli_fixture(tmp_path, audit="AUDITED_PASS")
    assert completed.returncode == 0
    assert report["status"] == "ACCEPTED"
    assert report["research_replay_eligible"] is True
    assert report["confirmatory_validation_eligible"] is False
    assert report["production_eligible"] is False


def test_cli_report_only_preserves_unclassified_fixture_as_ineligible(tmp_path):
    completed, report = _run_cli_fixture(
        tmp_path, audit="AUDITED_UNCLASSIFIED_COVERAGE"
    )
    assert completed.returncode == 0
    assert report["status"] == "ACCEPTED_WITH_UNCLASSIFIED_COVERAGE"
    assert report["research_replay_eligible"] is False
    assert report["confirmatory_validation_eligible"] is False
    assert report["production_eligible"] is False


def test_cli_report_only_writes_rejected_fixture_and_returns_rejection_code(tmp_path):
    import json

    manifest, raw = fixture(tmp_path)
    manifest["raw"]["sha256"] = "0" * 64
    manifest_path = tmp_path / "manifest.json"
    report_path = tmp_path / "report.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    import subprocess
    import sys

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/validate_mt5_research_manifest_v1.py",
            "--manifest", str(manifest_path),
            "--raw-csv", str(raw),
            "--output", str(report_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 2
    assert report_path.is_file()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["status"] == "REJECTED"
    assert "RAW_SHA256_MISMATCH" in report["errors"]
    assert report["research_replay_eligible"] is False
    assert report["confirmatory_validation_eligible"] is False
    assert report["production_eligible"] is False
