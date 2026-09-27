"""Join temporal-order and common-outcome forensic evidence case by case.

Research-only. No causal or canonical execution semantics are inferred.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def key(x):
    fp=x.get("fingerprint")
    return tuple(fp) if isinstance(fp,list) else (fp,)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--temporal",required=True)
    p.add_argument("--outcomes",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    t=load(a.temporal); o=load(a.outcomes)
    tm={key(r):r for r in t.get("rows",[])}
    om={key(r):r for r in o.get("rows",[])}
    rows=[]; counts={}; sums={}
    for k in sorted(set(tm)&set(om),key=str):
        tr=tm[k]; orow=om[k]
        d=orow.get("baseline",{}).get("r")
        rr=orow.get("reference",{}).get("r")
        dr=(float(rr)-float(d)) if isinstance(d,(int,float)) and isinstance(rr,(int,float)) else None
        cat=tr.get("category","MISSING_TEMPORAL")
        rec={"fingerprint":list(k),"temporal_category":cat,
             "baseline_fill_time":tr.get("baseline_fill_time"),
             "reference_activation_time":tr.get("reference_activation_time"),
             "reference_tp_first_touch":tr.get("reference_tp_first_touch"),
             "reference_tp_vs_baseline_fill_seconds":tr.get("reference_tp_vs_baseline_fill_seconds"),
             "baseline_r":d,"reference_r":rr,"r_delta":dr,
             "outcome_classification":orow.get("classification"),
             "outcome_differences":orow.get("differences",[])}
        rows.append(rec); counts[cat]=counts.get(cat,0)+1
        if isinstance(dr,(int,float)): sums[cat]=sums.get(cat,0.0)+dr
    result={"status":"COMPLETE","research_only":True,
            "temporal_rows":len(tm),"outcome_rows":len(om),"joined_rows":len(rows),
            "classification_counts":counts,"classification_r_delta":sums,
            "total_joined_r_delta":sum(sums.values()),
            "rows":rows,
            "note":"Case-level descriptive join of independent temporal and outcome forensics. This does not establish causality or canonical execution semantics."}
    q=Path(a.output);q.parent.mkdir(parents=True,exist_ok=True)
    q.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"status":"COMPLETE","joined_rows":len(rows),"classification_counts":counts,"classification_r_delta":sums,"total_joined_r_delta":sum(sums.values())},indent=2,ensure_ascii=False))
if __name__=="__main__":main()
