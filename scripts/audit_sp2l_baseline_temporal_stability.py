#!/usr/bin/env python3
"""
Deterministic temporal-stability audit for the frozen SP2L forensic population.

Purpose:
- Analyze the already-frozen RR=1 / Trail=OFF trade population by predefined,
  non-overlapping time windows.
- Do not optimize parameters or choose windows after seeing results.
- Use the trade CSV produced by the forensic MT5 Tester/replay.
- Timestamp assignment is based on entry_time_utc because this audit evaluates
  realized trade performance in the period in which the trade entered.

Default frozen windows:
  2025-09-25 -> 2025-12-25
  2025-12-25 -> 2026-03-25
  2026-03-25 -> 2026-06-25
  2026-06-25 -> 2026-09-25

The windows are fixed by the frozen research interval and are not selected
based on performance.

No pandas dependency.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path


FROZEN_START = "2025-09-25T00:00:00Z"
FROZEN_END = "2026-09-25T00:00:00Z"

# Fixed a priori: four consecutive three-month calendar windows.
DEFAULT_WINDOWS = (
    ("W1", "2025-09-25T00:00:00Z", "2025-12-25T00:00:00Z"),
    ("W2", "2025-12-25T00:00:00Z", "2026-03-25T00:00:00Z"),
    ("W3", "2026-03-25T00:00:00Z", "2026-06-25T00:00:00Z"),
    ("W4", "2026-06-25T00:00:00Z", "2026-09-25T00:00:00Z"),
)


@dataclass(frozen=True)
class Trade:
    signal_id: str
    setup_time: int
    entry_time: int
    result: str
    r: float


@dataclass(frozen=True)
class Window:
    name: str
    start: str
    end: str
    start_epoch: int
    end_epoch: int


def parse_utc(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        dt = datetime.strptime(value, "%Y.%m.%d %H:%M:%S")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def epoch(value: str) -> int:
    return int(parse_utc(value).timestamp())


def fmt_epoch(value: int) -> str:
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True, help="Frozen MT5 trade CSV to audit.")
    p.add_argument("--expected-signals", type=int, default=1480)
    p.add_argument("--start", default=FROZEN_START)
    p.add_argument("--end", default=FROZEN_END)
    p.add_argument(
        "--output-json",
        default="",
        help="Optional JSON output path.",
    )
    p.add_argument(
        "--output-csv",
        default="",
        help="Optional per-window CSV output path.",
    )
    return p.parse_args()


def load_trades(path: str) -> list[Trade]:
    out: list[Trade] = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {
            "signal_id",
            "setup_time_utc",
            "entry_time_utc",
            "result",
            "r",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        for row in reader:
            out.append(
                Trade(
                    signal_id=row["signal_id"].strip(),
                    setup_time=epoch(row["setup_time_utc"]),
                    entry_time=epoch(row["entry_time_utc"]),
                    result=row["result"].strip().upper(),
                    r=float(row["r"]),
                )
            )
    return out


def validate_trades(
    trades: list[Trade], expected_signals: int, start: int, end: int
) -> dict:
    ids = [t.signal_id for t in trades]
    duplicate_ids = sorted({x for x in ids if ids.count(x) > 1})
    outside = [
        t.signal_id
        for t in trades
        if not (start <= t.entry_time < end)
    ]
    invalid_results = sorted(
        {t.result for t in trades if t.result not in {"WIN", "LOSS", "BREAKEVEN", "AMBIGUOUS", "OPEN_OR_UNRESOLVED"}}
    )

    return {
        "expected_signals": expected_signals,
        "actual_signals": len(trades),
        "signal_count_matches_expected": len(trades) == expected_signals,
        "signal_ids_unique": not duplicate_ids,
        "duplicate_signal_ids": duplicate_ids,
        "entry_times_inside_frozen_interval": not outside,
        "outside_interval_signal_ids": outside,
        "invalid_results": invalid_results,
        "validation_pass": (
            len(trades) == expected_signals
            and not duplicate_ids
            and not outside
            and not invalid_results
        ),
    }


def wilson_interval(wins: int, decisive: int, z: float = 1.959963984540054) -> tuple[float | None, float | None]:
    if decisive <= 0:
        return None, None
    p = wins / decisive
    denom = 1.0 + z * z / decisive
    center = (p + z * z / (2.0 * decisive)) / denom
    half = (
        z
        * math.sqrt(
            p * (1.0 - p) / decisive
            + z * z / (4.0 * decisive * decisive)
        )
        / denom
    )
    return center - half, center + half


def summarize(name: str, start: str, end: str, trades: list[Trade]) -> dict:
    wins = sum(t.result == "WIN" for t in trades)
    losses = sum(t.result == "LOSS" for t in trades)
    breakeven = sum(t.result == "BREAKEVEN" for t in trades)
    ambiguous = sum(t.result == "AMBIGUOUS" for t in trades)
    unresolved = sum(t.result == "OPEN_OR_UNRESOLVED" for t in trades)
    decisive = wins + losses + breakeven

    gross_profit = sum(t.r for t in trades if t.r > 0.0)
    gross_loss = sum(-t.r for t in trades if t.r < 0.0)
    pf = gross_profit / gross_loss if gross_loss > 0.0 else None
    wr = wins / decisive if decisive else None
    ci_low, ci_high = wilson_interval(wins, decisive)

    cumulative = 0.0
    peak = 0.0
    max_dd = 0.0
    losing_streak = 0
    max_losing_streak = 0

    # CSV rows are expected to be chronological, but sort explicitly so the
    # audit is deterministic and independent of file row ordering.
    ordered = sorted(trades, key=lambda t: (t.entry_time, t.signal_id))
    for t in ordered:
        cumulative += t.r
        peak = max(peak, cumulative)
        max_dd = max(max_dd, peak - cumulative)
        if t.result == "LOSS":
            losing_streak += 1
            max_losing_streak = max(max_losing_streak, losing_streak)
        else:
            losing_streak = 0

    return {
        "window": name,
        "start_utc": start,
        "end_utc": end,
        "signals": len(trades),
        "wins": wins,
        "losses": losses,
        "breakeven": breakeven,
        "ambiguous": ambiguous,
        "open_or_unresolved": unresolved,
        "decisive": decisive,
        "win_rate_decisive_pct": None if wr is None else wr * 100.0,
        "wilson_95_low_pct": None if ci_low is None else ci_low * 100.0,
        "wilson_95_high_pct": None if ci_high is None else ci_high * 100.0,
        "gross_profit_R": gross_profit,
        "gross_loss_R": gross_loss,
        "net_R": sum(t.r for t in trades),
        "profit_factor": pf,
        "max_drawdown_R": max_dd,
        "max_losing_streak": max_losing_streak,
    }


def build_windows() -> list[Window]:
    return [
        Window(name, start, end, epoch(start), epoch(end))
        for name, start, end in DEFAULT_WINDOWS
    ]


def main() -> int:
    args = parse_args()
    frozen_start = epoch(args.start)
    frozen_end = epoch(args.end)

    if args.start != FROZEN_START or args.end != FROZEN_END:
        raise SystemExit(
            "Refusing non-frozen interval. This audit is intentionally locked to "
            f"{FROZEN_START} -> {FROZEN_END}."
        )

    trades = load_trades(args.csv)
    validation = validate_trades(
        trades, args.expected_signals, frozen_start, frozen_end
    )
    if not validation["validation_pass"]:
        raise SystemExit(
            "FROZEN_POPULATION_VALIDATION_FAILED\n"
            + json.dumps(validation, indent=2)
        )

    windows = build_windows()
    summaries = []
    assigned_ids: list[int] = []
    for w in windows:
        selected = [
            t for t in trades
            if w.start_epoch <= t.entry_time < w.end_epoch
        ]
        summaries.append(summarize(w.name, w.start, w.end, selected))
        assigned_ids.extend(t.signal_id for t in selected)

    coverage = {
        "all_signals_assigned_once": len(assigned_ids) == len(trades)
        and len(set(assigned_ids)) == len(trades),
        "assigned_signal_count": len(assigned_ids),
        "unassigned_signal_ids": sorted(
            set(t.signal_id for t in trades) - set(assigned_ids)
        ),
        "multiply_assigned_signal_ids": sorted(
            x for x in set(assigned_ids) if assigned_ids.count(x) > 1
        ),
    }

    total = summarize(
        "TOTAL_FROZEN_POPULATION",
        FROZEN_START,
        FROZEN_END,
        trades,
    )

    report = {
        "audit": "SP2L_BASELINE_RR1_TRAIL0_TEMPORAL_STABILITY",
        "mode": "NON_CANONICAL_FORENSIC",
        "canonical": False,
        "population_timestamp": "entry_time_utc",
        "window_definition": "four fixed consecutive three-month calendar windows; chosen before inspecting results",
        "frozen_interval": {
            "start_utc": FROZEN_START,
            "end_utc": FROZEN_END,
        },
        "contract": {
            "pgap": 1.0,
            "spike_multiplier": 1.5,
            "max_sl": 10.0,
            "rr": 1.0,
            "trail": "OFF",
        },
        "source_csv": str(Path(args.csv)),
        "validation": validation,
        "coverage": coverage,
        "total": total,
        "windows": summaries,
        "interpretation_guard": [
            "Descriptive temporal stability only; no parameter optimization.",
            "Wilson intervals are descriptive uncertainty intervals and are not the final statistical validation.",
            "No window is selected or excluded based on performance.",
            "Results do not promote any geometry or execution semantics to canonical.",
        ],
    }

    print("SP2L_BASELINE_TEMPORAL_STABILITY")
    print(f"source_csv={args.csv}")
    print(f"frozen_interval={FROZEN_START} -> {FROZEN_END}")
    print(f"population={len(trades)}")
    print(f"validation_pass={validation['validation_pass']}")
    print(f"coverage_pass={coverage['all_signals_assigned_once']}")
    for row in summaries:
        print(
            f"{row['window']}: signals={row['signals']} "
            f"decisive={row['decisive']} wins={row['wins']} losses={row['losses']} "
            f"ambiguous={row['ambiguous']} "
            f"wr={row['win_rate_decisive_pct']:.6f}%" if row['win_rate_decisive_pct'] is not None else "wr=NA%"
            f"net_R={row['net_R']:.6f} PF={row['profit_factor']}"
        )
    print(json.dumps(report, indent=2))

    if args.output_json:
        Path(args.output_json).write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
        )

    if args.output_csv:
        fields = list(summaries[0].keys()) if summaries else []
        with open(args.output_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(summaries)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
