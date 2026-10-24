import json
from pathlib import Path
from datetime import datetime, timezone
from statistics import mean

INPUT = Path("artifacts/SP2L_pl_pip_accounting_2026-09-14_2026-09-18.json")
OUTPUT = Path("artifacts/SP2L_temporal_rolling_stability_2026-09-14_2026-09-18.json")

data = json.loads(INPUT.read_text(encoding="utf-8"))
rows = [r for r in data["signals"] if r["outcome"] != "AMBIGUOUS"]

def dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)

def metrics(items):
    wins = [x for x in items if x["outcome"] == "WIN"]
    losses = [x for x in items if x["outcome"] == "LOSS"]
    decisive = len(wins) + len(losses)
    net = sum(float(x["realized_pips"]) for x in items)
    gp = sum(float(x["realized_pips"]) for x in wins)
    gl = abs(sum(float(x["realized_pips"]) for x in losses))
    return {
        "n": decisive,
        "wins": len(wins),
        "losses": len(losses),
        "win_rate_pct": 100 * len(wins) / decisive if decisive else None,
        "net_pips": net,
        "profit_factor": gp / gl if gl else None,
        "avg_win_pips": mean([float(x["realized_pips"]) for x in wins]) if wins else None,
        "avg_loss_pips_abs": mean([abs(float(x["realized_pips"])) for x in losses]) if losses else None,
    }

parsed = sorted([(dt(x["signal_time_utc"]), x) for x in rows], key=lambda z: z[0])

# Fixed calendar buckets for transparent temporal decomposition.
bounds = [
    ("2026-09-14", "2026-09-14T23:59:59+00:00"),
    ("2026-09-15", "2026-09-15T23:59:59+00:00"),
    ("2026-09-16", "2026-09-16T23:59:59+00:00"),
    ("2026-09-17", "2026-09-17T23:59:59+00:00"),
    ("2026-09-18", "2026-09-18T23:59:59+00:00"),
]

daily = []
for label, end_s in bounds:
    start = datetime.fromisoformat(label + "T00:00:00+00:00")
    end = datetime.fromisoformat(end_s)
    items = [x for t, x in parsed if start <= t <= end]
    m = metrics(items)
    m.update({"window_start_utc": start.isoformat(), "window_end_utc": end.isoformat()})
    daily.append(m)

# Rolling windows over chronological signals: 10 and 15 decisive trades.
rolling = []
for size in [10, 15]:
    if len(parsed) < size:
        continue
    for i in range(0, len(parsed) - size + 1):
        items = [x for _, x in parsed[i:i+size]]
        m = metrics(items)
        m.update({
            "window_type": f"{size}_decisive_trades",
            "start_signal_time_utc": parsed[i][0].isoformat(),
            "end_signal_time_utc": parsed[i+size-1][0].isoformat(),
        })
        rolling.append(m)

def summarize(items):
    wrs = [x["win_rate_pct"] for x in items if x["win_rate_pct"] is not None]
    nets = [x["net_pips"] for x in items]
    pfs = [x["profit_factor"] for x in items if x["profit_factor"] is not None]
    return {
        "windows": len(items),
        "win_rate_min_pct": min(wrs) if wrs else None,
        "win_rate_max_pct": max(wrs) if wrs else None,
        "win_rate_mean_pct": mean(wrs) if wrs else None,
        "net_pips_min": min(nets) if nets else None,
        "net_pips_max": max(nets) if nets else None,
        "positive_net_windows": sum(x > 0 for x in nets),
        "nonpositive_net_windows": sum(x <= 0 for x in nets),
        "profit_factor_min": min(pfs) if pfs else None,
        "profit_factor_max": max(pfs) if pfs else None,
    }

result = {
    "research_only": True,
    "artifact_type": "SP2L_TEMPORAL_ROLLING_STABILITY",
    "input_artifact": str(INPUT),
    "input_artifact_sha256": data.get("source_artifact_sha256"),
    "sample": {
        "signals_in_input": len(data["signals"]),
        "decisive_used": len(rows),
        "ambiguous_excluded": sum(x["outcome"] == "AMBIGUOUS" for x in data["signals"]),
    },
    "daily_windows": daily,
    "rolling_windows": {
        "10_trade": {
            "summary": summarize([x for x in rolling if x["window_type"] == "10_decisive_trades"]),
            "windows": [x for x in rolling if x["window_type"] == "10_decisive_trades"],
        },
        "15_trade": {
            "summary": summarize([x for x in rolling if x["window_type"] == "15_decisive_trades"]),
            "windows": [x for x in rolling if x["window_type"] == "15_decisive_trades"],
        },
    },
    "guard": "RESEARCH_TEMPORAL_STABILITY_ONLY; NO_RULE_OR_PARAMETER_PROMOTION",
    "limitations": [
        "Only 37 decisive signals are available in this historical window.",
        "Daily buckets can have very small samples and are descriptive.",
        "Rolling windows overlap and are not independent samples.",
        "This is not a fresh post-boundary holdout.",
        "No temporal rule, parameter, direction filter, or trading authorization is inferred."
    ]
}

OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({
    "status": "ANALYZED",
    "output": str(OUTPUT),
    "daily_windows": result["daily_windows"],
    "rolling_summary": result["rolling_windows"]
}, ensure_ascii=False, indent=2))
