"""Isolate baseline-only SP2L population rows for deterministic reconciliation.

Research-only. This tool does not alter detector geometry or infer canonical rules.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

FIELDS=["direction","setup_time","before_spike_time","spike_time","after_spike_time",
        "entry_index","entry_time","entry","sl","tp"]

def load_baseline(path):
    d=json.loads(Path(path).read_text(encoding="utf-8"))
    rows=d.get("result",{}).get("signals_detail")
    if not isinstance(rows,list):
        raise ValueError("baseline result.signals_detail not found")
    return rows

def load_reference(path):
    d=json.loads(Path(path).read_text(encoding="utf-8"))
    rows=d.get("signal_ledger")
    if not isinstance(rows,list):
        raise ValueError("reference signal_ledger not found")
    return rows

def fp(x):
    return (x.get("direction"),x.get("entry_time"),x.get("entry"),x.get("sl"),x.get("tp"))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline-report",required=True)
    p.add_argument("--reference-report",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()

    b=load_baseline(a.baseline_report)
    r=load_reference(a.reference_report)
    rf={fp(x) for x in r}

    rows=[]
    for i,x in enumerate(b):
        if fp(x) not in rf:
            rows.append({
                "baseline_index":i,
                "fingerprint":list(fp(x)),
                "fields":{k:x.get(k) for k in FIELDS},
            })

    out={
        "status":"COMPLETE",
        "research_only":True,
        "purpose":"isolate_baseline_only_population_delta",
        "baseline_signals":len(b),
        "reference_signals":len(r),
        "baseline_only_count":len(rows),
        "reference_only_count":0,
        "baseline_only_rows":rows,
        "interpretation_limit":"Rows are isolated for inspection only. No cause is inferred from this artifact.",
    }
    outp=Path(a.output)
    outp.parent.mkdir(parents=True,exist_ok=True)
    outp.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")

    print(json.dumps({
        "status":out["status"],
        "baseline_signals":len(b),
        "reference_signals":len(r),
        "baseline_only_count":len(rows),
        "baseline_only_rows":rows,
    },indent=2,ensure_ascii=False))

if __name__=="__main__":
    raise SystemExit(main())
