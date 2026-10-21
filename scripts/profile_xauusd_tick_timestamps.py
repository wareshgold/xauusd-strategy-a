from __future__ import annotations

"""Read-only profile of repeated millisecond timestamps in an XAUUSD tick CSV.GZ.

This is diagnostic only. It preserves input order and never repairs, sorts, or
drops rows. The output path must not already exist.
"""

import argparse
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def parse_utc(value: str | None) -> datetime | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        result = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if result.tzinfo is None or result.utcoffset() is None:
        return None
    return result.astimezone(timezone.utc)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _quote(row: dict[str, str]) -> tuple[float, float] | None:
    try:
        bid = float(row.get("bid") or "")
        ask = float(row.get("ask") or "")
    except (TypeError, ValueError):
        return None
    if not (math.isfinite(bid) and math.isfinite(ask) and bid > 0 and ask > 0):
        return None
    return bid, ask


def _sample_row(row: dict[str, str]) -> dict[str, str]:
    # Keep source values as strings to avoid losing formatting or implying precision.
    return {
        key: (row.get(key) or "")
        for key in ("time_msc", "time_utc", "bid", "ask", "last", "volume", "flags")
    }


def profile_dataset(source: Path, manifest_path: Path, sample_limit: int = 20) -> dict[str, Any]:
    if not source.is_file():
        raise FileNotFoundError(f"dataset not found: {source}")
    if not manifest_path.is_file():
        raise FileNotFoundError(f"manifest not found: {manifest_path}")
    if sample_limit < 1 or sample_limit > 200:
        raise ValueError("sample-limit must be between 1 and 200")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_hash = sha256_file(source)
    source_size = source.stat().st_size

    row_count = 0
    invalid_time_rows = 0
    invalid_utc_rows = 0
    utc_mismatch_rows = 0
    adjacent_out_of_order = 0
    unique_timestamp_groups = 0
    duplicate_rows = 0
    duplicate_groups = 0
    groups_with_different_quotes = 0
    duplicate_rows_different_from_first_quote = 0
    group_size_distribution: Counter[str] = Counter()
    max_group_size = 0
    max_group_samples: list[dict[str, Any]] = []
    differing_quote_samples: list[dict[str, Any]] = []
    duplicate_rows_by_utc_day: Counter[str] = Counter()
    differing_groups_by_utc_day: Counter[str] = Counter()
    previous_time_msc: int | None = None

    current_time: int | None = None
    current_rows = 0
    current_first_utc: datetime | None = None
    current_first_quote: tuple[float, float] | None = None
    current_quote_set: set[tuple[float, float]] = set()
    current_different_from_first = 0
    current_samples: list[dict[str, str]] = []
    current_differing_samples: list[dict[str, str]] = []
    current_day: str | None = None

    def finish_group() -> None:
        nonlocal unique_timestamp_groups, duplicate_rows, duplicate_groups
        nonlocal groups_with_different_quotes, duplicate_rows_different_from_first_quote
        nonlocal max_group_size, max_group_samples
        if current_time is None:
            return
        unique_timestamp_groups += 1
        group_size_distribution[str(current_rows)] += 1
        if current_rows > 1:
            extra = current_rows - 1
            duplicate_rows += extra
            duplicate_groups += 1
            if current_day:
                duplicate_rows_by_utc_day[current_day] += extra
        if len(current_quote_set) > 1:
            groups_with_different_quotes += 1
            if current_day:
                differing_groups_by_utc_day[current_day] += 1
        duplicate_rows_different_from_first_quote += current_different_from_first

        record = {
            "time_msc": current_time,
            "time_utc": current_first_utc.isoformat(timespec="milliseconds").replace("+00:00", "Z")
                if current_first_utc else None,
            "utc_day": current_day,
            "group_size": current_rows,
            "distinct_valid_bidask_pairs": len(current_quote_set),
            "duplicate_rows_with_bidask_different_from_first": current_different_from_first,
            "rows": current_samples,
            "differing_quote_rows": current_differing_samples,
        }
        if current_rows > max_group_size:
            max_group_size = current_rows
            max_group_samples = [record]
        elif current_rows == max_group_size and current_rows > 1 and len(max_group_samples) < sample_limit:
            max_group_samples.append(record)
        if len(current_quote_set) > 1 and len(differing_quote_samples) < sample_limit:
            differing_quote_samples.append(record)

    with gzip.open(source, "rt", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"time_msc", "time_utc", "bid", "ask", "last", "volume", "flags"}
        missing = sorted(required.difference(reader.fieldnames or []))
        if missing:
            raise ValueError(f"missing required CSV columns: {missing}")

        for row in reader:
            row_count += 1
            raw_time = (row.get("time_msc") or "").strip()
            try:
                time_msc = int(raw_time)
            except ValueError:
                invalid_time_rows += 1
                # Cannot reliably assign a malformed timestamp to a group.
                finish_group()
                current_time = None
                current_rows = 0
                current_first_utc = None
                current_first_quote = None
                current_quote_set = set()
                current_different_from_first = 0
                current_samples = []
                current_differing_samples = []
                current_day = None
                previous_time_msc = None
                continue

            if previous_time_msc is not None and time_msc < previous_time_msc:
                adjacent_out_of_order += 1
            previous_time_msc = time_msc

            parsed_utc = parse_utc(row.get("time_utc"))
            if parsed_utc is None:
                invalid_utc_rows += 1
            elif int(parsed_utc.timestamp() * 1000) != time_msc:
                utc_mismatch_rows += 1
            quote = _quote(row)

            if current_time != time_msc:
                finish_group()
                current_time = time_msc
                current_rows = 0
                current_first_utc = parsed_utc
                current_first_quote = quote
                current_quote_set = set()
                current_different_from_first = 0
                current_samples = []
                current_differing_samples = []
                current_day = parsed_utc.date().isoformat() if parsed_utc else None

            current_rows += 1
            if quote is not None:
                current_quote_set.add(quote)
            if current_rows > 1 and quote != current_first_quote:
                current_different_from_first += 1
                if len(current_differing_samples) < 4:
                    current_differing_samples.append(_sample_row(row))
            if len(current_samples) < 8:
                current_samples.append(_sample_row(row))
        finish_group()

    # Record small bounded examples with source row fields, including flags/volume/last.
    result = {
        "profile_schema_version": 1,
        "profile_type": "READ_ONLY_XAUUSD_REPEATED_TIMESTAMP_PROFILE",
        "source_artifact": str(source),
        "source_manifest": str(manifest_path),
        "source_status": manifest.get("status"),
        "source_sha256": source_hash,
        "manifest_sha256": manifest.get("artifact_sha256"),
        "sha256_matches_manifest": source_hash.lower() == str(manifest.get("artifact_sha256", "")).lower(),
        "source_size_bytes": source_size,
        "manifest_size_bytes": manifest.get("artifact_size_bytes"),
        "size_matches_manifest": source_size == manifest.get("artifact_size_bytes"),
        "csv_row_count": row_count,
        "manifest_tick_count": manifest.get("tick_count"),
        "row_count_matches_manifest": row_count == manifest.get("tick_count"),
        "invalid_time_msc_rows": invalid_time_rows,
        "invalid_time_utc_rows": invalid_utc_rows,
        "time_utc_timestamp_mismatch_rows": utc_mismatch_rows,
        "adjacent_out_of_order_transitions": adjacent_out_of_order,
        "unique_timestamp_groups": unique_timestamp_groups,
        "duplicate_timestamp_rows_beyond_first_occurrence": duplicate_rows,
        "duplicate_timestamp_groups": duplicate_groups,
        "groups_with_multiple_distinct_valid_bidask_pairs": groups_with_different_quotes,
        "duplicate_rows_with_bidask_different_from_first_occurrence": duplicate_rows_different_from_first_quote,
        "group_size_distribution": {
            key: group_size_distribution[key] for key in sorted(group_size_distribution, key=int)
        },
        "maximum_group_size": max_group_size,
        "duplicate_rows_by_utc_day": dict(sorted(duplicate_rows_by_utc_day.items())),
        "groups_with_different_quotes_by_utc_day": dict(sorted(differing_groups_by_utc_day.items())),
        "maximum_size_group_examples": max_group_samples[:sample_limit],
        "different_bidask_group_examples": differing_quote_samples[:sample_limit],
        "interpretation": (
            "Read-only diagnostics. Input rows are neither sorted nor modified. "
            "Groups are contiguous equal-time_msc runs; adjacent ordering is reported separately. "
            "A different quote is not by itself proof of corruption or proof of true market event order."
        ),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Existing .csv.gz dataset")
    parser.add_argument("--manifest", required=True, type=Path, help="Existing manifest JSON")
    parser.add_argument("--output", required=True, type=Path, help="New JSON report path; must not exist")
    parser.add_argument("--sample-limit", type=int, default=20, help="Bounded example count (1-200)")
    args = parser.parse_args()

    if args.output.exists():
        print(f"PROFILE_REFUSED_OUTPUT_EXISTS: {args.output}", file=sys.stderr)
        return 4
    try:
        result = profile_dataset(args.input, args.manifest, args.sample_limit)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    except Exception as exc:
        print(f"PROFILE_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    # Characterization is not an integrity certification; nonzero data quality
    # counters are deliberately reported, not automatically treated as failure.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
