"""Aggregate case-level cross-symbol control evidence.

Research-only. Summarizes, per XAUUSD case, how many of seven FX controls
are empty, partial, or continuous over the exact XAUUSD gap interval.
"""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path

CONTROLS = ["USDJPY","EURJPY","GBPUSD","GBPJPY","EURUSD","USDCHF","USDCAD"]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--output", required=True)
    args=p.parse_args()
    d=json.loads(Path(args.input).read_text(encoding="utf-8"))
    rows=d["results"]
    case_counts=Counter()
    per_case=[]
    for row in rows:
        counts=Counter()
        for name in CONTROLS:
            c=row["controls"][name]
            if c["interval_empty"]:
                k="EMPTY"
            elif c["interval_continuous"]:
                k="CONTINUOUS"
            else:
                k="PARTIAL"
            counts[k]+=1
        if counts["EMPTY"]==7: cls="ALL_CONTROLS_EMPTY"
        elif counts["CONTINUOUS"]==7: cls="ALL_CONTROLS_CONTINUOUS"
        elif counts["PARTIAL"]==7: cls="ALL_CONTROLS_PARTIAL"
        elif counts["EMPTY"]==0 and counts["PARTIAL"]==0: cls="ALL_CONTROLS_CONTINUOUS"
        elif counts["EMPTY"]==0 and counts["CONTINUOUS"]==0: cls="ALL_CONTROLS_PARTIAL"
        else: cls="MIXED"
        case_counts[cls]+=1
        per_case.append({
            "xau_gap_start_utc":row["xau_gap_start_utc"],
            "xau_gap_end_utc":row["xau_gap_end_utc"],
            "xau_pattern":row.get("xau_pattern"),
            "control_counts":dict(counts),
            "case_class":cls,
        })
    report={
        "status":"COMPLETE",
        "research_only":True,
        "session_cause":"UNRESOLVED",
        "session_approval":"NOT_ESTABLISHED",
        "population":len(rows),
        "case_class_counts":dict(sorted(case_counts.items())),
        "per_case":per_case,
        "interpretation":[
            "This aggregate describes exact UTC interval coverage across controls.",
            "Mixed control behavior does not establish a broker session cause.",
            "No session closure or canonical data rule is inferred or approved.",
        ],
    }
    Path(args.output).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("XAUUSD CROSS-SYMBOL CASE-LEVEL AGGREGATE")
    print(f"population={len(rows)}")
    for k,v in sorted(case_counts.items()): print(f"{k}={v}")
    print("SESSION_CAUSE=UNRESOLVED")
    print("SESSION_APPROVAL=NOT_ESTABLISHED")
    print("research_only=true")
    print("status=COMPLETE")
    print(f"artifact={args.output}")

if __name__=="__main__":
    main()
