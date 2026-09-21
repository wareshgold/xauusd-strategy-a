from __future__ import annotations

import json
from pathlib import Path
from statistics import mean


SL_PIPS = (50, 60, 70, 80)
RR = 2.0


def summarize(events: list[dict], sl_pips: int) -> dict:
    subset = [e for e in events if e.get("sl_pips") == sl_pips]
    resolved = [e for e in subset if e.get("outcome") in {"WIN", "LOSS"}]
    wins = sum(e["outcome"] == "WIN" for e in resolved)
    losses = sum(e["outcome"] == "LOSS" for e in resolved)
    r_values = [RR if e["outcome"] == "WIN" else -1.0 for e in resolved]
    gross_profit = sum(r for r in r_values if r > 0)
    gross_loss = -sum(r for r in r_values if r < 0)
    return {
        "sl_pips": sl_pips,
        "rr": RR,
        "candidate_count": len(subset),
        "resolved_count": len(resolved),
        "unresolved_count": len(subset) - len(resolved),
        "wins": wins,
        "losses": losses,
        "win_rate": (wins / len(resolved)) if resolved else None,
        "mean_r": mean(r_values) if r_values else None,
        "expectancy_r": mean(r_values) if r_values else None,
        "profit_factor": (gross_profit / gross_loss) if gross_loss else None,
    }


def run(input_path: Path, output_path: Path) -> dict:
    payload = json.loads(input_path.read_text())
    if payload.get("contract") != "SP2L_WORKING_RULES_EXPERIMENT_2026-09-15":
        raise ValueError("unexpected experiment contract")
    events = payload.get("events", [])
    for event in events:
        if event.get("outcome") == "WIN" and event.get("r") not in (None, RR):
            raise ValueError("WIN outcome must use frozen 2R result")
        if event.get("outcome") == "LOSS" and event.get("r") not in (None, -1.0):
            raise ValueError("LOSS outcome must use frozen -1R result")
        if event.get("outcome") not in {"WIN", "LOSS", "UNRESOLVED"}:
            raise ValueError("invalid outcome")
    report = {
        "status": "EXPLORATORY_RESULT_AVAILABLE" if events else "NO_EVENTS",
        "contract": payload["contract"],
        "dataset_sha256": payload.get("dataset_sha256"),
        "events_supplied": len(events),
        "parameter_grid": {"sl_pips": list(SL_PIPS), "rr": RR, "ma_timeframe": "M15", "ma_length": 50},
        "results": [summarize(events, sl) for sl in SL_PIPS],
        "production_signal": False,
        "canonical_geometry_frozen": False,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n")
    return report
