import json, math, statistics
from pathlib import Path
from collections import Counter, defaultdict

INPUT = Path("artifacts/SP2L_candle_level_assumption_dependency_2026-09-14_2026-09-18.json")
OUTPUT = Path("artifacts/SP2L_candle_level_dependency_stability_2026-09-14_2026-09-18.json")

p = json.loads(INPUT.read_text(encoding="utf-8"))
rows = p["signal_rows"]

def finite(xs):
    return [float(x) for x in xs if x is not None and math.isfinite(float(x))]

def summary(xs):
    xs = finite(xs)
    if not xs:
        return {"n": 0}
    q = statistics.quantiles(xs, n=4, method="inclusive") if len(xs) >= 2 else [xs[0]] * 3
    return {
        "n": len(xs),
        "mean": statistics.mean(xs),
        "median": statistics.median(xs),
        "stdev": statistics.stdev(xs) if len(xs) >= 2 else 0.0,
        "min": min(xs),
        "q1": q[0],
        "q3": q[2],
        "max": max(xs),
    }

def outcome_summary(items):
    decisive = [r for r in items if r["outcome"] in ("WIN","LOSS")]
    wins = sum(r["outcome"] == "WIN" for r in decisive)
    losses = sum(r["outcome"] == "LOSS" for r in decisive)
    return {
        "signals": len(items),
        "decisive": len(decisive),
        "wins": wins,
        "losses": losses,
        "ambiguous": sum(r["outcome"] == "AMBIGUOUS" for r in items),
        "decisive_win_rate_pct": (100.0*wins/len(decisive)) if decisive else None,
    }

features = {}
for candle in ("A","S","C","T","G"):
    features[f"{candle}_body_points"] = summary([r["body_points"][candle] for r in rows])
    features[f"{candle}_range_points"] = summary([r["range_points"][candle] for r in rows])
    features[f"{candle}_body_to_range"] = summary([r["body_to_range"][candle] for r in rows])

features["entry_sl_distance"] = summary([r["entry_sl_distance"] for r in rows])

sl_level_features = {}
for level in rows[0]["sl_to_context_levels"]:
    sl_level_features[level] = summary([r["sl_to_context_levels"][level] for r in rows])

by_direction = {}
for direction in ("BUY","SELL"):
    subset = [r for r in rows if r["direction"] == direction]
    by_direction[direction] = {
        "outcomes": outcome_summary(subset),
        "entry_sl_distance": summary([r["entry_sl_distance"] for r in subset]),
        "body_to_range": {
            c: summary([r["body_to_range"][c] for r in subset]) for c in ("A","S","C","T","G")
        },
    }

by_outcome = {}
for outcome in ("WIN","LOSS","AMBIGUOUS"):
    subset = [r for r in rows if r["outcome"] == outcome]
    by_outcome[outcome] = {
        "count": len(subset),
        "entry_sl_distance": summary([r["entry_sl_distance"] for r in subset]),
        "body_to_range": {
            c: summary([r["body_to_range"][c] for r in subset]) for c in ("A","S","C","T","G")
        },
    }

# Pre-declared coarse descriptive bands. These are reporting bins only, not trading rules.
bands = {
    "S_body_to_range_ge_0_5": lambda r: r["body_to_range"]["S"] >= 0.5,
    "S_body_to_range_lt_0_5": lambda r: r["body_to_range"]["S"] < 0.5,
    "S_range_ge_median": None,
    "entry_sl_distance_ge_median": None,
    "entry_sl_distance_lt_median": None,
}
s_median = statistics.median([r["range_points"]["S"] for r in rows])
sl_median = statistics.median([r["entry_sl_distance"] for r in rows])
bands["S_range_ge_median"] = lambda r: r["range_points"]["S"] >= s_median
bands["entry_sl_distance_ge_median"] = lambda r: r["entry_sl_distance"] >= sl_median
bands["entry_sl_distance_lt_median"] = lambda r: r["entry_sl_distance"] < sl_median

band_results = {}
for name, fn in bands.items():
    subset = [r for r in rows if fn(r)]
    band_results[name] = {
        "definition": "descriptive reporting band only; not a canonical filter",
        "count": len(subset),
        "outcomes": outcome_summary(subset),
    }

out = {
    "research_only": True,
    "artifact_type": "SP2L_CANDLE_LEVEL_DEPENDENCY_STABILITY_ANALYSIS",
    "input_artifact": str(INPUT),
    "input_artifact_sha256": p["report_sha256"],
    "signals": len(rows),
    "outcome_distribution": dict(Counter(r["outcome"] for r in rows)),
    "direction_distribution": dict(Counter(r["direction"] for r in rows)),
    "all_signal_feature_summaries": features,
    "by_direction": by_direction,
    "by_outcome": by_outcome,
    "descriptive_bands": band_results,
    "integrity": p["integrity"],
    "canonicalization_guard": "NO_RULE_OR_PARAMETER_PROMOTED; ALL_BANDS_ARE_REPORTING_ONLY",
    "interpretation": [
        "This artifact measures descriptive stability and outcome association only.",
        "No observed association establishes P-Gap geometry, trigger semantics, swing/SL anchor, AB=CD endpoints/tolerance, or pending-order lifecycle.",
        "No band, threshold, or outcome difference is promoted into a trading rule.",
        "The analysis is limited to the frozen 2026-09-14 through 2026-09-18 evidence window."
    ],
}
OUTPUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({
    "status":"ANALYZED",
    "output":str(OUTPUT),
    "signals":len(rows),
    "outcomes":out["outcome_distribution"],
    "directions":out["direction_distribution"],
    "signal_entry_sl_median":sl_median,
    "spike_range_median":s_median,
    "integrity":p["integrity"],
}, ensure_ascii=False, indent=2))
