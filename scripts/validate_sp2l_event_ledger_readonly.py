#!/usr/bin/env python3
"""Read-only structural/provenance validator for normalized SP2L event-ledger JSONL.

This validates record shape only. It does not infer fills, timestamps, ordering,
broker semantics, source fidelity, or profitability.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

EVENT_TYPES = {
    "SIGNAL_CANDIDATE", "ORDER_SUBMITTED", "ORDER_REJECTED",
    "ORDER_CANCELLED", "ORDER_EXPIRED", "ENTRY_FILL",
    "SL_UPDATE_SUBMITTED", "SL_UPDATE_CONFIRMED", "SL_UPDATE_REJECTED",
    "EXIT_FILL", "DATA_END", "OPEN_AT_END", "UNKNOWN", "AMBIGUOUS",
}
EVIDENCE_CLASSES = {"source_observed", "synthetic_fixture", "ohlc_proxy", "derived_assessment"}
REQUIRED_KEYS = {
    "schema_version", "run_id", "event_id", "candidate_id", "trade_id",
    "strategy_id", "profile_id", "source_commit", "config_sha256",
    "dataset_sha256", "event_type", "source_event_ref",
    "source_artifact_sha256", "source_row_ref", "event_time_original",
    "event_timezone_basis", "event_time_utc", "source_sequence_id",
    "price", "volume", "side", "order_id", "position_id", "deal_id",
    "evidence_class", "notes", "warnings",
}
HASH_KEYS = {"config_sha256", "dataset_sha256", "source_artifact_sha256"}
IDENTITY_KEYS = {"schema_version", "run_id", "event_id", "strategy_id", "profile_id",
                 "event_type", "source_event_ref", "evidence_class"}
HEX_64 = re.compile(r"^[0-9a-fA-F]{64}$")


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_rows(rows: list[Any]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    seen_ids: set[tuple[str, str]] = set()

    def issue(index: int, code: str, detail: str) -> None:
        issues.append({"row": index, "code": code, "detail": detail})

    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            issue(index, "ROW_NOT_OBJECT", "Each JSONL row must be a JSON object.")
            continue

        missing = sorted(REQUIRED_KEYS - row.keys())
        if missing:
            issue(index, "MISSING_KEYS", ",".join(missing))
        for key in IDENTITY_KEYS:
            if key in row and not _nonempty(row[key]):
                issue(index, "INVALID_IDENTITY", f"{key} must be a non-empty string.")
        if row.get("event_type") not in EVENT_TYPES:
            issue(index, "INVALID_EVENT_TYPE", "event_type is not in the research vocabulary.")
        if row.get("evidence_class") not in EVIDENCE_CLASSES:
            issue(index, "INVALID_EVIDENCE_CLASS", "evidence_class is not recognized.")

        run_id, event_id = row.get("run_id"), row.get("event_id")
        if _nonempty(run_id) and _nonempty(event_id):
            key = (run_id, event_id)
            if key in seen_ids:
                issue(index, "DUPLICATE_EVENT_ID", "event_id must be unique within run_id.")
            seen_ids.add(key)

        for key in HASH_KEYS:
            value = row.get(key)
            if value is not None and (not isinstance(value, str) or not HEX_64.fullmatch(value)):
                issue(index, "INVALID_HASH", f"{key} must be null or a 64-character hex SHA-256.")

        warnings = row.get("warnings")
        if "warnings" in row and not isinstance(warnings, list):
            issue(index, "INVALID_WARNINGS", "warnings must be a list.")
        if isinstance(warnings, list) and any(not isinstance(v, str) for v in warnings):
            issue(index, "INVALID_WARNINGS", "Every warnings item must be a string.")
        if "notes" in row and row["notes"] is not None and not isinstance(row["notes"], str):
            issue(index, "INVALID_NOTES", "notes must be null or a string.")

        utc_value = row.get("event_time_utc")
        original_value = row.get("event_time_original")
        basis = row.get("event_timezone_basis")
        if utc_value is not None:
            if not _nonempty(utc_value):
                issue(index, "INVALID_UTC_TIME", "event_time_utc must be null or a non-empty ISO timestamp.")
            else:
                try:
                    parsed = datetime.fromisoformat(utc_value.replace("Z", "+00:00"))
                    if parsed.tzinfo is None or parsed.utcoffset() is None:
                        issue(index, "NAIVE_UTC_TIME", "event_time_utc must include an explicit UTC offset.")
                    elif parsed.utcoffset().total_seconds() != 0:
                        issue(index, "NON_UTC_TIME", "event_time_utc must be normalized to UTC.")
                except (TypeError, ValueError):
                    issue(index, "INVALID_UTC_TIME", "event_time_utc is not a valid ISO timestamp.")
            if not _nonempty(original_value):
                issue(index, "UTC_WITHOUT_ORIGINAL", "UTC conversion requires the original timestamp.")
            if not _nonempty(basis):
                issue(index, "UTC_WITHOUT_BASIS", "UTC conversion requires documented timezone evidence.")
        if utc_value is None and (original_value is not None or basis is not None):
            # Original/source timezone may be preserved even while UTC remains unresolved.
            pass

        for key in ("source_row_ref", "source_artifact_sha256", "source_commit",
                    "config_sha256", "dataset_sha256", "source_sequence_id",
                    "price", "volume", "side", "order_id", "position_id", "deal_id",
                    "candidate_id", "trade_id"):
            # These fields are deliberately nullable; presence is checked separately.
            if key not in row:
                continue

    return {
        "research_only": True,
        "validator_version": 1,
        "rows_seen": len(rows),
        "valid": not issues,
        "issue_count": len(issues),
        "issues": issues,
        "interpretation": (
            "Structural/provenance validation only; passing does not establish event truth, "
            "timestamp correctness, fills, ordering, execution fidelity, or profitability."
        ),
    }


def audit(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    rows: list[Any] = []
    parse_issues: list[dict[str, Any]] = []
    for index, line in enumerate(raw.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            parse_issues.append({
                "row": index, "code": "INVALID_JSONL",
                "detail": f"Invalid JSON at line {index}: {exc.msg}",
            })
    result = validate_rows(rows)
    result["input_path"] = str(path)
    result["input_sha256"] = hashlib.sha256(raw).hexdigest()
    result["input_size_bytes"] = len(raw)
    if parse_issues:
        result["issues"] = parse_issues + result["issues"]
        result["issue_count"] = len(result["issues"])
        result["valid"] = False
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Existing JSONL ledger (read-only).")
    parser.add_argument("--output", type=Path, help="Optional NEW report path; existing outputs are never overwritten.")
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"Input file does not exist: {args.input}")
    rendered = json.dumps(audit(args.input), indent=2, ensure_ascii=False) + "\n"
    if args.output:
        if args.output.exists():
            parser.error(f"Refusing to overwrite existing output: {args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    # Invalid ledger is a validation failure, not a parser/runtime crash.
    return 0 if json.loads(rendered)["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
