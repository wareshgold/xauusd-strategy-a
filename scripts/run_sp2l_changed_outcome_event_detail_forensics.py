"""Detailed descriptive report for changed-outcome first-event differences.

Reads the event-forensics JSON and emits compact per-case event details.
Research-only: no canonical execution semantics are inferred.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def event_summary(x):
    if not isinstance(x,dict): return {"status":"UNRESOLVED","reason":"missing_event_record"}
    if x.get("status")=="UNRESOLVED": return {"status":"UNRESOLVED","reason":x.get("reason")}
    b=x.get("bar")
    return {
        "event":x.get("event"),
        "time":x.get("time"),
        "bars_scanned":x.get("bars_scanned"),
        "bar":{
            "time":b.get("time") if isinstance(b,dict) else None,
            "time_utc":b.get("time_utc") if isinstance(b,dict) else None,
            "open":b.get("open") if isinstance(b,dict) else None,
            "high":b.get("high") if isinstance(b,dict) else None,
            "low":b.get("low") if isinstance(b,dict) else None,
            "close":b.get("close") if isinstance(b,dict) else None,
        } if isinstance(b,dict) else None
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    x=json.loads(Path(a.input).read_text(encoding="utf-8"))
    rows=[]
    for i,row in enumerate(x.get("rows",[]),1):
        if row.get("category") not in ("FIRST_EVENT_DIFFERENCE","UNRESOLVED"): continue
        be=event_summary(row.get("baseline_first_event"))
        re=event_summary(row.get("reference_first_event"))
        rows.append({
            "case":i,
            "fingerprint":row.get("fingerprint"),
            "category":row.get("category"),
            "differences":row.get("differences",[]),
            "baseline_r":row.get("baseline_r"),
            "reference_r":row.get("reference_r"),
            "r_delta":row.get("r_delta"),
            "baseline_first_event":be,
            "reference_first_event":re,
        })
    result={
        "status":"COMPLETE",
        "research_only":True,
        "input_target_count":x.get("target_count"),
        "selected_count":len(rows),
        "selected_category_counts":{
            "FIRST_EVENT_DIFFERENCE":sum(r["category"]=="FIRST_EVENT_DIFFERENCE" for r in rows),
            "UNRESOLVED":sum(r["category"]=="UNRESOLVED" for r in rows),
        },
        "source_r_delta":x.get("source_r_delta"),
        "rows":rows,
        "note":"Descriptive event/time/OHLC extraction only. The recorded context windows may not cover every minute between start and end; no absence of an event is treated as causal proof."
    }
    q=Path(a.output);q.parent.mkdir(parents=True,exist_ok=True)
    q.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({
        "status":"COMPLETE",
        "selected_count":len(rows),
        "selected_category_counts":result["selected_category_counts"],
        "output":str(q)
    },indent=2,ensure_ascii=False))
if __name__=="__main__": main()
