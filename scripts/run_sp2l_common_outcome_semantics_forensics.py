"""Reconcile outcomes for the common V2 signal population.

Research-only. No canonical rule selection.
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

def outcome_label(x):
    r = x.get("r")
    if r is None:
        return x.get("result", "NON_DECISIVE")
    return "WIN" if float(r) > 0 else "LOSS" if float(r) < 0 else "NON_DECISIVE"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--baseline-report", required=True)
    p.add_argument("--reference-report", required=True)
    p.add_argument("--reconciliation-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    b = load(a.baseline_report)
    r = load(a.reference_report)
    rec = load(a.reconciliation_report)

    baseline = b["result"]["signals_detail"]
    reference_ledger = r["signal_ledger"]
    reference_trades = r.get("results", {}).get("trades_detail", [])

    bmap = {fp(x): x for x in baseline}
    smap = {fp(x): x for x in reference_ledger}
    tmap = {fp(x): x for x in reference_trades}

    common = set(bmap) & set(smap)
    baseline_only = set(bmap) - set(smap)
    reference_only = set(smap) - set(bmap)

    counts = Counter()
    rows = []
    common_baseline_r = 0.0
    common_reference_r = 0.0

    for k in sorted(common, key=str):
        bs = bmap[k]
        rt = tmap.get(k)
        if rt is None:
            classification = "REFERENCE_NO_TRADE"
            counts[classification] += 1
            rows.append({
                "fingerprint": list(k),
                "baseline_result": outcome_label(bs),
                "baseline_r": bs.get("r"),
                "reference_trade": None,
                "differences": [],
                "classification": classification,
            })
            if isinstance(bs.get("r"), (int, float)):
                common_baseline_r += float(bs["r"])
            continue

        br = float(bs["r"]) if isinstance(bs.get("r"), (int, float)) else None
        rr = float(rt["r"]) if isinstance(rt.get("r"), (int, float)) else None
        if br is not None:
            common_baseline_r += br
        if rr is not None:
            common_reference_r += rr

        differences = []
        if outcome_label(bs) != outcome_label(rt):
            differences.append("RESULT")
        if bs.get("fill_time") != rt.get("activation_time"):
            differences.append("FILL_TIME")
        if bs.get("exit_time") != rt.get("exit_time"):
            differences.append("EXIT_TIME")
        if bs.get("exit_reason") != rt.get("exit_reason"):
            differences.append("EXIT_REASON")
        if br is not None and rr is not None and abs(br - rr) > 1e-9:
            differences.append("R")

        classification = "OUTCOME_IDENTICAL" if not differences else "OUTCOME_DIFFERENT"
        counts[classification] += 1
        if differences:
            counts["DIFF:" + ",".join(differences)] += 1

        rows.append({
            "fingerprint": list(k),
            "baseline": {
                "result": outcome_label(bs), "fill_time": bs.get("fill_time"),
                "exit_time": bs.get("exit_time"), "exit_reason": bs.get("exit_reason"), "r": br
            },
            "reference": {
                "result": outcome_label(rt), "activation_time": rt.get("activation_time"),
                "exit_time": rt.get("exit_time"), "exit_reason": rt.get("exit_reason"), "r": rr
            },
            "differences": differences,
            "classification": classification,
        })

    reference_trade_keys = set(tmap)
    reference_trade_common = reference_trade_keys & common
    reference_trade_noncommon = reference_trade_keys - common

    result = {
        "status": "COMPLETE",
        "research_only": True,
        "purpose": "common_222_outcome_semantics_reconciliation_hardened",
        "input_reconciliation_status": rec.get("status"),
        "population": {
            "baseline_signals": len(bmap),
            "reference_signals": len(smap),
            "common_signals": len(common),
            "baseline_only_signals": len(baseline_only),
            "reference_only_signals": len(reference_only),
            "reference_trades_total": len(reference_trades),
            "reference_trades_common": len(reference_trade_common),
            "reference_trades_noncommon": len(reference_trade_noncommon),
            "common_signals_without_reference_trade": len(common - reference_trade_keys),
        },
        "r_reconciliation": {
            "baseline_common_r": common_baseline_r,
            "reference_common_r": common_reference_r,
            "common_delta_reference_minus_baseline": common_reference_r - common_baseline_r,
            "reference_report_net_r": r.get("results", {}).get("net_r"),
            "reference_trade_r_sum_all": sum(float(x["r"]) for x in reference_trades if isinstance(x.get("r"), (int, float))),
            "reference_trade_r_sum_noncommon": sum(float(x["r"]) for x in reference_trades if fp(x) not in common and isinstance(x.get("r"), (int, float))),
        },
        "classification_counts": dict(counts),
        "rows": rows,
        "interpretation_limit": "Descriptive reconciliation only; no causal or canonical rule inference.",
    }

    q = Path(a.output)
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({
        "status": result["status"],
        "population": result["population"],
        "r_reconciliation": result["r_reconciliation"],
        "classification_counts": result["classification_counts"],
    }, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    raise SystemExit(main())
