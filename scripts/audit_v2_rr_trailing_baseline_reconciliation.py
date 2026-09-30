"""Reconcile V2 baseline exits against the 12-variant forensic trailing matrix.

NON_CANONICAL_FORENSIC. This script does not select a production configuration.
It verifies trade identity preservation and decomposes outcome changes.
"""
from __future__ import annotations
import argparse, json
from collections import Counter

KEYS = ("direction", "setup_time", "entry_time", "entry", "sl")


def load(path):
    return json.loads(open(path, encoding="utf-8").read())


def key(row):
    return (
        row.get("direction"),
        row.get("setup_time"),
        row.get("entry_time"),
        round(float(row.get("entry", 0.0)), 10),
        round(float(row.get("sl", 0.0)), 10),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    base = load(args.baseline)
    matrix = load(args.matrix)

    baseline_rows = base.get("outcomes", {}).get("signals_detail")
    if baseline_rows is None:
        baseline_rows = base.get("signals_detail")
    if baseline_rows is None:
        raise SystemExit("Baseline signals_detail not found")

    bmap = {key(x): x for x in baseline_rows}
    variants = []
    global_identity_failures = []

    for v in matrix["variants"]:
        rows = v["trades"]
        counts = Counter()
        changes = Counter()
        changed_examples = []

        for row in rows:
            k = key(row)
            b = bmap.get(k)
            if b is None:
                global_identity_failures.append({
                    "rr": v["rr"], "trail_pips": v["trail_pips"], "key": k
                })
                counts["MISSING_BASELINE"] += 1
                continue

            br = b.get("result")
            mr = row.get("result")
            counts[f"BASE_{br}__MATRIX_{mr}"] += 1

            if br != mr:
                changes[f"{br}_TO_{mr}"] += 1
                if len(changed_examples) < 20:
                    changed_examples.append({
                        "direction": row["direction"],
                        "setup_time": row["setup_time"],
                        "entry_time": row["entry_time"],
                        "baseline_result": br,
                        "matrix_result": mr,
                        "baseline_r": b.get("r"),
                        "matrix_r": row.get("r"),
                        "matrix_reason": row.get("reason"),
                        "exit_time": row.get("exit_time"),
                    })

        variants.append({
            "rr": v["rr"],
            "trail_pips": v["trail_pips"],
            "signal_count": len(rows),
            "baseline_population_matches": len(rows) - counts["MISSING_BASELINE"],
            "outcome_transition_counts": dict(counts),
            "outcome_changes": dict(changes),
            "changed_examples_first_20": changed_examples,
        })

    result = {
        "status": "COMPLETE",
        "mode": "NON_CANONICAL_FORENSIC",
        "baseline": args.baseline,
        "matrix": args.matrix,
        "baseline_signals": len(baseline_rows),
        "matrix_population_signals": matrix.get("population_signals"),
        "global_identity_failures": len(global_identity_failures),
        "identity_failure_examples": global_identity_failures[:20],
        "variants": variants,
        "interpretation": {
            "purpose": "Explain how trailing changes the same V2 signal population.",
            "selection": "No configuration is selected or promoted.",
            "expected_baseline_result_set": ["WIN", "LOSS", "AMBIGUOUS", "OPEN_AT_END"],
            "expected_matrix_result_set": ["WIN", "LOSS", "BREAKEVEN", "AMBIGUOUS", "OPEN_OR_UNRESOLVED"],
        },
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(json.dumps({
        "status": result["status"],
        "baseline_signals": result["baseline_signals"],
        "matrix_signals": result["matrix_population_signals"],
        "identity_failures": result["global_identity_failures"],
        "variants": [
            {
                "rr": x["rr"],
                "trail_pips": x["trail_pips"],
                "changes": x["outcome_changes"],
            }
            for x in variants
        ],
        "output": args.output,
    }, indent=2))


if __name__ == "__main__":
    main()
