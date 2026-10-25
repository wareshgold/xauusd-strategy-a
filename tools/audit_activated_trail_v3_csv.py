#!/usr/bin/env python3
"""Read-only audit for activated-trailing proxy V3 trade CSVs.

Checks artifact identity and directional R arithmetic only. It does not validate
source fidelity, trailing activation, OHLC event ordering, fills, or canonical
Strategy A semantics. Input files are never edited.

Rows not marked CLOSED are treated as unresolved candidates: blank exit fields
are expected and are not misreported as invalid numeric data. The console output
is concise; --report-out optionally writes the full JSON report to a new file.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

REQUIRED_COLUMNS = {
    "strategy", "variant", "direction", "setup_time_utc", "entry_time_utc",
    "entry_proxy", "sl_initial", "target", "risk_price", "exit_time_utc",
    "exit_price", "exit_reason", "status", "r_multiple",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: missing CSV header")
        return list(reader.fieldnames), list(reader)


def as_float(row: dict[str, str], field: str, row_number: int) -> float:
    try:
        value = float(row[field])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"row {row_number}: invalid {field}={row.get(field)!r}") from exc
    if not math.isfinite(value):
        raise ValueError(f"row {row_number}: non-finite {field}={value!r}")
    return value


def audit(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"CSV not found: {path}")
    columns, rows = read_csv(path)
    missing = sorted(REQUIRED_COLUMNS - set(columns))
    if missing:
        raise ValueError(f"{path}: missing required columns: {missing}")

    variants: dict[str, int] = {}
    exit_reasons: dict[str, int] = {}
    statuses: dict[str, int] = {}
    positive_r_sl_rows: list[dict[str, Any]] = []
    r_mismatches: list[dict[str, Any]] = []
    invalid_rows: list[dict[str, Any]] = []
    unresolved_rows: list[dict[str, Any]] = []
    closed_rows = 0

    for row_number, row in enumerate(rows, start=2):
        variant = row.get("variant", "")
        reason = row.get("exit_reason", "")
        status = row.get("status", "").strip().upper()
        variants[variant] = variants.get(variant, 0) + 1
        exit_reasons[reason] = exit_reasons.get(reason, 0) + 1
        statuses[status] = statuses.get(status, 0) + 1

        if status != "CLOSED":
            unresolved_rows.append({
                "csv_row": row_number,
                "status": status,
                "exit_reason": reason,
                "exit_time_utc": row.get("exit_time_utc", ""),
                "exit_price_blank": not bool(row.get("exit_price", "").strip()),
                "r_multiple_blank": not bool(row.get("r_multiple", "").strip()),
            })
            if bool(row.get("exit_price", "").strip()) != bool(row.get("r_multiple", "").strip()):
                invalid_rows.append({
                    "csv_row": row_number,
                    "error": "non-CLOSED row has only one of exit_price/r_multiple populated",
                    "status": status,
                })
            continue

        closed_rows += 1
        try:
            entry = as_float(row, "entry_proxy", row_number)
            exit_price = as_float(row, "exit_price", row_number)
            risk = as_float(row, "risk_price", row_number)
            reported_r = as_float(row, "r_multiple", row_number)
            direction = row.get("direction", "").strip().upper()
            if risk <= 0:
                raise ValueError(f"row {row_number}: risk_price must be positive, got {risk}")
            if direction == "BUY":
                diagnostic_r = (exit_price - entry) / risk
            elif direction == "SELL":
                diagnostic_r = (entry - exit_price) / risk
            else:
                raise ValueError(f"row {row_number}: unsupported direction {direction!r}")

            if abs(diagnostic_r - reported_r) > 1e-5:
                r_mismatches.append({
                    "csv_row": row_number,
                    "direction": direction,
                    "entry_proxy": entry,
                    "exit_price": exit_price,
                    "risk_price": risk,
                    "reported_r": reported_r,
                    "diagnostic_r": round(diagnostic_r, 10),
                    "difference": round(reported_r - diagnostic_r, 10),
                })
            if reason.strip().upper() == "SL" and diagnostic_r > 1e-8:
                positive_r_sl_rows.append({
                    "csv_row": row_number,
                    "direction": direction,
                    "setup_time_utc": row.get("setup_time_utc", ""),
                    "entry_time_utc": row.get("entry_time_utc", ""),
                    "entry_proxy": entry,
                    "sl_initial": row.get("sl_initial", ""),
                    "exit_time_utc": row.get("exit_time_utc", ""),
                    "exit_price": exit_price,
                    "risk_price": risk,
                    "reported_r": reported_r,
                    "diagnostic_r": round(diagnostic_r, 10),
                    "note": "diagnostic flag only; moved stop or documented semantics may explain this",
                })
        except ValueError as exc:
            invalid_rows.append({"csv_row": row_number, "error": str(exc), "status": status})

    return {
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
        "columns": columns,
        "data_rows": len(rows),
        "closed_rows": closed_rows,
        "non_closed_unresolved_rows": len(unresolved_rows),
        "variants": variants,
        "exit_reasons": exit_reasons,
        "statuses": statuses,
        "directional_r_arithmetic_mismatch_count": len(r_mismatches),
        "directional_r_arithmetic_mismatches": r_mismatches,
        "sl_with_positive_directional_r_count": len(positive_r_sl_rows),
        "sl_with_positive_directional_r": positive_r_sl_rows,
        "invalid_closed_or_partially_populated_rows_count": len(invalid_rows),
        "invalid_rows": invalid_rows,
        "unresolved_rows": unresolved_rows,
        "interpretation_limit": (
            "Checks file identity and directional R arithmetic only. It does not establish "
            "source fidelity, trailing activation, fill behavior, intrabar OHLC ordering, "
            "stop/target precedence, or canonical rules."
        ),
    }


def concise(report: dict[str, Any]) -> dict[str, Any]:
    def one(file_report: dict[str, Any]) -> dict[str, Any]:
        return {
            "path": file_report["path"],
            "size_bytes": file_report["size_bytes"],
            "sha256": file_report["sha256"],
            "data_rows": file_report["data_rows"],
            "closed_rows": file_report["closed_rows"],
            "non_closed_unresolved_rows": file_report["non_closed_unresolved_rows"],
            "variants": file_report["variants"],
            "exit_reasons": file_report["exit_reasons"],
            "statuses": file_report["statuses"],
            "directional_r_arithmetic_mismatch_count": file_report["directional_r_arithmetic_mismatch_count"],
            "directional_r_arithmetic_mismatches_sample": file_report["directional_r_arithmetic_mismatches"][:10],
            "sl_with_positive_directional_r_count": file_report["sl_with_positive_directional_r_count"],
            "sl_with_positive_directional_r_sample": file_report["sl_with_positive_directional_r"][:10],
            "invalid_closed_or_partially_populated_rows_count": file_report["invalid_closed_or_partially_populated_rows_count"],
            "invalid_rows_sample": file_report["invalid_rows"][:10],
            "unresolved_rows_sample": file_report["unresolved_rows"][:10],
        }

    return {
        "audit_type": report["audit_type"],
        "files_byte_for_byte_equal": report["files_byte_for_byte_equal"],
        "same_sha256": report["same_sha256"],
        "same_size_bytes": report["same_size_bytes"],
        "same_data_rows": report["same_data_rows"],
        "file_a": one(report["file_a"]),
        "file_b": one(report["file_b"]),
        "full_report_path": report.get("full_report_path"),
        "interpretation_limit": report["file_a"]["interpretation_limit"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_a", type=Path, help="First CSV path")
    parser.add_argument("csv_b", type=Path, help="Second CSV path")
    parser.add_argument(
        "--report-out", type=Path,
        help="Optional path for full JSON report; must not already exist",
    )
    args = parser.parse_args()

    report_a = audit(args.csv_a)
    report_b = audit(args.csv_b)
    bytes_equal = args.csv_a.read_bytes() == args.csv_b.read_bytes()
    report = {
        "audit_type": "read_only_activated_trail_v3_csv_diagnostic",
        "files_byte_for_byte_equal": bytes_equal,
        "same_sha256": report_a["sha256"] == report_b["sha256"],
        "same_size_bytes": report_a["size_bytes"] == report_b["size_bytes"],
        "same_data_rows": report_a["data_rows"] == report_b["data_rows"],
        "file_a": report_a,
        "file_b": report_b,
    }
    if args.report_out:
        if args.report_out.exists():
            raise FileExistsError(f"Refusing to overwrite existing report: {args.report_out}")
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        report["full_report_path"] = str(args.report_out.resolve())

    print(json.dumps(concise(report), indent=2, ensure_ascii=False))
    return 0 if bytes_equal else 2


if __name__ == "__main__":
    raise SystemExit(main())
