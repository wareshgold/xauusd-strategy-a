"""Classify the 18 common SP2L V2 result-changing cases from M1 forensic output.

Conservative descriptive classification only. It never infers canonical semantics.
"""
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def classify(row):
    d=set(row.get("differences",[])); b=row["baseline"]; r=row["reference"]
    if "RESULT" not in d and "R" not in d: return "OTHER"
    bw=b.get("fill_time"); rw=r.get("activation_time")
    if bw is None or rw is None: return "UNRESOLVED"
    # Conservative: timing is only a candidate cause when fill timestamps differ.
    if bw != rw:
        # Same-bar evidence: exit is on activation/fill bar for either side.
        if (b.get("exit_time") is not None and b.get("exit_time")==bw) or (r.get("exit_time") is not None and r.get("exit_time")==rw):
            return "SAME_BAR"
        if row.get("mt5_context",{}).get("gap_between_baseline_fill_and_exit",0)>0 or row.get("mt5_context",{}).get("gap_between_reference_fill_and_exit",0)>0:
            return "DATA_GAP"
        if b.get("exit_time") != r.get("exit_time") or b.get("exit_reason") != r.get("exit_reason"):
            return "ENTRY_TIMING_CAUSED_OUTCOME_CHANGE"
        return "ENTRY_TIMING_CAUSED_OUTCOME_CHANGE"
    if b.get("exit_time") != r.get("exit_time") or b.get("exit_reason") != r.get("exit_reason"):
        return "EXIT_TIMING_CAUSED_OUTCOME_CHANGE"
    return "OTHER"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    x=load(a.input); rows=x["rows"]; counts=Counter(); by=defaultdict(float); details=[]
    for row in rows:
        c=classify(row); counts[c]+=1
        br=row["baseline"].get("r"); rr=row["reference"].get("r")
        if isinstance(br,(int,float)) and isinstance(rr,(int,float)):
            by[c]+=float(rr)-float(br)
        details.append({"fingerprint":row["fingerprint"],"classification":c,"differences":row.get("differences",[]),
                        "baseline_r":br,"reference_r":rr,"r_delta":(float(rr)-float(br)) if isinstance(br,(int,float)) and isinstance(rr,(int,float)) else None,
                        "baseline_fill_time":row["baseline"].get("fill_time"),"reference_activation_time":row["reference"].get("activation_time"),
                        "baseline_exit_time":row["baseline"].get("exit_time"),"reference_exit_time":row["reference"].get("exit_time"),
                        "baseline_exit_reason":row["baseline"].get("exit_reason"),"reference_exit_reason":row["reference"].get("exit_reason")})
    out={"status":"COMPLETE","research_only":True,"input_target_count":len(rows),
         "category_counts":dict(counts),"category_r_delta":dict(by),
         "sum_classified_r_delta":sum(by.values()),
         "reported_source_r_delta":x.get("r_delta_reported"),
         "reconciliation_note":"This classifier is deliberately conservative and descriptive. Category assignment is not a canonical fill/exit decision.",
         "details":details}
    q=Path(a.output); q.parent.mkdir(parents=True,exist_ok=True); q.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({k:out[k] for k in ("status","input_target_count","category_counts","category_r_delta","sum_classified_r_delta","reported_source_r_delta")},indent=2,ensure_ascii=False))
if __name__=="__main__": raise SystemExit(main())
