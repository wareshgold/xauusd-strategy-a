"""Analyze temporal ordering of Reference TP versus Baseline fill.

Research-only. Uses retained raw MT5 M1 bars from the full-path forensic
artifact. Does not define canonical fill or execution semantics.
"""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

def epoch(v):
    if v is None: return None
    if isinstance(v,(int,float)): return int(v)
    return int(datetime.fromisoformat(str(v).replace("Z","+00:00")).timestamp())

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True); p.add_argument("--output",required=True)
    a=p.parse_args()
    x=json.loads(Path(a.input).read_text(encoding="utf-8"))
    rows=[]; counts={}; r_sums={}
    for row in x.get("rows",[]):
        if row.get("status") in ("ERROR","UNRESOLVED"): continue
        b=row.get("baseline",{}); r=row.get("reference",{})
        bars=row.get("path",{}).get("raw_m1",[])
        fp=row.get("fingerprint")
        direction=str(fp[0]) if isinstance(fp,list) and fp else str(fp or "").split("|")[0]
        fill=epoch(b.get("fill_time"))
        activation=epoch(r.get("activation_time"))
        if fill is None or activation is None:
            cat="MISSING_BOUNDARY"; rec={"fingerprint":fp,"category":cat}
        else:
            ref_tp=None; ref_sl=None; base_tp=None; base_sl=None
            for bar in bars:
                t=int(bar["time"])
                if ref_tp is None and ((direction=="BUY" and bar["high"]>=r.get("tp")) or (direction=="SELL" and bar["low"]<=r.get("tp"))): ref_tp=t
                if ref_sl is None and ((direction=="BUY" and bar["low"]<=r.get("sl")) or (direction=="SELL" and bar["high"]>=r.get("sl"))): ref_sl=t
                if base_tp is None and ((direction=="BUY" and bar["high"]>=b.get("tp")) or (direction=="SELL" and bar["low"]<=b.get("tp"))): base_tp=t
                if base_sl is None and ((direction=="BUY" and bar["low"]<=b.get("sl")) or (direction=="SELL" and bar["high"]>=b.get("sl"))): base_sl=t
            if ref_tp is None: cat="REFERENCE_TP_NOT_FOUND"
            elif ref_tp < fill: cat="REFERENCE_TP_BEFORE_BASELINE_FILL"
            elif ref_tp == fill: cat="REFERENCE_TP_ON_BASELINE_FILL_M1"
            else: cat="REFERENCE_TP_AFTER_BASELINE_FILL"
            d=row.get("r_delta")
            if not isinstance(d,(int,float)):
                br,rr=b.get("r"),r.get("r")
                d=float(rr)-float(br) if isinstance(br,(int,float)) and isinstance(rr,(int,float)) else None
            rec={"fingerprint":fp,"baseline_fill_time":b.get("fill_time"),"reference_activation_time":r.get("activation_time"),
                 "reference_tp_first_touch":datetime.fromtimestamp(ref_tp,timezone.utc).isoformat() if ref_tp is not None else None,
                 "reference_sl_first_touch":datetime.fromtimestamp(ref_sl,timezone.utc).isoformat() if ref_sl is not None else None,
                 "baseline_tp_first_touch":datetime.fromtimestamp(base_tp,timezone.utc).isoformat() if base_tp is not None else None,
                 "baseline_sl_first_touch":datetime.fromtimestamp(base_sl,timezone.utc).isoformat() if base_sl is not None else None,
                 "reference_tp_vs_baseline_fill_seconds":ref_tp-fill if ref_tp is not None else None,
                 "category":cat,"baseline_r":b.get("r"),"reference_r":r.get("r"),"r_delta":d}
        rows.append(rec); counts[cat]=counts.get(cat,0)+1
        d=rec.get("r_delta")
        if isinstance(d,(int,float)): r_sums[cat]=r_sums.get(cat,0.0)+float(d)
    result={"status":"COMPLETE","research_only":True,"input_target_count":x.get("input_target_count"),
            "rows_analyzed":len(rows),"classification_counts":counts,"classification_r_delta":r_sums,
            "rows":rows,"note":"Descriptive temporal ordering only; no causal or canonical execution semantics are inferred."}
    q=Path(a.output); q.parent.mkdir(parents=True,exist_ok=True)
    q.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"status":"COMPLETE","rows_analyzed":len(rows),"classification_counts":counts,"classification_r_delta":r_sums},indent=2,ensure_ascii=False))
if __name__=="__main__": main()
