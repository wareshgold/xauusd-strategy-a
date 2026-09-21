import json
import math
import random
import statistics
from pathlib import Path

INPUT = Path("artifacts/SP2L_author_replica_4week_stability_matrix.json")
OUTPUT = Path("artifacts/SP2L_statistical_uncertainty_4week_2026-09-19.json")

B = 20000
SEED = 20260919
Z = 1.959963984540054

def wilson_interval(wins, decisive, z=Z):
    if decisive == 0:
        return None, None

    p = wins / decisive
    denom = 1 + z * z / decisive
    center = (p + z * z / (2 * decisive)) / denom
    half = (
        z
        * math.sqrt(
            (p * (1 - p) / decisive)
            + (z * z / (4 * decisive * decisive))
        )
        / denom
    )
    return center - half, center + half

def profit_factor_from_R(values):
    wins = sum(v for v in values if v > 0)
    losses = -sum(v for v in values if v < 0)
    if losses == 0:
        return None
    return wins / losses

def summarize(values):
    wins = sum(1 for v in values if v > 0)
    losses = sum(1 for v in values if v < 0)
    decisive = wins + losses
    total_r = sum(values)

    wr = wins / decisive if decisive else None
    pf = profit_factor_from_R(values)

    return {
        "trades": len(values),
        "wins": wins,
        "losses": losses,
        "decisive": decisive,
        "win_rate": wr,
        "total_R": total_r,
        "profit_factor": pf,
    }

def quantiles(values):
    values = sorted(values)
    n = len(values)

    def q(p):
        if not values:
            return None
        if n == 1:
            return values[0]
        pos = (n - 1) * p
        lo = math.floor(pos)
        hi = math.ceil(pos)
        if lo == hi:
            return values[lo]
        return values[lo] + (values[hi] - values[lo]) * (pos - lo)

    return {
        "p025": q(0.025),
        "p50": q(0.50),
        "p975": q(0.975),
    }

def max_drawdown(values):
    equity = 0.0
    peak = 0.0
    max_dd = 0.0

    for v in values:
        equity += v
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)

    return max_dd

with INPUT.open("r", encoding="utf-8") as f:
    data = json.load(f)

weeks = data["weeks"]

# Flatten only decisive baseline trades.
all_decisive = []
week_values = []

for week in weeks:
    values = []

    for trade in week["trades"]:
        outcome = trade["outcome"]

        if outcome == "WIN":
            values.append(1.0)
        elif outcome == "LOSS":
            values.append(-1.0)
        elif outcome == "AMBIGUOUS":
            continue
        else:
            raise ValueError(
                f"Unexpected outcome {outcome!r} in "
                f"{week['week_start_utc']}"
            )

    week_values.append(values)
    all_decisive.extend(values)

observed = summarize(all_decisive)
wilson_low, wilson_high = wilson_interval(
    observed["wins"],
    observed["decisive"],
)

# Time-preserving block bootstrap:
# each replicate resamples complete observed weeks with replacement.
# Within each selected week, chronological trade order is preserved.
rng = random.Random(SEED)

bootstrap_wr = []
bootstrap_total_r = []
bootstrap_pf = []
bootstrap_dd = []

n_weeks = len(week_values)

for _ in range(B):
    sampled_values = []

    for _week in range(n_weeks):
        selected = rng.randrange(n_weeks)
        sampled_values.extend(week_values[selected])

    result = summarize(sampled_values)

    bootstrap_wr.append(result["win_rate"])
    bootstrap_total_r.append(result["total_R"])
    bootstrap_pf.append(
        result["profit_factor"]
        if result["profit_factor"] is not None
        else float("inf")
    )
    bootstrap_dd.append(max_drawdown(sampled_values))

# PF can become infinite in unusual bootstrap replicates.
finite_pf = [x for x in bootstrap_pf if math.isfinite(x)]

report = {
    "status": "ANALYZED",
    "research_only": True,
    "method": "TIME_PRESERVING_WEEK_BLOCK_BOOTSTRAP",
    "seed": SEED,
    "bootstrap_replicates": B,

    "input": str(INPUT),
    "symbol": data["symbol"],
    "timeframe": data["timeframe"],
    "config": data["config"],

    "sample": {
        "weeks": n_weeks,
        "signals": sum(w["signals"] for w in weeks),
        "wins": sum(w["wins"] for w in weeks),
        "losses": sum(w["losses"] for w in weeks),
        "ambiguous": sum(w["ambiguous"] for w in weeks),
        "open_or_unresolved": sum(w["open_or_unresolved"] for w in weeks),
        "decisive": observed["decisive"],
    },

    "observed_baseline": {
        **observed,
        "wilson_95pct": {
            "lower": wilson_low,
            "upper": wilson_high,
        },
    },

    "weekly_blocks": [
        {
            "week_start_utc": w["week_start_utc"],
            "week_end_utc": w["week_end_utc"],
            "signals": w["signals"],
            "wins": w["wins"],
            "losses": w["losses"],
            "ambiguous": w["ambiguous"],
            "decisive": w["wins"] + w["losses"],
            "decisive_win_rate": w["decisive_win_rate"],
            "total_R": w["total_R"],
            "profit_factor": w["profit_factor"],
        }
        for w in weeks
    ],

    "bootstrap_95pct": {
        "win_rate": quantiles(bootstrap_wr),
        "total_R": quantiles(bootstrap_total_r),
        "profit_factor_finite_only": quantiles(finite_pf),
        "max_drawdown_R": quantiles(bootstrap_dd),
        "infinite_profit_factor_replicates": B - len(finite_pf),
    },

    "interpretation": {
        "purpose": "Descriptive uncertainty assessment of the frozen baseline over the observed four-week sample.",
        "wilson": "The Wilson interval describes uncertainty around the observed decisive trade win rate; it is not an out-of-sample guarantee.",
        "bootstrap": "The bootstrap resamples complete weeks with replacement to preserve within-week chronological structure and avoid treating all trades as independent Bernoulli observations.",
        "limits": [
            "Only four observed weekly blocks are available.",
            "Week-level resampling cannot establish independent out-of-sample validity.",
            "Historical observations may share regime, market, and execution dependencies.",
            "The bootstrap does not validate unresolved geometry.",
            "The bootstrap does not validate the 81-parameter grid.",
            "Ambiguous outcomes are excluded from decisive win-rate calculations and are not reassigned.",
            "No parameter promotion, rule promotion, BUY/SELL authorization, or live-trading authorization follows from this analysis."
        ],
    },

    "disposition": "DESCRIPTIVE_UNCERTAINTY_EVIDENCE_LIMITED_BY_FOUR_WEEK_BLOCK_COUNT",
    "guard": "RESEARCH_STATISTICS_ONLY_NO_RULE_OR_PARAMETER_PROMOTION",
}

with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print(json.dumps({
    "status": report["status"],
    "output": str(OUTPUT),
    "weeks": n_weeks,
    "signals": report["sample"]["signals"],
    "decisive": report["sample"]["decisive"],
    "ambiguous": report["sample"]["ambiguous"],
    "observed_wr": observed["win_rate"],
    "wilson_95pct": [wilson_low, wilson_high],
    "bootstrap_replicates": B,
}, indent=2))
