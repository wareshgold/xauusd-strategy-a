from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

from scripts.migrate_legacy_mt5_manifest_to_v1 import migrate_legacy_manifest


def make_pair(tmp_path: Path):
    raw = tmp_path / "legacy.csv"
    rows = [
        {"timestamp": "2026-08-21T01:00:00Z", "open": "1", "high": "2", "low": "0.5", "close": "1.5", "tick_volume": "10", "spread": "2", "real_volume": "0"},
        {"timestamp": "2026-08-21T01:03:00Z", "open": "1.5", "high": "2", "low": "1", "close": "1.8", "tick_volume": "11", "spread": "2", "real_volume": "0"},
    ]
    with raw.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator=chr(10))
        writer.writeheader()
        writer.writerows(rows)
    legacy = {
        "dataset_id": "legacy-fixture",
        "provider": "MetaTrader5 terminal API",
        "terminal": "Otet Group MT5 Terminal",
        "server": "OtetGroup-MT5",
        "symbol": "XAUUSD.ecn",
        "timeframe": "M1",
        "requested_interval_utc": {"start": "2026-08-21T00:00:00Z", "end": "2026-08-21T01:05:00Z"},
        "actual_first_utc": rows[0]["timestamp"],
        "actual_last_utc": rows[-1]["timestamp"],
        "requested_bar_count": 66,
        "actual_bar_count": 2,
        "retrieval_timestamp_utc": "2026-08-22T00:00:00Z",
        "artifact": raw.name,
        "artifact_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
        "invalid_row_count": 0,
        "invalid_rows": [],
        # Deliberately misleading legacy counters are not imported into v1.
        "gap_count": 0,
        "gap_ranges": [],
    }
    return legacy, raw


def test_migration_recomputes_gap_from_raw_and_does_not_copy_legacy_gap_fields(tmp_path):
    legacy, raw = make_pair(tmp_path)
    migrated = migrate_legacy_manifest(legacy, raw)
    assert migrated["schema"] == {"id": "sp2l.mt5-research-evidence", "version": "1.0.0"}
    assert migrated["audit_status"] == "AUDITED_UNCLASSIFIED_COVERAGE"
    assert migrated["discontinuity_count"] == 1
    assert migrated["unclassified_gaps"][0]["interval_minutes"] == 3.0
    assert migrated["unclassified_gaps"][0]["kind"] == "unclassified_gap"
    assert "gap_ranges" not in migrated
    assert "missing_bars" not in migrated
    assert migrated["raw"]["sha256"] == legacy["artifact_sha256"]


def test_migration_fails_closed_on_raw_hash_mismatch(tmp_path):
    legacy, raw = make_pair(tmp_path)
    raw.write_text(raw.read_text(encoding="utf-8") + chr(10), encoding="utf-8")
    with pytest.raises(ValueError, match="LEGACY_RAW_SHA256_MISMATCH"):
        migrate_legacy_manifest(legacy, raw)


def test_migration_fails_closed_on_missing_source_metadata(tmp_path):
    legacy, raw = make_pair(tmp_path)
    del legacy["retrieval_timestamp_utc"]
    with pytest.raises(ValueError, match="LEGACY_REQUIRED_FIELDS_MISSING"):
        migrate_legacy_manifest(legacy, raw)


def test_migration_marks_duplicate_timestamp_as_audit_failure(tmp_path):
    legacy, raw = make_pair(tmp_path)
    text = raw.read_text(encoding="utf-8")
    raw.write_text(text.replace("2026-08-21T01:03:00Z", "2026-08-21T01:00:00Z"), encoding="utf-8")
    legacy["artifact_sha256"] = hashlib.sha256(raw.read_bytes()).hexdigest()
    legacy["actual_last_utc"] = "2026-08-21T01:00:00Z"
    migrated = migrate_legacy_manifest(legacy, raw)
    assert migrated["audit_status"] == "AUDITED_FAIL"
    assert migrated["chronological"] is False
    assert migrated["ordering_anomalies"][0]["kind"] == "duplicate_timestamp"
