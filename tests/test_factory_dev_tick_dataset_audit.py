import gzip
import hashlib
import json
from pathlib import Path

import pytest

from scripts.audit_factory_dev_tick_dataset import (
    EXPECTED_ARTIFACT,
    EXPECTED_DATASET_ID,
    EXPECTED_END,
    EXPECTED_MANIFEST,
    EXPECTED_START,
    AuditError,
    audit_dataset,
    write_receipt,
)


def make_inputs(tmp_path: Path):
    dataset = tmp_path / EXPECTED_ARTIFACT
    manifest_path = tmp_path / EXPECTED_MANIFEST
    rows = [
        ["1787274005864", "2026-08-21T01:00:05.864Z", "4518.99", "4519.20", "0.0", "0.0", "134"],
        ["1787274005864", "2026-08-21T01:00:05.864Z", "4519.00", "4519.21", "0.0", "0.0", "134"],
        ["1787274006864", "2026-08-21T01:00:06.864Z", "4519.01", "4519.22", "0.0", "0.0", "134"],
    ]
    with gzip.open(dataset, "wt", encoding="utf-8", newline="") as stream:
        import csv
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["time_msc", "time_utc", "bid", "ask", "last", "volume", "flags"])
        writer.writerows(rows)

    compressed = dataset.read_bytes()
    manifest = {
        "artifact": EXPECTED_ARTIFACT,
        "artifact_sha256": hashlib.sha256(compressed).hexdigest(),
        "artifact_size_bytes": len(compressed),
        "dataset_id": EXPECTED_DATASET_ID,
        "interval_utc": {
            "start_inclusive": EXPECTED_START,
            "end_exclusive": EXPECTED_END,
        },
        "purpose": "RESEARCH_ONLY_OFFLINE_STRATEGY_COMPARISON",
        "symbol": "XAUUSD.ecn",
        "tick_count": len(rows),
        "trading_actions_taken": False,
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return dataset, manifest_path


def test_audit_is_read_only_and_records_duplicate_quote_changes(tmp_path):
    dataset, manifest = make_inputs(tmp_path)
    dataset_before = dataset.read_bytes()
    manifest_before = manifest.read_bytes()

    receipt = audit_dataset(dataset, manifest)

    assert receipt["audit_status"] == "INTEGRITY_AND_BASIC_QUOTE_CHECKS_PASS"
    assert receipt["dataset"]["tick_count"] == 3
    assert receipt["checks"]["adjacent_duplicate_timestamps"] == 1
    assert receipt["checks"]["duplicate_timestamp_groups"] == 1
    assert receipt["checks"]["duplicate_groups_with_different_bid_ask"] == 1
    assert receipt["checks"]["zero_last_rows"] == 3
    assert receipt["checks"]["zero_volume_rows"] == 3
    assert receipt["gate_b"] == "BLOCKED_SOURCE_GEOMETRY_UNRESOLVED"
    assert dataset.read_bytes() == dataset_before
    assert manifest.read_bytes() == manifest_before


def test_receipt_creation_is_deterministic_and_refuses_overwrite(tmp_path):
    dataset, manifest = make_inputs(tmp_path)
    output = tmp_path / "receipt.json"

    first = write_receipt(dataset, manifest, output)
    saved = output.read_bytes()

    assert json.loads(saved)["dataset"]["artifact_sha256"] == first["dataset"]["artifact_sha256"]
    with pytest.raises(AuditError, match="refusing to overwrite"):
        write_receipt(dataset, manifest, output)
    assert output.read_bytes() == saved


def test_wrong_artifact_name_is_rejected(tmp_path):
    dataset, manifest = make_inputs(tmp_path)
    renamed = tmp_path / "different.csv.gz"
    renamed.write_bytes(dataset.read_bytes())

    with pytest.raises(AuditError, match="fixed DEVELOPMENT"):
        audit_dataset(renamed, manifest)


def test_manifest_hash_mismatch_is_rejected(tmp_path):
    dataset, manifest = make_inputs(tmp_path)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["artifact_sha256"] = "0" * 64
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(AuditError, match="SHA-256"):
        audit_dataset(dataset, manifest)


def test_holdout_overlapping_interval_is_rejected(tmp_path):
    dataset, manifest = make_inputs(tmp_path)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["interval_utc"]["end_exclusive"] = "2026-09-20T00:00:00+00:00"
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(AuditError, match="interval"):
        audit_dataset(dataset, manifest)


def test_crossed_quote_is_rejected(tmp_path):
    dataset, manifest = make_inputs(tmp_path)
    with gzip.open(dataset, "wt", encoding="utf-8", newline="") as stream:
        import csv
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["time_msc", "time_utc", "bid", "ask", "last", "volume", "flags"])
        writer.writerow(["1787274005864", "2026-08-21T01:00:05.864Z", "4519.30", "4519.20", "0", "0", "134"])
    compressed = dataset.read_bytes()
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["artifact_sha256"] = hashlib.sha256(compressed).hexdigest()
    payload["artifact_size_bytes"] = len(compressed)
    payload["tick_count"] = 1
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(AuditError, match="Bid/Ask"):
        audit_dataset(dataset, manifest)
