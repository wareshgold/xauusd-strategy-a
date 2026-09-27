"""Deterministic descriptive event scan for the 18 changed-outcome M1 paths.

Uses only recorded M1 OHLC and already-recorded trade levels/timestamps.
Research-only: no canonical execution semantics are inferred.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from datetime import datetime

def ep(v):
    if v is None:return None
    if isinstance(v,(int,float)):return int(v)
    return int(datetime.fromisoformat(str(v).replace("Z","+00:00")).timestamp())

def first_event(bars,start,end,direction,sl,tp):
    if not isinstance(sl,(int,float)) or not isinstance(tp,(int,float)):
        return {"status":"UNRESOLVED","reason":"invalid_levels"}
    s=ep(start); e=ep(end)
    if s is None:return {"status":"UNRESOLVED","reason":"start_time_missing"}
    eligible=[b for b in bars if b["time"]>=s and (e is None or b["time"]<=e)]
    for b in eligible:
        sl_hit=b["low"]<=sl if direction=="BUY" else b["high"]>=sl
        tp_hit=b["high"]>=tp if direction=="BUY" else b["low"]<=tp
        if sl_hit and tp_hit:ev="BOTH_SAME_M1"
        elif sl_hit:ev="SL_TOUCH"
        elif tp_hit:ev="TP_TOUCH"
        else:continue
        return {"event":ev,"time":b["time_utc"],"bar":b}
    return {"event":"NO_LEVEL_TOUCH_IN_PATH","bars_scanned":len(eligible)}

def direction_of(fp):
    if isinstance(fp,str):return fp.split("|")[0]
    if isinstance(fp,list) and fp:return str(fp[0])
    return None

def main():
    p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--output",required=True);a=p.parse_args()
    x=json.loads(Path(a.input).read_text(encoding="utf-8"));out=[];cat={};rsum={}
    for row in x["rows"]:
        b=row["baseline"];r=row["reference"];allbars={}
        for key in ("around_baseline_fill","around_baseline_exit","around_reference_activation","around_reference_exit"):
            for z in row.get("m1",{}).get(key,[]):allbars[z["time"]]=z
        bars=[allbars[k] for k in sorted(allbars)]
        direction=direction_of(row["fingerprint"])
        if direction not in ("BUY","SELL"):
            be=re={"status":"UNRESOLVED","reason":"direction_missing_or_unknown"};c="UNRESOLVED"
        else:
            be=first_event(bars,b.get("fill_time"),b.get("exit_time"),direction,b.get("sl"),b.get("tp"))
            re=first_event(bars,r.get("activation_time"),r.get("exit_time"),direction,r.get("sl"),r.get("tp"))
            if be.get("status")=="UNRESOLVED" or re.get("status")=="UNRESOLVED":c="UNRESOLVED"
            elif be.get("event")=="BOTH_SAME_M1" or re.get("event")=="BOTH_SAME_M1":c="SAME_BAR"
            elif be.get("event")=="NO_LEVEL_TOUCH_IN_PATH" or re.get("event")=="NO_LEVEL_TOUCH_IN_PATH":c="PATH_INCOMPLETE"
            elif be.get("event")!=re.get("event"):c="FIRST_EVENT_DIFFERENCE"
            else:c="SAME_FIRST_EVENT"
        cat[c]=cat.get(c,0)+1;bd=b.get("r");rd=r.get("r")
        if isinstance(bd,(int,float)) and isinstance(rd,(int,float)):rsum[c]=rsum.get(c,0.0)+float(rd)-float(bd)
        out.append({"fingerprint":row["fingerprint"],"differences":row.get("differences",[]),"category":c,"baseline_first_event":be,"reference_first_event":re,"baseline_r":bd,"reference_r":rd,"r_delta":float(rd)-float(bd) if isinstance(bd,(int,float)) and isinstance(rd,(int,float)) else None})
    result={"status":"COMPLETE","research_only":True,"target_count":len(out),"category_counts":cat,"category_r_delta":rsum,"source_r_delta":x.get("source_r_delta"),"rows":out,"note":"Descriptive M1 OHLC scan only; no canonical execution semantics inferred."}
    q=Path(a.output);q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"status":"COMPLETE","target_count":len(out),"category_counts":cat,"category_r_delta":rsum},indent=2,ensure_ascii=False))
if __name__=="__main__":main()
