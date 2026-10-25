#!/usr/bin/env python3
"""Apply explicit round-trip transaction costs to an existing SP2L trailing matrix.

This is a post-processing audit: source JSON/CSV artifacts are never modified.
Cost is charged once per completed, decisive trade (entry through exit).
Ambiguous and unresolved trades remain excluded from decisive net metrics.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path


def as_float(value, *, default=None):
    if value is None or value == "":
        return default
    return float(value)


def is_true(value):
    return str(value).strip().lower() in {"true", "1", "yes"}


def scenario_key(row):
    def norm(v):
        if v is None or str(v).strip() == "":
            return ""
        return f"{float(v):.8g}"
    return (row.get("scenario", ""), norm(row.get("activation_price")), norm(row.get("trail_distance_price")))


def summarize_net(rows, cost_usd, volume, contract_size):
    decisive = []
    for row in rows:
        gross_r = as_float(row.get("realized_R"))
        risk_price = as_float(row.get("risk_price"))
        ambiguous = is_true(row.get("ambiguous"))
        if ambiguous or gross_r is None:
            row["cost_usd"] = ""
            row["risk_usd"] = ""
            row["cost_R"] = ""
            row["net_R"] = ""
            row["net_outcome"] = "AMBIGUOUS" if ambiguous else "UNRESOLVED"
            continue
        if risk_price is None or risk_price <= 0:
            raise ValueError(f"Invalid risk_price for decisive trade: {row}")
        risk_usd = risk_price * volume * contract_size
        if not math.isfinite(risk_usd) or risk_usd <= 0:
            raise ValueError(f"Invalid dollar risk for trade: {row}")
        cost_r = cost_usd / risk_usd
        net_r = gross_r - cost_r
        row["cost_usd"] = f"{cost_usd:.8f}"
        row["risk_usd"] = f"{risk_usd:.8f}"
        row["cost_R"] = f"{cost_r:.10f}"
        row["net_R"] = f"{net_r:.10f}"
        row["net_outcome"] = "WIN" if net_r > 1e-12 else ("LOSS" if net_r < -1e-12 else "BREAKEVEN")
        decisive.append((row, net_r))

    ordered = sorted(
        decisive,
        key=lambda item: (
            int(float(item[0]["exit_time"])) if item[0].get("exit_time") else 2**63 - 1,
            int(float(item[0].get("trigger_time") or 0)),
        ),
    )
    wins = [r for r, value in ordered if value > 1e-12]
    losses = [r for r, value in ordered if value < -1e-12]
    breakevens = [r for r, value in ordered if abs(value) <= 1e-12]
    net_total = sum(value for _, value in ordered)
    gross_win = sum(value for _, value in ordered if value > 1e-12)
    gross_loss = abs(sum(value for _, value in ordered if value < -1e-12))

    equity = peak = max_dd = 0.0
    consecutive = longest_consecutive = 0
    for _, value in ordered:
        equity += value
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
        if value < -1e-12:
            consecutive += 1
            longest_consecutive = max(longest_consecutive, consecutive)
        else:
            consecutive = 0

    return {
        "net_cost_usd_per_trade": cost_usd,
        "net_cost_model": "fixed round-trip cost per completed decisive trade",
        "volume_lots": volume,
        "contract_size": contract_size,
        "net_decisive": len(ordered),
        "net_wins": len(wins),
        "net_losses": len(losses),
        "net_breakeven": len(breakevens),
        "net_win_rate_pct": 100 * len(wins) / len(ordered) if ordered else None,
        "net_R": net_total,
        "net_profit_factor": gross_win / gross_loss if gross_loss > 0 else None,
        "net_max_drawdown_R": max_dd,
        "net_max_consecutive_losses": longest_consecutive,
        "costed_trades": len(ordered),
        "total_cost_usd": cost_usd * len(ordered),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--matrix-csv", required=True, type=Path)
    ap.add_argument("--trades-csv", required=True, type=Path)
    ap.add_argument("--cost-usd", type=float, default=0.05,
                    help="round-trip cost per trade, charged once (default: 0.05 USD)")
    ap.add_argument("--volume", type=float, default=0.01,
                    help="lots used to convert initial price risk to USD (default: 0.01)")
    ap.add_argument("--contract-size", type=float, default=100.0,
                    help="contract size in underlying units per lot (default: 100)")
    ap.add_argument("--output-prefix", type=Path, default=None,
                    help="output path prefix; defaults to the matrix CSV path without _matrix.csv")
    args = ap.parse_args()

    if not args.matrix_csv.is_file() or not args.trades_csv.is_file():
        raise FileNotFoundError("Both --matrix-csv and --trades-csv must exist.")
    if not math.isfinite(args.cost_usd) or args.cost_usd < 0:
        raise ValueError("--cost-usd must be finite and >= 0")
    if not math.isfinite(args.volume) or args.volume <= 0:
        raise ValueError("--volume must be finite and > 0")
    if not math.isfinite(args.contract_size) or args.contract_size <= 0:
        raise ValueError("--contract-size must be finite and > 0")

    with args.matrix_csv.open(newline="", encoding="utf-8-sig") as f:
        matrix = list(csv.DictReader(f))
    with args.trades_csv.open(newline="", encoding="utf-8-sig") as f:
        trades = list(csv.DictReader(f))
    if not matrix or not trades:
        raise ValueError("Input matrix/trades CSV is empty.")
    required = {"scenario", "risk_price", "realized_R", "exit_time", "trigger_time", "ambiguous"}
    missing = required - set(trades[0])
    if missing:
        raise ValueError(f"Trades CSV missing required columns: {sorted(missing)}")

    grouped = {}
    for trade in trades:
        grouped.setdefault(scenario_key(trade), []).append(trade)

    result_rows = []
    summaries = {}
    for source in matrix:
        key = scenario_key(source)
        group = grouped.get(key, [])
        if not group:
            raise ValueError(f"No trade rows match matrix scenario {key}")
        summary = summarize_net(group, args.cost_usd, args.volume, args.contract_size)
        summaries[key] = summary
        out = {}
        for name, value in source.items():
            if name == "net_R":
                out["gross_net_R"] = value
            else:
                out[name] = value
            if name in {"signals", "decisive", "wins", "losses", "ambiguous", "open_or_unresolved",
                        "win_rate_decisive_pct", "profit_factor", "max_drawdown_R",
                        "max_consecutive_losses"}:
                out[f"gross_{name}"] = value
        out.update(summary)
        result_rows.append(out)

    prefix = args.output_prefix
    if prefix is None:
        name = args.matrix_csv.name
        if name.endswith("_matrix.csv"):
            name = name[:-len("_matrix.csv")]
        else:
            name = args.matrix_csv.stem
        prefix = args.matrix_csv.with_name(name + "_COST_ADJUSTED")
    prefix.parent.mkdir(parents=True, exist_ok=True)

    matrix_out = prefix.with_name(prefix.name + "_matrix.csv")
    trades_out = prefix.with_name(prefix.name + "_trades.csv")
    snapshot_out = prefix.with_name(prefix.name + "_SNAPSHOT.md")
    json_out = prefix.with_suffix(".json")

    fields = list(dict.fromkeys(k for row in result_rows for k in row))
    with matrix_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(result_rows)

    trade_fields = list(dict.fromkeys(k for row in trades for k in row))
    with trades_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=trade_fields)
        writer.writeheader()
        writer.writerows(trades)

    payload = {
        "status": "COMPLETE",
        "research_only": True,
        "source_matrix_csv": str(args.matrix_csv.resolve()),
        "source_trades_csv": str(args.trades_csv.resolve()),
        "cost_model": {
            "round_trip_cost_usd_per_completed_decisive_trade": args.cost_usd,
            "volume_lots": args.volume,
            "contract_size": args.contract_size,
            "risk_usd_formula": "risk_price * volume_lots * contract_size",
            "cost_R_formula": "cost_usd / risk_usd",
            "cost_applied_to": "completed, non-ambiguous trades only",
            "ambiguous_and_unresolved": "excluded from net decisive metrics; preserved and not assigned a guessed outcome",
        },
        "scenario_count": len(result_rows),
        "scenarios": result_rows,
    }
    json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    snapshot_out.write_text(
        "# SP2L V3 Trailing Matrix — Round-Trip Cost-Adjusted Audit\n\n"
        f"Created UTC: {datetime.now(timezone.utc).isoformat()}\n"
        f"Source matrix: {args.matrix_csv}\nSource trades: {args.trades_csv}\n"
        f"Round-trip cost: \${args.cost_usd:.4f} per completed decisive trade\n"
        f"Volume: {args.volume} lots; contract size: {args.contract_size}\n"
        "Risk USD = initial risk price × volume × contract size. Cost R = round-trip cost USD / risk USD.\n"
        "Gross source artifacts are not modified. Ambiguous and unresolved outcomes are not assigned invented net results.\n"
        "Costs are fixed per trade; this is a minimum-cost sensitivity analysis, not a full spread/slippage replay.\n"
        "Independent trades may overlap; trade-level drawdown is not portfolio/account drawdown.\n"
        "This is research-only and does not authorize live execution.\n\n"
        f"Matrix CSV: {matrix_out.name}\nTrades CSV: {trades_out.name}\nJSON: {json_out.name}\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": "COMPLETE",
        "scenario_count": len(result_rows),
        "source_trades": len(trades),
        "costed_trades_total_across_scenarios": sum(s["costed_trades"] for s in summaries.values()),
        "round_trip_cost_usd": args.cost_usd,
        "matrix_csv": str(matrix_out),
        "trades_csv": str(trades_out),
        "json": str(json_out),
        "snapshot": str(snapshot_out),
        "research_only": True,
    }, indent=2))


if __name__ == "__main__":
    main()
