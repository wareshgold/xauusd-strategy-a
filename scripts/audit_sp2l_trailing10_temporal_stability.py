"""Audit Trail-10 temporal stability from a frozen MT5 Tester trade export.

Research-only. This script does not define Strategy A geometry and cannot
promote trailing to canonical. It validates that one full-window MT5 Tester
trade export covers the predefined windows, then computes Trail-10 outcomes
per window.

The input CSV must come from Sp2lV2Mt5Tester.mq5 with:
  RR=1.0
  trail_pips=10.0
and must preserve the signal population generated from one continuous
M1 history interval. The script intentionally refuses partial coverage.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


WINDOWS = [
    ("W1", "2025-09-25T00:00:00Z", "2025-12-25T00:00:00Z"),
    ("W2", "2025-12-25T00:00:00Z", "2026-03-25T00:00:00Z"),
    ("W3", "2026-03-25T00:00:00Z", "2026-06-25T00:00:00Z"),
    ("W4", "2026-06-25T00:00:00Z", "2026-09-25T00:00:00Z"),
]


def parse_utc(value: str) -> datetime:
    value = value.strip()
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y.%m.%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    raise ValueError(f"unsupported UTC timestamp: {value!r}")


def wilson(wins: int, n: int) -> tuple[float | None, float | None]:
    if n <= 0:
        return None, None
    p = wins / n
    z = 1.959963984540054
    den = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / den
    half = z * ((p * (1.0 - p) / n) + z * z / (4.0 * n * n)) ** 0.5 / den
    return center - half, center + half


def assign_window(entry_time: datetime):
    for name, start_s, end_s in WINDOWS:
        start = parse_utc(start_s)
        end = parse_utc(end_s)
        if start <= entry_time < end:
            return name
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trades-csv", required=True)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    rows = []
    with open(args.trades_csv, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if not row.get("entry_time_utc"):
                continue
            rows.append(row)

    expected_start = parse_utc(WINDOWS[0][1])
    expected_end = parse_utc(WINDOWS[-1][2])
    entry_times = [parse_utc(r["entry_time_utc"]) for r in rows]

    coverage_pass = bool(entry_times) and min(entry_times) <= expected_start
    coverage_pass = coverage_pass and max(entry_times) >= expected_end

    rr_values = sorted({float(r["rr"]) for r in rows if r.get("rr")})
    trail_values = sorted({float(r["trail_pips"]) for r in rows if r.get("trail_pips")})

    duplicate_ids = len(rows) - len({r["signal_id"] for r in rows})

    by_window = {name: [] for name, _, _ in WINDOWS}
    outside = 0
    for r, entry_time in zip(rows, entry_times):
        w = assign_window(entry_time)
        if w is None:
            outside += 1
        else:
            by_window[w].append(r)

    results = []
    for name, start_s, end_s in WINDOWS:
        bucket = by_window[name]
        counts = Counter(r["result"] for r in bucket)
        decisive = counts["WIN"] + counts["LOSS"] + counts["BREAKEVEN"]
        wins = counts["WIN"]
        losses = counts["LOSS"]
        be = counts["BREAKEVEN"]
        amb = counts["AMBIGUOUS"]
        net_r = sum(float(r.get("r") or 0.0) for r in bucket if r["result"] in {"WIN", "LOSS", "BREAKEVEN"})
        gp = sum(max(0.0, float(r.get("r") or 0.0)) for r in bucket)
        gl = -sum(min(0.0, float(r.get("r") or 0.0)) for r in bucket)
        pf = gp / gl if gl > 0 else None
        wr = 100.0 * wins / decisive if decisive else None
        lo, hi = wilson(wins, decisive)
        results.append({
            "window": name,
            "start_utc": start_s,
            "end_utc": end_s,
            "signals": len(bucket),
            "decisive": decisive,
            "wins": wins,
            "losses": losses,
            "breakeven": be,
            "ambiguous": amb,
            "win_rate_decisive_pct": wr,
            "wilson_95_low_pct": None if lo is None else lo * 100.0,
            "wilson_95_high_pct": None if hi is None else hi * 100.0,
            "net_R": net_r,
            "profit_factor": pf,
            "trailing_activated": sum(r.get("trailing_activated") == "1" for r in bucket),
        })

    result = {
        "status": "PASS" if coverage_pass and duplicate_ids == 0 and rr_values == [1.0] and trail_values == [10.0] else "BLOCKED",
        "mode": "NON_CANONICAL_FORENSIC",
        "experiment": "SP2L_TRAIL10_TEMPORAL_STABILITY",
        "population_rows": len(rows),
        "duplicate_signal_id_count": duplicate_ids,
        "outside_predefined_windows": outside,
        "input_contract": {
            "rr_values": rr_values,
            "trail_pips_values": trail_values,
            "required_rr": 1.0,
            "required_trail_pips": 10.0,
        },
        "required_continuous_coverage": {
            "start_utc": WINDOWS[0][1],
            "end_utc": WINDOWS[-1][2],
            "pass": coverage_pass,
        },
        "windows": results,
        "interpretation_boundary": (
            "This is a temporal-stability audit of a research-only MT5 Tester "
            "export. It does not establish source confirmation, canonical "
            "geometry, live execution equivalence, or production readiness."
        ),
    }

    output = args.output
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
