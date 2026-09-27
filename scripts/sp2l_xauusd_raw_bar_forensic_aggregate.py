"""Aggregate XAUUSD raw-bar boundary forensic observations (research-only).

Consumes the JSON emitted by sp2l_xauusd_raw_bar_boundary_forensics.py and
produces a compact descriptive report. It never infers or approves broker
session/maintenance causes and never changes canonical strategy geometry.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


PATTERNS = (
    "EXACT_23:59_TO_01:00",
    "23:58_TO_01:00",
    "23:59_TO_00:59",
    "OTHER",
)


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def month_key(value: str) -> str:
    return dt(value).strftime("%Y-%m")


def weekday_key(value: str) -> str:
    return dt(value).strftime("%A")


def observed_minutes(row: dict) -> int | None:
    before = row.get("last_bar_before")
    after = row.get("first_bar_after")
    if not before or not after:
        return None
    return int((dt(after["time_utc"]) - dt(before["time_utc"])).total_seconds() // 60)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output")
    args = parser.parse_args()

    src = Path(args.input)
    data = json.loads(src.read_text(encoding="utf-8"))
    rows = data.get("results", [])

    pattern_counts = Counter(r.get("observed_boundary_pattern", "OTHER") for r in rows)
    weekday_counts = Counter(
        weekday_key(r["gap"]["start_utc"])
        for r in rows
        if r.get("gap", {}).get("start_utc")
    )
    month_counts = Counter(
        month_key(r["gap"]["start_utc"])
        for r in rows
        if r.get("gap", {}).get("start_utc")
    )
    length_counts = Counter(
        n for n in (observed_minutes(r) for r in rows) if n is not None
    )
    outliers = [
        {
            "case_id": r.get("case_id"),
            "gap_start_utc": r.get("gap", {}).get("start_utc"),
            "gap_end_utc": r.get("gap", {}).get("end_utc"),
            "last_bar_before_utc": (r.get("last_bar_before") or {}).get("time_utc"),
            "first_bar_after_utc": (r.get("first_bar_after") or {}).get("time_utc"),
            "pattern": r.get("observed_boundary_pattern"),
            "observed_boundary_minutes": observed_minutes(r),
        }
        for r in rows
        if r.get("observed_boundary_pattern") == "OTHER"
    ]

    report = {
        "status": "COMPLETE",
        "research_only": True,
        "session_cause": "UNRESOLVED",
        "session_approval": "NOT_ESTABLISHED",
        "source_artifact": str(src),
        "population": len(rows),
        "pattern_counts": {p: pattern_counts.get(p, 0) for p in PATTERNS},
        "weekday_counts": dict(sorted(weekday_counts.items())),
        "month_counts": dict(sorted(month_counts.items())),
        "observed_boundary_minutes_counts": {
            str(k): v for k, v in sorted(length_counts.items())
        },
        "outliers": outliers,
        "interpretation": [
            "The report is descriptive forensic evidence only.",
            "Recurring raw-bar boundary patterns do not establish broker session or maintenance cause.",
            "The 2026-09-07 non-rollover observation remains isolated as an outlier.",
            "No session closure is inferred, approved, or promoted to canonical data rules.",
        ],
    }

    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")

    print("XAUUSD RAW-BAR FORENSIC AGGREGATE")
    print("")
    print(f"population={report['population']}")
    print("pattern_counts:")
    for p in PATTERNS:
        print(f"  {p}={pattern_counts.get(p, 0)}")
    print("weekday_counts:")
    for k, v in sorted(weekday_counts.items()):
        print(f"  {k}={v}")
    print("month_counts:")
    for k, v in sorted(month_counts.items()):
        print(f"  {k}={v}")
    print("observed_boundary_minutes:")
    for k, v in sorted(length_counts.items()):
        print(f"  {k}={v}")
    print(f"outliers={len(outliers)}")
    for x in outliers:
        print(
            f"  {x['gap_start_utc']} -> {x['gap_end_utc']} | "
            f"{x['last_bar_before_utc']} -> {x['first_bar_after_utc']} | "
            f"{x['pattern']}"
        )
    print("")
    print("SESSION_CAUSE=UNRESOLVED")
    print("SESSION_APPROVAL=NOT_ESTABLISHED")
    print("research_only=true")
    print("status=COMPLETE")
    if args.output:
        print(f"artifact={args.output}")


if __name__ == "__main__":
    main()
