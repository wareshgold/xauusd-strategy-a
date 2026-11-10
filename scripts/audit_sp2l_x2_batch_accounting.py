#!/usr/bin/env python3
"""Offline forensic audit of X1/X2 batch accounting; reads existing artifacts only."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

PARENTS = ("FDT_A0.5_D0.3", "FDT_A0.75_D0.3")


def read_rows(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {
            "population_index", "config", "kind", "x1", "x2",
            "combined_decisive", "combined_gross_usd",
            "x2_admission_risk_usd", "x2_skip_reason",
        }
        missing = sorted(required - set(reader.fieldnames or ()))
        if missing:
            raise ValueError(f"TRADES_CSV_MISSING_COLUMNS: {missing}; found={reader.fieldnames}")
        return list(reader)


def as_bool(value):
    return str(value).strip().lower() == "true"


def as_float(value):
    return None if value in (None, "") else float(value)


def parent_from_config(config):
    matches = [p for p in PARENTS if config == p + "_X1_ONLY" or config.startswith(p + "_X2_")]
    if len(matches) != 1:
        raise ValueError(f"UNRECOGNIZED_OR_AMBIGUOUS_CONFIG: {config!r}")
    return matches[0]


def audit(path):
    rows = read_rows(path)
    baseline = {}
    experiments = defaultdict(dict)
    for row in rows:
        parent = parent_from_config(row["config"])
        row["_parent"] = parent
        row["_x1"] = json.loads(row["x1"]) if row.get("x1") else None
        row["_x2"] = json.loads(row["x2"]) if row.get("x2") else None
        key = (parent, int(row["population_index"]))
        if row["kind"] == "X1_ONLY":
            baseline[key] = row
        elif row["kind"] == "X1_X2":
            experiments[(parent, row["config"])][int(row["population_index"])] = row
        else:
            raise ValueError(f"UNRECOGNIZED_KIND: {row['kind']!r}")

    report = []
    for (parent, config), by_index in sorted(experiments.items()):
        paired_n = path_mismatches = 0
        x1_delta = x2_pnl = paired_delta = 0.0
        for index, row in sorted(by_index.items()):
            base = baseline.get((parent, index))
            if base is None:
                raise ValueError(f"MISSING_X1_BASELINE: parent={parent}, population_index={index}")
            if not (as_bool(base["combined_decisive"]) and as_bool(row["combined_decisive"])):
                continue
            b1, x1, x2 = base["_x1"], row["_x1"], row["_x2"]
            if not b1 or not x1 or as_float(b1.get("realized_usd")) is None or as_float(x1.get("realized_usd")) is None:
                continue
            paired_n += 1
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
        opened = sum(r["_x2"] is not None for r in by_index.values())
        risk_skips = sum(r.get("x2_skip_reason") == "X2_SKIPPED_RISK_BUDGET" for r in by_index.values())
        report.append({
            "parent": parent, "config": config, "paired_n": paired_n,
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
