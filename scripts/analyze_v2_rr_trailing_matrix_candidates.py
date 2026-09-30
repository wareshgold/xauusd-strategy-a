"""Research-only analysis of the validated V2 RR/trailing matrix.

Reads the FULL reconciliation artifact produced by
audit_v2_rr_trailing_matrix_full_reconciliation.py.

No canonical rule is selected. No production signal is generated.
Outputs:
- all 12 variants with WR, Net R, PF, DD, losing streak;
- separate maxima for each metric;
- Pareto frontier (descriptive, not a ranking);
- comparison against current Forward baseline (RR=1, no trailing);
- Wilson 95% CI for decisive win rate;
- explicit in-sample/selection warning.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def wilson(wins, n, z=1.959963984540054):
    if n == 0:
        return None, None
    p = wins / n
    den = 1 + z*z/n
    center = (p + z*z/(2*n)) / den
    half = z * math.sqrt((p*(1-p) + z*z/(4*n))/n) / den
    return 100*(center-half), 100*(center+half)


def dominates(a, b):
    # a is at least as good on every descriptive metric and strictly better
    # on at least one. Higher WR/NetR/PF are better; lower DD/streak are better.
    keys_hi = ("win_rate_decisive_pct", "net_R", "profit_factor")
    keys_lo = ("max_drawdown_R", "max_losing_streak")

    def hi_value(row, key):
        value = row[key]
        return float("inf") if key == "profit_factor" and value is None else value

    ge = all(hi_value(a, k) >= hi_value(b, k) for k in keys_hi)
    le = all(a[k] <= b[k] for k in keys_lo)
    strict = (
        any(hi_value(a, k) > hi_value(b, k) for k in keys_hi)
        or any(a[k] < b[k] for k in keys_lo)
    )
    return ge and le and strict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reconciliation", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    doc = load(args.reconciliation)
    if doc.get("status") != "COMPLETE":
        raise SystemExit("Reconciliation artifact is not COMPLETE")
    integ = doc["integrity"]
    if not integ.get("PASS"):
        raise SystemExit("BLOCKED: reconciliation integrity is not PASS")

    variants = []
    for x in doc["variants"]:
        s = x["matrix_summary"]
        pf = s["profit_factor"]
        if pf is None:
            pf_value = float("inf")
        else:
            pf_value = float(pf)
        lo, hi = wilson(s["wins"], s["decisive"])
        variants.append({
            "rr": x["rr"],
            "trail_pips": x["trail_pips"],
            "label": f"{x['rr']:.0f}R/{x['trail_pips']:.0f}p",
            "signals": s["signals"],
            "decisive": s["decisive"],
            "wins": s["wins"],
            "losses": s["losses"],
            "breakeven": s["breakeven"],
            "ambiguous": s["ambiguous"],
            "win_rate_decisive_pct": s["win_rate_decisive_pct"],
            "wilson95_low_pct": lo,
            "wilson95_high_pct": hi,
            "net_R": s["net_R"],
            "profit_factor": s["profit_factor"],
            "max_drawdown_R": s["max_drawdown_R"],
            "max_losing_streak": s["max_losing_streak"],
            "trailing_activated_count": s["trailing_activated_count"],
            "_pf_sort": pf_value,
        })

    baseline = doc["baseline_rr1_no_trailing"]
    base_lo, base_hi = wilson(baseline["wins"], baseline["decisive"])
    baseline_row = {
        "label": "CURRENT_FORWARD_BASELINE_1R_NO_TRAIL",
        **baseline,
        "wilson95_low_pct": base_lo,
        "wilson95_high_pct": base_hi,
        "profit_factor": baseline["wins"] / baseline["losses"] if baseline["losses"] else None,
        "max_drawdown_R": None,
        "max_losing_streak": None,
    }

    frontier = []
    for a in variants:
        if not any(dominates(b, a) for b in variants if b is not a):
            frontier.append(a["label"])

    def max_labels(key, reverse=True):
        vals = [v[key] for v in variants if v[key] is not None and math.isfinite(float(v[key]))]
        target = max(vals) if reverse else min(vals)
        return target, [v["label"] for v in variants if v[key] == target]

    maxima = {
        "highest_win_rate": max_labels("win_rate_decisive_pct"),
        "highest_net_R": max_labels("net_R"),
        "highest_profit_factor_finite": max_labels("profit_factor"),
        "lowest_max_drawdown": max_labels("max_drawdown_R", reverse=False),
        "lowest_max_losing_streak": max_labels("max_losing_streak", reverse=False),
    }

    # Current forward is no-trailing baseline; compare only metrics that are
    # directly available for it without inventing DD/streak.
    for v in variants:
        v["delta_vs_current_baseline"] = {
            "win_rate_pp": v["win_rate_decisive_pct"] - baseline["win_rate_decisive_pct"],
            "net_R": v["net_R"] - baseline["net_R"],
            "decisive_count_delta": v["decisive"] - baseline["decisive"],
        }

    variants.sort(key=lambda v: (-v["win_rate_decisive_pct"], -v["net_R"], v["max_drawdown_R"], v["max_losing_streak"], -v["_pf_sort"]))

    result = {
        "status": "COMPLETE",
        "mode": "NON_CANONICAL_FORENSIC",
        "source_reconciliation": args.reconciliation,
        "integrity": integ,
        "current_forward_reference": baseline_row,
        "variants_by_descriptive_order": variants,
        "metric_maxima": maxima,
        "pareto_frontier_labels": frontier,
        "interpretation": {
            "selection_status": "NO_SINGLE_BEST_SELECTED",
            "why": [
                "All 12 variants use the same 3-month in-sample population.",
                "Trailing is not source-confirmed and remains NON_CANONICAL_FORENSIC.",
                "Choosing the highest in-sample metric would introduce selection bias.",
                "A candidate must be tested on an untouched validation/holdout population before any Forward change is treated as evidence of generalization."
            ],
            "next_research_step": "Use the descriptive maxima/frontier to define a small pre-registered candidate set, then run untouched validation and only after that a fresh Forward comparison."
        }
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({
        "status": "COMPLETE",
        "integrity_PASS": integ["PASS"],
        "current_forward_baseline": {
            "win_rate_decisive_pct": baseline["win_rate_decisive_pct"],
            "net_R": baseline["net_R"],
            "signals": baseline["signals"],
            "decisive": baseline["decisive"],
        },
        "metric_maxima": maxima,
        "pareto_frontier": frontier,
        "variants": [
            {
                "label": v["label"],
                "WR_pct": v["win_rate_decisive_pct"],
                "WR95": [v["wilson95_low_pct"], v["wilson95_high_pct"]],
                "net_R": v["net_R"],
                "PF": v["profit_factor"],
                "DD_R": v["max_drawdown_R"],
                "max_loss_streak": v["max_losing_streak"],
            }
            for v in variants
        ],
        "output": str(out),
    }, indent=2))


if __name__ == "__main__":
    main()
