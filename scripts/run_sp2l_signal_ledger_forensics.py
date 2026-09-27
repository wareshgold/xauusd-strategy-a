"""Forensic reconciliation of two SP2L replay ledgers.

Research-only. Preserves duplicate fingerprints and row order.
Never chooses a preferred result or canonical rule.
"""
from __future__ import annotations
import argparse, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

SIGNAL_FIELDS = ["direction", "entry_time", "entry", "sl", "tp"]
OUTCOME_FIELDS = ["result", "fill_time", "exit_time", "exit_reason"]

def load(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return d, d.get("result", d).get("signals_detail", [])

def norm(v):
    return round(v, 8) if isinstance(v, float) else v

def fingerprint(x):
    return tuple([x.get("direction"), x.get("entry_time"), norm(x.get("entry")),
                  norm(x.get("sl")), norm(x.get("tp"))])

def ledger_hash(rows):
    raw = json.dumps([fingerprint(x) for x in rows], separators=(",", ":"), sort_keys=False)
    return hashlib.sha256(raw.encode()).hexdigest()

def classify(a, b):
    if fingerprint(a) != fingerprint(b):
        dif = [f for f in SIGNAL_FIELDS if norm(a.get(f)) != norm(b.get(f))]
        if "entry_time" in dif: return "TRIGGER_OR_INDEXING", dif
        if any(f in dif for f in ["entry", "sl", "tp"]): return "GEOMETRY_OR_CONFIG", dif
        return "SIGNAL_POPULATION", dif
    dif = [f for f in OUTCOME_FIELDS if norm(a.get(f)) != norm(b.get(f))]
    return ("FILL_OR_OUTCOME", dif) if dif else ("IDENTICAL", [])

def keyed_rows(rows):
    groups = defaultdict(list)
    for i, row in enumerate(rows):
        groups[fingerprint(row)].append((i, row))
    return groups

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--baseline-report", required=True)
    p.add_argument("--reference-report", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    da, A = load(args.baseline_report)
    db, B = load(args.reference_report)
    ga, gb = keyed_rows(A), keyed_rows(B)
    ka, kb = set(ga), set(gb)
    common_keys = sorted(ka & kb, key=str)
    matched, categories, samples = [], Counter(), {}
    duplicate_keys = {
        "baseline": {str(k): len(v) for k, v in ga.items() if len(v) > 1},
        "reference": {str(k): len(v) for k, v in gb.items() if len(v) > 1},
    }
    for k in common_keys:
        arows, brows = ga[k], gb[k]
        for j in range(min(len(arows), len(brows))):
            ai, a = arows[j]; bi, b = brows[j]
            cat, dif = classify(a, b)
            categories[cat] += 1
            matched.append({"baseline_index": ai, "reference_index": bi,
                            "fingerprint": list(k), "classification": cat, "fields": dif})
    baseline_only = [{"index": i, "fingerprint": list(k)} for k in sorted(ka-kb, key=str) for i,_ in ga[k]]
    reference_only = [{"index": i, "fingerprint": list(k)} for k in sorted(kb-ka, key=str) for i,_ in gb[k]]
    for m in matched:
        if m["classification"] != "IDENTICAL":
            samples.setdefault(m["classification"], m)
    duplicate_counts = {
        "baseline_duplicate_fingerprint_keys": len(duplicate_keys["baseline"]),
        "reference_duplicate_fingerprint_keys": len(duplicate_keys["reference"]),
        "baseline_duplicate_rows": sum(v-1 for v in duplicate_keys["baseline"].values()),
        "reference_duplicate_rows": sum(v-1 for v in duplicate_keys["reference"].values()),
    }
    out = {
        "status":"COMPLETE","research_only":True,
        "purpose":"222_reproduced_vs_227_baseline_multiplicity_preserving_reconciliation",
        "baseline":args.baseline_report,"reference":args.reference_report,
        "baseline_signals":len(A),"reference_signals":len(B),
        "baseline_ledger_hash":ledger_hash(A),"reference_ledger_hash":ledger_hash(B),
        "unique_baseline_fingerprints":len(ka),"unique_reference_fingerprints":len(kb),
        "common_fingerprints":len(common_keys),
        "baseline_only_rows":len(baseline_only),"reference_only_rows":len(reference_only),
        "duplicate_counts":duplicate_counts,
        "common_multiplicity_matched_rows":sum(min(len(ga[k]),len(gb[k])) for k in common_keys),
        "common_classification_counts":dict(categories),"samples":samples,
        "baseline_result":da.get("result",{}),"reference_result":db.get("result",{}),
        "matching_contract":{"preserve_duplicate_fingerprints":True,
          "preserve_input_order_within_fingerprint":True,"no_dict_overwrite":True,
          "fingerprint_fields":SIGNAL_FIELDS}
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(out,indent=2,ensure_ascii=False))

if __name__ == "__main__":
    raise SystemExit(main())
