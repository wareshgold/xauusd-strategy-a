"""Read-only audit of timestamp sequences in an existing CSV.

Duplicate timestamps, invalid timestamps, or backward ordering fail the
structural audit. Forward gaps are reported separately and do not imply a
market closure, bad data, or a trading-session rule.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_utc(value: Any, row_number: int) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"row {row_number}: timestamp is empty")
    raw = value.strip()
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"row {row_number}: invalid ISO-8601 timestamp {raw!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"row {row_number}: timestamp must include a UTC offset")
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"row {row_number}: timestamp must be UTC, got {raw!r}")
    return parsed.astimezone(timezone.utc)


def audit_timestamp_sequence(
    csv_path: str | Path,
    timestamp_column: str,
    interval_minutes: float = 1.0,
) -> dict[str, Any]:
    """Audit an existing CSV without modifying it.

    Gaps are descriptive only. This function does not infer sessions, holidays,
    broker offsets, data-provider behavior, or whether any row is tradable.
    """
    source = Path(csv_path)
    errors: list[str] = []
    parsed_rows: list[tuple[int, datetime]] = []
    duplicate_examples: list[dict[str, Any]] = []
    backward_examples: list[dict[str, Any]] = []
    gap_examples: list[dict[str, Any]] = []
    report: dict[str, Any] = {
        "mode": "RESEARCH_TIMESTAMP_SEQUENCE_AUDIT",
        "source_csv": str(source),
        "timestamp_column": timestamp_column,
        "expected_interval_minutes": interval_minutes,
        "canonical": False,
        "market_session_approval": "NOT_ESTABLISHED",
        "research_interpretation": "TIMESTAMP_STRUCTURE_ONLY_GAPS_UNCLASSIFIED",
        "source_artifacts_modified": False,
    }

    if (
        not isinstance(interval_minutes, (int, float))
        or isinstance(interval_minutes, bool)
        or not math.isfinite(interval_minutes)
        or interval_minutes <= 0
    ):
        errors.append("interval_minutes must be a finite positive number")
    if not isinstance(timestamp_column, str) or not timestamp_column.strip():
        errors.append("timestamp_column must be a non-empty string")
    if errors:
        report.update({"status": "STRUCTURAL_INTEGRITY_FAIL", "errors": errors})
        return report

    try:
        if not source.is_file():
            raise ValueError(f"CSV not found: {source}")
        source_hash_before = _sha256(source)
        with source.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or timestamp_column not in reader.fieldnames:
                raise ValueError(
                    f"timestamp column {timestamp_column!r} not found in CSV header"
                )
            row_count = 0
            invalid_count = 0
            for row_number, row in enumerate(reader, start=2):
                row_count += 1
                try:
                    parsed_rows.append(
                        (row_number, _parse_utc(row.get(timestamp_column), row_number))
                    )
                except ValueError as exc:
                    invalid_count += 1
                    errors.append(str(exc))

        timestamps = [stamp for _, stamp in parsed_rows]
        counts = Counter(timestamps)
        duplicate_groups = [
            stamp for stamp, count in counts.items() if count > 1
        ]
        duplicate_count = sum(count - 1 for count in counts.values() if count > 1)
        for stamp in sorted(duplicate_groups)[:10]:
            duplicate_examples.append({
                "timestamp_utc": stamp.isoformat().replace("+00:00", "Z"),
                "occurrences": counts[stamp],
            })

        backward_count = 0
        gap_interval_count = 0
        estimated_missing_intervals = 0
        expected_seconds = float(interval_minutes) * 60.0
        for (previous_row, previous), (current_row, current) in zip(
            parsed_rows, parsed_rows[1:]
        ):
            delta_seconds = (current - previous).total_seconds()
            if delta_seconds < 0:
                backward_count += 1
                if len(backward_examples) < 10:
                    backward_examples.append({
                        "previous_row": previous_row,
                        "previous_utc": previous.isoformat().replace("+00:00", "Z"),
                        "current_row": current_row,
                        "current_utc": current.isoformat().replace("+00:00", "Z"),
                    })
            elif delta_seconds > expected_seconds:
                gap_interval_count += 1
                aligned_steps = round(delta_seconds / expected_seconds)
                if aligned_steps >= 2 and abs(
                    delta_seconds - aligned_steps * expected_seconds
                ) < 1e-6:
                    estimated_missing_intervals += aligned_steps - 1
                if len(gap_examples) < 10:
                    gap_examples.append({
                        "previous_row": previous_row,
                        "previous_utc": previous.isoformat().replace("+00:00", "Z"),
                        "current_row": current_row,
                        "current_utc": current.isoformat().replace("+00:00", "Z"),
                        "elapsed_minutes": delta_seconds / 60.0,
                    })

        source_hash_after = _sha256(source)
        if source_hash_before != source_hash_after:
            errors.append("source CSV bytes changed during audit")
        if duplicate_count:
            errors.append(f"duplicate timestamps detected: {duplicate_count} excess row(s)")
        if backward_count:
            errors.append(f"backward timestamp transitions detected: {backward_count}")

        report.update({
            "source_sha256": source_hash_before,
            "row_count": row_count,
            "valid_timestamp_count": len(parsed_rows),
            "invalid_timestamp_count": invalid_count,
            "unique_timestamp_count": len(counts),
            "duplicate_timestamp_count": duplicate_count,
            "duplicate_timestamp_group_count": len(duplicate_groups),
            "duplicate_examples": duplicate_examples,
            "backward_transition_count": backward_count,
            "backward_examples": backward_examples,
            "forward_gap_interval_count": gap_interval_count,
            "estimated_missing_intervals_when_exactly_aligned": estimated_missing_intervals,
            "gap_examples": gap_examples,
            "source_sha256_after_audit": source_hash_after,
        })
    except (OSError, csv.Error, UnicodeError, ValueError) as exc:
        errors.append(str(exc))

    report["errors"] = errors
    report["status"] = (
        "STRUCTURAL_INTEGRITY_FAIL" if errors else "STRUCTURAL_INTEGRITY_PASS"
    )
    report["meaning"] = (
        "No invalid, duplicate, or backward timestamps were detected; forward gaps remain unclassified."
        if not errors else
        "Timestamp structure failed validation; do not silently repair or discard source rows."
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", help="Path to an existing CSV; input is read-only")
    parser.add_argument("--timestamp-column", required=True, help="CSV column containing ISO-8601 UTC timestamps")
    parser.add_argument("--interval-minutes", type=float, default=1.0, help="Expected interval in minutes (default: 1)")
    args = parser.parse_args()
    report = audit_timestamp_sequence(
        args.csv_path, args.timestamp_column, args.interval_minutes
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "STRUCTURAL_INTEGRITY_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
