#!/usr/bin/env python3
"""Research-only concentration/stability analysis for the completed SP2L FX discovery matrix.

This consumes an existing matrix CSV. It does not rerun backtests and does not
select or promote canonical Strategy A rules.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import median


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output-csv", required=True)
    ap.add_argument("--output-json", required=True)
    args = ap.parse_args()

    rows = list(csv.DictReader(Path(args.input).open(newline="", encoding="utf-8")))
    if not rows:
        raise SystemExit("input CSV is empty")

    required = {
        "symbol_requested",
        "p_gap_pips",
        "spike_multiplier",
        "max_sl_pips",
        "net_r",
    }
    missing = sorted(required - set(rows[0]))
    if missing:
        raise SystemExit(f"missing required columns: {missing}")

    groups: dict[tuple[float, float, float], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (f(row, "p_gap_pips"), f(row, "spike_multiplier"), f(row, "max_sl_pips"))
        groups[key].append(row)

    out = []
    for key, rs in groups.items():
        per_symbol: dict[str, float] = defaultdict(float)
        for row in rs:
            per_symbol[row["symbol_requested"]] += f(row, "net_r")

        values = list(per_symbol.values())
        total = sum(values)
        positive = sum(v > 0 for v in values)
        negative = sum(v < 0 for v in values)
        flat = sum(v == 0 for v in values)
        top_symbol, top_symbol_net = max(per_symbol.items(), key=lambda kv: kv[1])
        top_share = (
            top_symbol_net / total if total > 0 and top_symbol_net > 0 else math.nan
        )

        leave_one_out = {
            symbol: total - value for symbol, value in per_symbol.items()
        }
        worst_leave_one_out = min(leave_one_out.values())

        out.append({
            "p_gap_pips": key[0],
            "spike_multiplier": key[1],
            "max_sl_pips": key[2],
            "symbols": len(per_symbol),
            "positive_symbols": positive,
            "negative_symbols": negative,
            "flat_symbols": flat,
            "all_symbols_positive": positive == len(per_symbol),
            "net_r": total,
            "mean_symbol_net_r": total / len(values),
            "median_symbol_net_r": median(values),
            "min_symbol_net_r": min(values),
            "max_symbol_net_r": max(values),
            "top_symbol": top_symbol,
            "top_symbol_net_r": top_symbol_net,
            "top_symbol_share_of_total": top_share,
            "worst_leave_one_out_net_r": worst_leave_one_out,
            "min_symbol_values": json.dumps(
                {s: per_symbol[s] for s in sorted(per_symbol)},
                separators=(",", ":"),
            ),
        })

    out.sort(key=lambda x: (
        -x["net_r"],
        -x["positive_symbols"],
        x["top_symbol_share_of_total"] if math.isfinite(x["top_symbol_share_of_total"]) else math.inf,
        x["p_gap_pips"],
        x["spike_multiplier"],
        x["max_sl_pips"],
    ))

    fields = list(out[0].keys())
    with Path(args.output_csv).open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(out)

    payload = {
        "status": "COMPLETE",
        "research_only": True,
        "input_rows": len(rows),
        "configurations": len(out),
        "analysis": [
            "Per-symbol net R is summed from the completed matrix; no backtest is rerun.",
            "top_symbol_share_of_total is descriptive concentration, not a selection criterion.",
            "worst_leave_one_out_net_r removes the strongest positive symbol from the aggregate.",
            "No configuration is promoted to canonical Strategy A.",
            "This is a discovery/stability diagnostic; untouched validation and multiple-testing controls remain required."
        ],
        "results": out,
    }
    Path(args.output_json).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"COMPLETE rows={len(rows)} configurations={len(out)}")
    print(f"CSV={args.output_csv}")
    print(f"JSON={args.output_json}")
    for i, x in enumerate(out[:10], 1):
        print(
            f"{i:02d} PGap={x['p_gap_pips']} Spike={x['spike_multiplier']} SL={x['max_sl_pips']} "
            f"NetR={x['net_r']:.4f} Pos/Neg={x['positive_symbols']}/{x['negative_symbols']} "
            f"Top={x['top_symbol']} TopShare={x['top_symbol_share_of_total']:.4f} "
            f"WorstLeaveOneOut={x['worst_leave_one_out_net_r']:.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
