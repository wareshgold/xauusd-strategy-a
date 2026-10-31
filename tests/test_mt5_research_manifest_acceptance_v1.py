from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from scripts.validate_mt5_research_manifest_v1 import evaluate_manifest


def fixture(tmp_path: Path, *, audit: str = "AUDITED_PASS"):
    raw = tmp_path / "raw.csv"
    rows = [
        {"timestamp": "2026-07-01T01:00:00Z", "open": "1", "high": "2", "low": "0.5", "close": "1.5", "tick_volume": "10", "spread": "2", "real_volume": "0"},
        {"timestamp": "2026-07-01T01:01:00Z", "open": "1.5", "high": "2", "low": "1", "close": "1.8", "tick_volume": "11", "spread": "2", "real_volume": "0"},
    ]
    with raw.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\\n")
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
