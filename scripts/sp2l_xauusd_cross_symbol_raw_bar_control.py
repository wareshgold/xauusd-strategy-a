"""Cross-symbol control for XAUUSD raw-bar boundary cases (research-only).

For each XAUUSD forensic gap, query configured control symbols over the same
UTC interval and inspect the nearest M1 bars surrounding the XAUUSD boundary.
This is descriptive evidence only; it does not infer session cause.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5


DEFAULT_CONTROLS = {
    "USDJPY": "USDJPY.ecn",
    "EURJPY": "EURJPY.ecn",
    "GBPUSD": "GBPUSD.ecn",
    "GBPJPY": "GBPJPY.ecn",
    "EURUSD": "EURUSD.ecn",
    "USDCHF": "USDCHF.ecn",
    "USDCAD": "USDCAD.ecn",
}


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def boundary(rows: list[dict], start: datetime, end: datetime) -> dict:
    before = [x for x in rows if dt(x["time_utc"]) < start]
    after = [x for x in rows if dt(x["time_utc"]) >= end]
    lb = before[-1] if before else None
    fa = after[0] if after else None
    if not lb or not fa:
        return {"pattern": "NO_BOUNDARY", "last_bar_before": lb, "first_bar_after": fa}
    delta = int((dt(fa["time_utc"]) - dt(lb["time_utc"])).total_seconds() // 60)
    return {
        "pattern": (
            "23:59_TO_01:00" if dt(lb["time_utc"]).minute == 59 and dt(fa["time_utc"]).minute == 0 and delta == 61
            else "23:58_TO_01:00" if dt(lb["time_utc"]).minute == 58 and dt(fa["time_utc"]).minute == 0
            else "23:59_TO_00:59" if dt(lb["time_utc"]).minute == 59 and dt(fa["time_utc"]).minute == 59
            else "OTHER"
        ),
        "observed_boundary_minutes": delta,
        "last_bar_before": lb,
        "first_bar_after": fa,
    }


def fetch(symbol: str, start: datetime, end: datetime) -> list[dict]:
    bars = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start - timedelta(minutes=3), end + timedelta(minutes=3))
    if bars is None:
        return []
    return [
        {
            "time_utc": iso(datetime.fromtimestamp(int(b["time"]), tz=timezone.utc)),
            "open": float(b["open"]),
            "high": float(b["high"]),
            "low": float(b["low"]),
            "close": float(b["close"]),
            "volume": int(b["tick_volume"]),
        }
        for b in bars
    ]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--mt5-path", required=True)
    p.add_argument("--output")
    p.add_argument("--limit", type=int, default=58)
    p.add_argument("--controls", default=",".join(DEFAULT_CONTROLS))
    args = p.parse_args()

    src = Path(args.input)
    data = json.loads(src.read_text(encoding="utf-8"))
    xau_rows = data.get("results", [])[:args.limit]
    controls = {name: DEFAULT_CONTROLS[name] for name in args.controls.split(",") if name in DEFAULT_CONTROLS}

    if not mt5.initialize(path=args.mt5_path):
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    results = []
    try:
        for xau in xau_rows:
            gap = xau["gap"]
            start, end = dt(gap["start_utc"]), dt(gap["end_utc"])
            row = {
                "xau_gap_start_utc": gap["start_utc"],
                "xau_gap_end_utc": gap["end_utc"],
                "xau_pattern": xau.get("observed_boundary_pattern"),
                "controls": {},
            }
            for requested, broker in controls.items():
                bars = fetch(broker, start, end)
                b = boundary(bars, start, end)
                row["controls"][requested] = {
                    "broker_symbol": broker,
                    **b,
                    "bars_returned": len(bars),
                }
            results.append(row)
    finally:
        mt5.shutdown()

    pattern_counts = {
        requested: Counter(
            row["controls"][requested]["pattern"]
            for row in results
        )
        for requested in controls
    }
    report = {
        "status": "COMPLETE",
        "research_only": True,
        "session_cause": "UNRESOLVED",
        "session_approval": "NOT_ESTABLISHED",
        "source_artifact": str(src),
        "xau_cases": len(results),
        "controls": controls,
        "pattern_counts": {
            symbol: dict(sorted(counts.items()))
            for symbol, counts in pattern_counts.items()
        },
        "results": results,
        "interpretation": [
            "This is a descriptive cross-symbol control, not a causal session test.",
            "Control-symbol boundary behavior must not be used to approve or reject an XAUUSD session rule by itself.",
            "No session closure is inferred, approved, or promoted to canonical data rules.",
        ],
    }

    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")

    print("XAUUSD CROSS-SYMBOL RAW-BAR CONTROL")
    print("")
    print(f"xau_cases={len(results)}")
    for symbol, counts in sorted(report["pattern_counts"].items()):
        print(f"{symbol}: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    print("")
    print("SESSION_CAUSE=UNRESOLVED")
    print("SESSION_APPROVAL=NOT_ESTABLISHED")
    print("research_only=true")
    print("status=COMPLETE")
    if args.output:
        print(f"artifact={args.output}")


if __name__ == "__main__":
    main()
