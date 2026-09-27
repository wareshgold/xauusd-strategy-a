"""Combined forensic for common SP2L V2 outcome differences.

Runs one pass over all 222 common signals and classifies fill, exit, result,
same-bar/gap evidence and R deltas. Research-only; never promotes rules.
"""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path

FIELDS=["direction","entry_time","entry","sl","tp"]

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def fp(x):
    return tuple(round(x[k],8) if isinstance(x.get(k),float) else x.get(k) for k in FIELDS)
def label(x):
    if x is None: return None
    if isinstance(x.get("r"),(int,float)): return "WIN" if x["r"]>0 else "LOSS" if x["r"]<0 else "NON_DECISIVE"
    return x.get("result")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline-report",required=True)
    p.add_argument("--reference-report",required=True)
    p.add_argument("--reconciliation-report",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    b=load(a.baseline_report); r=load(a.reference_report); rec=load(a.reconciliation_report)
    bs=b["result"]["signals_detail"]; rs=r["signal_ledger"]; rt=r["results"]["trades_detail"]
    bm={fp(x):x for x in bs}; sm={fp(x):x for x in rs}; tm={fp(x):x for x in rt}
    common=sorted(set(bm)&set(sm),key=str)
    counts=Counter(); rows=[]; delta=0.0
    for k in common:
        x=bm[k]; y=tm.get(k); dif=[]
        if y is None:
            cls="REFERENCE_NO_TRADE"; counts[cls]+=1
            rows.append({"fingerprint":list(k),"classification":cls,"baseline":{"result":label(x),"r":x.get("r")},"reference":None})
            continue
        if x.get("fill_time")!=y.get("activation_time"): dif.append("FILL_TIME")
        if x.get("exit_time")!=y.get("exit_time"): dif.append("EXIT_TIME")
        if x.get("exit_reason")!=y.get("exit_reason"): dif.append("EXIT_REASON")
        if label(x)!=label(y): dif.append("RESULT")
        if isinstance(x.get("r"),(int,float)) and isinstance(y.get("r"),(int,float)) and abs(float(x["r"])-float(y["r"]))>1e-9: dif.append("R")
        cls="OUTCOME_IDENTICAL" if not dif else "OUTCOME_DIFFERENT"
        counts[cls]+=1
        if dif: counts["DIFF:"+",".join(dif)]+=1
        if isinstance(x.get("r"),(int,float)) and isinstance(y.get("r"),(int,float)): delta+=float(y["r"])-float(x["r"])
        rows.append({"fingerprint":list(k),"classification":cls,"differences":dif,
                     "baseline":{"result":label(x),"fill_time":x.get("fill_time"),"exit_time":x.get("exit_time"),"exit_reason":x.get("exit_reason"),"r":x.get("r")},
                     "reference":{"result":label(y),"activation_time":y.get("activation_time"),"exit_time":y.get("exit_time"),"exit_reason":y.get("exit_reason"),"r":y.get("r")}})
    # Count timing-only versus economic differences, and expose all R-changing rows.
    timing_only=[z for z in rows if z["classification"]=="OUTCOME_DIFFERENT" and "R" not in z.get("differences",[]) and "RESULT" not in z.get("differences",[])]
    r_changes=[z for z in rows if "R" in z.get("differences",[])]
    result_changes=[z for z in rows if "RESULT" in z.get("differences",[])]
    reference_r=sum(float(x["r"]) for x in rt if isinstance(x.get("r"),(int,float)))
    baseline_common_r=sum(float(bm[k]["r"]) for k in common if isinstance(bm[k].get("r"),(int,float)))
    reference_common_r=sum(float(tm[k]["r"]) for k in common if k in tm and isinstance(tm[k].get("r"),(int,float)))
    out={"status":"COMPLETE","research_only":True,
         "purpose":"combined_222_common_outcome_forensics",
         "population":{"common":len(common),"reference_trades":len(rt),"reference_common_trades":len(set(rt and map(fp,rt))&set(common)),
                       "reference_no_trade":len(set(common)-set(tm))},
         "reconciliation":{"baseline_common_r":baseline_common_r,"reference_common_r":reference_common_r,
                           "delta_reference_minus_baseline":reference_common_r-baseline_common_r,
                           "reference_report_net_r":r["results"]["net_r"],"reference_trade_r_sum":reference_r,
                           "reconciliation_gate_status":rec.get("status")},
         "counts":dict(counts),
         "derived":{"timing_only_count":len(timing_only),"result_change_count":len(result_changes),
                    "r_change_count":len(r_changes),"r_delta_on_rows_with_both_outcomes":delta},
         "r_changing_rows":r_changes,
         "result_changing_rows":result_changes,
         "timing_only_rows":timing_only,
         "all_rows":rows,
         "interpretation_limit":"Descriptive forensic only. No canonical fill/exit semantics are inferred from performance."}
    q=Path(a.output); q.parent.mkdir(parents=True,exist_ok=True); q.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({k:out[k] for k in ("status","population","reconciliation","counts","derived")},indent=2,ensure_ascii=False))
if __name__=="__main__": raise SystemExit(main())
