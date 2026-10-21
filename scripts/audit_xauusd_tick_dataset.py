from __future__ import annotations

"""Read-only integrity and timestamp audit for a compressed XAUUSD tick dataset.

The source CSV.GZ and its manifest are never modified. The report is written to
a separate path. Timestamp duplicate counts are repeated rows beyond the first
occurrence of each time_msc; out-of-order counts are adjacent descending
transitions. These are distinct diagnostics and are not silently repaired.
"""

import argparse
from contextlib import closing
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = {"time_msc", "time_utc", "bid", "ask"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_time_utc_msc(value: str | None) -> int | None:
    """Parse a timezone-aware ISO-8601 timestamp into integer Unix milliseconds."""
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    delta = parsed.astimezone(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)
    return delta.days * 86_400_000 + delta.seconds * 1_000 + delta.microseconds // 1_000


def audit_dataset(source: Path, manifest_path: Path) -> dict[str, Any]:
    if not source.is_file():
        raise FileNotFoundError(f"dataset not found: {source}")
    if not manifest_path.is_file():
        raise FileNotFoundError(f"manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual_hash = sha256_file(source)
    actual_size = source.stat().st_size
    hash_matches = actual_hash.lower() == str(manifest.get("artifact_sha256", "")).lower()
    size_matches = actual_size == manifest.get("artifact_size_bytes")

    row_count = 0
    invalid_time_count = 0
    invalid_time_utc_count = 0
    time_utc_mismatch_count = 0
    missing_quote_count = 0
    crossed_quote_count = 0
    valid_quote_count = 0
    duplicate_timestamp_rows = 0
    duplicate_same_utc_same_quote = 0
    duplicate_same_utc_different_quote = 0
    duplicate_different_utc = 0
    out_of_order_transitions = 0
    first_time_msc = None
    last_time_msc = None
    previous_time_msc = None
    columns: list[str] = []

    # Disk-backed set avoids keeping ~10.8 million timestamps in Python RAM.
    with tempfile.TemporaryDirectory(prefix="sp2l_tick_audit_") as temp_dir:
        db_path = Path(temp_dir) / "timestamps.sqlite3"
        with closing(sqlite3.connect(db_path)) as connection:
            with connection as db:
                db.execute(
                    "CREATE TABLE seen ("
                    "time_msc INTEGER PRIMARY KEY, first_time_utc_msc INTEGER, "
                    "first_time_utc_raw TEXT, first_bid REAL, first_ask REAL)"
                )
                with gzip.open(source, "rt", encoding="utf-8-sig", newline="") as stream:
                    reader = csv.DictReader(stream)
                    columns = list(reader.fieldnames or [])
                    missing_columns = sorted(REQUIRED_COLUMNS.difference(columns))
                    if missing_columns:
                        raise ValueError(f"missing required CSV columns: {missing_columns}")

                    for row in reader:
                        row_count += 1
                        raw_time = (row.get("time_msc") or "").strip()
                        try:
                            time_msc = int(raw_time)
                        except (TypeError, ValueError):
                            invalid_time_count += 1
                            continue

                        if first_time_msc is None:
                            first_time_msc = time_msc
                        last_time_msc = time_msc
                        if previous_time_msc is not None and time_msc < previous_time_msc:
                            out_of_order_transitions += 1
                        previous_time_msc = time_msc

                        raw_time_utc = (row.get("time_utc") or "").strip()
                        time_utc_msc = parse_time_utc_msc(raw_time_utc)
                        if time_utc_msc is None:
                            invalid_time_utc_count += 1
                        elif time_utc_msc != time_msc:
                            time_utc_mismatch_count += 1

                        try:
                            bid = float(row.get("bid") or "")
                            ask = float(row.get("ask") or "")
                            quote_valid = math.isfinite(bid) and math.isfinite(ask) and bid > 0 and ask > 0
                        except (TypeError, ValueError):
                            quote_valid = False
                            bid = ask = 0.0

                        cursor = db.execute(
                            "INSERT OR IGNORE INTO seen("
                            "time_msc, first_time_utc_msc, first_time_utc_raw, first_bid, first_ask"
                            ") VALUES (?, ?, ?, ?, ?)",
                            (time_msc, time_utc_msc, raw_time_utc, bid if quote_valid else None,
                             ask if quote_valid else None),
                        )
                        if cursor.rowcount == 0:
                            duplicate_timestamp_rows += 1
                            first = db.execute(
                                "SELECT first_time_utc_msc, first_time_utc_raw, first_bid, first_ask "
                                "FROM seen WHERE time_msc = ?",
                                (time_msc,),
                            ).fetchone()
                            first_utc_msc, first_utc_raw, first_bid, first_ask = first
                            same_utc = (
                                time_utc_msc == first_utc_msc
                                if time_utc_msc is not None and first_utc_msc is not None
                                else raw_time_utc == first_utc_raw
                            )
                            if not same_utc:
                                duplicate_different_utc += 1
                            elif (
                                quote_valid and first_bid is not None and first_ask is not None
                                and bid == first_bid and ask == first_ask
                            ):
                                duplicate_same_utc_same_quote += 1
                            else:
                                duplicate_same_utc_different_quote += 1
                        if not quote_valid:
                            missing_quote_count += 1
                        elif ask < bid:
                            crossed_quote_count += 1
                        else:
                            valid_quote_count += 1

    expected_rows = manifest.get("tick_count")
    result = {
        "audit_schema_version": 1,
        "audit_type": "READ_ONLY_XAUUSD_TICK_DATASET_INTEGRITY_AND_TIMESTAMP_AUDIT",
        "source_artifact": str(source),
        "source_manifest": str(manifest_path),
        "source_status": manifest.get("status"),
        "source_sha256": actual_hash,
        "manifest_sha256": manifest.get("artifact_sha256"),
        "sha256_matches_manifest": hash_matches,
        "source_size_bytes": actual_size,
        "manifest_size_bytes": manifest.get("artifact_size_bytes"),
        "size_matches_manifest": size_matches,
        "csv_columns": columns,
        "csv_row_count": row_count,
        "manifest_tick_count": expected_rows,
        "row_count_matches_manifest": row_count == expected_rows,
        "invalid_time_msc_rows": invalid_time_count,
        "invalid_time_utc_rows": invalid_time_utc_count,
        "time_utc_timestamp_mismatch_rows": time_utc_mismatch_count,
        "duplicate_timestamp_rows_beyond_first_occurrence": duplicate_timestamp_rows,
        "duplicate_timestamp_rows_same_time_utc_same_bidask": duplicate_same_utc_same_quote,
        "duplicate_timestamp_rows_same_time_utc_different_bidask": duplicate_same_utc_different_quote,
        "duplicate_timestamp_rows_different_time_utc": duplicate_different_utc,
        "adjacent_out_of_order_transitions": out_of_order_transitions,
        "first_time_msc_in_file_order": first_time_msc,
        "last_time_msc_in_file_order": last_time_msc,
        "valid_non_crossed_bidask_rows": valid_quote_count,
        "missing_or_invalid_bidask_rows": missing_quote_count,
        "crossed_quote_rows": crossed_quote_count,
        "source_manifest_duplicate_or_out_of_order_count": manifest.get(
            "duplicate_or_out_of_order_timestamp_count"
        ),
        "interpretation": (
            "Diagnostics only. No rows were reordered, removed, repaired, or written back. "
            "Duplicate counts are repeated rows beyond the first global occurrence of a time_msc; "
            "out-of-order counts are adjacent transitions where time_msc decreases."
        ),
    }
    hard_checks = (
        hash_matches,
        size_matches,
        row_count == expected_rows,
        invalid_time_count == 0,
        invalid_time_utc_count == 0,
        time_utc_mismatch_count == 0,
        missing_quote_count == 0,
        crossed_quote_count == 0,
    )
    result["integrity_gate"] = "PASS" if all(hard_checks) else "FAIL"
    result["timestamp_review_required"] = (
        duplicate_timestamp_rows > 0 or out_of_order_transitions > 0
    )
    if result["integrity_gate"] == "FAIL":
        result["status"] = "FAIL"
    elif result["timestamp_review_required"]:
        result["status"] = "PASS_WITH_TIMESTAMP_WARNINGS"
    else:
        result["status"] = "PASS"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Existing .csv.gz dataset")
    parser.add_argument("--manifest", required=True, type=Path, help="Existing manifest JSON")
    parser.add_argument("--output", required=True, type=Path, help="New JSON report path; must not exist")
    args = parser.parse_args()

    if args.output.exists():
        print(f"AUDIT_REFUSED_OUTPUT_EXISTS: {args.output}", file=sys.stderr)
        return 4
    try:
        result = audit_dataset(args.input, args.manifest)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    except Exception as exc:
        print(f"AUDIT_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["integrity_gate"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
