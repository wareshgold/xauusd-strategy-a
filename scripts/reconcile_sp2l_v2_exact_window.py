#!/usr/bin/env python3
"""Trade-level reconciliation for the legacy SP2L V2 forensic contract.

Non-canonical forensic tooling only.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

START = datetime(2026, 8, 26, tzinfo=timezone.utc)
END = datetime(2026, 9, 25, tzinfo=timezone.utc)

ALIASES = {
    "entry_time_utc": ["entry_time_utc", "entry_time", "entry_utc", "entryTimeUtc", "signal_time_utc", "time_utc"],
    "setup_time_utc": ["setup_time_utc", "setup_time", "setup_utc", "setupTimeUtc"],
    "direction": ["direction", "side", "type"],
    "entry": ["entry", "entry_price", "entryPrice"],
    "sl": ["sl", "stop_loss", "stopLoss", "stop"],
    "result": ["result", "outcome", "status"],
    "r": ["r", "R", "result_r", "net_r"],
}


def pick(row, names):
    for name in names:
        value = row.get(name)
        if value not in ("", None):
            return value
    return None


def normalize(row):
    out = {key: pick(row, names) for key, names in ALIASES.items()}
    if out["entry_time_utc"] is None and row.get("timestamp") is not None:
        out["entry_time_utc"] = row["timestamp"]
    if out["direction"] is not None:
        out["direction"] = str(out["direction"]).upper()
    return out


def flatten(obj):
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                yield item
            yield from flatten(item)
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from flatten(value)


def parse_time(value):
    if value is None:
        return None
    text = str(value).strip().replace("Z", "+00:00")
    formats = (
        lambda: datetime.fromisoformat(text),
        lambda: datetime.strptime(text, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
        lambda: datetime.strptime(text, "%Y.%m.%d %H:%M:%S").replace(tzinfo=timezone.utc),
    )
    for parser in formats:
        try:
            result = parser()
            if result.tzinfo is None:
                result = result.replace(tzinfo=timezone.utc)
            return result.astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def load_rows(path):
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [normalize(row) for row in csv.DictReader(handle)]

    obj = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for item in flatten(obj):
        row = normalize(item)
        if row["entry_time_utc"] is not None and (
            row["direction"] is not None or row["entry"] is not None
        ):
            rows.append(row)
    return rows


def in_window(row):
    timestamp = parse_time(row["entry_time_utc"])
    return timestamp is not None and START <= timestamp < END


def number(value):
    return round(float(value), 5) if value not in (None, "") else None


def key(row):
    timestamp = parse_time(row["entry_time_utc"])
    return (
        timestamp.isoformat() if timestamp else "",
        row["direction"] or "",
        number(row["entry"]),
        number(row["sl"]),
    )


def stats(rows):
    counts = Counter(
        str(row["result"]).upper()
        for row in rows
        if row["result"] is not None
    )
    decisive = counts["WIN"] + counts["LOSS"] + counts["BREAKEVEN"]
    win_rate = 100.0 * counts["WIN"] / decisive if decisive else 0.0
    net_r = sum(
        float(row["r"])
        for row in rows
        if row["r"] not in (None, "")
    )
    return {
        "signals": len(rows),
        "decisive": decisive,
        "WIN": counts["WIN"],
        "LOSS": counts["LOSS"],
        "BREAKEVEN": counts["BREAKEVEN"],
        "AMBIGUOUS": counts["AMBIGUOUS"],
        "win_rate_decisive_pct": win_rate,
        "net_R": net_r,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", required=True, type=Path)
    parser.add_argument("--backtest", required=True, type=Path)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/forensic/runtime-m1-replay"),
    )
    args = parser.parse_args()

    runtime_rows = [row for row in load_rows(args.runtime) if in_window(row)]
    backtest_rows = [row for row in load_rows(args.backtest) if in_window(row)]

    if not runtime_rows:
        raise RuntimeError("No runtime trades found in exact window.")
    if not backtest_rows:
        raise RuntimeError(
            "No backtest trades found in exact window. "
            "If the backtest artifact stores only a summary, supply its trade-level CSV/export."
        )

    runtime_keys = [key(row) for row in runtime_rows]
    backtest_keys = [key(row) for row in backtest_rows]
    runtime_counts = Counter(runtime_keys)
    backtest_counts = Counter(backtest_keys)

    common = sum((runtime_counts & backtest_counts).values())
    runtime_only_count = sum((runtime_counts - backtest_counts).values())
    backtest_only_count = sum((backtest_counts - runtime_counts).values())

    runtime_only = [
        row for row in runtime_rows
        if runtime_counts[key(row)] > backtest_counts[key(row)]
    ]
    backtest_only = [
        row for row in backtest_rows
        if backtest_counts[key(row)] > runtime_counts[key(row)]
    ]

    result = {
        "mode": "NON_CANONICAL_FORENSIC",
        "experiment": "SP2L_V2_EXACT_WINDOW_RECONCILIATION",
        "window_utc": {
            "start": START.isoformat(),
            "end_exclusive": END.isoformat(),
        },
        "runtime": stats(runtime_rows),
        "backtest": stats(backtest_rows),
        "matching_key": "entry_time_utc + direction + entry + sl",
        "common_trades": common,
        "runtime_only": runtime_only_count,
        "backtest_only": backtest_only_count,
        "coverage_match_pct": 100.0 * common / max(len(runtime_rows), len(backtest_rows)),
        "runtime_only_examples": runtime_only[:25],
        "backtest_only_examples": backtest_only[:25],
        "notes": [
            "Diagnostic only; does not alter geometry or execution semantics.",
            "A JSON summary without trade-level records cannot support trade-level reconciliation.",
        ],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = args.output_dir / f"SP2L_EXACT_WINDOW_RECON_{stamp}.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(result, indent=2))
    print(f"RECON_JSON={output}")


if __name__ == "__main__":
    main()
