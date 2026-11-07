#!/usr/bin/env python
"""Day-cluster stability diagnostics for paired SP2L trailing-vs-fixed-RR audit.

Read-only. Reuses the evidence-qualified 66-position population and UTC day
mapping from analyze_sp2l_session_direction_day_robustness.py. Reports only
aggregate day-level statistics; never emits dates, timestamps, prices, tickets,
position identifiers, or trade-level rows.

This is exploratory in-sample analysis, not strategy selection or validation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from analyze_sp2l_session_direction_day_robustness import RRS, load_entry_instants, number

EXPECTED_TRADES = 66
EPSILON = 1e-9


def load_rows(bundle: Path, paired_csv: Path):
    instants = load_entry_instants(bundle)
    with paired_csv.open(newline="", encoding="utf-8") as stream:
        source_rows = list(csv.DictReader(stream))
    if len(source_rows) != EXPECTED_TRADES:
        raise SystemExit(
            f"CSV_POPULATION_GATE_FAILED expected={EXPECTED_TRADES} actual={len(source_rows)}"
        )
    expected_keys = [f"T{i:03d}" for i in range(1, EXPECTED_TRADES + 1)]
    if [row.get("trade_key") for row in source_rows] != expected_keys:
        raise SystemExit("TRADE_ORDER_GATE_FAILED")

    dates = sorted({instant.date() for instant in instants})
    labels = {day: f"D{index + 1:02d}" for index, day in enumerate(dates)}
    rows = []
    for source, instant in zip(source_rows, instants):
        deltas = {}
        for rr in RRS:
            raw = source.get(f"actual_minus_rr{rr}_usd")
            deltas[rr] = number(raw) if raw not in ("", None) else None
        rows.append({
            "day": labels[instant.date()],
            "direction": source.get("direction", "UNKNOWN"),
            "actual_net": number(source.get("actual_net_usd")),
            "deltas": deltas,
        })
    if len(dates) != 4:
        raise SystemExit(f"DAY_CLUSTER_GATE_FAILED expected=4 actual={len(dates)}")
    return rows, labels


def rr_values(rows, rr):
    return [row["deltas"][rr] for row in rows if row["deltas"][rr] is not None]


def mean(values):
    return round(float(np.mean(values)), 4) if values else None


def daily_aggregates(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["day"]].append(row)
    result = {}
    for day in sorted(grouped):
        day_rows = grouped[day]
        result[day] = {
            "n": len(day_rows),
            "buy_n": sum(r["direction"] == "BUY" for r in day_rows),
            "sell_n": sum(r["direction"] == "SELL" for r in day_rows),
            "actual_net_mean_usd": mean([r["actual_net"] for r in day_rows]),
            "rr": {},
        }
        for rr in RRS:
            values = rr_values(day_rows, rr)
            result[day]["rr"][f"RR{rr}"] = {
                "paired_n": len(values),
                "trade_weighted_mean_delta_usd": mean(values),
                "delta_sum_usd": round(float(sum(values)), 4) if values else None,
                "positive_trade_n": sum(v > 0.005 for v in values),
                "negative_trade_n": sum(v < -0.005 for v in values),
                "neutral_trade_n": sum(abs(v) <= 0.005 for v in values),
            }
    return result


def summarize_rr(rows, daily):
    output = {}
    for rr in RRS:
        values = rr_values(rows, rr)
        day_means = [
            daily[day]["rr"][f"RR{rr}"]["trade_weighted_mean_delta_usd"]
            for day in sorted(daily)
            if daily[day]["rr"][f"RR{rr}"]["paired_n"] > 0
        ]
        day_sums = {
            day: daily[day]["rr"][f"RR{rr}"]["delta_sum_usd"]
            for day in sorted(daily)
        }
        total_sum = sum(v for v in day_sums.values() if v is not None)
        positive_days = sum(v > 0.005 for v in day_means)
        negative_days = sum(v < -0.005 for v in day_means)
        neutral_days = sum(abs(v) <= 0.005 for v in day_means)
        contribution = {}
        for day, value in day_sums.items():
            contribution[day] = {
                "delta_sum_usd": value,
                "share_of_total_delta_sum": (
                    round(value / total_sum, 4)
                    if value is not None and abs(total_sum) > EPSILON else None
                ),
            }

        lodo = {}
        for omitted in sorted(daily):
            kept = [r for r in rows if r["day"] != omitted]
            kept_values = rr_values(kept, rr)
            kept_day_means = [
                daily[day]["rr"][f"RR{rr}"]["trade_weighted_mean_delta_usd"]
                for day in sorted(daily) if day != omitted
                and daily[day]["rr"][f"RR{rr}"]["paired_n"] > 0
            ]
            lodo[omitted] = {
                "remaining_trade_n": len(kept_values),
                "trade_weighted_mean_delta_usd": mean(kept_values),
                "equal_weight_day_mean_delta_usd": mean(kept_day_means),
                "positive_remaining_days": sum(v > 0.005 for v in kept_day_means),
                "negative_remaining_days": sum(v < -0.005 for v in kept_day_means),
            }

        output[f"RR{rr}"] = {
            "paired_trade_n": len(values),
            "trade_weighted_mean_delta_usd": mean(values),
            "equal_weight_day_mean_delta_usd": mean(day_means),
            "positive_day_n": positive_days,
            "negative_day_n": negative_days,
            "neutral_day_n": neutral_days,
            "day_sign_consistency": (
                "ALL_POSITIVE" if positive_days == len(day_means) else
                "ALL_NEGATIVE" if negative_days == len(day_means) else
                "MIXED"
            ),
            "total_delta_sum_usd": round(float(total_sum), 4),
            "day_contribution": contribution,
            "leave_one_day_out": lodo,
            "iid_trade_bootstrap_used": False,
            "cluster_inference_status": "NOT_ESTIMATED_ONLY_4_DAY_CLUSTERS",
        }
    return output


def direction_day_report(rows, daily):
    result = {}
    for direction in ("BUY", "SELL"):
        direction_rows = [r for r in rows if r["direction"] == direction]
        by_day = {}
        for day in sorted(daily):
            day_rows = [r for r in direction_rows if r["day"] == day]
            if not day_rows:
                by_day[day] = {"n": 0, "rr": {}}
                continue
            by_day[day] = {"n": len(day_rows), "rr": {}}
            for rr in RRS:
                values = rr_values(day_rows, rr)
                by_day[day]["rr"][f"RR{rr}"] = {
                    "paired_n": len(values),
                    "mean_delta_usd": mean(values),
                    "delta_sum_usd": round(float(sum(values)), 4) if values else None,
                    "sign": (
                        "POSITIVE" if values and np.mean(values) > 0.005 else
                        "NEGATIVE" if values and np.mean(values) < -0.005 else
                        "NEUTRAL_OR_MISSING"
                    ),
                }
        direction_summary = {}
        for rr in RRS:
            values = rr_values(direction_rows, rr)
            day_means = [
                by_day[day]["rr"][f"RR{rr}"]["mean_delta_usd"]
                for day in sorted(by_day)
                if by_day[day]["rr"].get(f"RR{rr}", {}).get("paired_n", 0)
            ]
            direction_summary[f"RR{rr}"] = {
                "paired_trade_n": len(values),
                "trade_weighted_mean_delta_usd": mean(values),
                "positive_day_n": sum(v > 0.005 for v in day_means),
                "negative_day_n": sum(v < -0.005 for v in day_means),
                "day_signs": {
                    day: by_day[day]["rr"].get(f"RR{rr}", {}).get("sign", "NO_DATA")
                    for day in sorted(by_day)
                },
            }
        result[direction] = {
            "trade_n": len(direction_rows),
            "rr_summary": direction_summary,
            "by_day": by_day,
        }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", help="Private weekly audit ZIP")
    parser.add_argument("paired_csv", help="paired_trade_results_anonymized.csv")
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    rows, _ = load_rows(
        Path(args.bundle).expanduser().resolve(),
        Path(args.paired_csv).expanduser().resolve(),
    )
    daily = daily_aggregates(rows)
    rr_report = summarize_rr(rows, daily)
    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir else Path(args.paired_csv).expanduser().resolve().parent
        / "SP2L_DAY_CLUSTER_STABILITY_QC"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "DAY_CLUSTER_STABILITY_COMPLETE",
        "population_n": len(rows),
        "day_cluster_n": len(daily),
        "comparison_sign": "positive_delta_means_actual_trailing_better_than_fixed_rr",
        "daily_aggregates": daily,
        "rr_summary": rr_report,
        "direction_day_analysis": direction_day_report(rows, daily),
        "method": {
            "primary_unit": "UTC entry-date day bucket; equal-weight day summaries are reported separately from trade-weighted summaries.",
            "day_labels": "Chronological D01...D04; no calendar dates emitted.",
            "positive_day_threshold_usd": 0.005,
            "contribution": "Each day's sum of paired trade deltas divided by the total paired delta sum; share is null when the total is numerically zero.",
            "leave_one_day_out": "Recomputes both trade-weighted and equal-weight remaining-day means after omitting each day.",
            "confidence_intervals": "No cluster bootstrap or cluster confidence interval is reported because only four day clusters are present.",
        },
        "limitations": [
            "All 66 observations are from the same in-sample weekly audit; no untouched holdout.",
            "Only four day clusters exist; day-level inference is descriptive and highly uncertain.",
            "Equal-weight day means and trade-weighted means answer different questions and must not be conflated.",
            "Day contribution shares can be unstable when the total delta sum is near zero.",
            "BUY/SELL by-day cells may have very small sample counts; no subgroup is eligible for strategy selection.",
            "The RR counterfactuals are research comparisons, not canonical execution rules.",
            "No session filter, RR choice, strategy rule, or live configuration is selected or changed.",
        ],
        "privacy": "Aggregate-only; no calendar dates, exact times, prices, tickets, position identifiers, or individual trade rows.",
    }
    path = output_dir / "day_cluster_stability_report.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()

    print("DAY_CLUSTER_STABILITY_COMPLETE")
    print(f"TRADES={len(rows)} DAYS={len(daily)}")
    print("RR_DAY_STABILITY")
    for name, item in rr_report.items():
        print(
            name,
            f"TRADE_MEAN={item['trade_weighted_mean_delta_usd']}",
            f"EQUAL_DAY_MEAN={item['equal_weight_day_mean_delta_usd']}",
            f"POSITIVE_DAYS={item['positive_day_n']}",
            f"NEGATIVE_DAYS={item['negative_day_n']}",
            f"LODO_MIN={min(x['trade_weighted_mean_delta_usd'] for x in item['leave_one_day_out'].values())}",
            f"LODO_MAX={max(x['trade_weighted_mean_delta_usd'] for x in item['leave_one_day_out'].values())}",
        )
    print("REPORT=", path)
    print("REPORT_SHA256=", digest)


if __name__ == "__main__":
    main()
