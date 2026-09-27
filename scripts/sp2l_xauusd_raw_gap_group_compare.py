"""Compare XAUUSD raw gap boundary groups without inferring session cause.

Research-only. Compares the two rollover-like groups and the OTHER outlier.
"""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--output",required=True)
    a=p.parse_args()
    d=json.loads(Path(a.input).read_text(encoding="utf-8"))
    groups=d.get("groups",{})
    out={}
    for name,g in groups.items():
        cases=g.get("cases",[])
        out[name]={
            "count":len(cases),
            "gap_start_minutes":dict(Counter(x["gap_start_utc"][11:16] for x in cases)),
            "gap_end_minutes":dict(Counter(x["gap_end_utc"][11:16] for x in cases)),
            "observed_boundary_minutes":dict(Counter(str(x["observed_boundary_minutes"]) for x in cases)),
            "boundary_examples":cases[:5],
        }
    report={
        "status":"COMPLETE","research_only":True,
        "session_cause":"UNRESOLVED","session_approval":"NOT_ESTABLISHED",
        "population":d.get("population",0),"groups":out,
        "interpretation":[
            "This comparison is descriptive forensic evidence only.",
            "The 23:58_TO_01:00 and EXACT_23:59_TO_01:00 groups are retained as distinct observed patterns.",
            "The OTHER group remains isolated and is not normalized into rollover.",
            "No broker session, maintenance cause, closure rule, or canonical data rule is inferred."
        ]
    }
    Path(a.output).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("XAUUSD RAW-GAP GROUP COMPARISON")
    print(f"population={report['population']}")
    for k,v in out.items():
        print(f"{k}={v['count']}")
        print("  starts=" + ", ".join(f"{a}:{b}" for a,b in v["gap_start_minutes"].items()))
        print("  ends=" + ", ".join(f"{a}:{b}" for a,b in v["gap_end_minutes"].items()))
        print("  boundaries=" + ", ".join(f"{a}:{b}" for a,b in v["observed_boundary_minutes"].items()))
    print("SESSION_CAUSE=UNRESOLVED")
    print("SESSION_APPROVAL=NOT_ESTABLISHED")
    print("research_only=true")
    print("status=COMPLETE")
    print(f"artifact={a.output}")

if __name__=="__main__":
    main()
