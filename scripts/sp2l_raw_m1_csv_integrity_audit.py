"""Read-only structural audit for raw MT5 M1 OHLC CSV artifacts.

This audit checks bytes, schema, row integrity, UTC minute timestamps, ordering,
duplicates, OHLC bounds, and non-negative volume fields. Timestamp gaps are
reported only as observations: this module does not infer market closures,
active sessions, DST, or missing expected bars.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_COLUMNS = (
    "timestamp", "open", "high", "low", "close",
    "tick_volume", "spread", "real_volume",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _utc_minute(value: str, row_number: int) -> datetime:
    if not value:
        raise ValueError(f"row {row_number}: timestamp is empty")
    text = value.strip().replace("Z", "+00:00")
    try:
        result = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"row {row_number}: invalid ISO timestamp {value!r}") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError(f"row {row_number}: timestamp must include a UTC offset")
    if result.utcoffset().total_seconds() != 0:
        raise ValueError(f"row {row_number}: timestamp must be UTC, got {value!r}")
    result = result.astimezone(timezone.utc)
    if result.second != 0 or result.microsecond != 0:
        raise ValueError(f"row {row_number}: M1 timestamp must be on a minute boundary")
    return result


def audit_raw_m1_csv(csv_path: str | Path, manifest_path: str | Path | None = None) -> dict[str, Any]:
    source = Path(csv_path)
    errors: list[str] = []
    warnings: list[str] = []
    timestamps: list[datetime] = []
    row_count = 0
    invalid_rows = 0
    duplicate_timestamps = 0
    out_of_order_pairs = 0
    timestamp_gaps: list[dict[str, Any]] = []
    min_timestamp = max_timestamp = None
    previous = None
    seen: set[datetime] = set()

    result: dict[str, Any] = {
        "mode": "RESEARCH_RAW_MT5_M1_CSV_INTEGRITY_AUDIT",
        "canonical": False,
        "source_artifacts_modified": False,
        "source_csv": str(source),
        "status": "STRUCTURAL_INTEGRITY_FAIL",
        "row_count": 0,
        "invalid_row_count": 0,
        "duplicate_timestamp_count": 0,
        "out_of_order_pair_count": 0,
        "timestamp_gap_count": 0,
        "timestamp_gaps": timestamp_gaps,
        "errors": errors,
        "warnings": warnings,
    }
    if not source.is_file():
        errors.append(f"CSV not found: {source}")
        return result

    result["csv_sha256"] = _sha256(source)
    try:
        with source.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fields = reader.fieldnames or []
            missing = [column for column in REQUIRED_COLUMNS if column not in fields]
            if missing:
                errors.append(f"missing required columns: {', '.join(missing)}")
            if len(fields) != len(set(fields)):
                errors.append("CSV contains duplicate column names")
            if not fields:
                errors.append("CSV header is missing")
            for row_number, row in enumerate(reader, start=2):
                row_count += 1
                row_invalid = False
                try:
                    stamp = _utc_minute(row.get("timestamp", ""), row_number)
                    if stamp in seen:
                        duplicate_timestamps += 1
                        errors.append(f"row {row_number}: duplicate timestamp {stamp.isoformat()}")
                    seen.add(stamp)
                    if previous is not None:
                        delta = int((stamp - previous).total_seconds())
                        if delta <= 0:
                            out_of_order_pairs += 1
                            errors.append(f"row {row_number}: timestamp is not strictly increasing")
                        elif delta > 60:
                            timestamp_gaps.append({
                                "from_utc": previous.isoformat().replace("+00:00", "Z"),
                                "to_utc": stamp.isoformat().replace("+00:00", "Z"),
                                "delta_seconds": delta,
                                "missing_minute_slots": max(0, delta // 60 - 1),
                                "interpretation": "UNCLASSIFIED_TIMESTAMP_GAP",
                            })
                    previous = stamp
                    min_timestamp = stamp if min_timestamp is None or stamp < min_timestamp else min_timestamp
                    max_timestamp = stamp if max_timestamp is None or stamp > max_timestamp else max_timestamp

                    values = {}
                    for column in ("open", "high", "low", "close"):
                        value = float(row[column])
                        if not math.isfinite(value) or value <= 0:
                            raise ValueError(f"{column} must be finite and positive")
                        values[column] = value
                    if values["high"] < max(values["open"], values["close"], values["low"]):
                        raise ValueError("high is below another OHLC value")
                    if values["low"] > min(values["open"], values["close"], values["high"]):
                        raise ValueError("low is above another OHLC value")
                    for column in ("tick_volume", "spread", "real_volume"):
                        value = int(row[column])
                        if value < 0:
                            raise ValueError(f"{column} must be non-negative")
                        if str(value) != str(row[column]).strip() and float(row[column]) != value:
                            raise ValueError(f"{column} must be an integer")
                except (KeyError, TypeError, ValueError, OverflowError) as exc:
                    row_invalid = True
                    errors.append(f"row {row_number}: {exc}")
                if row_invalid:
                    invalid_rows += 1
    except (OSError, UnicodeError, csv.Error) as exc:
        errors.append(f"could not read CSV: {exc}")

    result.update({
        "row_count": row_count,
        "invalid_row_count": invalid_rows,
        "duplicate_timestamp_count": duplicate_timestamps,
        "out_of_order_pair_count": out_of_order_pairs,
        "timestamp_gap_count": len(timestamp_gaps),
        "first_timestamp_utc": min_timestamp.isoformat().replace("+00:00", "Z") if min_timestamp else None,
        "last_timestamp_utc": max_timestamp.isoformat().replace("+00:00", "Z") if max_timestamp else None,
    })
    if row_count == 0:
        errors.append("CSV contains a header but no data rows")

    if manifest_path is not None:
        manifest_source = Path(manifest_path)
        try:
            manifest = json.loads(manifest_source.read_text(encoding="utf-8"))
            if not isinstance(manifest, dict):
                raise ValueError("manifest root must be an object")
            result["source_manifest"] = str(manifest_source)
            expected_artifact = manifest.get("artifact")
            if expected_artifact != source.name:
                errors.append(f"manifest artifact must match CSV filename {source.name!r}")
            expected_hash = manifest.get("artifact_sha256")
            if not isinstance(expected_hash, str) or len(expected_hash) != 64:
                errors.append("manifest artifact_sha256 must be a 64-character SHA-256")
            elif expected_hash.lower() != result["csv_sha256"].lower():
                errors.append("manifest artifact_sha256 does not match CSV bytes")
            expected_count = manifest.get("returned_bar_count")
            if not isinstance(expected_count, int) or isinstance(expected_count, bool) or expected_count < 0:
                errors.append("manifest returned_bar_count must be a non-negative integer")
            elif expected_count != row_count:
                errors.append(f"manifest returned_bar_count={expected_count} disagrees with CSV row_count={row_count}")
            interval = manifest.get("requested_interval_utc")
            if not isinstance(interval, dict) or not interval.get("start") or not interval.get("end"):
                errors.append("manifest requested_interval_utc start/end are required")
            else:
                try:
                    start = _utc_minute(interval["start"], 0)
                    end = _utc_minute(interval["end"], 0)
                    if min_timestamp is not None and (min_timestamp < start or max_timestamp > end):
                        errors.append("CSV timestamp range falls outside manifest requested interval")
                except (TypeError, ValueError) as exc:
                    errors.append(f"manifest interval invalid: {exc}")
            if manifest.get("session_calendar_historical_applicability") == "UNVERIFIED":
                warnings.append("manifest expected-active-bar counts depend on a session calendar whose historical applicability is UNVERIFIED")
            expected_active = manifest.get("expected_active_bar_count")
            if isinstance(expected_active, int) and not isinstance(expected_active, bool):
                result["manifest_expected_active_bar_count_diagnostic_only"] = expected_active
                result["manifest_count_difference_diagnostic_only"] = row_count - expected_active
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"manifest invalid/unreadable: {exc}")

    result["status"] = "STRUCTURAL_INTEGRITY_PASS" if not errors else "STRUCTURAL_INTEGRITY_FAIL"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path")
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    result = audit_raw_m1_csv(args.csv_path, args.manifest)
    result["generated_utc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    output = Path(args.output) if args.output else None
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if output:
        output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["status"] == "STRUCTURAL_INTEGRITY_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
