#!/usr/bin/env python3
"""Explicit, lossless-field migration from the legacy MT5 manifest to v1.

The legacy manifest and raw CSV are read-only inputs. Timestamp discontinuities
are recomputed from the exact raw CSV; legacy gap_ranges/missing_bars claims are
never copied or interpreted as v1 discontinuities or market-session facts.
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

SCHEMA = {"id": "sp2l.mt5-research-evidence", "version": "1.0.0"}
REQUIRED_COLUMNS = {"timestamp", "open", "high", "low", "close", "tick_volume", "spread", "real_volume"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp lacks UTC offset")
    return parsed.astimezone(timezone.utc)


def migrate_legacy_manifest(legacy: dict[str, Any], raw_csv: Path) -> dict[str, Any]:
    required = (
        "dataset_id", "provider", "terminal", "server", "symbol", "timeframe",
        "requested_interval_utc", "actual_first_utc", "actual_last_utc",
        "requested_bar_count", "actual_bar_count", "retrieval_timestamp_utc",
        "artifact", "artifact_sha256", "invalid_row_count", "invalid_rows",
    )
    missing = [key for key in required if key not in legacy]
    if missing:
        raise ValueError("LEGACY_REQUIRED_FIELDS_MISSING:" + ",".join(missing))
    if not raw_csv.is_file():
        raise ValueError("RAW_ARTIFACT_NOT_FOUND")
    actual_hash = sha256_file(raw_csv)
    if actual_hash.lower() != str(legacy["artifact_sha256"]).lower():
        raise ValueError("LEGACY_RAW_SHA256_MISMATCH")
    if legacy["invalid_row_count"] != 0 or legacy["invalid_rows"] != []:
        raise ValueError("LEGACY_MANIFEST_REPORTS_INVALID_ROWS")

    with raw_csv.open("r", newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if not REQUIRED_COLUMNS.issubset(set(reader.fieldnames or [])):
            raise ValueError("RAW_CSV_SCHEMA_MISMATCH")
        rows = list(reader)
    if len(rows) != legacy["actual_bar_count"]:
        raise ValueError("LEGACY_RAW_ROW_COUNT_MISMATCH")
    if not rows:
        raise ValueError("RAW_CSV_EMPTY")
    if rows[0]["timestamp"] != legacy["actual_first_utc"]:
        raise ValueError("LEGACY_FIRST_TIMESTAMP_MISMATCH")
    if rows[-1]["timestamp"] != legacy["actual_last_utc"]:
        raise ValueError("LEGACY_LAST_TIMESTAMP_MISMATCH")

    invalid: list[dict[str, Any]] = []
    discontinuities: list[dict[str, Any]] = []
    chronological = True
    previous = None
    for index, row in enumerate(rows):
        try:
            current = parse_utc(row["timestamp"])
            numbers = [float(row[key]) for key in ("open", "high", "low", "close", "tick_volume")]
            if any(not math.isfinite(number) for number in numbers):
                raise ValueError("non-finite")
            open_, high, low, close, _volume = numbers
            if not (high >= max(open_, close) and low <= min(open_, close) and high >= low):
                raise ValueError("invalid OHLC")
        except (TypeError, ValueError, KeyError):
            invalid.append({"index": index, "reason": "invalid_timestamp_number_or_ohlc"})
            continue
        if previous is not None:
            delta = (current - previous).total_seconds() / 60.0
            if delta <= 0:
                chronological = False
                discontinuities.append({
                    "from": rows[index - 1]["timestamp"],
                    "to": row["timestamp"],
                    "interval_minutes": delta,
                    "kind": "duplicate_timestamp" if delta == 0 else "non_chronological",
                })
            elif delta > 1:
                discontinuities.append({
                    "from": rows[index - 1]["timestamp"],
                    "to": row["timestamp"],
                    "interval_minutes": delta,
                    "kind": "unclassified_gap",
                })
        previous = current

    ordering = [item for item in discontinuities if item["kind"] in {"duplicate_timestamp", "non_chronological"}]
    gaps = [item for item in discontinuities if item["kind"] == "unclassified_gap"]
    if invalid or ordering:
        audit_status = "AUDITED_FAIL"
    elif gaps:
        audit_status = "AUDITED_UNCLASSIFIED_COVERAGE"
    else:
        audit_status = "AUDITED_PASS"

    return {
        "schema": SCHEMA,
        "evidence_type": "research_only_mt5_acquisition",
        "dataset_id": legacy["dataset_id"],
        "note": "Migrated from legacy manifest; legacy gap_ranges were not mapped. All adjacent timestamp intervals were recomputed from the exact hash-verified raw CSV.",
        "provider": legacy["provider"],
        "terminal": legacy["terminal"],
        "server": legacy["server"],
        "symbol": legacy["symbol"],
        "timeframe": legacy["timeframe"],
        "requested_interval_utc": legacy["requested_interval_utc"],
        "actual_first_utc": rows[0]["timestamp"],
        "actual_last_utc": rows[-1]["timestamp"],
        "requested_bar_count": legacy["requested_bar_count"],
        "actual_bar_count": len(rows),
        "timestamp_discontinuities": discontinuities,
        "discontinuity_count": len(discontinuities),
        "invalid_rows": invalid,
        "invalid_row_count": len(invalid),
        "chronological": chronological,
        "ordering_anomalies": ordering,
        "unclassified_gaps": gaps,
        "retrieval_timestamp_utc": legacy["retrieval_timestamp_utc"],
        "raw": {"path": str(raw_csv), "sha256": actual_hash},
        "limitations": [
            "legacy_manifest_fields_preserved_only_where_semantics_are_explicit",
            "timestamp_discontinuities_recomputed_from_raw_csv",
            "legacy_gap_ranges_and_missing_bars_not_migrated",
            "positive_intervals_over_one_minute_are_unclassified_not_proven_missing_market_bars",
            "session_calendar_applicability_not_asserted",
            "research_only_no_strategy_logic",
        ],
        "audit_status": audit_status,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-manifest", required=True, type=Path)
    parser.add_argument("--raw-csv", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    legacy = json.loads(args.legacy_manifest.read_text(encoding="utf-8"))
    migrated = migrate_legacy_manifest(legacy, args.raw_csv)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(migrated, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
    print(json.dumps({
        "status": "MIGRATED",
        "output": str(args.output),
        "dataset_id": migrated["dataset_id"],
        "audit_status": migrated["audit_status"],
        "discontinuity_count": migrated["discontinuity_count"],
        "invalid_row_count": migrated["invalid_row_count"],
        "research_replay_eligible": migrated["audit_status"] == "AUDITED_PASS",
    }, indent=2))
    return 0 if migrated["audit_status"] in {"AUDITED_PASS", "AUDITED_UNCLASSIFIED_COVERAGE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
