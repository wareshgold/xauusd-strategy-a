"""Research-only SP2L MT5 discovery matrix runner.

This runner does NOT define canonical Strategy A geometry. It evaluates an
explicit parameter grid supplied by the operator, separately per symbol, using
the existing MT5 M1 replay engine and shared research detector.

The grid is never inferred, optimized, or changed by this script. The exact
values used are recorded in the output so a selected configuration can later
be frozen and compatibility-checked by the forward runner.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import run_sp2l_mt5_local_multi_symbol_backtest as replay


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "artifacts" / "backtest-mt5-discovery"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_values(raw: str, name: str) -> list[float]:
    values = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            values.append(float(item))
        except ValueError as exc:
            raise SystemExit(f"Invalid {name} value: {item!r}") from exc
    if not values:
        raise SystemExit(f"{name} must contain at least one numeric value")
    return values


def run_matrix(symbol: str, rates: np.ndarray, grid: list[dict]) -> list[dict]:
    rows = []
    original = {
        "P_GAP_PRICE": replay.P_GAP_PRICE,
        "SPIKE_MULTIPLIER": replay.SPIKE_MULTIPLIER,
        "MAX_SL_DISTANCE": replay.MAX_SL_DISTANCE,
        "TP_R": replay.TP_R,
    }

    try:
        for idx, params in enumerate(grid, start=1):
            replay.P_GAP_PRICE = params["p_gap_price"]
            replay.SPIKE_MULTIPLIER = params["spike_multiplier"]
            replay.MAX_SL_DISTANCE = params["max_sl_distance"]
            replay.TP_R = params["tp_r"]

            result = replay.run_symbol(symbol, rates)
            row = {
                "grid_id": idx,
                **params,
                "symbol": symbol,
                "signals": result["signals"],
                "wins": result["wins"],
                "losses": result["losses"],
                "ambiguous": result["ambiguous"],
                "open_at_end": result["open_at_end"],
                "data_gap": result["data_gap"],
                "decisive": result["decisive"],
                "win_rate_pct": result["win_rate_pct"],
                "wilson_95_ci_pct": result["wilson_95_ci_pct"],
                "net_r": result["net_r"],
                "profit_factor_simplified": result["profit_factor_simplified"],
                "max_drawdown_r": result["max_drawdown_r"],
                "max_consecutive_losses": result["max_consecutive_losses"],
                "by_direction": result["by_direction"],
            }
            rows.append(row)

            print(
                f"[MATRIX] {symbol} {idx}/{len(grid)} "
                f"pGap={params['p_gap_price']} "
                f"spike={params['spike_multiplier']} "
                f"SL={params['max_sl_distance']} "
                f"tpR={params['tp_r']} "
                f"signals={row['signals']} decisive={row['decisive']} "
                f"WR={row['win_rate_pct']} netR={row['net_r']}",
                flush=True,
            )
    finally:
        for key, value in original.items():
            setattr(replay, key, value)

    return rows


def rank_rows(rows: list[dict]) -> list[dict]:
    # Descriptive ordering only. The script does not declare a canonical winner.
    # Primary ordering is net R, then decisive sample size, then WR.
    return sorted(
        rows,
        key=lambda x: (
            float("-inf") if x["net_r"] is None else x["net_r"],
            -int(x["decisive"]),
            float("-inf") if x["win_rate_pct"] is None else x["win_rate_pct"],
        ),
        reverse=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="UTC ISO, e.g. 2026-08-26T00:00:00Z")
    parser.add_argument("--end", required=True, help="UTC ISO, e.g. 2026-09-25T23:59:59Z")
    parser.add_argument("--symbols", default="XAUUSD,EURUSD,USDJPY")
    parser.add_argument("--p-gap-values", required=True, help="Comma-separated research values")
    parser.add_argument("--spike-values", required=True, help="Comma-separated research values")
    parser.add_argument("--sl-values", required=True, help="Comma-separated research values")
    parser.add_argument("--tp-values", required=True, help="Comma-separated research values")
    parser.add_argument("--mt5-path", default=None)
    args = parser.parse_args()

    p_gaps = parse_values(args.p_gap_values, "p-gap-values")
    spikes = parse_values(args.spike_values, "spike-values")
    sls = parse_values(args.sl_values, "sl-values")
    tps = parse_values(args.tp_values, "tp-values")

    grid = [
        {
            "p_gap_price": p,
            "spike_multiplier": s,
            "max_sl_distance": sl,
            "tp_r": tp,
        }
        for p in p_gaps
        for s in spikes
        for sl in sls
        for tp in tps
    ]

    if not grid:
        raise SystemExit("Empty matrix")

    requested = [x.strip().upper() for x in args.symbols.split(",") if x.strip()]

    if args.mt5_path:
        initialized = replay.mt5.initialize(path=str(Path(args.mt5_path)))
    else:
        initialized = replay.mt5.initialize()

    if not initialized:
        terminal = None if args.mt5_path else replay.find_mt5_terminal()
        if terminal is None or not replay.mt5.initialize(path=str(terminal)):
            print(json.dumps({
                "status": "MT5_INIT_FAILED",
                "error": replay.mt5.last_error(),
                "terminal_path": str(terminal) if terminal else None,
            }, indent=2))
            return 2

    try:
        discovered = replay.discover_symbols(requested)
        usable = {k: v for k, v in discovered.items() if v["symbol"]}

        start = datetime.fromisoformat(args.start.replace("Z", "+00:00"))
        end = datetime.fromisoformat(args.end.replace("Z", "+00:00"))

        report = {
            "status": "RESEARCH_ONLY",
            "mode": "SP2L_MT5_DISCOVERY_MATRIX",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "period": {"start_utc": start.isoformat(), "end_utc": end.isoformat()},
            "timeframe": "M1",
            "requested_bases": requested,
            "resolved_symbols": discovered,
            "matrix": {
                "p_gap_values": p_gaps,
                "spike_values": spikes,
                "sl_values": sls,
                "tp_values": tps,
                "grid_size": len(grid),
                "evaluation_count": len(grid) * len(usable),
                "ordering": "descriptive_netR_then_decisive_then_WR_only",
                "canonical": False,
            },
            "research_session_filter": {
                "enabled": replay.SESSION_FILTER_ENABLED,
                "window": "London open -> New York close",
                "london_open_local": replay.LONDON_SESSION_OPEN,
                "new_york_close_local": replay.NEW_YORK_SESSION_CLOSE,
                "canonical": False,
            },
            "outcomes": {},
            "selection_status": "NO_CONFIGURATION_SELECTED_BY_SCRIPT",
            "notes": [
                "Every grid value is supplied explicitly by the operator; no parameter is inferred or optimized by this runner.",
                "Each asset is evaluated independently against the same explicit matrix.",
                "Rows are descriptively ordered only; the script does not promote a winner to canonical Strategy A.",
                "The selected configuration for forward testing must be a separately documented research decision and then frozen.",
                "Forward compatibility must compare the frozen per-asset configuration against the exact matrix row before any forward run.",
                "P-Gap, fill semantics, and execution semantics remain research-only/unresolved where source evidence is unresolved.",
            ],
        }

        for base, meta in usable.items():
            symbol = meta["symbol"]
            print(f"[MT5] {base} -> {symbol}: downloading M1 history once ...", flush=True)
            rates = replay.fetch_rates(symbol, start, end)
            rows = run_matrix(symbol, rates, grid)
            report["outcomes"][base] = {
                "symbol": symbol,
                "bars": int(len(replay.filter_rates_to_research_session(rates))),
                "history_chunks": replay.fetch_rates.last_diagnostics,
                "rows": rows,
                "descriptive_ranked_rows": rank_rows(rows),
            }

        failed = [x for x in requested if x not in report["outcomes"]]
        report["status"] = "COMPLETE" if not failed else "INCOMPLETE_SYMBOLS"
        report["failed_symbols"] = failed

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = OUT_DIR / f"SP2L_MT5_DISCOVERY_MATRIX_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        print(json.dumps({
            "status": report["status"],
            "report": str(path),
            "grid_size_per_symbol": len(grid),
            "evaluation_count": len(grid) * len(usable),
            "symbols": {k: v["symbol"] for k, v in discovered.items()},
        }, indent=2))
        return 0 if not failed else 3
    finally:
        replay.mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
