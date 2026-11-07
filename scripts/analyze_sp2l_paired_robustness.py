#!/usr/bin/env python
"""Robustness diagnostics for anonymized SP2L V3.1 paired outcomes.

Reads paired_trade_results_anonymized.csv emitted by
compare_sp2l_v31_trailing_vs_fixed_rr.py. Does not access MT5, the runner,
orders, positions, or private raw history. Trade order is the source CSV order
(entry chronology); no calendar-day inference is made because dates are
intentionally absent from the anonymized file.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

RRS = range(1, 7)
BLOCK_LENGTHS = (2, 3, 5, 10)
REPS = 20000
SEED = 20261107


def f(row, key):
    value = row.get(key, "")
    return None if value in (None, "") else float(value)


def mean_ci(values, reps=REPS, seed=SEED):
    x = np.asarray(values, dtype=float)
    if len(x) < 2:
        return None
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(reps, len(x)))
    means = x[idx].mean(axis=1)
    return [round(float(np.quantile(means, .025)), 4),
            round(float(np.quantile(means, .975)), 4)]


def block_ci(values, block_len, reps=REPS, seed=SEED):
    """Circular moving-block bootstrap; preserves short-range order locally."""
    x = np.asarray(values, dtype=float)
    n = len(x)
    if n < 2:
        return None
    L = min(block_len, n)
    blocks_needed = math.ceil(n / L)
    offsets = np.arange(L)
    rng = np.random.default_rng(seed + block_len)
    means = np.empty(reps)
    for i in range(reps):
        starts = rng.integers(0, n, size=blocks_needed)
        sample = np.concatenate([x[(s + offsets) % n] for s in starts])[:n]
        means[i] = sample.mean()
    return [round(float(np.quantile(means, .025)), 4),
            round(float(np.quantile(means, .975)), 4)]


def summarize(values):
    x = np.asarray(values, dtype=float)
    if not len(x):
        return {"n": 0}
    positive = x[x > .005]
    negative = x[x < -.005]
    total_positive = float(positive.sum()) if len(positive) else 0.0
    sorted_pos = np.sort(positive)[::-1]
    concentration = {}
    for k in (1, 3, 5):
        concentration[f"top_{k}_share_of_positive_delta"] = (
            round(float(sorted_pos[:k].sum() / total_positive), 4)
            if total_positive > 0 else None
        )
    leave_one = [float(np.delete(x, i).mean()) for i in range(len(x))] if len(x) > 1 else []
    trimmed = np.sort(x)
    trim_n = int(len(trimmed) * .10)
    if trim_n and len(trimmed) - 2 * trim_n > 0:
        trimmed = trimmed[trim_n:-trim_n]
    return {
        "n": int(len(x)),
        "sum_delta_usd": round(float(x.sum()), 2),
        "mean_delta_usd": round(float(x.mean()), 4),
        "median_delta_usd": round(float(np.median(x)), 4),
        "actual_better": int(len(positive)),
        "fixed_rr_better": int(len(negative)),
        "near_equal": int(len(x) - len(positive) - len(negative)),
        "iid_bootstrap_95pct_ci_mean": mean_ci(x),
        "trimmed_10pct_mean_usd": round(float(trimmed.mean()), 4),
        "leave_one_out_mean_min_usd": round(min(leave_one), 4) if leave_one else None,
        "leave_one_out_mean_max_usd": round(max(leave_one), 4) if leave_one else None,
        **concentration,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="Anonymized paired_trade_results_anonymized.csv")
    ap.add_argument("--output", default="")
    args = ap.parse_args()
    source = Path(args.csv).expanduser().resolve()
    with source.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 66:
        raise SystemExit(f"POPULATION_GATE_FAILED expected=66 actual={len(rows)}")
    required = {"direction", "actual_net_usd", "successful_trail_updates"}
    for rr in RRS:
        required.add(f"actual_minus_rr{rr}_usd")
    missing = sorted(required - set(rows[0]))
    if missing:
        raise SystemExit("SCHEMA_GATE_FAILED missing=" + ",".join(missing))

    report = {
        "status": "ROBUSTNESS_DIAGNOSTICS_COMPLETE",
        "input": source.name,
        "population": len(rows),
        "ordering": "CSV source order (entry chronology); sequence blocks are approximate dependence diagnostics",
        "tests": {},
        "limitations": [
            "Only 66 in-sample positions; no untouched holdout.",
            "Trade-level iid bootstrap assumes independence and is shown only as a reference.",
            "Circular moving-block bootstrap is a sensitivity diagnostic, not a validated time-series model.",
            "Calendar-day stability is not tested because anonymized CSV intentionally contains no dates.",
            "Successful trailing-update subgroups are descriptive and endogenous; they do not estimate causal effect.",
            "Positive-delta concentration measures compare actual trailing with each fixed-RR counterfactual, not absolute profitability.",
            "Fixed-RR outcomes remain barrier-price proxies with no slippage or executable-fill model."
        ]
    }

    for rr in RRS:
        key = f"actual_minus_rr{rr}_usd"
        paired = [(i, r, f(r, key)) for i, r in enumerate(rows) if f(r, key) is not None]
        values = [v for _, _, v in paired]
        result = summarize(values)
        result["block_bootstrap_95pct_ci_mean"] = {
            str(L): block_ci(values, L) for L in BLOCK_LENGTHS
        }
        result["direction_subgroups"] = {}
        result["update_subgroups"] = {}
        for label, predicate, target in (
            ("BUY", lambda r: r["direction"] == "BUY", result["direction_subgroups"]),
            ("SELL", lambda r: r["direction"] == "SELL", result["direction_subgroups"]),
            ("HAS_SUCCESSFUL_UPDATE", lambda r: int(r["successful_trail_updates"]) > 0, result["update_subgroups"]),
            ("NO_SUCCESSFUL_UPDATE", lambda r: int(r["successful_trail_updates"]) == 0, result["update_subgroups"]),
        ):
            subset = [v for _, r, v in paired if predicate(r)]
            target[label] = summarize(subset)
        report["tests"][f"RR{rr}"] = result

    output = Path(args.output).expanduser().resolve() if args.output else source.with_name("paired_robustness_report.json")
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    output.write_text(payload, encoding="utf-8")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print("ROBUSTNESS_DIAGNOSTICS_COMPLETE")
    print("TRADES=", len(rows))
    for rr in RRS:
        x = report["tests"][f"RR{rr}"]
        print(f"RR{rr} N={x['n']} MEAN={x['mean_delta_usd']} MEDIAN={x['median_delta_usd']} "
              f"IID_CI={x['iid_bootstrap_95pct_ci_mean']} BLOCK_CI={x['block_bootstrap_95pct_ci_mean']} "
              f"TOP1_SHARE={x['top_1_share_of_positive_delta']} "
              f"TRIMMED_MEAN={x['trimmed_10pct_mean_usd']} "
              f"LOO_MIN={x['leave_one_out_mean_min_usd']}")
        for group in ("BUY", "SELL"):
            g = x["direction_subgroups"][group]
            print(f"  {group} N={g['n']} MEAN={g.get('mean_delta_usd')}")
        for group in ("HAS_SUCCESSFUL_UPDATE", "NO_SUCCESSFUL_UPDATE"):
            g = x["update_subgroups"][group]
            print(f"  {group} N={g['n']} MEAN={g.get('mean_delta_usd')}")
    print("REPORT=", output)
    print("REPORT_SHA256=", digest)


if __name__ == "__main__":
    main()
