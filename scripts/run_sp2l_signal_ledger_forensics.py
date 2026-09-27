"""Forensic reconciliation of two SP2L replay ledgers.

Research-only. This tool never chooses a preferred result or canonical rule.
It compares signal fingerprints and outcome fields, then classifies differences.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

FIELDS = ["direction","entry_time","entry","sl","tp","result","fill_time","exit_time","exit_reason"]

def load(path):
    d=json.loads(Path(path).read_text(encoding="utf-8"))
    return d, d.get("result", d).get("signals_detail", [])

def norm(v):
    if isinstance(v,float): return round(v,8)
    return v

def fingerprint(x):
    return (x.get("direction"), x.get("entry_time"), norm(x.get("entry")), norm(x.get("sl")), norm(x.get("tp")))

def ledger_hash(rows):
    raw=json.dumps([fingerprint(x) for x in rows],separators=(",",":"),sort_keys=False)
    return hashlib.sha256(raw.encode()).hexdigest()

def classify(a,b):
    if fingerprint(a)!=fingerprint(b):
        geo=["direction","entry_time","entry","sl","tp"]
        dif=[f for f in geo if norm(a.get(f))!=norm(b.get(f))]
        if "entry_time" in dif: return "TRIGGER_OR_INDEXING",dif
        if any(f in dif for f in ["entry","sl","tp"]): return "GEOMETRY_OR_CONFIG",dif
        return "SIGNAL_POPULATION",dif
    outcome=["result","fill_time","exit_time","exit_reason"]
    dif=[f for f in outcome if norm(a.get(f))!=norm(b.get(f))]
    return ("FILL_OR_OUTCOME",dif) if dif else ("IDENTICAL",[])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline-report",required=True)
    p.add_argument("--reference-report",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    da,A=load(args.baseline_report); db,B=load(args.reference_report)
    ma={fingerprint(x):x for x in A}; mb={fingerprint(x):x for x in B}
    common=sorted(set(ma)&set(mb), key=str)
    only_a=[ma[k] for k in sorted(set(ma)-set(mb),key=str)]
    only_b=[mb[k] for k in sorted(set(mb)-set(ma),key=str)]
    cats={}
    samples={}
    for k in common:
        cat,dif=classify(ma[k],mb[k]); cats[cat]=cats.get(cat,0)+1
        if cat!="IDENTICAL" and cat not in samples: samples[cat]={"a":ma[k],"b":mb[k],"fields":dif}
    out={"status":"COMPLETE","research_only":True,
         "baseline":args.baseline_report,"reference":args.reference_report,
         "baseline_signals":len(A),"reference_signals":len(B),
         "baseline_ledger_hash":ledger_hash(A),"reference_ledger_hash":ledger_hash(B),
         "common_fingerprints":len(common),"baseline_only":len(only_a),"reference_only":len(only_b),
         "common_classification_counts":cats,"samples":samples,
         "baseline_result":da.get("result",{}),"reference_result":db.get("result",{})}
    Path(args.output).write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(out,indent=2,ensure_ascii=False))

if __name__=="__main__": raise SystemExit(main())
