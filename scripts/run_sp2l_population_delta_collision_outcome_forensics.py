"""Compare outcomes for the five baseline-only entry-index collisions.

Research-only. This forensic joins baseline-only rows to the reference signal
occupying the same entry_index and reports both outcome records when present.
It does not infer or change any canonical rule.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--baseline-report", required=True)
    p.add_argument("--reference-report", required=True)
    p.add_argument("--collision-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    baseline = load_json(a.baseline_report)
    reference = load_json(a.reference_report)
    collision = load_json(a.collision_report)

    bsignals = baseline["result"]["signals_detail"]
    rsignals = reference["signal_ledger"]
    rtrades = reference.get("results", {}).get("trades_detail", [])

    b_by_index = {int(x["entry_index"]): x for x in bsignals}
    r_by_index = {int(x["entry_index"]): x for x in rsignals}

    # Reference trades_detail is the actual outcome ledger for the reproduced
    # 222 run. Match by entry_index first; retain all matches defensively.
    rtrade_by_index = {}
    for t in rtrades:
        if "entry_index" in t:
            rtrade_by_index.setdefault(int(t["entry_index"]), []).append(t)

    rows = []
    for c in collision["rows"]:
        b = c["baseline_only_signal"]
        ei = int(b["entry_index"])
        occupants = c["same_entry_index_reference_occupants"]
        if len(occupants) != 1:
            rows.append({
                "entry_index": ei,
                "status": "UNEXPECTED_REFERENCE_OCCUPANCY_COUNT",
                "reference_occupant_count": len(occupants),
            })
            continue

        r = occupants[0]
        bt = b_by_index.get(ei)
        rt = rtrade_by_index.get(ei, [])

        rows.append({
            "entry_index": ei,
            "baseline_only": {
                "direction": b["direction"],
                "setup_time": b.get("setup_time"),
                "entry_time": b["entry_time"],
                "entry": b["entry"],
                "sl": b["sl"],
                "tp": b["tp"],
                "result": bt.get("result") if bt else b.get("result"),
                "r": bt.get("r") if bt else None,
                "fill_time": bt.get("fill_time") if bt else None,
                "exit_time": bt.get("exit_time") if bt else None,
                "exit_reason": bt.get("exit_reason") if bt else None,
            },
            "reference_occupant": {
                "direction": r["direction"],
                "setup_time": r.get("setup_time"),
                "entry_time": r["entry_time"],
                "entry": r["entry"],
                "sl": r["sl"],
                "tp": r["tp"],
                "risk": r.get("risk"),
            },
            "reference_outcome_matches": [
                {
                    "entry_index": t.get("entry_index"),
                    "direction": t.get("direction"),
                    "entry_time": t.get("entry_time"),
                    "entry": t.get("entry"),
                    "sl": t.get("sl"),
                    "tp": t.get("tp"),
                    "activation_time": t.get("activation_time"),
                    "exit_time": t.get("exit_time"),
                    "exit": t.get("exit"),
                    "r": t.get("r"),
                    "exit_reason": t.get("exit_reason"),
                    "completed": t.get("completed"),
                }
                for t in rt
            ],
            "reference_outcome_match_count": len(rt),
        })

    def r_value(row, side):
        vals = row.get(side, {}).get("r")
        return float(vals) if isinstance(vals, (int, float)) else None

    baseline_r = sum(r_value(x, "baseline_only") or 0.0 for x in rows)
    reference_r = 0.0
    reference_r_count = 0
    for x in rows:
        for t in x.get("reference_outcome_matches", []):
            if isinstance(t.get("r"), (int, float)):
                reference_r += float(t["r"])
                reference_r_count += 1

    out = {
        "status": "COMPLETE",
        "research_only": True,
        "purpose": "outcome_comparison_for_entry_index_collision_population_delta",
        "collision_rows": len(rows),
        "baseline_only_collision_r_sum": baseline_r,
        "reference_occupant_matched_trade_r_sum": reference_r,
        "reference_occupant_matched_trade_count": reference_r_count,
        "r_difference_reference_minus_baseline_only": reference_r - baseline_r,
        "rows": rows,
        "interpretation_limit": (
            "This joins existing report ledgers only. It does not establish "
            "causality, canonical trigger semantics, or a performance winner."
        ),
    }
    q = Path(a.output)
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "status": out["status"],
        "collision_rows": out["collision_rows"],
        "baseline_only_collision_r_sum": out["baseline_only_collision_r_sum"],
        "reference_occupant_matched_trade_r_sum": out["reference_occupant_matched_trade_r_sum"],
        "reference_occupant_matched_trade_count": out["reference_occupant_matched_trade_count"],
        "r_difference_reference_minus_baseline_only": out["r_difference_reference_minus_baseline_only"],
        "rows": rows,
    }, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    raise SystemExit(main())
