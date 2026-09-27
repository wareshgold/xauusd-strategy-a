"""Forensic mapping of baseline-only rows to reference entry indices.

Research-only. Tests whether each baseline-only row's entry_index is already
occupied by a different reference signal, while preserving all fields.
No geometry or outcome rule is changed.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline-report",required=True)
    p.add_argument("--reference-report",required=True)
    p.add_argument("--delta-report",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()

    b=json.loads(Path(a.baseline_report).read_text(encoding="utf-8"))
    r=json.loads(Path(a.reference_report).read_text(encoding="utf-8"))
    d=json.loads(Path(a.delta_report).read_text(encoding="utf-8"))
    baseline=b["result"]["signals_detail"]
    reference=r["signal_ledger"]
    targets=d["baseline_only_rows"]

    ref_by_index={}
    for x in reference:
        ref_by_index.setdefault(int(x["entry_index"]),[]).append(x)
    base_by_index={}
    for x in baseline:
        base_by_index.setdefault(int(x["entry_index"]),[]).append(x)

    rows=[]
    for item in targets:
        # run_sp2l_population_delta_forensics persists the signal fields under
        # "fields"; older/manual artifacts may expose them directly.
        s=item.get("fields") or item.get("signal") or item
        ei=int(s["entry_index"])
        occupants=ref_by_index.get(ei,[])
        rows.append({
            "baseline_only_signal":s,
            "same_entry_index_reference_occupants":occupants,
            "same_entry_index_reference_count":len(occupants),
            "same_entry_index_baseline_count":len(base_by_index.get(ei,[])),
            "classification":(
                "REFERENCE_INDEX_OCCUPIED_BY_OTHER_SIGNAL" if occupants
                else "REFERENCE_INDEX_UNOCCUPIED"
            ),
        })

    counts={}
    for x in rows:
        counts[x["classification"]]=counts.get(x["classification"],0)+1
    out={
        "status":"COMPLETE","research_only":True,
        "purpose":"test_entry_index_collision_as_population_delta_explanation",
        "baseline_signals":len(baseline),"reference_signals":len(reference),
        "baseline_only_count":len(targets),
        "classification_counts":counts,
        "rows":rows,
        "interpretation_limit":"Index occupancy is descriptive evidence only; it does not establish canonical trigger semantics."
    }
    q=Path(a.output); q.parent.mkdir(parents=True,exist_ok=True)
    q.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"status":"COMPLETE","classification_counts":counts,"rows":rows},indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
