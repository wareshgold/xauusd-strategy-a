"""Analyze full-path forensic output deterministically.

Aggregates first-event pairs, timing, and R deltas. Research-only.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path\nfrom datetime import datetime\n\ndef epoch(v):\n    if v is None:return None\n    if isinstance(v,(int,float)):return int(v)\n    return int(datetime.fromisoformat(str(v).replace("Z","+00:00")).timestamp())\n

def main():
    p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--output",required=True);a=p.parse_args()
    x=json.loads(Path(a.input).read_text(encoding="utf-8"))
    pair_counts={};pair_r={};timing=[]
    for row in x.get("rows",[]):
        if row.get("status") in ("ERROR","UNRESOLVED"): continue
        be=row.get("baseline",{}).get("first_event",{});re=row.get("reference",{}).get("first_event",{})
        bp=be.get("event");rp=re.get("event")
        pair=f"{bp}->{rp}"
        pair_counts[pair]=pair_counts.get(pair,0)+1
        d=row.get("r_delta")
        if isinstance(d,(int,float)):pair_r[pair]=pair_r.get(pair,0.0)+float(d)
        bt=be.get("time");rt=re.get("time")
        if bt and rt: timing.append({"fingerprint":row.get("fingerprint"),"baseline_event":bp,"reference_event":rp,"baseline_event_time":bt,"reference_event_time":rt,"event_time_delta_seconds":abs(epoch(bt)-epoch(rt))})
    result={"status":"COMPLETE","research_only":True,"rows_analyzed":len(timing),"event_pair_counts":pair_counts,"event_pair_r_delta":pair_r,"r_delta_sum":sum(v for v in pair_r.values()),"rows":timing,"note":"Descriptive aggregation of full MT5 M1 path forensic output. Event-pair association is not causal proof and does not define canonical execution semantics."}
    q=Path(a.output);q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"status":"COMPLETE","rows_analyzed":len(timing),"event_pair_counts":pair_counts,"event_pair_r_delta":pair_r},indent=2,ensure_ascii=False))
if __name__=="__main__":main()
