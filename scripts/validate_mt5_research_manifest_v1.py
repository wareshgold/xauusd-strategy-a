#!/usr/bin/env python3
"""Fail-closed acceptance gate for sp2l.mt5-research-evidence v1.

Verifies manifest/schema consistency and the exact raw CSV. It does not infer
broker sessions, prove market-calendar completeness, or authorize production.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_ID = "sp2l.mt5-research-evidence"
SCHEMA_VERSION = "1.0.0"


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


def evaluate_manifest(manifest: dict[str, Any], raw_csv: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    schema = manifest.get("schema")
    if not isinstance(schema, dict) or schema.get("id") != SCHEMA_ID or schema.get("version") != SCHEMA_VERSION:
        errors.append("UNSUPPORTED_OR_MISSING_SCHEMA")

    audit = manifest.get("audit_status")
    if audit not in {"AUDITED_PASS", "AUDITED_UNCLASSIFIED_COVERAGE", "AUDITED_FAIL"}:
        errors.append("UNKNOWN_AUDIT_STATUS")

    raw = manifest.get("raw")
    expected_hash = raw.get("sha256") if isinstance(raw, dict) else None
    if not isinstance(expected_hash, str) or len(expected_hash) != 64:
        errors.append("RAW_SHA256_MISSING_OR_INVALID")
    if not raw_csv.is_file():
        errors.append("RAW_ARTIFACT_NOT_FOUND")
        actual_hash = None
    else:
        actual_hash = sha256_file(raw_csv)
        if isinstance(expected_hash, str) and actual_hash.lower() != expected_hash.lower():
            errors.append("RAW_SHA256_MISMATCH")

    expected_rows = manifest.get("actual_bar_count")
    if isinstance(expected_rows, bool) or not isinstance(expected_rows, int) or expected_rows <= 0:
        errors.append("ACTUAL_BAR_COUNT_INVALID")
        expected_rows = None

    try:
        with raw_csv.open("r", newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            required = {"timestamp", "open", "high", "low", "close", "tick_volume", "spread", "real_volume"}
            if not required.issubset(set(reader.fieldnames or [])):
                errors.append("RAW_CSV_SCHEMA_MISMATCH")
                rows = []
            else:
                rows = list(reader)
        if expected_rows is not None and len(rows) != expected_rows:
            errors.append("RAW_ROW_COUNT_MISMATCH")
        if rows:
            if rows[0]["timestamp"] != manifest.get("actual_first_utc"):
                errors.append("ACTUAL_FIRST_TIMESTAMP_MISMATCH")
            if rows[-1]["timestamp"] != manifest.get("actual_last_utc"):
                errors.append("ACTUAL_LAST_TIMESTAMP_MISMATCH")
            previous = None
            for row in rows:
                current = parse_utc(row["timestamp"])
                if previous is not None and current <= previous:
                    errors.append("RAW_TIMESTAMP_ORDER_INVALID")
                    break
                previous = current
    except (OSError, UnicodeError, csv.Error, KeyError, TypeError, ValueError):
        errors.append("RAW_CSV_UNREADABLE_OR_TIMESTAMP_INVALID")

    if manifest.get("invalid_row_count") != 0 or manifest.get("invalid_rows") != []:
        errors.append("MANIFEST_REPORTS_INVALID_ROWS")

    discontinuities = manifest.get("timestamp_discontinuities")
    if not isinstance(discontinuities, list):
        errors.append("TIMESTAMP_DISCONTINUITIES_INVALID")
        discontinuities = []
    if manifest.get("discontinuity_count") != len(discontinuities):
        errors.append("DISCONTINUITY_COUNT_MISMATCH")
    ordering = [x for x in discontinuities if isinstance(x, dict) and x.get("kind") in {"duplicate_timestamp", "non_chronological"}]
    gaps = [x for x in discontinuities if isinstance(x, dict) and x.get("kind") == "unclassified_gap"]
    if manifest.get("ordering_anomalies") != ordering:
        errors.append("ORDERING_ANOMALIES_INCONSISTENT")
    if manifest.get("unclassified_gaps") != gaps:
        errors.append("UNCLASSIFIED_GAPS_INCONSISTENT")
    # Recompute adjacent timestamp discontinuities from the raw CSV; do not
    # trust internally consistent but fabricated manifest lists.
    observed = []
    if rows:
        for left, right in zip(rows, rows[1:]):
            left_dt, right_dt = parse_utc(left["timestamp"]), parse_utc(right["timestamp"])
            delta = (right_dt - left_dt).total_seconds() / 60.0
            if delta <= 0:
                observed.append({
                    "from": left["timestamp"], "to": right["timestamp"],
                    "interval_minutes": delta,
                    "kind": "duplicate_timestamp" if delta == 0 else "non_chronological",
                })
            elif delta > 1:
                observed.append({
                    "from": left["timestamp"], "to": right["timestamp"],
                    "interval_minutes": delta, "kind": "unclassified_gap",
                })
    if observed != discontinuities:
        errors.append("RAW_DISCONTINUITIES_DO_NOT_MATCH_MANIFEST")

    if audit == "AUDITED_PASS" and discontinuities:
        errors.append("PASS_STATUS_CONTRADICTS_DISCONTINUITIES")
    if audit == "AUDITED_UNCLASSIFIED_COVERAGE":
        if not gaps or ordering:
            errors.append("UNCLASSIFIED_STATUS_CONTRADICTS_DISCONTINUITIES")
        warnings.append("OBSERVED_GAPS_LACK_AUTHORIZED_HISTORICAL_SESSION_CLASSIFICATION")
    if audit == "AUDITED_FAIL":
        errors.append("ACQUISITION_AUDIT_FAILED")

    if not errors and audit == "AUDITED_PASS":
        status = "ACCEPTED"
    elif not errors and audit == "AUDITED_UNCLASSIFIED_COVERAGE":
        status = "ACCEPTED_WITH_UNCLASSIFIED_COVERAGE"
    else:
        status = "REJECTED"

    return {
        "contract": {"id": "sp2l.mt5-research-acceptance", "version": "1.0.0"},
        "dataset_id": manifest.get("dataset_id"),
        "status": status,
        "research_replay_eligible": status == "ACCEPTED",
        "confirmatory_validation_eligible": False,
        "production_eligible": False,
        "audit_status": audit,
        "raw_artifact": str(raw_csv),
        "raw_sha256_actual": actual_hash,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "limitations": [
            "ACCEPTED is structural and hash acceptance, not proof of requested market-session completeness",
            "no broker calendar or missing-trading-bar count is inferred",
            "confirmatory validation requires independent frozen-protocol and holdout gates",
            "this gate never emits trading decisions",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--raw-csv", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = evaluate_manifest(manifest, args.raw_csv)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] in {"ACCEPTED", "ACCEPTED_WITH_UNCLASSIFIED_COVERAGE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
