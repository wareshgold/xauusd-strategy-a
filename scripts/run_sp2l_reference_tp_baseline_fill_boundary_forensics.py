"""Reconstruct the temporal boundary between Reference TP and Baseline fill.

Research-only. Describes observed M1 events; does not infer or define
canonical fill/execution semantics.
"""
from __future__ import annotations
import argparse,json
from datetime import datetime,timezone
from pathlib import Path

def epoch(v):
    if v is None:return None
    if isinstance(v,(int,float)):return int(v)
    return int(datetime.fromisoformat(str(v).replace("Z","+00:00")).timestamp())

def iso(v):
    return datetime.fromtimestamp(v,timezone.utc).isoformat() if v is not None else None

def key(x):
    fp=x.get("fingerprint")
    return tuple(fp) if isinstance(fp,list) else (fp,)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--full-path",required=True)
    p.add_argument("--reconciliation",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    full=json.loads(Path(a.full_path).read_text(encoding="utf-8"))
    rec=json.loads(Path(a.reconciliation).read_text(encoding="utf-8"))
    target={key(r) for r in rec.get("rows",[]) if r.get("temporal_category")=="REFERENCE_TP_BEFORE_BASELINE_FILL"}
    rows=[]
    for row in full.get("rows",[]):
        if key(row) not in target: continue
        fp=row.get("fingerprint",[])
        direction=str(fp[0]) if fp else ""
        b=row.get("baseline",{}); r=row.get("reference",{})
        fill=epoch(b.get("fill_time")); activation=epoch(r.get("activation_time"))
        entry=b.get("entry"); sl=b.get("sl"); tp=r.get("tp")
        bars=row.get("path",{}).get("raw_m1",[])
        events=[]
        if activation is not None and fill is not None:
            for bar in bars:
                t=int(bar["time"])
                if t<activation or t>fill: continue
                h=bar.get("high"); l=bar.get("low")
                events.append({"time":t,"time_iso":iso(t),"open":bar.get("open"),"high":h,"low":l,"close":bar.get("close"),
                               "entry_touch":((l<=entry) if direction=="BUY" else (h>=entry)) if isinstance(entry,(int,float)) else None,
                               "reference_tp_touch":((h>=tp) if direction=="BUY" else (l<=tp)) if isinstance(tp,(int,float)) else None,
                               "baseline_sl_touch":((l<=sl) if direction=="BUY" else (h>=sl)) if isinstance(sl,(int,float)) else None})
        entry_touch_times=[x["time"] for x in events if x["entry_touch"]]
        tp_touch_times=[x["time"] for x in events if x["reference_tp_touch"]]
        first_entry=entry_touch_times[0] if entry_touch_times else None
        first_tp=tp_touch_times[0] if tp_touch_times else None
        rows.append({"fingerprint":list(fp),"direction":direction,
                     "reference_activation_time":r.get("activation_time"),
                     "baseline_fill_time":b.get("fill_time"),
                     "baseline_entry":entry,"reference_tp":tp,
                     "reference_tp_before_fill":first_tp is not None and first_tp<fill if fill is not None else None,
                     "entry_level_first_touch_between_activation_and_fill":iso(first_entry),
                     "reference_tp_first_touch_between_activation_and_fill":iso(first_tp),
                     "entry_touch_before_reference_tp":first_entry is not None and first_tp is not None and first_entry<first_tp,
                     "entry_touch_count_between_activation_and_fill":len(entry_touch_times),
                     "reference_tp_touch_count_between_activation_and_fill":len(tp_touch_times),
                     "boundary_m1_count":len(events),
                     "boundary_events":events})
    result={"status":"COMPLETE","research_only":True,"target_count":len(target),"rows_analyzed":len(rows),
            "rows":rows,
            "note":"Observed M1 boundary reconstruction only. It does not establish causality or canonical fill/execution semantics."}
    q=Path(a.output);q.parent.mkdir(parents=True,exist_ok=True)
    q.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"status":"COMPLETE","target_count":len(target),"rows_analyzed":len(rows)},indent=2))
if __name__=="__main__":main()
