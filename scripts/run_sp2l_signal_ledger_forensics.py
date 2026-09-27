"""Forensic reconciliation of V2 signal populations and, where available, trade outcomes.

Research-only. No canonical rule or performance winner is selected.
"""
from __future__ import annotations
import argparse, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

FIELDS=["direction","entry_time","entry","sl","tp"]
OUTCOME_FIELDS=["result","fill_time","exit_time","exit_reason"]

def load(path):
    d=json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(d.get("result"),dict) and isinstance(d["result"].get("signals_detail"),list):
        return d,d["result"]["signals_detail"],"baseline_result.signals_detail"
    if isinstance(d.get("signal_ledger"),list):
        return d,d["signal_ledger"],"v2_signal_ledger"
    if isinstance(d.get("results"),dict) and isinstance(d["results"].get("trades_detail"),list):
        return d,d["results"]["trades_detail"],"v2_results.trades_detail"
    raise ValueError(f"No supported ledger schema found in {path}")

def norm(v): return round(v,8) if isinstance(v,float) else v

def canonical_row(x,schema):
    row={k:x.get(k) for k in FIELDS}
    if schema=="baseline_result.signals_detail":
        row.update({k:x.get(k) for k in OUTCOME_FIELDS})
    elif schema=="v2_results.trades_detail":
        row.update({
            "result":"WIN" if x.get("r")==1 else "LOSS" if x.get("r")==-1 else
                     ("INCOMPLETE" if not x.get("completed",True) else None),
            "fill_time":x.get("activation_time"),"exit_time":x.get("exit_time"),
            "exit_reason":x.get("exit_reason")})
    else:
        row.update({k:None for k in OUTCOME_FIELDS})
    return row

def fingerprint(x): return tuple(norm(x.get(k)) for k in FIELDS)

def ledger_hash(rows):
    return hashlib.sha256(json.dumps([fingerprint(x) for x in rows],
        separators=(",",":"),sort_keys=False).encode()).hexdigest()

def groups(rows):
    g=defaultdict(list)
    for i,x in enumerate(rows): g[fingerprint(x)].append((i,x))
    return g

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline-report",required=True)
    p.add_argument("--reference-report",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    db,rb,sb=load(a.baseline_report);dr,rr,sr=load(a.reference_report)
    B=[canonical_row(x,sb) for x in rb];R=[canonical_row(x,sr) for x in rr]
    gb,gr=groups(B),groups(R);kb,kr=set(gb),set(gr);common=sorted(kb&kr,key=str)

    bo=[{"index":i,"fingerprint":list(k)} for k in sorted(kb-kr,key=str) for i,_ in gb[k]]
    ro=[{"index":i,"fingerprint":list(k)} for k in sorted(kr-kb,key=str) for i,_ in gr[k]]

    outcome_counts=Counter(); outcome_samples={}
    for k in common:
        for j in range(min(len(gb[k]),len(gr[k]))):
            _,b=gb[k][j];_,r=gr[k][j]
            if sr=="v2_signal_ledger":
                outcome_counts["REFERENCE_OUTCOME_NOT_PERSISTED"]+=1
            else:
                dif=[f for f in OUTCOME_FIELDS if norm(b.get(f))!=norm(r.get(f))]
                outcome_counts["FILL_OR_OUTCOME" if dif else "IDENTICAL"]+=1
                if dif: outcome_samples.setdefault("FILL_OR_OUTCOME",{"fingerprint":list(k),"fields":dif})

    bd={str(k):len(v) for k,v in gb.items() if len(v)>1}
    rd={str(k):len(v) for k,v in gr.items() if len(v)>1}
    out={
      "status":"COMPLETE","research_only":True,
      "purpose":"population_first_222_reproduced_vs_227_baseline_reconciliation",
      "schemas":{"baseline":sb,"reference":sr},
      "baseline":{"path":a.baseline_report,"signals":len(B),"unique_fingerprints":len(gb),"ledger_hash":ledger_hash(B)},
      "reference":{"path":a.reference_report,"signals":len(R),"unique_fingerprints":len(gr),"ledger_hash":ledger_hash(R)},
      "common_fingerprints":len(common),"baseline_only_rows":len(bo),"reference_only_rows":len(ro),
      "duplicate_counts":{
        "baseline_duplicate_fingerprint_keys":len(bd),"reference_duplicate_fingerprint_keys":len(rd),
        "baseline_duplicate_rows":sum(v-1 for v in bd.values()),
        "reference_duplicate_rows":sum(v-1 for v in rd.values())},
      "common_multiplicity_matched_rows":sum(min(len(gb[k]),len(gr[k])) for k in common),
      "population_classification_counts":{"COMMON":sum(min(len(gb[k]),len(gr[k])) for k in common),
                                           "BASELINE_ONLY":len(bo),"REFERENCE_ONLY":len(ro)},
      "outcome_classification_counts":dict(outcome_counts),
      "samples":{"outcome":outcome_samples},
      "matching_contract":{
        "duplicate_multiplicity_preserved":True,"input_order_preserved_within_fingerprint":True,
        "no_dict_overwrite":True,"population_first":True,
        "reference_signal_ledger_used_when_present":True,
        "trade_outcomes_not_inferred_from_signal_population":True},
      "baseline_summary":db.get("result",{}),"reference_summary":dr.get("results",{})
    }
    outp=Path(a.output);outp.parent.mkdir(parents=True,exist_ok=True)
    outp.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({k:out[k] for k in ("status","baseline","reference","common_fingerprints","baseline_only_rows","reference_only_rows","duplicate_counts","common_multiplicity_matched_rows","population_classification_counts","outcome_classification_counts")},indent=2,ensure_ascii=False))

if __name__=="__main__": raise SystemExit(main())
