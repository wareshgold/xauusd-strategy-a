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
    assert receipt["checks"]["manifest_stable_during_audit"] is True
    assert "manifest_sha256_match" not in receipt["checks"]
    assert receipt["dataset"]["tick_count"] == 3
    assert receipt["checks"]["adjacent_duplicate_timestamps"] == 1
    assert receipt["checks"]["duplicate_timestamp_groups"] == 1
    assert receipt["checks"]["duplicate_groups_with_different_bid_ask"] == 1
    assert receipt["checks"]["zero_last_rows"] == 3
    assert receipt["checks"]["zero_volume_rows"] == 3
    assert receipt["dataset"]["provenance_status"] == "UNANCHORED_OBSERVED_DIGEST"
    assert receipt["gate_a"] == "LIMITED_DEVELOPMENT_TOOLING_ONLY_APPROVED_PROVENANCE_UNANCHORED"
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

@pytest.mark.parametrize(
    "outside_timestamp",
    [
        "2026-08-20T23:59:59.999Z",
        "2026-09-19T00:00:00.000Z",
    ],
)
def test_observed_tick_outside_half_open_interval_is_rejected(tmp_path, outside_timestamp):
    from datetime import datetime

    dataset, manifest = make_inputs(tmp_path)
    with gzip.open(dataset, "rt", encoding="utf-8", newline="") as stream:
        import csv
        reader = csv.reader(stream)
        rows = list(reader)
    parsed = datetime.fromisoformat(outside_timestamp.replace("Z", "+00:00"))
    rows[1][0] = str(int(parsed.timestamp() * 1000))
    rows[1][1] = outside_timestamp
    with gzip.open(dataset, "wt", encoding="utf-8", newline="") as stream:
        import csv
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerows(rows)

    compressed = dataset.read_bytes()
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["artifact_sha256"] = hashlib.sha256(compressed).hexdigest()
    payload["artifact_size_bytes"] = len(compressed)
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(AuditError, match="declared-interval"):
        audit_dataset(dataset, manifest)



def rewrite_fixture(dataset: Path, manifest_path: Path, rows):
    import csv

    with gzip.open(dataset, "wt", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["time_msc", "time_utc", "bid", "ask", "last", "volume", "flags"])
        writer.writerows(rows)

    compressed = dataset.read_bytes()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["artifact_sha256"] = hashlib.sha256(compressed).hexdigest()
    payload["artifact_size_bytes"] = len(compressed)
    payload["tick_count"] = len(rows)
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")


def read_fixture_rows(dataset: Path):
    import csv

    with gzip.open(dataset, "rt", encoding="utf-8", newline="") as stream:
        return list(csv.reader(stream))[1:]


def test_timestamp_text_mismatch_is_rejected(tmp_path):
    dataset, manifest = make_inputs(tmp_path)
    rows = read_fixture_rows(dataset)
    rows[0][1] = "2026-08-21T01:00:05.865Z"
    rewrite_fixture(dataset, manifest, rows)

    with pytest.raises(AuditError, match="timestamp consistency"):
        audit_dataset(dataset, manifest)


def test_out_of_order_source_rows_are_rejected(tmp_path):
    dataset, manifest = make_inputs(tmp_path)
    rows = read_fixture_rows(dataset)
    rewrite_fixture(dataset, manifest, [rows[0], rows[2], rows[1]])

    with pytest.raises(AuditError, match="nondecreasing timestamp order"):
        audit_dataset(dataset, manifest)


def test_non_finite_numeric_values_are_rejected(tmp_path):
    dataset, manifest = make_inputs(tmp_path)
    rows = read_fixture_rows(dataset)
    rows[1][2] = "nan"
    rewrite_fixture(dataset, manifest, rows)

    with pytest.raises(AuditError, match="numeric, timestamp consistency"):
        audit_dataset(dataset, manifest)


def test_receipt_cannot_overwrite_dataset_input(tmp_path):
    dataset, manifest = make_inputs(tmp_path)
    original = dataset.read_bytes()

    with pytest.raises(AuditError, match="cannot overwrite either input"):
        write_receipt(dataset, manifest, dataset)

    assert dataset.read_bytes() == original


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("dataset_id", "unexpected-id", "dataset_id"),
        ("purpose", "LIVE_TRADING", "purpose"),
        ("trading_actions_taken", True, "trading actions"),
        ("artifact", "other.csv.gz", "artifact name"),
    ],
)
def test_manifest_identity_and_scope_mismatches_are_rejected(tmp_path, field, value, message):
    dataset, manifest = make_inputs(tmp_path)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload[field] = value
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(AuditError, match=message):
        audit_dataset(dataset, manifest)


@pytest.mark.parametrize(
    ("bid", "ask"),
    [
        ("0", "4519.20"),
        ("4519.00", "0"),
        ("-1", "4519.20"),
    ],
)
def test_nonpositive_bid_or_ask_is_rejected(tmp_path, bid, ask):
    dataset, manifest = make_inputs(tmp_path)
    rows = read_fixture_rows(dataset)
    rows[0][2] = bid
    rows[0][3] = ask
    rewrite_fixture(dataset, manifest, rows)

    with pytest.raises(AuditError, match="Bid/Ask"):
        audit_dataset(dataset, manifest)


def test_receipt_cannot_overwrite_manifest_input(tmp_path):
    dataset, manifest = make_inputs(tmp_path)
    original = manifest.read_bytes()

    with pytest.raises(AuditError, match="cannot overwrite either input"):
        write_receipt(dataset, manifest, manifest)

    assert manifest.read_bytes() == original


def test_duplicate_group_summary_distinguishes_quote_changes_and_same_quotes(tmp_path):
    dataset, manifest = make_inputs(tmp_path)
    rows = read_fixture_rows(dataset)
    rewrite_fixture(dataset, manifest, [rows[0], rows[1], rows[2], rows[2]])

    receipt = audit_dataset(dataset, manifest)
    checks = receipt["checks"]

    assert checks["duplicate_timestamp_groups"] == 2
    assert checks["duplicate_timestamp_groups_size_2"] == 2
    assert checks["duplicate_timestamp_groups_size_3_plus"] == 0
    assert checks["max_rows_in_timestamp_group"] == 2
    assert checks["duplicate_groups_with_different_bid_ask"] == 1
    assert checks["duplicate_groups_with_same_bid_ask"] == 1


def test_duplicate_group_summary_reports_three_or_more_rows(tmp_path):
    dataset, manifest = make_inputs(tmp_path)
    rows = read_fixture_rows(dataset)
    repeated_timestamp = rows[0][0]
    repeated_time_text = rows[0][1]
    rows[1][0] = repeated_timestamp
    rows[1][1] = repeated_time_text
    rows[2][0] = repeated_timestamp
    rows[2][1] = repeated_time_text
    rewrite_fixture(dataset, manifest, rows)

    receipt = audit_dataset(dataset, manifest)
    checks = receipt["checks"]

    assert checks["duplicate_timestamp_groups"] == 1
    assert checks["duplicate_timestamp_groups_size_2"] == 0
    assert checks["duplicate_timestamp_groups_size_3_plus"] == 1
    assert checks["max_rows_in_timestamp_group"] == 3
    assert checks["duplicate_groups_with_different_bid_ask"] == 1


@pytest.mark.parametrize(
    "malformed_row",
    [
        ["1787274005864", "2026-08-21T01:00:05.864Z", "4518.99", "4519.20", "0.0", "0.0"],
        ["1787274005864", "2026-08-21T01:00:05.864Z", "4518.99", "4519.20", "0.0", "0.0", "134", "EXTRA"],
    ],
)
def test_csv_rows_with_missing_or_extra_cells_are_rejected(tmp_path, malformed_row):
    dataset, manifest = make_inputs(tmp_path)
    rewrite_fixture(dataset, manifest, [malformed_row])

    with pytest.raises(AuditError, match="required column count"):
        audit_dataset(dataset, manifest)


def test_duplicate_groups_must_be_adjacent_in_source_order(tmp_path):
    dataset, manifest = make_inputs(tmp_path)
    rows = read_fixture_rows(dataset)
    # A timestamp repeated after a later timestamp is out of order; the audit
    # must reject rather than silently treating the repeated values as a group.
    rewrite_fixture(dataset, manifest, [rows[0], rows[2], rows[1]])

    with pytest.raises(AuditError, match="nondecreasing timestamp order"):
        audit_dataset(dataset, manifest)


def test_submillisecond_utc_timestamp_is_rejected(tmp_path):
    dataset, manifest = make_inputs(tmp_path)
    rows = read_fixture_rows(dataset)
    # time_msc is integer milliseconds; finer precision cannot be silently truncated.
    rows[0][1] = "2026-08-21T01:00:05.864001Z"
    rewrite_fixture(dataset, manifest, rows)

    with pytest.raises(AuditError, match="timestamp consistency"):
        audit_dataset(dataset, manifest)
