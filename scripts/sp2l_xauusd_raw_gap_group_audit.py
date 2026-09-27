"""Group and audit XAUUSD raw-M1 gap cases.

Research-only. Consumes the actual raw-forensics schema without normalizing
rollover-like observations or the isolated OTHER case.
"""
from __future__ import annotations
import argparse, json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

def dt(s):
    return datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(timezone.utc)

def get_gap(row): return row.get("gap", row)
def get_pattern(row): return row.get("observed_boundary_pattern") or row.get("pattern") or "OTHER"
def get_time(value):
    if isinstance(value, dict): return value.get("time_utc") or value.get("time")
    return value

def main():
    p=argparse.ArgumentParser(); p.add_argument("input"); p.add_argument("--output",required=True); args=p.parse_args()
    data=json.loads(Path(args.input).read_text(encoding="utf-8")); rows=data.get("results",[])
    groups=defaultdict(list)
    for row in rows: groups[get_pattern(row)].append(row)
    summaries={}
    for pattern,items in sorted(groups.items()):
        starts=Counter(dt(get_gap(x)["start_utc"]).strftime("%H:%M") for x in items)
        ends=Counter(dt(get_gap(x)["end_utc"]).strftime("%H:%M") for x in items)
        cases=[]
        for x in items:
            g=get_gap(x)
            cases.append({"gap_start_utc":g["start_utc"],"gap_end_utc":g["end_utc"],
                          "last_bar_before_utc":get_time(x.get("last_bar_before")) or x.get("last_bar_before_utc"),
                          "first_bar_after_utc":get_time(x.get("first_bar_after")) or x.get("first_bar_after_utc"),
                          "observed_boundary_minutes":x.get("observed_boundary_minutes")})
        summaries[pattern]={"count":len(items),"gap_start_utc_minute_counts":dict(sorted(starts.items())),
                           "gap_end_utc_minute_counts":dict(sorted(ends.items())),"cases":cases}
    report={"status":"COMPLETE","research_only":True,"session_cause":"UNRESOLVED",
            "session_approval":"NOT_ESTABLISHED","population":len(rows),"groups":summaries,
            "interpretation":["Grouping is descriptive forensic evidence only.",
            "Rollover-like timestamp recurrence does not establish broker session cause.",
            "The OTHER group is retained separately and is not normalized into rollover.",
            "No session closure or canonical data rule is inferred or approved."]}
    Path(args.output).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("XAUUSD RAW-GAP GROUP AUDIT"); print(f"population={len(rows)}")
    for k,v in summaries.items():
        print(f"{k}={v['count']}"); print("  starts=" + ", ".join(f"{a}:{b}" for a,b in v["gap_start_utc_minute_counts"].items())); print("  ends=" + ", ".join(f"{a}:{b}" for a,b in v["gap_end_utc_minute_counts"].items()))
    print("SESSION_CAUSE=UNRESOLVED"); print("SESSION_APPROVAL=NOT_ESTABLISHED"); print("research_only=true"); print("status=COMPLETE"); print(f"artifact={args.output}")
if __name__=="__main__": main()