"""Deterministic data-quality gate for SP2L MT5 matrix rows.

No broker session calendar is inferred. Weekend-only gaps are classified as
calendar closure. Non-weekend gaps remain unresolved unless an authoritative
external session source is supplied; recurring patterns are diagnostics only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class GapClassification:
    classification: str
    missing_minutes: int
    weekend_minutes: int
    non_weekend_minutes: int


def classify_gap(interval: dict[str, Any]) -> GapClassification:
    missing = int(interval.get("missing_minutes", 0))
    weekend = int(interval.get("calendar_weekend_minutes", 0))
    non_weekend = int(interval.get("non_weekend_minutes", max(0, missing - weekend)))

    if missing <= 0:
        return GapClassification("NO_GAP", 0, 0, 0)
    if non_weekend == 0:
        return GapClassification("WEEKEND_CLOSURE", missing, weekend, 0)
    return GapClassification("UNRESOLVED_DATA_GAP", missing, weekend, non_weekend)


def classify_row(row: dict[str, Any]) -> dict[str, Any]:
    intervals = row.get("gap_intervals", [])
    classified = [classify_gap(g) for g in intervals]
    unresolved = sum(g.non_weekend_minutes for g in classified if g.classification == "UNRESOLVED_DATA_GAP")
    weekend = sum(g.missing_minutes for g in classified if g.classification == "WEEKEND_CLOSURE")

    if unresolved:
        status = "DATA_QUALITY_UNRESOLVED"
    else:
        status = "PASS"

    return {
        "case_id": row["case_id"],
        "requested_symbol": row["requested_symbol"],
        "broker_symbol": row["broker_symbol"],
        "week_start_utc": row["week_start_utc"],
        "week_end_utc": row["week_end_utc"],
        "status": status,
        "weekend_closure_minutes": weekend,
        "unresolved_data_gap_minutes": unresolved,
        "gap_count": len(intervals),
        "gap_classifications": [
            {
                "classification": g.classification,
                "missing_minutes": g.missing_minutes,
                "weekend_minutes": g.weekend_minutes,
                "non_weekend_minutes": g.non_weekend_minutes,
            }
            for g in classified
        ],
    }


def evaluate_artifact(data: dict[str, Any]) -> dict[str, Any]:
    rows = [classify_row(r) for r in data["results"]]
    return {
        "status": "COMPLETE",
        "mode": "RESEARCH_MT5_MATRIX_DATA_QUALITY_GATE",
        "canonical": False,
        "policy": {
            "WEEKEND_CLOSURE": "allowed calendar closure; not treated as missing data",
            "UNRESOLVED_DATA_GAP": "non-weekend gap without authoritative session evidence",
            "RECURRING_CLOSURE_CANDIDATE": "diagnostic only; never auto-approved",
            "replay_rule": "DATA_QUALITY_UNRESOLVED rows must not be silently treated as complete",
        },
        "cases": len(rows),
        "pass_cases": sum(r["status"] == "PASS" for r in rows),
        "unresolved_cases": sum(r["status"] == "DATA_QUALITY_UNRESOLVED" for r in rows),
        "rows": rows,
    }
