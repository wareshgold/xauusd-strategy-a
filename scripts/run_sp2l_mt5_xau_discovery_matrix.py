"""Research-only XAUUSD discovery matrix.

Price-unit parity runner for XAUUSD.ecn. This intentionally avoids FX pip
normalization and delegates signal/outcome semantics to the shared MT5 replay
engine used by the existing XAUUSD replay.

Research-only; never canonical and never used to generate production orders.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import run_sp2l_mt5_local_multi_symbol_backtest as replay

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "artifacts" / "backtest-mt5-xau-discovery"
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


def run_matrix(rates: np.ndarray, grid: list[dict]) -> list[dict]:
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
            replay.MAX_SL_DISTANCE = params["max_sl_price"]
            replay.TP_R = params["tp_r"]

            result = replay.run_symbol("XAUUSD.ecn", rates)
            row = {
                "grid_id": idx,
                **params,
                "symbol": "XAUUSD.ecn",
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
                f"[XAU-DISCOVERY] {idx}/{len(grid)} "
                f"pGap={params['p_gap_price']} spike={params['spike_multiplier']} "
                f"SL={params['max_sl_price']} tpR={params['tp_r']} "
                f"signals={row['signals']} decisive={row['decisive']} "
                f"WR={row['win_rate_pct']} netR={row['net_r']}",
                flush=True,
            )
    finally:
        for key, value in original.items():
            setattr(replay, key, value)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--p-gap-price", required=True)
    parser.add_argument("--spike-values", required=True)
    parser.add_argument("--max-sl-price", required=True)
    parser.add_argument("--tp-values", required=True)
    parser.add_argument("--mt5-path", required=True)
    args = parser.parse_args()

    p_gaps = parse_values(args.p_gap_price, "p-gap-price")
    spikes = parse_values(args.spike_values, "spike-values")
    sls = parse_values(args.max_sl_price, "max-sl-price")
    tps = parse_values(args.tp_values, "tp-values")

    grid = [
        {
            "p_gap_price": p,
            "spike_multiplier": s,
            "max_sl_price": sl,
            "tp_r": tp,
        }
        for p in p_gaps
        for s in spikes
        for sl in sls
        for tp in tps
    ]

    start = datetime.fromisoformat(args.start.replace("Z", "+00:00"))
    end = datetime.fromisoformat(args.end.replace("Z", "+00:00"))

    if not replay.mt5.initialize(path=str(Path(args.mt5_path))):
        raise SystemExit(f"MT5 initialization failed: {replay.mt5.last_error()}")

    try:
        discovered = replay.discover_symbols(["XAUUSD"])
        meta = discovered.get("XAUUSD")
        if not meta or not meta.get("symbol"):
            raise SystemExit(f"XAUUSD symbol discovery failed: {discovered}")

        symbol = meta["symbol"]
        if symbol != "XAUUSD.ecn":
            raise SystemExit(f"XAUUSD resolved to unexpected symbol: {symbol}")

        print(f"[MT5] XAUUSD -> {symbol}: downloading M1 history once ...", flush=True)
        rates = replay.fetch_rates(symbol, start, end)
        rows = run_matrix(rates, grid)

        report = {
            "status": "COMPLETE",
            "research_only": True,
            "canonical": False,
            "mode": "SP2L_MT5_XAUUSD_DISCOVERY_MATRIX_PRICE_UNITS",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "period": {
                "start_utc": start.isoformat(),
                "end_utc": end.isoformat(),
            },
            "timeframe": "M1",
            "symbol_requested": "XAUUSD",
            "symbol_used": symbol,
            "grid": {
                "p_gap_price": p_gaps,
                "spike_values": spikes,
                "max_sl_price": sls,
                "tp_values": tps,
                "grid_size": len(grid),
            },
            "unit_policy": {
                "p_gap": "DIRECT_PRICE_DISTANCE",
                "max_sl": "DIRECT_PRICE_DISTANCE",
                "no_fx_pip_conversion": True,
                "xau_practical_pip_reference": 0.10,
                "note": "The pip reference is documentary only; matrix parameters are direct XAU price distances.",
            },
            "session_filter": {
                "enabled": replay.SESSION_FILTER_ENABLED,
                "window": "London open -> New York close",
            },
            "semantics_source": "scripts/run_sp2l_mt5_local_multi_symbol_backtest.py",
            "rows": rows,
            "selection_status": "NO_CONFIGURATION_SELECTED_BY_SCRIPT",
        }

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = OUT_DIR / f"SP2L_MT5_XAUUSD_DISCOVERY_MATRIX_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({"status": "COMPLETE", "report": str(path), "rows": len(rows)}, indent=2))
        return 0
    finally:
        replay.mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
