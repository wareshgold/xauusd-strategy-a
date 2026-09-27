"""Analyze full-path forensic output deterministically.

Research-only reconciliation of event pairs, timing, and R deltas.
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime
from pathlib import Path

def epoch(v):
    if v is None:
        return None
    if isinstance(v,(int,float)):
        return int(v)
    return int(datetime.fromisoformat(str(v).replace("Z","+00:00")).timestamp())

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    x=json.loads(Path(a.input).read_text(encoding="utf-8"))
    pair_counts={}
    pair_r={}
    timing=[]
    r_delta_sum=0.0
    rows_out=[]
    for row in x.get("rows",[]):
        if row.get("status") in ("ERROR","UNRESOLVED"):
            continue
        be=row.get("baseline",{}).get("first_event",{})
        re=row.get("reference",{}).get("first_event",{})
        bp=be.get("event"); rp=re.get("event")
        pair=f"{bp}->{rp}"
        pair_counts[pair]=pair_counts.get(pair,0)+1
        d=row.get("r_delta")
        if not isinstance(d,(int,float)):
            br=row.get("baseline_r"); rr=row.get("reference_r")
            if isinstance(br,(int,float)) and isinstance(rr,(int,float)):
                d=float(rr)-float(br)
        if isinstance(d,(int,float)):
            pair_r[pair]=pair_r.get(pair,0.0)+float(d)
            r_delta_sum+=float(d)
        bt=be.get("time"); rt=re.get("time")
        rec={
            "fingerprint":row.get("fingerprint"),
            "baseline_event":bp,
            "reference_event":rp,
            "baseline_event_time":bt,
            "reference_event_time":rt,
            "event_time_delta_seconds":abs(epoch(bt)-epoch(rt)) if bt and rt else None,
            "r_delta":d,
        }
        timing.append(rec)
        rows_out.append(rec)
    result={
        "status":"COMPLETE","research_only":True,
        "source_target_count":x.get("input_target_count"),
        "rows_with_valid_forensic_record":len(x.get("rows",[])),
        "rows_analyzed":len(rows_out),
        "event_pair_counts":pair_counts,
        "event_pair_r_delta":pair_r,
        "r_delta_sum":r_delta_sum,
        "rows":rows,
        "note":"Descriptive full-M1 reconciliation. R delta is taken from forensic row when present, otherwise reference_r-baseline_r. Event-pair association is not causal proof and does not define canonical execution semantics."
    }
    q=Path(a.output); q.parent.mkdir(parents=True,exist_ok=True)
    q.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({
        "status":"COMPLETE","rows_analyzed":len(rows_out),
        "event_pair_counts":pair_counts,
        "event_pair_r_delta":pair_r,
        "r_delta_sum":r_delta_sum
    },indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
