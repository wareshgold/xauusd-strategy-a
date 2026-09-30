"""Audit per-signal outcome transitions from the V2 RR=1 trailing matrix.

NON_CANONICAL_FORENSIC only. This script does not select or promote any
strategy rule. It compares the exact OFF baseline against requested trailing
variants using the matrix artifact's shared signal population.

For each trailing variant it reports:
- OFF result -> trailing result transition counts
- R delta by transition
- USD P&L delta by transition
- baseline/trailing ambiguous and unresolved transitions
- signal identity mismatches (should be zero)

Usage:
  python scripts/audit_v2_trailing_transition_matrix.py \
    --input artifacts/forensic/2026-09-30/V2_3MONTH_EXACT_FORWARD_BASELINE_TRAILING_USD.json \
    --output artifacts/forensic/2026-09-30/V2_3MONTH_TRAILING_TRANSITIONS.json
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


BASELINE_TRAIL = 0.0
DEFAULT_TRAILS = [10.0, 20.0, 30.0, 50.0]
RESULTS = {"WIN", "LOSS", "BREAKEVEN", "AMBIGUOUS", "OPEN_OR_UNRESOLVED"}


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") != "COMPLETE":
        raise ValueError(f"input status is not COMPLETE: {data.get('status')}")
    return data


def key(row: dict) -> tuple:
    # signal_index is generated from the shared population; entry_time is a
    # secondary identity check so accidental row replacement cannot hide.
    return (
        int(row["signal_index"]),
        int(row["entry_time"]),
        str(row["direction"]),
        round(float(row["entry"]), 10),
        round(float(row["sl"]), 10),
    )


def index_variant(variant: dict) -> dict:
    return {key(row): row for row in variant["trades"]}


def transition_name(a: str, b: str) -> str:
    return f"{a}_TO_{b}"


def summarize_transition(rows: list[tuple[dict, dict]]) -> dict:
    counts = defaultdict(int)
    r_delta = defaultdict(float)
    usd_delta = defaultdict(float)
    for base, trail in rows:
        a = str(base["result"])
        b = str(trail["result"])
        name = transition_name(a, b)
        counts[name] += 1
        if base.get("r") is not None and trail.get("r") is not None:
            r_delta[name] += float(trail["r"]) - float(base["r"])
        if base.get("pnl_usd") is not None and trail.get("pnl_usd") is not None:
            usd_delta[name] += float(trail["pnl_usd"]) - float(base["pnl_usd"])
    return {
        "counts": dict(sorted(counts.items())),
        "net_r_delta_by_transition": dict(sorted((k, round(v, 10)) for k, v in r_delta.items())),
        "net_usd_delta_by_transition": dict(sorted((k, round(v, 10)) for k, v in usd_delta.items())),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--trail-pips", nargs="+", type=float, default=DEFAULT_TRAILS)
    args = ap.parse_args()

    data = load(Path(args.input))
    variants = data["variants"]
    lookup = {(float(v["rr"]), float(v["trail_pips"])): v for v in variants}

    baseline_variant = lookup.get((1.0, BASELINE_TRAIL))
    if baseline_variant is None:
        raise ValueError("RR=1 / trail=0 OFF baseline is missing")

    baseline = index_variant(baseline_variant)
    results = []
    for trail in args.trail_pips:
        variant = lookup.get((1.0, float(trail)))
        if variant is None:
            raise ValueError(f"RR=1 / trail={trail} is missing")
        current = index_variant(variant)

        base_keys = set(baseline)
        current_keys = set(current)
        missing_from_trailing = sorted(base_keys - current_keys)
        extra_in_trailing = sorted(current_keys - base_keys)
        if missing_from_trailing or extra_in_trailing:
            raise ValueError(
                f"population mismatch trail={trail}: "
                f"missing={len(missing_from_trailing)} extra={len(extra_in_trailing)}"
            )

        pairs = [(baseline[k], current[k]) for k in sorted(base_keys)]
        transitions = summarize_transition(pairs)

        comparable_r = [
            float(t["r"]) - float(b["r"])
            for b, t in pairs
            if b.get("r") is not None and t.get("r") is not None
        ]
        comparable_usd = [
            float(t["pnl_usd"]) - float(b["pnl_usd"])
            for b, t in pairs
            if b.get("pnl_usd") is not None and t.get("pnl_usd") is not None
        ]

        results.append({
            "rr": 1.0,
            "trail_pips": float(trail),
            "population_signals": len(pairs),
            "identity_mismatches": 0,
            "baseline_summary": baseline_variant["summary"],
            "trailing_summary": variant["summary"],
            "total_net_r_delta": round(sum(comparable_r), 10),
            "total_net_usd_delta": round(sum(comparable_usd), 10),
            "comparable_r_pairs": len(comparable_r),
            "comparable_usd_pairs": len(comparable_usd),
            "transitions": transitions,
        })

    out = {
        "status": "COMPLETE",
        "mode": "NON_CANONICAL_FORENSIC",
        "experiment": "V2_XAUUSD_RR1_OFF_VS_TRAILING_TRANSITIONS",
        "source_artifact": str(Path(args.input)),
        "baseline": {"rr": 1.0, "trail_pips": 0.0, "semantics": "OFF"},
        "variants": results,
        "interpretation_guard": [
            "This is transition accounting only; it does not rank or select a strategy.",
            "Trailing behavior is NON_CANONICAL_FORENSIC and source-unconfirmed.",
            "AMBIGUOUS and OPEN_OR_UNRESOLVED outcomes are retained rather than inferred.",
        ],
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": out["status"],
        "output": args.output,
        "variants": [
            {
                "trail_pips": r["trail_pips"],
                "population_signals": r["population_signals"],
                "identity_mismatches": r["identity_mismatches"],
                "net_R_delta": r["total_net_r_delta"],
                "net_USD_delta": r["total_net_usd_delta"],
                "transitions": r["transitions"]["counts"],
            }
            for r in results
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
