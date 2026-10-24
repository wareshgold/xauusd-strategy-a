"""Research-only Multiple-Testing Guard for the pre-registered SP2L 4-week 81-point matrix.

This module does NOT select a winner, optimize parameters, assign significance,
or promote any parameter. It only describes the breadth and concentration of
the already-computed parameter surface.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

INPUT = Path("artifacts/SP2L_parameter_stability_4week_81_matrix_2026-09-19.json")
OUTPUT = Path("artifacts/SP2L_multiple_testing_guard_2026-09-19.json")

BASELINE = {
    "pGap": 1.0,
    "spikeMultiplier": 1.5,
    "maxSL": 10.0,
    "tpR": 1.0,
}

data = json.loads(INPUT.read_text(encoding="utf-8"))
rows = data["combinations"]

def vals(key):
    return [float(r[key]) for r in rows if r.get(key) is not None]

def percentile(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    pos = (len(xs) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return xs[lo]
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)

def distribution(xs):
    xs = sorted(xs)
    return {
        "n": len(xs),
        "min": xs[0],
        "q1": percentile(xs, 0.25),
        "median": percentile(xs, 0.50),
        "q3": percentile(xs, 0.75),
        "max": xs[-1],
        "mean": statistics.mean(xs),
        "stdev": statistics.stdev(xs) if len(xs) >= 2 else 0.0,
        "iqr": percentile(xs, 0.75) - percentile(xs, 0.25),
    }

def rank_fraction(value, xs):
    """Fraction of tested combinations at or below the baseline value."""
    return sum(x <= value for x in xs) / len(xs) if xs else None

baseline = next(
    r for r in rows
    if all(float(r[k]) == v for k, v in BASELINE.items())
)

wr_values = vals("decisive_wr")
r_values = vals("total_R")
pf_values = vals("profit_factor")

positive_r = sum(float(r["total_R"]) > 0 for r in rows)
above_60 = sum(float(r["decisive_wr"]) > 0.60 for r in rows)

# No "best" combination is selected. These are distributional diagnostics only.
result = {
    "research_only": True,
    "artifact_type": "SP2L_MULTIPLE_TESTING_GUARD",
    "input_artifact": str(INPUT),
    "sample": {
        "combinations": len(rows),
        "grid": data.get("grid"),
        "weeks": data.get("weeks"),
    },
    "baseline": {
        **BASELINE,
        "signals": baseline["signals"],
        "wins": baseline["wins"],
        "losses": baseline["losses"],
        "ambiguous": baseline["ambiguous"],
        "decisive_wr": baseline["decisive_wr"],
        "total_R": baseline["total_R"],
        "profit_factor": baseline["profit_factor"],
        "wr_rank_fraction_at_or_below": rank_fraction(baseline["decisive_wr"], wr_values),
        "total_R_rank_fraction_at_or_below": rank_fraction(baseline["total_R"], r_values),
        "pf_rank_fraction_at_or_below": rank_fraction(baseline["profit_factor"], pf_values),
    },
    "surface_distribution": {
        "decisive_win_rate": distribution(wr_values),
        "total_R": distribution(r_values),
        "profit_factor": distribution(pf_values),
    },
    "breadth": {
        "positive_total_R_count": positive_r,
        "positive_total_R_pct": 100.0 * positive_r / len(rows),
        "above_60pct_wr_count": above_60,
        "above_60pct_wr_pct": 100.0 * above_60 / len(rows),
    },
    "concentration": {
        "wr_top_quartile_threshold": percentile(wr_values, 0.75),
        "r_top_quartile_threshold": percentile(r_values, 0.75),
        "pf_top_quartile_threshold": percentile(pf_values, 0.75),
        "baseline_in_wr_top_quartile": baseline["decisive_wr"] >= percentile(wr_values, 0.75),
        "baseline_in_R_top_quartile": baseline["total_R"] >= percentile(r_values, 0.75),
        "baseline_in_PF_top_quartile": baseline["profit_factor"] >= percentile(pf_values, 0.75),
    },
    "interpretation": [
        "The 81-combination surface is explicitly treated as a multiple-comparison search space.",
        "No highest-performing combination is selected or reported as a winner.",
        "Distributional breadth is descriptive evidence only and is not a statistical significance test.",
        "Baseline rank describes its position within the already-tested surface; it does not authorize parameter promotion.",
        "No p-value, family-wise error rate, false-discovery rate, or multiple-testing-adjusted significance claim is made.",
        "The same historical observations are reused across combinations, so combination results are not independent experiments.",
        "No production parameter may be selected from this matrix solely because of observed performance."
    ],
    "guard": "RESEARCH_MULTIPLE_TESTING_ONLY; NO_RULE_OR_PARAMETER_PROMOTION",
    "disposition": "DESCRIPTIVE_ONLY_NO_AUTOMATIC_PASS_FAIL",
}

OUTPUT.parent.mkdir(exist_ok=True)
OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps({
    "status": "ANALYZED",
    "output": str(OUTPUT),
    "combinations": len(rows),
    "baseline": result["baseline"],
    "breadth": result["breadth"],
    "surface_distribution": result["surface_distribution"],
    "concentration": result["concentration"],
    "disposition": result["disposition"],
}, ensure_ascii=False, indent=2))
