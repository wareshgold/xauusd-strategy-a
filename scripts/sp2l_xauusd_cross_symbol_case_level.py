"""Case-level comparison of XAUUSD gap intervals against FX controls.

Research-only. Compares exact UTC interval coverage, boundary bars, and missing
M1 timestamps for each of the 58 XAUUSD forensic cases. It does not infer
session cause or promote a data rule.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

CONTROLS = {
    "USDJPY": "USDJPY.ecn", "EURJPY": "EURJPY.ecn", "GBPUSD": "GBPUSD.ecn",
    "GBPJPY": "GBPJPY.ecn", "EURUSD": "EURUSD.ecn", "USDCHF": "USDCHF.ecn",
    "USDCAD": "USDCAD.ecn",
}


def dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def iso(d: datetime) -> str:
    return d.astimezone(timezone.utc).isoformat()


def fetch(symbol: str, start: datetime, end: datetime) -> list[datetime]:
    rows = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1,
                                start - timedelta(minutes=3),
                                end + timedelta(minutes=3))
    if rows is None:
        return []
    return [datetime.fromtimestamp(int(x["time"]), tz=timezone.utc) for x in rows]


def inspect(times: list[datetime], start: datetime, end: datetime) -> dict:
    inside = sorted(t for t in times if start <= t < end)
    expected = int((end - start).total_seconds() // 60)
    observed = len(inside)
    missing = expected - observed
    before = max((t for t in times if t < start), default=None)
    after = min((t for t in times if t >= end), default=None)
    same_interval = observed == 0
    continuous = observed == expected and all(
        b - a == timedelta(minutes=1) for a, b in zip(inside, inside[1:])
    )
    return {
        "expected_minutes": expected,
        "observed_minutes": observed,
        "missing_minutes": missing,
        "interval_empty": same_interval,
        "interval_continuous": continuous,
        "last_bar_before_utc": iso(before) if before else None,
        "first_bar_at_or_after_end_utc": iso(after) if after else None,
        "observed_first_inside_utc": iso(inside[0]) if inside else None,
        "observed_last_inside_utc": iso(inside[-1]) if inside else None,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--mt5-path", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--limit", type=int, default=58)
    args = p.parse_args()

    src = Path(args.input)
    data = json.loads(src.read_text(encoding="utf-8"))
    cases = data.get("results", [])[:args.limit]

    if not mt5.initialize(path=args.mt5_path):
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    results = []
    try:
        for case in cases:
            start, end = dt(case["xau_gap_start_utc"]), dt(case["xau_gap_end_utc"])
            row = {
                "xau_gap_start_utc": case["xau_gap_start_utc"],
                "xau_gap_end_utc": case["xau_gap_end_utc"],
                "xau_pattern": case.get("xau_pattern"),
                "controls": {},
            }
            for name, broker in CONTROLS.items():
                times = fetch(broker, start, end)
                row["controls"][name] = {
                    "broker_symbol": broker,
                    **inspect(times, start, end),
                }
            results.append(row)
    finally:
        mt5.shutdown()

    classifications = Counter()
    for row in results:
        for name in CONTROLS:
            c = row["controls"][name]
            if c["interval_empty"]:
                cls = "CONTROL_INTERVAL_EMPTY"
            elif c["interval_continuous"]:
                cls = "CONTROL_INTERVAL_CONTINUOUS"
            else:
                cls = "CONTROL_INTERVAL_PARTIAL"
            classifications[f"{name}:{cls}"] += 1

    report = {
        "status": "COMPLETE",
        "research_only": True,
        "session_cause": "UNRESOLVED",
        "session_approval": "NOT_ESTABLISHED",
        "population": len(results),
        "classification_counts": dict(sorted(classifications.items())),
        "results": results,
        "interpretation": [
            "Exact UTC interval coverage is descriptive forensic evidence only.",
            "Empty/partial/continuous control intervals do not establish session cause.",
            "No broker session, maintenance, or canonical data rule is inferred.",
        ],
    }
    Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("XAUUSD CROSS-SYMBOL CASE-LEVEL CONTROL")
    print(f"population={len(results)}")
    for k, v in sorted(classifications.items()):
        print(f"{k}={v}")
    print("SESSION_CAUSE=UNRESOLVED")
    print("SESSION_APPROVAL=NOT_ESTABLISHED")
    print("research_only=true")
    print("status=COMPLETE")
    print(f"artifact={args.output}")


if __name__ == "__main__":
    main()
