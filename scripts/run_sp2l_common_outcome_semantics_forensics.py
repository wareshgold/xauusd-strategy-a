"""Compare outcome semantics for the 222 common V2 signals.

Research-only. Matches baseline and reference by signal fingerprint, then
compares their persisted outcome records. No canonical rule is selected.
"""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path

FIELDS = ["direction", "entry_time", "entry", "sl", "tp"]

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def fp(x):
    return tuple(round(x[k], 8) if isinstance(x.get(k), float) else x.get(k) for k in FIELDS)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline-report",required=True)
    p.add_argument("--reference-report",required=True)
    p.add_argument("--reconciliation-report",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()

    b=load(a.baseline_report); r=load(a.reference_report); rec=load(a.reconciliation_report)
    bs=b["result"]["signals_detail"]
    rs=r["signal_ledger"]
    bt_by_fp={fp(x):x for x in bs}
    rt_by_fp={}
    for x in r.get("results",{}).get("trades_detail",[]):
        rt_by_fp[fp(x)]=x

    common=[]
    for row in rec.get("population_classification_counts",{}),:
        pass
    # Use ledger intersection directly; reconciliation is an input guard.
    keys=sorted(set(map(fp,bs)) & set(map(fp,rs)), key=str)

    counts=Counter()
    rows=[]
    for k in keys:
        bsignal=bt_by_fp[k]
        rsig=next(x for x in rs if fp(x)==k)
        btrade=bsignal
        rtrade=rt_by_fp.get(k)

        bres=btrade.get("result")
        rres=None
        if rtrade:
            rres = "WIN" if rtrade.get("r",0)>0 else "LOSS" if rtrade.get("r",0)<0 else "NON_DECISIVE"
        diffs=[]
        if rtrade is None:
            classification="REFERENCE_TRADE_NOT_MATCHED"
        else:
            if bres != rres:
                diffs.append("RESULT")
            if btrade.get("fill_time") != rtrade.get("activation_time"):
                diffs.append("FILL_TIME")
            if btrade.get("exit_time") != rtrade.get("exit_time"):
                diffs.append("EXIT_TIME")
            if btrade.get("exit_reason") != rtrade.get("exit_reason"):
                diffs.append("EXIT_REASON")
            br=btrade.get("r"); rr=rtrade.get("r")
            if br is not None and rr is not None and abs(float(br)-float(rr))>1e-9:
                diffs.append("R")
            classification="IDENTICAL_OUTCOME_RECORD" if not diffs else "OUTCOME_SEMANTIC_DIFFERENCE"
        counts[classification]+=1
        if diffs:
            counts["DIFF:"+",".join(diffs)]+=1
        rows.append({
            "fingerprint":list(k),
            "baseline":{"result":bres,"fill_time":btrade.get("fill_time"),"exit_time":btrade.get("exit_time"),
                        "exit_reason":btrade.get("exit_reason"),"r":btrade.get("r")},
            "reference":{"result":rres,"activation_time":rtrade.get("activation_time") if rtrade else None,
                         "exit_time":rtrade.get("exit_time") if rtrade else None,
                         "exit_reason":rtrade.get("exit_reason") if rtrade else None,
                         "r":rtrade.get("r") if rtrade else None},
            "differences":diffs,"classification":classification,
        })

    result={
        "status":"COMPLETE","research_only":True,
        "purpose":"common_222_outcome_semantics_reconciliation",
        "common_signal_count":len(keys),
        "classification_counts":dict(counts),
        "net_r_baseline":sum(float(x["baseline"]["r"]) for x in rows if isinstance(x["baseline"]["r"],(int,float))),
        "net_r_reference":sum(float(x["reference"]["r"]) for x in rows if isinstance(x["reference"]["r"],(int,float))),
        "net_r_difference_reference_minus_baseline":(
            sum(float(x["reference"]["r"]) for x in rows if isinstance(x["reference"]["r"],(int,float))) -
            sum(float(x["baseline"]["r"]) for x in rows if isinstance(x["baseline"]["r"],(int,float)))
        ),
        "rows":rows,
        "interpretation_limit":"Descriptive ledger reconciliation only; no causal or canonical rule inference.",
    }
    q=Path(a.output); q.parent.mkdir(parents=True,exist_ok=True)
    q.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("status","common_signal_count","classification_counts","net_r_baseline","net_r_reference","net_r_difference_reference_minus_baseline")},indent=2,ensure_ascii=False))

if __name__=="__main__":
    raise SystemExit(main())
