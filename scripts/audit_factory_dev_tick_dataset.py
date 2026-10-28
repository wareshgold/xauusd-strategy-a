"""Read-only integrity/quote audit for the fixed SP2L DEVELOPMENT tick dataset.

This tool does not infer strategy rules, change raw inputs, or authorize backtests.
It writes a new JSON receipt only when the requested development artifact passes
its integrity and basic quote checks. Existing output paths are never overwritten.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
from typing import Any

EXPECTED_ARTIFACT = "xauusd-ecn-ticks-20260821_20260919.csv.gz"
EXPECTED_MANIFEST = "xauusd-ecn-ticks-20260821_20260919.manifest.json"
EXPECTED_DATASET_ID = "xauusd-ecn-tick-bidask-20260821-20260919"
EXPECTED_START = "2026-08-21T00:00:00+00:00"
EXPECTED_END = "2026-09-19T00:00:00+00:00"
EXPECTED_HEADER = ["time_msc", "time_utc", "bid", "ask", "last", "volume", "flags"]
HOLDOUT_START = "2026-09-19T00:00:00+00:00"


class AuditError(ValueError):
    """Raised when an input fails the fixed DEVELOPMENT audit contract."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_utc_ms(value: str) -> int:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    delta = parsed.astimezone(timezone.utc) - epoch
    total_microseconds = (
        (delta.days * 86_400 + delta.seconds) * 1_000_000 + delta.microseconds
    )
    if total_microseconds % 1_000:
        raise ValueError("timestamp must have millisecond precision")
    return total_microseconds // 1_000


def audit_dataset(dataset_path: Path, manifest_path: Path) -> dict[str, Any]:
    """Return deterministic audit evidence without modifying either input."""
    dataset_path = dataset_path.resolve()
    manifest_path = manifest_path.resolve()
    if dataset_path.name != EXPECTED_ARTIFACT:
        raise AuditError("only the fixed DEVELOPMENT dataset is eligible")
    if manifest_path.name != EXPECTED_MANIFEST:
        raise AuditError("unexpected manifest filename")
    if dataset_path == manifest_path:
        raise AuditError("dataset and manifest paths must differ")

    manifest_before = manifest_path.read_bytes()
    manifest = json.loads(manifest_before.decode("utf-8"))
    artifact_before = dataset_path.stat()
    actual_hash = sha256_file(dataset_path)
    manifest_after = manifest_path.read_bytes()
    artifact_after = dataset_path.stat()
    if manifest_before != manifest_after:
        raise AuditError("manifest changed during audit")
    if (artifact_before.st_size, artifact_before.st_mtime_ns) != (
        artifact_after.st_size, artifact_after.st_mtime_ns
    ):
        raise AuditError("dataset metadata changed during audit")

    if manifest.get("artifact") != EXPECTED_ARTIFACT:
        raise AuditError("manifest artifact name mismatch")
    if manifest.get("dataset_id") != EXPECTED_DATASET_ID:
        raise AuditError("manifest dataset_id mismatch")
    interval = manifest.get("interval_utc", {})
    if interval.get("start_inclusive") != EXPECTED_START or interval.get("end_exclusive") != EXPECTED_END:
        raise AuditError("manifest interval does not match fixed DEVELOPMENT interval")
    if interval.get("end_exclusive") > HOLDOUT_START:
        raise AuditError("development interval overlaps the Fresh Holdout boundary")
    if manifest.get("purpose") != "RESEARCH_ONLY_OFFLINE_STRATEGY_COMPARISON":
        raise AuditError("manifest purpose is not research-only")
    if manifest.get("trading_actions_taken") is not False:
        raise AuditError("manifest does not explicitly deny trading actions")

    byte_size = dataset_path.stat().st_size
    if byte_size != manifest.get("artifact_size_bytes"):
        raise AuditError("artifact size does not match manifest")
    if actual_hash != manifest.get("artifact_sha256"):
        raise AuditError("artifact SHA-256 does not match manifest")

    rows = 0
    duplicates = 0
    out_of_order = 0
    duplicate_groups = 0
    duplicate_quote_change_groups = 0
    duplicate_groups_size_2 = 0
    duplicate_groups_size_3_plus = 0
    max_timestamp_group_size = 0
    duplicate_groups_same_bid_ask = 0
    missing_bidask = 0
    nonpositive_bidask = 0
    crossed = 0
    invalid_numeric = 0
    timestamp_errors = 0
    timestamp_mismatches = 0
    out_of_interval_timestamps = 0
    expected_start_ms = _parse_utc_ms(EXPECTED_START)
    expected_end_ms = _parse_utc_ms(EXPECTED_END)
    gaps_over_60s = 0
    max_positive_gap_ms = 0
    zero_last = 0
    zero_volume = 0
    spread_min = math.inf
    spread_max = -math.inf
    spread_sum = 0.0
    spread_count = 0
    first_row = None
    last_row = None
    previous_ms = None
    group_ms = None
    group_size = 0
    group_quotes: set[tuple[float, float]] = set()

    def finish_group() -> None:
        nonlocal duplicate_groups, duplicate_quote_change_groups
        nonlocal duplicate_groups_size_2, duplicate_groups_size_3_plus
        nonlocal max_timestamp_group_size, duplicate_groups_same_bid_ask
        max_timestamp_group_size = max(max_timestamp_group_size, group_size)
        if group_size > 1:
            duplicate_groups += 1
            if group_size == 2:
                duplicate_groups_size_2 += 1
            else:
                duplicate_groups_size_3_plus += 1
            if len(group_quotes) > 1:
                duplicate_quote_change_groups += 1
            else:
                duplicate_groups_same_bid_ask += 1

    try:
        with gzip.open(dataset_path, "rt", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != EXPECTED_HEADER:
                raise AuditError("CSV header does not match the required schema")
            for line_number, row in enumerate(reader, start=2):
                rows += 1
                # DictReader stores surplus CSV cells under the None key and
                # missing cells as None values. Reject either shape explicitly
                # rather than silently auditing a partial/over-wide row.
                if None in row or any(row.get(field) is None for field in EXPECTED_HEADER):
                    raise AuditError(f"CSV row {line_number} does not match the required column count")
                try:
                    timestamp_ms = int(row["time_msc"])
                    bid = float(row["bid"])
                    ask = float(row["ask"])
                    last = float(row["last"])
                    volume = float(row["volume"])
                    int(row["flags"])
                    if not all(math.isfinite(x) for x in (bid, ask, last, volume)):
                        raise ValueError("non-finite numeric field")
                except (TypeError, ValueError):
                    invalid_numeric += 1
                    continue

                if timestamp_ms < expected_start_ms or timestamp_ms >= expected_end_ms:
                    out_of_interval_timestamps += 1

                try:
                    text_ms = _parse_utc_ms(row["time_utc"])
                except (TypeError, ValueError, OverflowError):
                    timestamp_errors += 1
                else:
                    if text_ms != timestamp_ms:
                        timestamp_mismatches += 1

                if first_row is None:
                    first_row = {"line": line_number, "time_msc": timestamp_ms, "time_utc": row["time_utc"]}
                last_row = {"line": line_number, "time_msc": timestamp_ms, "time_utc": row["time_utc"]}

                if previous_ms is not None:
                    delta = timestamp_ms - previous_ms
                    if delta == 0:
                        duplicates += 1
                    elif delta < 0:
                        out_of_order += 1
                    else:
                        max_positive_gap_ms = max(max_positive_gap_ms, delta)
                        if delta > 60_000:
                            gaps_over_60s += 1
                previous_ms = timestamp_ms

                if group_ms is None:
                    group_ms = timestamp_ms
                elif timestamp_ms != group_ms:
                    finish_group()
                    group_ms = timestamp_ms
                    group_size = 0
                    group_quotes = set()
                group_size += 1
                group_quotes.add((bid, ask))

                if bid <= 0 or ask <= 0:
                    nonpositive_bidask += 1
                if bid == 0 or ask == 0:
                    missing_bidask += 1
                if bid > ask:
                    crossed += 1
                if bid > 0 and ask > 0 and ask >= bid:
                    spread = ask - bid
                    spread_min = min(spread_min, spread)
                    spread_max = max(spread_max, spread)
                    spread_sum += spread
                    spread_count += 1
                if last == 0:
                    zero_last += 1
                if volume == 0:
                    zero_volume += 1
            finish_group()
    except (OSError, EOFError, csv.Error) as exc:
        raise AuditError(f"GZIP/CSV read failed: {type(exc).__name__}: {exc}") from exc

    if rows == 0:
        raise AuditError("dataset contains no tick rows")
    if rows != manifest.get("tick_count"):
        raise AuditError("row count does not match manifest")
    if invalid_numeric or timestamp_errors or timestamp_mismatches or out_of_interval_timestamps:
        raise AuditError("numeric, timestamp consistency, or declared-interval checks failed")
    if missing_bidask or nonpositive_bidask or crossed:
        raise AuditError("basic Bid/Ask quality checks failed")
    if out_of_order:
        raise AuditError("source rows are not in nondecreasing timestamp order")

    return {
        "schema_version": 1,
        "audit_kind": "FIXED_DEVELOPMENT_TICK_BIDASK_INTEGRITY",
        "audit_status": "INTEGRITY_AND_BASIC_QUOTE_CHECKS_PASS",
        "dataset": {
            "dataset_id": EXPECTED_DATASET_ID,
            "role": "DEVELOPMENT",
            "symbol": manifest.get("symbol"),
            "interval_utc": interval,
            "artifact": dataset_path.name,
            "manifest": manifest_path.name,
            "provenance_status": "UNANCHORED_OBSERVED_DIGEST",
            "artifact_size_bytes": byte_size,
            "artifact_sha256": actual_hash,
            "manifest_sha256": hashlib.sha256(manifest_before).hexdigest(),
            "tick_count": rows,
            "first_observed_tick": first_row,
            "last_observed_tick": last_row,
        },
        "checks": {
            "manifest_size_match": True,
            "manifest_stable_during_audit": True,
            "manifest_row_count_match": True,
            "gzip_csv_read": True,
            "expected_header": True,
            "timestamp_parse_errors": timestamp_errors,
            "time_msc_time_utc_mismatches": timestamp_mismatches,
            "observed_timestamps_outside_declared_interval": out_of_interval_timestamps,
            "invalid_numeric_rows": invalid_numeric,
            "missing_bid_or_ask_rows": missing_bidask,
            "nonpositive_bid_or_ask_rows": nonpositive_bidask,
            "crossed_quotes": crossed,
            "adjacent_duplicate_timestamps": duplicates,
            "adjacent_out_of_order_timestamps": out_of_order,
            "duplicate_timestamp_groups": duplicate_groups,
            "duplicate_timestamp_groups_size_2": duplicate_groups_size_2,
            "duplicate_timestamp_groups_size_3_plus": duplicate_groups_size_3_plus,
            "max_rows_in_timestamp_group": max_timestamp_group_size,
            "duplicate_groups_with_different_bid_ask": duplicate_quote_change_groups,
            "duplicate_groups_with_same_bid_ask": duplicate_groups_same_bid_ask,
            "gaps_over_60_seconds": gaps_over_60s,
            "max_positive_adjacent_gap_ms": max_positive_gap_ms,
            "zero_last_rows": zero_last,
            "zero_volume_rows": zero_volume,
            "spread_min": spread_min if spread_count else None,
            "spread_mean": spread_sum / spread_count if spread_count else None,
            "spread_max": spread_max if spread_count else None,
        },
        "limitations": [
            "Observed gaps are recorded; their causes are not inferred.",
            "Duplicate-millisecond rows are preserved and are not deduplicated or sorted.",
            "Zero Last/Volume fields are not interpreted as trade prints or traded volume.",
            "No strategy geometry, fill semantics, performance edge, or production eligibility is established.",
            "Fresh Holdout is not read by this tool; its boundary is only enforced against the fixed development interval.",
            "Acquisition provenance remains UNANCHORED_OBSERVED_DIGEST; human approval permits limited DEVELOPMENT tooling only.",
        ],
        "gate_a": "LIMITED_DEVELOPMENT_TOOLING_ONLY_APPROVED_PROVENANCE_UNANCHORED",
        "gate_b": "BLOCKED_SOURCE_GEOMETRY_UNRESOLVED",
        "gate_c": "BLOCKED_ADAPTER_AND_EXECUTION_CONTRACT_REVIEW_REQUIRED",
        "gate_d": "BLOCKED",
    }


def write_receipt(dataset_path: Path, manifest_path: Path, output_path: Path) -> dict[str, Any]:
    output_path = output_path.resolve()
    dataset_resolved = dataset_path.resolve()
    manifest_resolved = manifest_path.resolve()
    if output_path in (dataset_resolved, manifest_resolved):
        raise AuditError("receipt output cannot overwrite either input")
    if output_path.exists():
        raise AuditError("receipt output already exists; refusing to overwrite")
    receipt = audit_dataset(dataset_path, manifest_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    # Exclusive creation prevents accidental replacement of an existing receipt.
    with output_path.open("xb") as stream:
        stream.write(encoded)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    receipt = write_receipt(args.dataset, args.manifest, args.output)
    print(json.dumps({
        "receipt_path": str(args.output.resolve()),
        "audit_status": receipt["audit_status"],
        "dataset_sha256": receipt["dataset"]["artifact_sha256"],
        "tick_count": receipt["dataset"]["tick_count"],
        "gate_a": receipt["gate_a"],
        "gate_b": receipt["gate_b"],
        "gate_c": receipt["gate_c"],
        "gate_d": receipt["gate_d"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
