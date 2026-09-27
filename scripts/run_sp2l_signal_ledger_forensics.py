"""Forensic reconciliation of the reproduced 222 V2 ledger against the 227 baseline.

Research-only. The two reports have different schemas; mapping is explicit.
No canonical rule or performance winner is selected.
"""
from __future__ import annotations
import argparse, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

FIELDS = ["direction", "entry_time", "entry", "sl", "tp"]
OUTCOME_FIELDS = ["result", "fill_time", "exit_time", "exit_reason"]

def load(path):
    d=json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(d.get("result"),dict) and isinstance(d["result"].get("signals_detail"),list):
        return d,d["result"]["signals_detail"],"baseline_result.signals_detail"
    if isinstance(d.get("results"),dict) and isinstance(d["results"].get("trades_detail"),list):
        return d,d["results"]["trades_detail"],"v2_results.trades_detail"
    raise ValueError(f"No supported ledger schema found in {path}")

def norm(v):
    return round(v,8) if isinstance(v,float) else v

def canonical_row(x, schema):
    if schema=="baseline_result.signals_detail":
        return {
            "direction":x.get("direction"),"entry_time":x.get("entry_time"),
            "entry":x.get("entry"),"sl":x.get("sl"),"tp":x.get("tp"),
            "result":x.get("result"),"fill_time":x.get("fill_time"),
            "exit_time":x.get("exit_time"),"exit_reason":x.get("exit_reason"),
        }
    return {
        "direction":x.get("direction"),"entry_time":x.get("entry_time"),
        "entry":x.get("entry"),"sl":x.get("sl"),"tp":x.get("tp"),
        "result":("WIN" if x.get("r")==1 else "LOSS" if x.get("r")==-1 else
                  ("INCOMPLETE" if not x.get("completed",True) else None)),
        "fill_time":x.get("activation_time"),"exit_time":x.get("exit_time"),
        "exit_reason":x.get("exit_reason"),
    }

def fingerprint(x):
    return tuple(norm(x.get(k)) for k in FIELDS)

def ledger_hash(rows):
    return hashlib.sha256(json.dumps([fingerprint(x) for x in rows],
        separators=(",",":"),sort_keys=False).encode()).hexdigest()

def groups(rows):
    g=defaultdict(list)
    for i,x in enumerate(rows): g[fingerprint(x)].append((i,x))
    return g

def classify(a,b):
    if fingerprint(a)!=fingerprint(b):
        dif=[f for f in FIELDS if norm(a.get(f))!=norm(b.get(f))]
        if "entry_time" in dif:return "TRIGGER_OR_INDEXING",dif
        if any(f in dif for f in ("entry","sl","tp")):return "GEOMETRY_OR_CONFIG",dif
        return "SIGNAL_POPULATION",dif
    dif=[f for f in OUTCOME_FIELDS if norm(a.get(f))!=norm(b.get(f))]
    return ("FILL_OR_OUTCOME",dif) if dif else ("IDENTICAL",[])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline-report",required=True);p.add_argument("--reference-report",required=True)
    p.add_argument("--output",required=True);a=p.parse_args()
    db,rb,sb=load(a.baseline_report);dr,rr,sr=load(a.reference_report)
    B=[canonical_row(x,sb) for x in rb];R=[canonical_row(x,sr) for x in rr]
    gb,gr=groups(B),groups(R);kb,kr=set(gb),set(gr);common=sorted(kb&kr,key=str)
    cats=Counter();samples={};matched=[]
    for k in common:
        for j in range(min(len(gb[k]),len(gr[k]))):
            bi,b=gb[k][j];ri,r=gr[k][j];cat,dif=classify(b,r);cats[cat]+=1
            rec={"baseline_index":bi,"reference_index":ri,"fingerprint":list(k),
                 "classification":cat,"fields":dif}
            matched.append(rec)
            if cat!="IDENTICAL":samples.setdefault(cat,rec)
    bo=[{"index":i,"fingerprint":list(k)} for k in sorted(kb-kr,key=str) for i,_ in gb[k]]
    ro=[{"index":i,"fingerprint":list(k)} for k in sorted(kr-kb,key=str) for i,_ in gr[k]]
    bd={str(k):len(v) for k,v in gb.items() if len(v)>1};rd={str(k):len(v) for k,v in gr.items() if len(v)>1}
    out={
      "status":"COMPLETE","research_only":True,
      "purpose":"222_reproduced_vs_227_baseline_multiplicity_preserving_reconciliation",
      "schemas":{"baseline":sb,"reference":sr},
      "baseline":{"path":a.baseline_report,"signals":len(B),"unique_fingerprints":len(gb),
                  "ledger_hash":ledger_hash(B)},
      "reference":{"path":a.reference_report,"signals":len(R),"unique_fingerprints":len(gr),
                   "ledger_hash":ledger_hash(R)},
      "common_fingerprints":len(common),"baseline_only_rows":len(bo),"reference_only_rows":len(ro),
      "duplicate_counts":{
        "baseline_duplicate_fingerprint_keys":len(bd),"reference_duplicate_fingerprint_keys":len(rd),
        "baseline_duplicate_rows":sum(v-1 for v in bd.values()),
        "reference_duplicate_rows":sum(v-1 for v in rd.values())},
      "common_multiplicity_matched_rows":sum(min(len(gb[k]),len(gr[k])) for k in common),
      "common_classification_counts":dict(cats),"samples":samples,
      "matching_contract":{"duplicate_multiplicity_preserved":True,
        "input_order_preserved_within_fingerprint":True,"no_dict_overwrite":True,
        "baseline_mapping":"signals_detail fields used directly",
        "reference_mapping":"trades_detail; activation_time mapped to fill_time; r mapped to result"},
      "baseline_summary":db.get("result",{}),"reference_summary":dr.get("results",{})
    }
    outp=Path(a.output);outp.parent.mkdir(parents=True,exist_ok=True)
    outp.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(out,indent=2,ensure_ascii=False))

if __name__=="__main__":raise SystemExit(main())
