from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
from scripts.audit_legacy_mt5_manifest_inventory import audit_pair


def make_pair(tmp_path: Path, audit_status="AUDITED_UNCLASSIFIED_COVERAGE"):
    raw = tmp_path / "month.csv"
    rows = [
        {"timestamp": "2026-07-01T01:00:00Z", "open": "1", "high": "2", "low": "0.5", "close": "1.5"},
        {"timestamp": "2026-07-01T01:03:00Z", "open": "1.5", "high": "2", "low": "1", "close": "1.8"},
    ]
    with raw.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "dataset_id": "fixture-month", "provider": "MetaTrader5 terminal API",
        "terminal": "Otet Group MT5 Terminal", "server": "OtetGroup-MT5",
        "symbol": "XAUUSD.ecn", "timeframe": "M1",
        "requested_interval_utc": {"start": rows[0]["timestamp"], "end": rows[-1]["timestamp"]},
        "session_calendar_id": "observation-only",
        "session_calendar_historical_applicability": "UNVERIFIED",
        "expected_active_bar_count": 10, "returned_bar_count": 2,
        "missing_expected_timestamps": ["2026-07-01T01:01:00Z"],
        "artifact": raw.name, "artifact_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
        "retrieval_timestamp_utc": "2026-07-02T00:00:00Z", "audit_status": audit_status,
    }
    manifest_path = tmp_path / "month.manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path, raw


def test_legacy_audit_fail_is_preserved_and_blocks_inventory(tmp_path):
    manifest, raw = make_pair(tmp_path, "AUDITED_FAIL")
    result = audit_pair(manifest, raw)
    assert result["status"] == "BLOCKED"
    assert "LEGACY_AUDIT_STATUS_ALREADY_FAIL" in result["errors"]
    assert result["raw"]["sha256_matches_legacy"] is True
    assert result["raw"]["row_count"] == 2


def test_hash_mismatch_blocks_inventory(tmp_path):
    manifest, raw = make_pair(tmp_path)
    raw.write_bytes(raw.read_bytes() + b"\n")
    result = audit_pair(manifest, raw)
    assert result["status"] == "BLOCKED"
    assert "RAW_SHA256_MISMATCH_OR_MISSING" in result["errors"]


def test_positive_gap_is_reported_not_interpreted_as_missing_market_bar(tmp_path):
    manifest, raw = make_pair(tmp_path)
    result = audit_pair(manifest, raw)
    assert result["raw"]["positive_interval_over_60_seconds_count"] == 1
    assert "POSITIVE_TIMESTAMP_GAPS_REQUIRE_SOURCE_AND_SESSION_REVIEW" in result["warnings"]
    assert result["status"] == "REVIEW_REQUIRED"
    assert result["legacy"]["session_calendar_historical_applicability"] == "UNVERIFIED"
