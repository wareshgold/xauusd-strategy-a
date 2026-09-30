"""
Forensic coverage audit for the exact MT5 Tester-exported M1 history CSV.
No strategy logic is applied. This only verifies temporal/data coverage.
"""
from __future__ import annotations
import argparse, csv, json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

def parse_epoch(v: str) -> int:
    return int(v.strip())

def fmt(e: int) -> str:
    return datetime.fromtimestamp(e, timezone.utc).isoformat().replace("+00:00","Z")

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--output-json", default="")
    args=p.parse_args()
    rows=[]
    with open(args.csv,"r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if "time_epoch_utc" not in (reader.fieldnames or []):
            raise ValueError("Missing time_epoch_utc column")
        for row in reader:
            rows.append(parse_epoch(row["time_epoch_utc"]))
    if not rows:
        raise ValueError("History CSV is empty")
    rows_sorted=sorted(rows)
    counts=Counter(datetime.fromtimestamp(e,timezone.utc).strftime("%Y-%m") for e in rows)
    report={
        "audit":"SP2L_TESTER_M1_HISTORY_COVERAGE",
        "source_csv":args.csv,
        "bars":len(rows),
        "unique_timestamps":len(set(rows)),
        "duplicate_timestamp_count":len(rows)-len(set(rows)),
        "first_bar_utc":fmt(rows_sorted[0]),
        "last_bar_utc":fmt(rows_sorted[-1]),
        "counts_by_month_utc":dict(sorted(counts.items())),
        "expected_window":{
            "start_utc":"2025-09-25T00:00:00Z",
            "end_utc":"2026-09-25T00:00:00Z",
            "expected_bars":94652,
        },
    }
    print("SP2L_TESTER_M1_HISTORY_COVERAGE")
    print(f"source_csv={args.csv}")
    print(f"bars={report['bars']}")
    print(f"unique_timestamps={report['unique_timestamps']}")
    print(f"duplicate_timestamp_count={report['duplicate_timestamp_count']}")
    print(f"first_bar_utc={report['first_bar_utc']}")
    print(f"last_bar_utc={report['last_bar_utc']}")
    print("counts_by_month_utc="+json.dumps(report["counts_by_month_utc"],sort_keys=True))
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        print(f"output_json={args.output_json}")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
