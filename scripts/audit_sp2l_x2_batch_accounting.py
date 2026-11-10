#!/usr/bin/env python3
"""Offline forensic audit of X1/X2 batch accounting; reads existing artifacts only."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def read_rows(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def as_bool(value):
    return str(value).strip().lower() == "true"


def as_float(value):
    return None if value in (None, "") else float(value)


def audit(path):
    rows = read_rows(path)
    baseline = {}
    experiments = defaultdict(dict)
    for row in rows:
        row["x1"] = json.loads(row["x1"]) if row.get("x1") else None
        row["x2"] = json.loads(row["x2"]) if row.get("x2") else None
        key = (row["parent"], int(row["population_index"]))
        if row["kind"] == "X1_ONLY":
            baseline[key] = row
        else:
            experiments[(row["parent"], row["config"])][int(row["population_index"])] = row

    report = []
    for (parent, config), by_index in sorted(experiments.items()):
        paired = []
        path_mismatches = 0
        x1_delta = x2_pnl = paired_delta = 0.0
        for index, row in by_index.items():
            base = baseline[(parent, index)]
            if not (as_bool(base["combined_decisive"]) and as_bool(row["combined_decisive"])):
                continue
            b1, x1, x2 = base["x1"], row["x1"], row["x2"]
            if not b1 or not x1 or as_float(b1.get("realized_usd")) is None or as_float(x1.get("realized_usd")) is None:
                continue
            paired.append(index)
            fields = ("exit_price", "exit_time_utc", "reason", "final_sl", "trailing_updates", "realized_usd")
            if any(b1.get(k) != x1.get(k) for k in fields):
                path_mismatches += 1
            dx1 = float(x1["realized_usd"]) - float(b1["realized_usd"])
            dx2 = float(x2["realized_usd"]) if x2 and as_float(x2.get("realized_usd")) is not None else 0.0
            dtotal = float(row["combined_gross_usd"]) - float(base["combined_gross_usd"])
            x1_delta += dx1
            x2_pnl += dx2
            paired_delta += dtotal
        attempts = sum(as_float(r["x2_admission_risk_usd"]) is not None for r in by_index.values())
        opened = sum(r["x2"] is not None for r in by_index.values())
        risk_skips = sum(r.get("x2_skip_reason") == "X2_SKIPPED_RISK_BUDGET" for r in by_index.values())
        report.append({
            "config": config, "paired_n": len(paired),
            "x1_path_mismatches": path_mismatches,
            "x1_delta_usd": round(x1_delta, 4),
            "x2_realized_usd": round(x2_pnl, 4),
            "decomposed_delta_usd": round(x1_delta + x2_pnl, 4),
            "paired_delta_usd": round(paired_delta, 4),
            "decomposition_error_usd": round(paired_delta - x1_delta - x2_pnl, 8),
            "x2_admission_attempts": attempts, "x2_opened": opened,
            "x2_risk_budget_rejections": risk_skips,
        })
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--trades-csv", required=True)
    args = p.parse_args()
    for row in audit(args.trades_csv):
        print(json.dumps(row, sort_keys=True))


if __name__ == "__main__":
    main()
