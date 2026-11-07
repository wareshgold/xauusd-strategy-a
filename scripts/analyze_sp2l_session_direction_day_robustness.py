#!/usr/bin/env python
"""Read-only session x direction x day robustness diagnostics for SP2L.

Inputs: the private weekly audit ZIP and the existing anonymized paired CSV.
No MT5 calls, order operations, live-runner access, or canonical rule selection.
Only aggregate outputs are written; no dates, timestamps, prices, tickets, or
position identifiers are emitted.

Session hours are explicit research conventions, converted with IANA zones so
DST is applied at each entry instant. A trade is classified by entry time.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

SYMBOL = "XAUUSD.ecn"
MAGIC = 26092301
RRS = range(1, 7)
LONDON = ZoneInfo("Europe/London")
NEW_YORK = ZoneInfo("America/New_York")
TOKYO = ZoneInfo("Asia/Tokyo")
BOOTSTRAP_REPS = 20000
BASE_SEED = 20261107
PRIMARY_GROUPS = ("LONDON", "TOKYO", "NEW_YORK", "LONDON_NEW_YORK_OVERLAP")
ALL_GROUPS = (
    "LONDON", "TOKYO", "NEW_YORK", "LONDON_NEW_YORK_OVERLAP",
    "LONDON_ONLY", "NEW_YORK_ONLY", "OUTSIDE_LONDON_NEW_YORK",
    "OUTSIDE_CORE_SESSIONS",
)


def number(value):
    try:
        return float(value) if value is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def parse_utc(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def load_entry_instants(bundle):
    """Reconstruct exactly the same 66 evidence-qualified entries as prior QC."""
    with zipfile.ZipFile(bundle) as archive:
        deals = json.load(archive.open("raw/mt5_history_deals.json"))
        events = []
        with archive.open("raw/runner_files/forward_events.jsonl") as stream:
            for line in stream:
                try:
                    events.append(json.loads(line))
                except Exception:
                    continue

    by_position = defaultdict(list)
    for deal in deals:
        if deal.get("symbol") == SYMBOL and deal.get("position_id") is not None:
            by_position[str(deal["position_id"])].append(deal)

    theoretical_sl = defaultdict(set)
    first_lifecycle = {}
    for event in events:
        position = str(event.get("position", "") or "")
        if not position:
            continue
        if event.get("event") == "TELEGRAM_DEAL_LIFECYCLE":
            sl = number(event.get("theoretical_sl"))
            if sl:
                theoretical_sl[position].add(round(sl, 8))
        elif event.get("event") == "POSITION_LIFECYCLE":
            sl = number(event.get("sl"))
            instant = parse_utc(event.get("ts_utc"))
            if sl and instant and (
                position not in first_lifecycle or instant < first_lifecycle[position][0]
            ):
                first_lifecycle[position] = (instant, sl)

    selected = []
    for position, rows in by_position.items():
        entries = [d for d in rows if int(d.get("entry", -1)) == 0]
        exits = [d for d in rows if int(d.get("entry", -1)) == 1]
        if len(entries) != 1 or len(exits) != 1:
            continue
        entry = entries[0]
        if str(entry.get("magic")) != str(MAGIC) or int(entry.get("type", -1)) not in (0, 1):
            continue
        sl_values = theoretical_sl.get(position, set())
        lifecycle = first_lifecycle.get(position)
        if len(sl_values) != 1 or lifecycle is None:
            continue
        sl = next(iter(sl_values))
        life_time, life_sl = lifecycle
        if abs(sl - life_sl) > 1e-7:
            continue
        entry_ms = int(entry.get("time_msc") or int(entry.get("time", 0)) * 1000)
        if life_time.timestamp() * 1000 > entry_ms:
            continue
        selected.append((
            entry_ms, position,
            datetime.fromtimestamp(entry_ms / 1000, timezone.utc),
        ))

    selected.sort(key=lambda item: (item[0], item[1]))
    if len(selected) != 66:
        raise SystemExit(f"POPULATION_GATE_FAILED expected=66 actual={len(selected)}")
    return [item[2] for item in selected]


def bootstrap_ci(values, seed):
    values = np.asarray(values, dtype=float)
    if len(values) < 2:
        return None
    rng = np.random.default_rng(seed)
    draws = values[rng.integers(0, len(values), size=(BOOTSTRAP_REPS, len(values)))]
    samples = np.mean(draws, axis=1)
    return [
        round(float(np.quantile(samples, 0.025)), 4),
        round(float(np.quantile(samples, 0.975)), 4),
    ]


def stable_seed(label, rr=0):
    digest = hashlib.sha256(label.encode("utf-8")).digest()
    return BASE_SEED + int.from_bytes(digest[:4], "big") + rr * 1009


def summarize(rows, label, min_n=20, min_days=3):
    days = sorted({row["day_bucket"] for row in rows})
    gate_pass = len(rows) >= min_n and len(days) >= min_days
    result = {
        "n": len(rows),
        "distinct_day_buckets": len(days),
        "actual_net_mean_usd": round(float(np.mean([r["actual_net"] for r in rows])), 4) if rows else None,
        "minimum_n_for_screen": min_n,
        "minimum_days_for_screen": min_days,
        "screen_sample_gate_pass": gate_pass,
        "paired_deltas": {},
    }
    for rr in RRS:
        values = [r["deltas"][rr] for r in rows if r["deltas"][rr] is not None]
        result["paired_deltas"][f"RR{rr}"] = {
            "paired_n": len(values),
            "mean_delta_usd": round(float(np.mean(values)), 4) if values else None,
            "median_delta_usd": round(float(np.median(values)), 4) if values else None,
            "bootstrap_iid_95pct_ci_mean_usd": (
                bootstrap_ci(values, stable_seed(label, rr)) if gate_pass and len(values) >= 2 else None
            ),
            "actual_better_n": sum(v > 0.005 for v in values),
            "fixed_rr_better_n": sum(v < -0.005 for v in values),
        }
    return result


def day_sensitivity(rows):
    buckets = sorted({r["day_bucket"] for r in rows})
    output = {}
    for omitted in buckets:
        kept = [r for r in rows if r["day_bucket"] != omitted]
        entry = {"remaining_n": len(kept), "paired_deltas": {}}
        for rr in RRS:
            values = [r["deltas"][rr] for r in kept if r["deltas"][rr] is not None]
            entry["paired_deltas"][f"RR{rr}"] = (
                round(float(np.mean(values)), 4) if values else None
            )
        output[omitted] = entry
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", help="Private weekly audit ZIP")
    parser.add_argument("paired_csv", help="paired_trade_results_anonymized.csv")
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    instants = load_entry_instants(Path(args.bundle).expanduser().resolve())
    source = Path(args.paired_csv).expanduser().resolve()
    with source.open(newline="", encoding="utf-8") as stream:
        source_rows = list(csv.DictReader(stream))
    if len(source_rows) != 66:
        raise SystemExit(f"CSV_POPULATION_GATE_FAILED expected=66 actual={len(source_rows)}")
    if [r.get("trade_key") for r in source_rows] != [f"T{i:03d}" for i in range(1, 67)]:
        raise SystemExit("TRADE_ORDER_GATE_FAILED")

    dates = sorted({instant.date() for instant in instants})
    day_labels = {day: f"D{index + 1:02d}" for index, day in enumerate(dates)}
    rows = []
    utc_hours = defaultdict(list)
    london_hours = defaultdict(list)
    ny_hours = defaultdict(list)

    for source_row, instant in zip(source_rows, instants):
        london = instant.astimezone(LONDON)
        ny = instant.astimezone(NEW_YORK)
        tokyo = instant.astimezone(TOKYO)
        in_london = 8 <= london.hour < 17
        in_ny = 8 <= ny.hour < 17
        in_tokyo = 9 <= tokyo.hour < 18
        overlap = in_london and in_ny

        memberships = {
            "LONDON": in_london,
            "TOKYO": in_tokyo,
            "NEW_YORK": in_ny,
            "LONDON_NEW_YORK_OVERLAP": overlap,
            "LONDON_ONLY": in_london and not in_ny,
            "NEW_YORK_ONLY": in_ny and not in_london,
            "OUTSIDE_LONDON_NEW_YORK": not in_london and not in_ny,
            "OUTSIDE_CORE_SESSIONS": not in_london and not in_ny and not in_tokyo,
        }
        deltas = {
            rr: (
                number(source_row[f"actual_minus_rr{rr}_usd"])
                if source_row.get(f"actual_minus_rr{rr}_usd") not in ("", None)
                else None
            )
            for rr in RRS
        }
        row = {
            "day_bucket": day_labels[instant.date()],
            "direction": source_row.get("direction", "UNKNOWN"),
            "actual_net": number(source_row.get("actual_net_usd")),
            "deltas": deltas,
            "memberships": memberships,
        }
        rows.append(row)
        utc_hours[f"{instant.hour:02d}"].append(row)
        london_hours[f"{london.hour:02d}"].append(row)
        ny_hours[f"{ny.hour:02d}"].append(row)

    group_reports = {}
    for name in ALL_GROUPS:
        group = [r for r in rows if r["memberships"][name]]
        group_reports[name] = {
            "overall": summarize(group, name, min_n=20, min_days=3),
            "by_direction": {
                direction: summarize(
                    [r for r in group if r["direction"] == direction],
                    f"{name}_{direction}", min_n=10, min_days=3,
                )
                for direction in ("BUY", "SELL")
            },
            "leave_one_day_out_mean_delta_usd": day_sensitivity(group),
        }

    primary_screen = {
        name: {
            "n": group_reports[name]["overall"]["n"],
            "distinct_day_buckets": group_reports[name]["overall"]["distinct_day_buckets"],
            "eligible_for_exploratory_review": group_reports[name]["overall"]["screen_sample_gate_pass"],
        }
        for name in PRIMARY_GROUPS
    }

    def hourly_report(groups, zone_name):
        report = {}
        for hour, group in sorted(groups.items()):
            report[hour] = summarize(group, f"{zone_name}_{hour}", min_n=10, min_days=3)
        return report

    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir else source.parent / "SP2L_SESSION_ROBUSTNESS_QC"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "SESSION_DIRECTION_DAY_ROBUSTNESS_COMPLETE",
        "population": 66,
        "scope": {
            "entry_time_only": True,
            "timezone_method": "IANA zoneinfo; Europe/London, America/New_York, Asia/Tokyo; DST applied per entry instant.",
            "session_definitions": {
                "London": "08:00-16:59 Europe/London",
                "New_York": "08:00-16:59 America/New_York",
                "Tokyo": "09:00-17:59 Asia/Tokyo",
                "overlap": "Entry instant inside both London and New York definitions",
            },
            "relative_day_method": "UTC entry date mapped chronologically to D01...; no calendar dates emitted.",
            "primary_groups": list(PRIMARY_GROUPS),
            "minimum_sample_gates": {
                "primary_session": {"n": 20, "distinct_day_buckets": 3},
                "direction_subgroup": {"n": 10, "distinct_day_buckets": 3},
                "hourly_group": {"n": 10, "distinct_day_buckets": 3},
            },
            "bootstrap": {
                "method": "IID trade-level percentile bootstrap",
                "replicates": BOOTSTRAP_REPS,
                "seed_base": BASE_SEED,
                "warning": "IID intervals do not account for within-day dependence; only four day clusters exist, so no day-cluster confidence interval is claimed.",
            },
        },
        "primary_screen_gates": primary_screen,
        "groups": group_reports,
        "hourly": {
            "UTC": hourly_report(utc_hours, "UTC"),
            "London_local": hourly_report(london_hours, "LONDON_LOCAL"),
            "New_York_local": hourly_report(ny_hours, "NEW_YORK_LOCAL"),
        },
        "limitations": [
            "All results are in-sample diagnostics on the same 66 positions; no untouched holdout.",
            "Session windows are research conventions, not source-confirmed SP2L rules.",
            "Session memberships overlap by design; do not treat group counts as independent.",
            "Entry-time classification does not imply the full trade occurred inside that session.",
            "IID bootstrap intervals are descriptive and can be too narrow under serial or day-level dependence.",
            "Four relative day buckets are insufficient for reliable cluster bootstrap or time-series inference.",
            "Direction and session subgroup comparisons are exploratory; multiplicity is not converted into a selection claim.",
            "Minimum-N gates only prevent very small groups from being screened; passing a gate does not establish an edge.",
            "No session filter, strategy rule, execution semantic, or live configuration is selected or changed.",
        ],
        "privacy": "Aggregate-only report; no calendar dates, exact times, prices, tickets, position identifiers, or raw trade rows.",
    }
    report_path = output_dir / "session_direction_day_robustness_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    digest = hashlib.sha256(report_path.read_bytes()).hexdigest()

    print("SESSION_DIRECTION_DAY_ROBUSTNESS_COMPLETE")
    print("TRADES=66")
    print("PRIMARY_SCREEN_GATES")
    for name, item in primary_screen.items():
        print(name, "N=", item["n"], "DAYS=", item["distinct_day_buckets"],
              "ELIGIBLE_FOR_EXPLORATORY_REVIEW=", item["eligible_for_exploratory_review"])
    print("PRIMARY_GROUP_MEANS")
    for name in PRIMARY_GROUPS:
        overall = group_reports[name]["overall"]
        print(name, "N=", overall["n"], "ACTUAL_NET_MEAN=", overall["actual_net_mean_usd"],
              " ".join(
                  f"RR{rr}={overall['paired_deltas'][f'RR{rr}']['mean_delta_usd']}"
                  for rr in RRS
              ))
        for direction, detail in group_reports[name]["by_direction"].items():
            d = detail["overall"]
            print(" ", direction, "N=", d["n"], "DAYS=", d["distinct_day_buckets"],
                  "ACTUAL_NET_MEAN=", d["actual_net_mean_usd"],
                  " ".join(f"RR{rr}={d['paired_deltas'][f'RR{rr}']['mean_delta_usd']}" for rr in RRS))
    print("REPORT=", report_path)
    print("REPORT_SHA256=", digest)


if __name__ == "__main__":
    main()
