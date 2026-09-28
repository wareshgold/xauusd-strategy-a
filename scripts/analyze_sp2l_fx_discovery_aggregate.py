#!/usr/bin/env python3
"""Aggregate the completed SP2L FX discovery matrix by parameter configuration.

Research-only diagnostic. It does not select or promote canonical Strategy A rules.
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


def optional_f(row: dict[str, str], key: str) -> float | None:
    raw = row.get(key, "").strip()
    return None if raw == "" else float(raw)


def reconstruct_gross(
    net_r: float,
    pf: float | None,
    wins: int,
    losses: int,
) -> tuple[float, float]:
    """Recover gross profit/loss R without inventing missing PF semantics.

    Standard matrix semantics permit a blank PF when there are no losses
    (infinite/undefined PF) or when there are no trades. Those cases are
    reconstructable from the row's win/loss counts and net R. A finite PF is
    required when losses exist.
    """
    if wins == 0 and losses == 0:
        return (0.0, 0.0)

    if losses == 0:
        if wins > 0 and math.isfinite(net_r) and net_r > 0:
            return (net_r, 0.0)
        return (math.nan, math.nan)

    if pf is None or not math.isfinite(pf) or pf <= 0:
        return (math.nan, math.nan)

    if abs(pf - 1.0) < 1e-12:
        if abs(net_r) < 1e-12:
            return (math.nan, math.nan)
        return (math.nan, math.nan)

    loss = net_r / (pf - 1.0)
    profit = pf * loss
    if not math.isfinite(profit) or not math.isfinite(loss) or loss < 0:
        return (math.nan, math.nan)
    return (profit, abs(loss))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output-csv", required=True)
    ap.add_argument("--output-json", required=True)
    args = ap.parse_args()

    rows = list(csv.DictReader(Path(args.input).open(newline="", encoding="utf-8")))
    if not rows:
        raise SystemExit("input CSV is empty")

    groups: dict[tuple[float, float, float], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (f(row, "p_gap_pips"), f(row, "spike_multiplier"), f(row, "max_sl_pips"))
        groups[key].append(row)

    out = []
    for key, rs in groups.items():
        symbols = sorted({r["symbol_requested"] for r in rs})
        per_symbol = {}
        for symbol in symbols:
            srows = [r for r in rs if r["symbol_requested"] == symbol]
            per_symbol[symbol] = sum(f(r, "net_r") for r in srows)

        net_values = list(per_symbol.values())
        gross_profit_r = 0.0
        gross_loss_r = 0.0
        pf_reconstruct_ok = True
        for r in rs:
            p, l = reconstruct_gross(
                f(r, "net_r"),
                optional_f(r, "profit_factor"),
                int(r["wins"]),
                int(r["losses"]),
            )
            if math.isnan(p) or math.isnan(l):
                pf_reconstruct_ok = False
                break
            gross_profit_r += p
            gross_loss_r += l

        trades = sum(int(r["trades"]) for r in rs)
        wins = sum(int(r["wins"]) for r in rs)
        losses = sum(int(r["losses"]) for r in rs)
        if pf_reconstruct_ok and gross_loss_r > 0:
            aggregate_pf = gross_profit_r / gross_loss_r
            aggregate_pf_status = "FINITE"
        elif pf_reconstruct_ok and gross_profit_r > 0 and gross_loss_r == 0:
            aggregate_pf = None
            aggregate_pf_status = "INFINITE_NO_GROSS_LOSS"
        elif pf_reconstruct_ok and trades == 0:
            aggregate_pf = None
            aggregate_pf_status = "UNDEFINED_NO_TRADES"
        else:
            aggregate_pf = None
            aggregate_pf_status = "INVALID_RECONSTRUCTION"

        net_r = sum(f(r, "net_r") for r in rs)
        positive = sum(v > 0 for v in net_values)
        negative = sum(v < 0 for v in net_values)
        flat = len(net_values) - positive - negative
        worst_dd = max(f(r, "max_drawdown_r") for r in rs)

        out.append({
            "p_gap_pips": key[0],
            "spike_multiplier": key[1],
            "max_sl_pips": key[2],
            "symbols": len(symbols),
            "positive_symbols": positive,
            "negative_symbols": negative,
            "flat_symbols": flat,
            "trades": trades,
            "wins": wins,
            "losses": losses,
            "win_rate_pct": (wins / (wins + losses) * 100.0) if wins + losses else None,
            "net_r": net_r,
            "mean_symbol_net_r": sum(net_values) / len(net_values),
            "median_symbol_net_r": median(net_values),
            "aggregate_profit_factor": aggregate_pf,
            "aggregate_profit_factor_status": aggregate_pf_status,
            "worst_symbol_max_drawdown_r": worst_dd,
            "pf_reconstruction_ok": pf_reconstruct_ok,
        })

    out.sort(key=lambda x: (-x["net_r"], -x["trades"], x["p_gap_pips"], x["spike_multiplier"], x["max_sl_pips"]))

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
        "group_by": ["p_gap_pips", "spike_multiplier", "max_sl_pips"],
        "aggregation_notes": [
            "No configuration is promoted to canonical Strategy A.",
            "Aggregate PF is reconstructed from row-level net_r and PF using standard PF=gross_profit/gross_loss.",
            "A blank PF with wins>0 and losses=0 is treated as zero gross loss; aggregate status records the resulting infinite/undefined PF semantics.",
            "A zero-trade row contributes zero gross profit and zero gross loss; it does not invalidate the aggregate.",
            "Rows with losses require a finite row-level PF; otherwise aggregate PF reconstruction is marked invalid.",
            "Worst drawdown is the maximum reported single-symbol drawdown, not a portfolio-level drawdown.",
            "USD P&L is intentionally not inferred here; it requires broker/account-aware historical monetary calculation at 0.01 lot."
        ],
        "results": out,
    }
    Path(args.output_json).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"COMPLETE rows={len(rows)} configurations={len(out)}")
    print(f"CSV={args.output_csv}")
    print(f"JSON={args.output_json}")
    for i, x in enumerate(out[:10], 1):
        print(
            f"{i:02d} PGap={x['p_gap_pips']} Spike={x['spike_multiplier']} SL={x['max_sl_pips']} "
            f"Trades={x['trades']} WR={x['win_rate_pct']:.2f}% NetR={x['net_r']:.4f} "
            f"Pos/Neg={x['positive_symbols']}/{x['negative_symbols']} "
            f"PF={x['aggregate_profit_factor'] if x['aggregate_profit_factor'] is not None else x['aggregate_profit_factor_status']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
