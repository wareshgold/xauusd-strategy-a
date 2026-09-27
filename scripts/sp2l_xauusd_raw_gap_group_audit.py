"""Group and audit XAUUSD raw-M1 gap cases.

Research-only. Separates rollover-like cases from the isolated OTHER case and
measures exact raw boundary behavior. It does not infer session cause or
promote a normalization rule.
"""
from __future__ import annotations
import argparse, json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

def dt(s):
    return datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(timezone.utc)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--output",required=True)
    args=p.parse_args()
    d=json.loads(Path(args.input).read_text(encoding="utf-8"))
    rows=d.get("results", [])
    groups=defaultdict(list)
    for r in rows:
        pattern=r.get("observed_boundary_pattern","OTHER")
        groups[pattern].append(r)

    summaries={}
    for pattern,items in sorted(groups.items()):
        starts=Counter(dt(x["gap"]["start_utc"]).strftime("%H:%M") for x in items)
        ends=Counter(dt(x["gap"]["end_utc"]).strftime("%H:%M") for x in items)
        summaries[pattern]={
            "count":len(items),
            "gap_start_utc_minute_counts":dict(sorted(starts.items())),
            "gap_end_utc_minute_counts":dict(sorted(ends.items())),
            "cases":[{
                "gap_start_utc":x["gap"]["start_utc"],
                "gap_end_utc":x["gap"]["end_utc"],
                "last_bar_before_utc":x["last_bar_before_utc"],
                "first_bar_after_utc":x["first_bar_after_utc"],
                "observed_boundary_minutes":x["observed_boundary_minutes"],
            } for x in items],
        }

    report={
        "status":"COMPLETE",
        "research_only":True,
        "session_cause":"UNRESOLVED",
        "session_approval":"NOT_ESTABLISHED",
        "population":len(rows),
        "groups":summaries,
        "interpretation":[
            "Grouping is descriptive forensic evidence only.",
            "Rollover-like timestamp recurrence does not establish broker session cause.",
            "The OTHER group is retained separately and is not normalized into rollover.",
            "No session closure or canonical data rule is inferred or approved.",
        ],
    }
    Path(args.output).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("XAUUSD RAW-GAP GROUP AUDIT")
    print(f"population={len(rows)}")
    for k,v in summaries.items():
        print(f"{k}={v['count']}")
        print("  starts=" + ", ".join(f"{a}:{b}" for a,b in v["gap_start_utc_minute_counts"].items()))
        print("  ends=" + ", ".join(f"{a}:{b}" for a,b in v["gap_end_utc_minute_counts"].items()))
    print("SESSION_CAUSE=UNRESOLVED")
    print("SESSION_APPROVAL=NOT_ESTABLISHED")
    print("research_only=true")
    print("status=COMPLETE")
    print(f"artifact={args.output}")

if __name__=="__main__":
    main()
