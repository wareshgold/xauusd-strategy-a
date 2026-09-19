import json
from pathlib import Path
from statistics import mean, median, pstdev

INPUT = Path("artifacts/SP2L_pl_pip_accounting_2026-09-14_2026-09-18.json")
OUTPUT = Path("artifacts/SP2L_performance_decomposition_2026-09-14_2026-09-18.json")

data = json.loads(INPUT.read_text(encoding="utf-8"))
rows = data["signals"]

decisive = [r for r in rows if r["realized_pips"] is not None]
wins = [r for r in decisive if r["outcome"] == "WIN"]
losses = [r for r in decisive if r["outcome"] == "LOSS"]

def stats(values):
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "mean": mean(values),
        "median": median(values),
        "stdev_population": pstdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }

def pct(n, d):
    return (100.0 * n / d) if d else None

def group_metrics(items):
    w = [x for x in items if x["outcome"] == "WIN"]
    l = [x for x in items if x["outcome"] == "LOSS"]
    return {
        "signals": len(items),
        "wins": len(w),
        "losses": len(l),
        "decisive_win_rate_pct": pct(len(w), len(w) + len(l)),
        "net_pips": sum(x["realized_pips"] for x in items),
        "gross_profit_pips": sum(x["realized_pips"] for x in w),
        "gross_loss_pips_abs": abs(sum(x["realized_pips"] for x in l)),
        "net_pl_0_01_lot_usd": sum(x["realized_pl_account_currency"] for x in items),
        "profit_factor": (
            sum(x["realized_pl_account_currency"] for x in w)
            / abs(sum(x["realized_pl_account_currency"] for x in l))
        ) if l else None,
    }

by_direction = {
    direction: group_metrics([x for x in decisive if x["direction"] == direction])
    for direction in sorted({x["direction"] for x in decisive})
}

winner_pips = [x["realized_pips"] for x in wins]
loser_abs_pips = [abs(x["realized_pips"]) for x in losses]

# Sequential equity / drawdown in the archived signal order.
equity = 0.0
peak = 0.0
peak_index = None
max_dd = 0.0
max_dd_from = None
max_dd_to = None
curve = []
for i, x in enumerate(decisive):
    equity += x["realized_pl_account_currency"]
    if equity > peak:
        peak = equity
        peak_index = i
    dd = peak - equity
    if dd > max_dd:
        max_dd = dd
        max_dd_from = peak_index
        max_dd_to = i
    curve.append({"index": i, "equity_usd_0_01_lot": equity, "drawdown_usd": dd})

# Fixed-volume scaling is arithmetic only; no execution simulation.
lot_scales = {}
for lot in [0.01, 0.05, 0.10, 0.50, 1.00]:
    factor = lot / 0.01
    lot_scales[str(lot)] = {
        "net_pl_usd": sum(x["realized_pl_account_currency"] for x in decisive) * factor,
        "gross_profit_usd": sum(x["realized_pl_account_currency"] for x in wins) * factor,
        "gross_loss_usd_abs": abs(sum(x["realized_pl_account_currency"] for x in losses)) * factor,
        "max_sequential_drawdown_usd": max_dd * factor,
    }

out = {
    "research_only": True,
    "artifact_type": "SP2L_PERFORMANCE_DECOMPOSITION",
    "input_artifact": str(INPUT),
    "input_artifact_sha256": data.get("source_artifact_sha256"),
    "accounting_inputs": data["accounting_inputs"],
    "counts": {
        "all_signals": len(rows),
        "decisive": len(decisive),
        "wins": len(wins),
        "losses": len(losses),
        "ambiguous": sum(x["outcome"] == "AMBIGUOUS" for x in rows),
    },
    "r_to_price_accounting": {
        "realized_pips_all_decisive": sum(x["realized_pips"] for x in decisive),
        "winner_pip_distribution": stats(winner_pips),
        "loser_absolute_pip_distribution": stats(loser_abs_pips),
        "average_win_pips": mean(winner_pips) if winner_pips else None,
        "average_loss_pips_abs": mean(loser_abs_pips) if loser_abs_pips else None,
        "win_loss_pip_ratio": (
            mean(winner_pips) / mean(loser_abs_pips)
        ) if winner_pips and loser_abs_pips else None,
    },
    "by_direction": by_direction,
    "lot_scaling_arithmetic": lot_scales,
    "sequential_drawdown": {
        "max_drawdown_usd_0_01_lot": max_dd,
        "peak_signal_index": max_dd_from,
        "trough_signal_index": max_dd_to,
    },
    "canonicalization_guard": "RESEARCH_ACCOUNTING_ONLY; NO_STRATEGY_RULE_PROMOTED",
    "limitations": [
        "Ambiguous outcome is excluded from realized P/L.",
        "Commission, swap, slippage and spread execution effects are not reconstructed here.",
        "Lot scaling is arithmetic, not a live execution simulation.",
        "Historical signal ordering is used for sequential drawdown.",
        "No geometry, trigger, fill, pending-order or execution rule is inferred."
    ],
}

OUTPUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({
    "status": "ANALYZED",
    "output": str(OUTPUT),
    "counts": out["counts"],
    "r_to_price_accounting": out["r_to_price_accounting"],
    "by_direction": out["by_direction"],
    "lot_scaling_arithmetic": out["lot_scaling_arithmetic"],
    "sequential_drawdown": out["sequential_drawdown"],
}, ensure_ascii=False, indent=2))
