"""Temporal clustering of cross-symbol XAUUSD gap cases.

Research-only. Identifies the exact case classes, XAUUSD interval state, and
control EMPTY counts by weekday/hour/month. No causal/session inference.
"""
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path

CONTROLS=["USDJPY","EURJPY","GBPUSD","GBPJPY","EURUSD","USDCHF","USDCAD"]

def dt(s):
    return datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(timezone.utc)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--output",required=True)
    args=p.parse_args()
    d=json.loads(Path(args.input).read_text(encoding="utf-8"))
    rows=d["results"]
    classes=Counter()
    xau_states=Counter()
    by_weekday=defaultdict(Counter)
    by_hour=defaultdict(Counter)
    by_month=defaultdict(Counter)
    special=[]
    for row in rows:
        xau=dt(row["xau_gap_start_utc"])
        controls=[row["controls"][n] for n in CONTROLS]
        empty=sum(c["interval_empty"] for c in controls)
        partial=sum((not c["interval_empty"]) and (not c["interval_continuous"]) for c in controls)
        continuous=sum(c["interval_continuous"] for c in controls)
        cls=("ALL_CONTROLS_EMPTY" if empty==7 else
             "ALL_CONTROLS_CONTINUOUS" if continuous==7 else
             "ALL_CONTROLS_PARTIAL" if partial==7 else "MIXED")
        xau_state="XAU_GAP_EMPTY" if not row["xau_pattern"] else "XAU_FORENSIC_GAP"
        classes[cls]+=1
        xau_states[xau_state]+=1
        by_weekday[xau.strftime("%A")][cls]+=1
        by_hour[xau.strftime("%H:00")][cls]+=1
        by_month[xau.strftime("%Y-%m")][cls]+=1
        if cls!="MIXED":
            special.append({
                "start":row["xau_gap_start_utc"],
                "end":row["xau_gap_end_utc"],
                "class":cls,
                "control_empty_count":empty,
                "control_partial_count":partial,
                "control_continuous_count":continuous,
            })
    report={
      "status":"COMPLETE","research_only":True,
      "session_cause":"UNRESOLVED","session_approval":"NOT_ESTABLISHED",
      "population":len(rows),
      "class_counts":dict(sorted(classes.items())),
      "xau_states":dict(sorted(xau_states.items())),
      "weekday_clusters":{k:dict(sorted(v.items())) for k,v in sorted(by_weekday.items())},
      "hour_clusters":{k:dict(sorted(v.items())) for k,v in sorted(by_hour.items())},
      "month_clusters":{k:dict(sorted(v.items())) for k,v in sorted(by_month.items())},
      "non_mixed_cases":special,
      "interpretation":[
        "Temporal clustering is descriptive forensic evidence only.",
        "Concentration by weekday, hour, or month does not establish session cause.",
        "No session closure, maintenance rule, or canonical data rule is inferred.",
      ]
    }
    Path(args.output).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("XAUUSD CROSS-SYMBOL TEMPORAL CLUSTER")
    print(f"population={len(rows)}")
    for k,v in sorted(classes.items()): print(f"{k}={v}")
    print("NON_MIXED_CASES")
    for x in special: print(f'{x["class"]} | {x["start"]} -> {x["end"]}')
    print("SESSION_CAUSE=UNRESOLVED")
    print("SESSION_APPROVAL=NOT_ESTABLISHED")
    print("research_only=true")
    print("status=COMPLETE")
    print(f"artifact={args.output}")
if __name__=="__main__": main()
