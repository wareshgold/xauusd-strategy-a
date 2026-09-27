"""Aggregate Reference-TP/Baseline-fill boundary observations.

Research-only. No causal or canonical execution semantics are inferred.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True); p.add_argument("--output",required=True)
    a=p.parse_args()
    d=json.loads(Path(a.input).read_text(encoding="utf-8"))
    rows=d.get("rows",[])
    cats={"ENTRY_BEFORE_TP":0,"TP_BEFORE_ENTRY":0,"NO_ENTRY_TOUCH":0,"SAME_M1":0,"UNRESOLVED":0}
    sums={}; deltas=[]; gaps=[]
    for r in rows:
        e=r.get("entry_level_first_touch_between_activation_and_fill")
        t=r.get("reference_tp_first_touch_between_activation_and_fill")
        if e is None and t is None: cat="NO_ENTRY_TOUCH"
        elif e is None: cat="NO_ENTRY_TOUCH"
        elif t is None: cat="ENTRY_BEFORE_TP"
        elif e==t: cat="SAME_M1"
        elif e<t: cat="ENTRY_BEFORE_TP"
        else: cat="TP_BEFORE_ENTRY"
        cats[cat]=cats.get(cat,0)+1
        dr=r.get("r_delta")
        if isinstance(dr,(int,float)):
            sums[cat]=sums.get(cat,0.0)+float(dr); deltas.append(float(dr))
        # timestamps are ISO strings; use provided temporal delta where available
        gap=r.get("reference_tp_vs_baseline_fill_seconds")
        if isinstance(gap,(int,float)): gaps.append(float(gap))
    result={"status":"COMPLETE","research_only":True,"rows_analyzed":len(rows),
            "boundary_classification_counts":cats,
            "boundary_classification_r_delta":sums,
            "r_delta_sum":sum(deltas),
            "tp_vs_baseline_fill_seconds":{"count":len(gaps),
                "min":min(gaps) if gaps else None,"max":max(gaps) if gaps else None,
                "mean":sum(gaps)/len(gaps) if gaps else None},
            "note":"Descriptive aggregation of observed M1 boundary fields. Missing Entry touch is not interpreted as proof of any fill rule; no causal or canonical execution semantics are inferred."}
    q=Path(a.output);q.parent.mkdir(parents=True,exist_ok=True)
    q.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__": main()
