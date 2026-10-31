#!/usr/bin/env python3
"""Read-only compatibility audit for monthly legacy MT5 manifests and CSVs.

This report does not migrate, repair, promote, or accept a dataset. Legacy
session-calendar and missing-timestamp claims are recorded as unverified
metadata only. Raw CSV integrity is independently recomputed.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from datetime import datetime
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp lacks timezone")
    return parsed


def audit_pair(manifest_path: Path, csv_path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "manifest_path": str(manifest_path), "raw_csv_path": str(csv_path),
        "status": "BLOCKED", "errors": [], "warnings": [], "raw": {}, "legacy": {},
        "interpretation": [
            "read_only_compatibility_audit_no_migration",
            "legacy_expected_active_bar_count_and_missing_expected_timestamps_are_not_market_truth",
            "legacy_session_calendar_historical_applicability_is_not_verified",
            "no_session_calendar_or_missing_market_bar_inference",
            "no_replay_confirmatory_validation_or_production_eligibility",
        ],
    }
    try:
        legacy = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        result["errors"].append("MANIFEST_UNREADABLE:" + type(exc).__name__)
        return result

    result["legacy"] = {
        "dataset_id": legacy.get("dataset_id"), "audit_status": legacy.get("audit_status"),
        "provider": legacy.get("provider"), "terminal": legacy.get("terminal"),
        "server": legacy.get("server"), "symbol": legacy.get("symbol"),
        "timeframe": legacy.get("timeframe"), "requested_interval_utc": legacy.get("requested_interval_utc"),
        "expected_active_bar_count": legacy.get("expected_active_bar_count"),
        "returned_bar_count": legacy.get("returned_bar_count"),
        "legacy_missing_expected_timestamps_count": len(legacy.get("missing_expected_timestamps"))
            if isinstance(legacy.get("missing_expected_timestamps"), list) else None,
        "session_calendar_id": legacy.get("session_calendar_id"),
        "session_calendar_historical_applicability": legacy.get("session_calendar_historical_applicability"),
        "artifact": legacy.get("artifact"), "artifact_sha256": legacy.get("artifact_sha256"),
    }
    required = ["dataset_id", "provider", "terminal", "server", "symbol", "timeframe",
                "requested_interval_utc", "artifact", "artifact_sha256", "returned_bar_count",
                "retrieval_timestamp_utc"]
    result["legacy"]["missing_fields"] = [key for key in required if key not in legacy]
    if result["legacy"]["missing_fields"]:
        result["errors"].append("LEGACY_REQUIRED_FIELDS_MISSING")

    if not csv_path.is_file():
        result["errors"].append("RAW_CSV_NOT_FOUND")
        return result
    actual_hash = sha256_file(csv_path)
    expected_hash = legacy.get("artifact_sha256")
    result["raw"]["sha256_actual"] = actual_hash
    result["raw"]["sha256_matches_legacy"] = isinstance(expected_hash, str) and actual_hash.lower() == expected_hash.lower()
    if not result["raw"]["sha256_matches_legacy"]:
        result["errors"].append("RAW_SHA256_MISMATCH_OR_MISSING")

    count = 0
    first_timestamp = last_timestamp = None
    previous_dt = None
    ordering_anomalies = positive_gaps = invalid_rows = 0
    try:
        with csv_path.open("r", newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            headers = list(reader.fieldnames or [])
            timestamp_key = next((key for key in ("timestamp", "time_utc", "time", "datetime") if key in headers), None)
            result["raw"]["csv_columns"] = headers
            result["raw"]["timestamp_column"] = timestamp_key
            if timestamp_key is None:
                result["errors"].append("TIMESTAMP_COLUMN_NOT_RECOGNIZED")
            for row in reader:
                count += 1
                try:
                    stamp = row[timestamp_key] if timestamp_key else None
                    if not stamp:
                        raise ValueError("empty timestamp")
                    current_dt = parse_timestamp(stamp)
                    if first_timestamp is None:
                        first_timestamp = stamp
                    if previous_dt is not None:
                        delta = (current_dt - previous_dt).total_seconds()
                        if delta <= 0:
                            ordering_anomalies += 1
                        elif delta > 60:
                            positive_gaps += 1
                    previous_dt = current_dt
                    last_timestamp = stamp
                    if all(key in headers for key in ("open", "high", "low", "close")):
                        o, h, l, c = (float(row[key]) for key in ("open", "high", "low", "close"))
                        if not all(math.isfinite(v) for v in (o, h, l, c)) or h < max(o, c) or l > min(o, c) or h < l:
                            raise ValueError("invalid OHLC")
                except (TypeError, ValueError, KeyError):
                    invalid_rows += 1
    except (OSError, UnicodeError, csv.Error) as exc:
        result["errors"].append("RAW_CSV_UNREADABLE:" + type(exc).__name__)
        return result

    result["raw"].update({
        "row_count": count, "first_timestamp": first_timestamp, "last_timestamp": last_timestamp,
        "ordering_anomaly_count": ordering_anomalies,
        "positive_interval_over_60_seconds_count": positive_gaps,
        "invalid_timestamp_or_ohlc_row_count": invalid_rows,
        "row_count_matches_legacy": count == legacy.get("returned_bar_count"),
    })
    if count == 0:
        result["errors"].append("RAW_CSV_EMPTY")
    if not result["raw"]["row_count_matches_legacy"]:
        result["errors"].append("RAW_ROW_COUNT_MISMATCH")
    if ordering_anomalies:
        result["errors"].append("RAW_TIMESTAMP_ORDER_ANOMALIES")
    if invalid_rows:
        result["errors"].append("RAW_INVALID_TIMESTAMP_OR_OHLC_ROWS")
    if positive_gaps:
        result["warnings"].append("POSITIVE_TIMESTAMP_GAPS_REQUIRE_SOURCE_AND_SESSION_REVIEW")
    if legacy.get("audit_status") == "AUDITED_FAIL":
        result["errors"].append("LEGACY_AUDIT_STATUS_ALREADY_FAIL")
    elif legacy.get("audit_status") not in {"AUDITED_PASS", "AUDITED_UNCLASSIFIED_COVERAGE"}:
        result["warnings"].append("LEGACY_AUDIT_STATUS_MISSING_OR_UNKNOWN")
    result["status"] = "BLOCKED" if result["errors"] else "REVIEW_REQUIRED"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--raw-csv", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = audit_pair(args.manifest, args.raw_csv)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"dataset_id": report.get("legacy", {}).get("dataset_id"),
        "status": report["status"], "errors": report["errors"], "warnings": report["warnings"],
        "report": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
