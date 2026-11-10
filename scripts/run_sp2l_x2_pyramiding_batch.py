from __future__ import annotations
"""Research-only X2 pyramiding batch. Offline OHLC replay; never imports MT5."""
import argparse
import csv
import hashlib
import json
import math
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from strategy_factory.x2_pyramiding_engine import replay_x2_signal
from strategy_factory.v3_management_engine import replay_management_trade, normalize_management_spec
from scripts.run_sp2l_v3_unified_management_matrix import load as load_frozen_inputs

CONTRACT = 100.0
VOLUME = 0.01
PULLBACK_R = 0.25
DISTANCE_PRICE = 0.3
ACTIVATIONS = (0.5, 0.75)
THRESHOLDS = (1.0, 1.5, 2.0)
PARENT_NAMES = {0.5: "FDT_A0.5_D0.3", 0.75: "FDT_A0.75_D0.3"}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def configurations():
    out = []
    for activation in ACTIVATIONS:
        parent = PARENT_NAMES[activation]
        out.append({"name": parent + "_X1_ONLY", "parent": parent,
                    "activation": activation, "threshold": None, "kind": "X1_ONLY"})
        for threshold in THRESHOLDS:
            out.append({"name": f"{parent}_X2_{threshold:g}R", "parent": parent,
                        "activation": activation, "threshold": threshold, "kind": "X1_X2"})
    assert len(out) == 8
    return out


def _utc_key(value):
    if not value:
        raise ValueError("realized leg missing exit timestamp")
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("exit timestamp must be timezone-aware")
    return dt.astimezone(timezone.utc).replace(second=0, microsecond=0).isoformat()


def cohort_drawdown(events):
    """events=(exit timestamp, realized USD); aggregate same-minute PnL first."""
    cohorts = defaultdict(float)
    for ts, pnl in events:
        cohorts[_utc_key(ts)] += float(pnl)
    equity = peak = max_dd = 0.0
    for ts in sorted(cohorts):
        equity += cohorts[ts]
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    return max_dd


def _leg_state(leg):
    if leg is None:
        return "NOT_OPENED"
    if leg.get("reason") == "M1_GAP_WHILE_OPEN":
        return "GAP_EXPOSED"
    if leg.get("ambiguous"):
        return "AMBIGUOUS"
    if leg.get("realized_usd") is not None:
        return "DECISIVE"
    return "OPEN_UNRESOLVED"


def _concentration(values):
    winners = sorted((float(x) for x in values if x > 0), reverse=True)
    total = sum(float(x) for x in values)
    return {f"gross_ex_top_{n}_winners_usd": total - sum(winners[:n])
            for n in (1, 3, 5, 10)}


def summarize(rows, kind):
    decisive = [r for r in rows if r["combined_decisive"]]
    pnl = [float(r["combined_gross_usd"]) for r in decisive]
    wins = [x for x in pnl if x > 0]
    losses = [x for x in pnl if x < 0]
    events = []
    for r in decisive:
        for leg in (r.get("x1"), r.get("x2")):
            if leg is not None:
                events.append((leg["exit_time_utc"], leg["realized_usd"]))
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    initial_budget = [float(r["initial_risk_usd"]) for r in decisive]
    net_r = sum(p / b for p, b in zip(pnl, initial_budget) if b > 0)
    out = {
        "signals": len(rows), "combined_decisive": len(decisive),
        "combined_ambiguous": sum(bool(r["combined_ambiguous"]) for r in rows),
        "combined_open_unresolved": sum(r["combined_state"] == "OPEN_UNRESOLVED" for r in rows),
        "combined_gap_exposed": sum(r["x1_state"] == "GAP_EXPOSED" or r["x2_state"] == "GAP_EXPOSED" for r in rows),
        "wins": len(wins), "losses": len(losses),
        "breakeven": len(decisive) - len(wins) - len(losses),
        "gross_usd": sum(pnl), "net_R_on_initial_signal_budget": net_r,
        "gross_profit_usd": gross_profit, "gross_loss_usd": gross_loss,
        "profit_factor": gross_profit / gross_loss if gross_loss else (None if not gross_profit else "infinity"),
        "average_R": net_r / len(decisive) if decisive else None,
        "max_drawdown_usd_exit_minute_cohorts": cohort_drawdown(events),
        "x1_decisive": sum(r["x1_state"] == "DECISIVE" for r in rows),
        "x1_ambiguous": sum(r["x1_state"] == "AMBIGUOUS" for r in rows),
        "x1_gap_exposed": sum(r["x1_state"] == "GAP_EXPOSED" for r in rows),
        "x1_open_unresolved": sum(r["x1_state"] == "OPEN_UNRESOLVED" for r in rows),
        "x2_opportunities": sum(r.get("x2_opportunities", 0) for r in rows),
        "x2_opened": sum(r["x2_state"] not in ("NOT_OPENED",) and r.get("x2") is not None for r in rows),
        "x2_skipped_risk_budget": sum(r.get("x2_skip_reason") == "X2_SKIPPED_RISK_BUDGET" for r in rows),
        "x2_ambiguous": sum(r["x2_state"] == "AMBIGUOUS" or r.get("x2_status") == "AMBIGUOUS" for r in rows),
        "x2_cancelled_or_other_skipped": sum(r.get("x2_status") in ("CANCELLED", "SKIPPED") and r.get("x2_skip_reason") != "X2_SKIPPED_RISK_BUDGET" for r in rows),
        "x2_decisive": sum(r["x2_state"] == "DECISIVE" for r in rows),
        "x2_gap_exposed": sum(r["x2_state"] == "GAP_EXPOSED" for r in rows),
        "x2_open_unresolved": sum(r["x2_state"] == "OPEN_UNRESOLVED" for r in rows),
        "x2_incremental_gross_usd": sum(float(r["x2"]["realized_usd"]) for r in decisive if r.get("x2") is not None),
        "x2_admissions": sum(r.get("x2_admission_risk_usd") is not None for r in rows),
        "max_combined_open_risk_usd": max((float(r.get("max_combined_open_risk_usd") or 0) for r in rows), default=0),
        "costs_modeled": False,
    }
    holds = [int(r["x2"]["bars_held"]) for r in rows if r.get("x2") is not None]
    out["x2_holding_bars_mean"] = statistics.mean(holds) if holds else None
    out["x2_holding_bars_median"] = statistics.median(holds) if holds else None
    out.update(_concentration(pnl))
    return out


def _record(candidate, result, config, index):
    x1 = result["x1"]
    x2 = result.get("x2")
    x1_state, x2_state = _leg_state(x1), _leg_state(x2)
    ambiguous = bool(result.get("combined_ambiguous"))
    decisive = bool(result.get("combined_decisive")) and not ambiguous
    if config["kind"] == "X1_ONLY":
        decisive = x1_state == "DECISIVE"
        ambiguous = x1_state == "AMBIGUOUS"
        combined = x1.get("realized_usd") if decisive else None
        combined_state = x1_state
        x2_state = "NOT_OPENED"
    else:
        combined = result.get("combined_gross_usd") if decisive else None
        if ambiguous:
            combined_state = "AMBIGUOUS"
        elif decisive:
            combined_state = "DECISIVE"
        elif x1_state == "GAP_EXPOSED" or x2_state == "GAP_EXPOSED":
            combined_state = "GAP_EXPOSED"
        else:
            combined_state = "OPEN_UNRESOLVED"
    return {
        "population_index": index, "trigger_time": candidate["trigger_time"],
        "direction": candidate["direction"], "signal_time_utc": candidate.get("signal_time_utc"),
        "source_variant": candidate.get("source_variant"), "config": config["name"],
        "kind": config["kind"], "initial_risk_usd": float(candidate["risk"]) * VOLUME * CONTRACT,
        "x1": x1, "x2": x2, "x1_state": x1_state, "x2_state": x2_state,
        "x2_status": result.get("x2_status", "NOT_TRIGGERED"),
        "x2_skip_reason": result.get("x2_skip_reason"),
        "x2_opportunities": result.get("x2_opportunities", 0),
        "x1_risk_at_x2_admission_usd": result.get("x1_risk_at_x2_admission_usd"),
        "x2_admission_risk_usd": result.get("x2_admission_risk_usd"),
        "max_combined_open_risk_usd": result.get("max_combined_open_risk_usd", 0),
        "combined_decisive": decisive, "combined_ambiguous": ambiguous,
        "combined_state": combined_state, "combined_gross_usd": combined,
    }


def run_batch(m1_path, entry_path, output_dir, point=0.01, contract_size=CONTRACT, volume=VOLUME):
    m1_path, entry_path, output_dir = Path(m1_path).resolve(), Path(entry_path).resolve(), Path(output_dir).resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing overwrite: {output_dir}")
    if not all(math.isfinite(float(x)) and float(x) > 0 for x in (point, contract_size, volume)):
        raise ValueError("point, contract_size and volume must be finite and positive")
    bars, population, inputs = load_frozen_inputs(m1_path, entry_path)
    configs = configurations()
    summaries, all_rows, paired = [], [], []
    baseline_by_parent = {}
    for config in configs:
        rows = []
        for i, candidate in enumerate(population, 1):
            activation = float(config["activation"])
            if config["kind"] == "X1_ONLY":
                spec = normalize_management_spec({
                    "mode": "TRAILING_R", "rr": None,
                    "activation_r": activation / float(candidate["risk"]),
                    "distance_r": DISTANCE_PRICE / float(candidate["risk"]),
                })
                result = replay_management_trade(candidate, bars, spec, mt5_point=point,
                    contract_size=contract_size, volume=volume)
                # Adapt the X1-only management result to the common leg schema.
                leg = dict(result)
                leg.setdefault("initial_sl", candidate["sl"])
                leg.setdefault("exit_time_utc", result.get("exit_time_utc"))
                leg.setdefault("realized_usd", result.get("realized_usd"))
                leg.setdefault("ambiguous", bool(result.get("ambiguous")))
                result = {"x1": leg, "x2": None, "combined_decisive":
                    leg.get("realized_usd") is not None and not leg.get("ambiguous"),
                    "combined_ambiguous": bool(leg.get("ambiguous")),
                    "combined_gross_usd": leg.get("realized_usd"),
                    "x2_status": "NOT_TRIGGERED", "x2_opportunities": 0}
            else:
                result = replay_x2_signal(candidate, bars, activation_price=activation,
                    trail_distance_price=DISTANCE_PRICE, threshold_r=float(config["threshold"]),
                    pullback_r=PULLBACK_R, volume=volume, contract_size=contract_size)
            rows.append(_record(candidate, result, config, i))
        sm = summarize(rows, config["kind"])
        sm.update({"config": config["name"], "parent": config["parent"],
                   "kind": config["kind"], "activation_price": activation,
                   "trail_distance_price": DISTANCE_PRICE, "threshold_R": config["threshold"]})
        summaries.append(sm)
        all_rows.extend(rows)
        if config["kind"] == "X1_ONLY":
            baseline_by_parent[config["parent"]] = {r["population_index"]: r for r in rows}
    for config in configs:
        if config["kind"] != "X1_X2":
            continue
        baseline = baseline_by_parent[config["parent"]]
        current = {r["population_index"]: r for r in all_rows if r["config"] == config["name"]}
        deltas = []
        for idx in sorted(baseline):
            b, x = baseline[idx], current[idx]
            if b["combined_decisive"] and x["combined_decisive"]:
                deltas.append(float(x["combined_gross_usd"]) - float(b["combined_gross_usd"]))
        paired.append({"config": config["name"], "parent": config["parent"],
                       "paired_decisive_n": len(deltas), "paired_delta_gross_usd": sum(deltas),
                       "x2_better": sum(d > 1e-12 for d in deltas),
                       "x1_only_better": sum(d < -1e-12 for d in deltas),
                       "equal": sum(abs(d) <= 1e-12 for d in deltas)})
    output_dir.mkdir(parents=True, exist_ok=False)
    stem = "SP2L_X2_PYRAMIDING_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    trades_path, summary_path = output_dir / (stem + "_TRADES.csv"), output_dir / (stem + "_SUMMARY.csv")
    pair_path, manifest_path = output_dir / (stem + "_PAIRED.csv"), output_dir / (stem + "_MANIFEST.json")
    def write_csv(path, rows):
        with path.open("x", encoding="utf-8-sig", newline="") as f:
            fields = list(dict.fromkeys(k for row in rows for k in row))
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in row.items()})
    write_csv(trades_path, all_rows)
    write_csv(summary_path, summaries)
    write_csv(pair_path, paired)
    manifest = {
        "research_only": True, "canonical": False, "mt5_accessed": False,
        "signal_rebuild": False, "configurations": configs, "population_count": len(population),
        "symbol": "XAUUSD.ecn", "timeframe": "M1", "inputs": inputs,
        "risk_budget": "X1 initial risk * fixed volume * contract; X2 admitted only within residual budget",
        "volume": volume, "contract_size": contract_size, "point_metadata_only": point,
        "pullback_R": PULLBACK_R, "trailing_distance_price": DISTANCE_PRICE,
        "costs": "SPREAD_COMMISSION_SLIPPAGE_NOT_MODELED",
        "drawdown": "same-minute realized leg PnL aggregated before equity/drawdown; ambiguous combined signals excluded",
        "semantics": "completed bars; X1 entry bar excluded; X2 next M1 open; independent leg stops; gaps ambiguous; no final TP",
        "artifacts": {p.name: {"sha256": sha(p), "bytes": p.stat().st_size}
                      for p in (trades_path, summary_path, pair_path)},
    }
    with manifest_path.open("x", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    sums_path = output_dir / (stem + "_SHA256SUMS.txt")
    with sums_path.open("x", encoding="utf-8") as f:
        for p in (trades_path, summary_path, pair_path, manifest_path):
            f.write(f"{sha(p)}  {p.name}\n")
    return {"output_dir": str(output_dir), "summaries": summaries, "paired": paired,
            "manifest": str(manifest_path), "input_hashes": inputs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m1-csv", required=True)
    parser.add_argument("--entry-csv", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--point", type=float, default=0.01)
    parser.add_argument("--contract-size", type=float, default=CONTRACT)
    parser.add_argument("--volume", type=float, default=VOLUME)
    args = parser.parse_args()
    result = run_batch(args.m1_csv, args.entry_csv, args.output_dir,
                       args.point, args.contract_size, args.volume)
    print(json.dumps({"status": "COMPLETE", "output_dir": result["output_dir"],
                      "summaries": result["summaries"], "paired": result["paired"],
                      "research_only": True, "canonical": False, "mt5_accessed": False},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
