#!/usr/bin/env python3
"""Diagnostic: inspect deterministic timestamp/price anchors between V2 Forward and Backtest.

Diagnostic only. Does not alter strategy geometry or define a canonical matching rule.
For each Forward signal_id, reports exact timestamp matches across all known backtest
time fields and nearest backtest timestamps for inspection. Price equality is reported
separately and is never used to select a match.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


TIME_FIELDS = (
    "setup_time",
    "before_spike_time",
    "spike_time",
    "after_spike_time",
    "entry_time",
)
PRICE_FIELDS = ("entry", "sl", "tp")
MAX_NEAREST = 10


def load_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def signal_ts(signal_id):
    try:
        return int(signal_id.split(":")[-2])
    except (AttributeError, IndexError, ValueError):
        return None


def iso(ts):
    if ts is None:
        return None
    return datetime.fromtimestamp(int(ts), timezone.utc).isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--forward", required=True)
    ap.add_argument("--backtest", required=True)
    ap.add_argument("--signals", nargs="*", default=None,
                    help="Optional signal IDs. If omitted, use all Forward signals.")
    ap.add_argument("--output", required=True)
    a = ap.parse_args()

    events = load_jsonl(Path(a.forward))
    backtest = json.loads(Path(a.backtest).read_text(encoding="utf-8"))
    rows = backtest.get("outcomes", {}).get("signals_detail", [])

    # Prefer TELEGRAM_SIGNAL, but retain lifecycle signal IDs if needed.
    forward_by_id = {}
    for e in events:
        sid = e.get("signal_id")
        if not sid:
            continue
        ts = signal_ts(sid)
        if ts is None:
            continue
        if e.get("event") == "TELEGRAM_SIGNAL":
            forward_by_id[sid] = e
        elif sid not in forward_by_id:
            forward_by_id[sid] = e

    selected = a.signals if a.signals else sorted(forward_by_id)
    results = []

    for sid in selected:
        sig = forward_by_id.get(sid, {})
        ts = signal_ts(sid)
        direction = sid.split(":")[-1] if sid.count(":") >= 2 else None

        candidates = [
            r for r in rows
            if r.get("direction") == direction
        ]

        exact = []
        nearest = []
        for r in candidates:
            deltas = {
                field: abs(int(r[field]) - ts)
                for field in TIME_FIELDS
                if r.get(field) is not None
            }
            if not deltas:
                continue
            min_delta = min(deltas.values())
            matched_fields = [f for f, d in deltas.items() if d == 0]
            if matched_fields:
                exact.append({
                    "matched_time_fields": matched_fields,
                    "row": r,
                })
            nearest.append({
                "min_delta_seconds": min_delta,
                "nearest_time_fields": [
                    f for f, d in deltas.items() if d == min_delta
                ],
                "row": r,
            })

        nearest.sort(key=lambda x: (
            x["min_delta_seconds"],
            int(x["row"].get("entry_time") or 0),
        ))

        forward_prices = {
            field: sig.get(field)
            for field in PRICE_FIELDS
            if sig.get(field) is not None
        }
        price_hits = []
        if forward_prices:
            for r in candidates:
                matched = []
                for field in PRICE_FIELDS:
                    fp = forward_prices.get(field)
                    bp = r.get(field)
                    if fp is None or bp is None:
                        continue
                    if float(fp) == float(bp):
                        matched.append(field)
                if matched:
                    price_hits.append({
                        "matched_price_fields": matched,
                        "row": r,
                    })

        results.append({
            "signal_id": sid,
            "direction": direction,
            "signal_timestamp": ts,
            "signal_timestamp_utc": iso(ts),
            "forward_event": sig,
            "exact_timestamp_matches": exact,
            "price_only_matches": price_hits,
            "nearest_timestamp_candidates": nearest[:MAX_NEAREST],
        })

    summary = {
        "status": "COMPLETE",
        "diagnostic_only": True,
        "rule_defined": False,
        "time_fields_inspected": list(TIME_FIELDS),
        "price_fields_inspected": list(PRICE_FIELDS),
        "backtest_rows": len(rows),
        "signals_inspected": len(results),
        "exact_timestamp_match_signals": sum(
            bool(x["exact_timestamp_matches"]) for x in results
        ),
        "price_only_match_signals": sum(
            bool(x["price_only_matches"]) for x in results
        ),
        "results": results,
    }

    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )

    print(json.dumps({
        k: v for k, v in summary.items() if k != "results"
    }, ensure_ascii=False, indent=2))
    print(f"SAVED: {out}")


if __name__ == "__main__":
    main()
