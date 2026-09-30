"""
Forensic coverage audit for the frozen SP2L RR1 / Trail0 population.

This audit does not evaluate strategy performance and does not alter the source CSV.
It answers one question: where in time are the 1480 exported trades actually located?

Reports:
- minimum/maximum setup and entry timestamps
- counts by UTC calendar month for setup and entry
- first/last 20 entry timestamps
- counts at/after each frozen temporal boundary
- distinct years/months represented
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


FROZEN_START = "2025-09-25T00:00:00Z"
FROZEN_END = "2026-09-25T00:00:00Z"
BOUNDARIES = (
    "2025-12-25T00:00:00Z",
    "2026-03-25T00:00:00Z",
    "2026-06-25T00:00:00Z",
    "2026-09-25T00:00:00Z",
)


def parse_utc(value: str) -> datetime:
    value = value.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        dt = datetime.strptime(value, "%Y.%m.%d %H:%M:%S")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def fmt(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def load(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"signal_id", "setup_time_utc", "entry_time_utc"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        return list(reader)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--output-json", default="")
    args = p.parse_args()

    rows = load(args.csv)
    parsed = [
        {
            "signal_id": r["signal_id"].strip(),
            "setup": parse_utc(r["setup_time_utc"]),
            "entry": parse_utc(r["entry_time_utc"]),
        }
        for r in rows
    ]

    entry_counter = Counter(x["entry"].strftime("%Y-%m") for x in parsed)
    setup_counter = Counter(x["setup"].strftime("%Y-%m") for x in parsed)
    entries = sorted(parsed, key=lambda x: (x["entry"], x["signal_id"]))
    boundaries = {
        b: sum(x["entry"] >= parse_utc(b) for x in parsed)
        for b in BOUNDARIES
    }

    report = {
        "audit": "SP2L_BASELINE_POPULATION_COVERAGE",
        "source_csv": args.csv,
        "frozen_interval": {"start_utc": FROZEN_START, "end_utc": FROZEN_END},
        "population": len(parsed),
        "entry_time": {
            "min_utc": fmt(entries[0]["entry"]) if entries else None,
            "max_utc": fmt(entries[-1]["entry"]) if entries else None,
            "distinct_months": sorted(entry_counter),
            "counts_by_month_utc": dict(sorted(entry_counter.items())),
        },
        "setup_time": {
            "min_utc": fmt(min(x["setup"] for x in parsed)) if parsed else None,
            "max_utc": fmt(max(x["setup"] for x in parsed)) if parsed else None,
            "distinct_months": sorted(setup_counter),
            "counts_by_month_utc": dict(sorted(setup_counter.items())),
        },
        "entry_boundary_counts": boundaries,
        "first_20_entries": [
            {"signal_id": x["signal_id"], "entry_time_utc": fmt(x["entry"])}
            for x in entries[:20]
        ],
        "last_20_entries": [
            {"signal_id": x["signal_id"], "entry_time_utc": fmt(x["entry"])}
            for x in entries[-20:]
        ],
    }

    print("SP2L_BASELINE_POPULATION_COVERAGE")
    print(f"source_csv={args.csv}")
    print(f"population={len(parsed)}")
    print(f"entry_min={report['entry_time']['min_utc']}")
    print(f"entry_max={report['entry_time']['max_utc']}")
    print("entry_counts_by_month_utc=" + json.dumps(report["entry_time"]["counts_by_month_utc"], sort_keys=True))
    print("setup_counts_by_month_utc=" + json.dumps(report["setup_time"]["counts_by_month_utc"], sort_keys=True))
    print("entry_boundary_counts=" + json.dumps(boundaries, sort_keys=True))
    print("first_entry=" + json.dumps(report["first_20_entries"][0] if entries else None))
    print("last_entry=" + json.dumps(report["last_20_entries"][-1] if entries else None))

    if args.output_json:
        Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"output_json={args.output_json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
