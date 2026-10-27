"""Research-only RR2/TRAIL4 matrix with USD-profit activation thresholds."""
from __future__ import annotations
import argparse, csv, hashlib, importlib, json, statistics, sys
from datetime import datetime, timezone
from pathlib import Path
import MetaTrader5 as mt5
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import run_sp2l_v3_xauusd_trailing_matrix as engine

OUT = ROOT / "artifacts" / "v3"
DEFAULT_THRESHOLDS_USD = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
DEFAULT_TRAIL_PIPS = [4, 5, 10, 15, 20, 30, 40, 50]


def parse_numbers(raw, name, allow_zero=False):
    try:
        values = [float(part.strip()) for part in raw.split(",") if part.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{name} must be comma-separated numbers") from exc
    if not values or any((v < 0) if allow_zero else (v <= 0) for v in values):
        raise argparse.ArgumentTypeError(f"{name} values must all be {'>= 0' if allow_zero else '> 0'}")
    return sorted(set(values))


def price_move_for_profit_usd(threshold_usd, contract_size, volume):
    """Linear USD XAUUSD approximation: price move × contract size × lots."""
    if threshold_usd < 0 or contract_size <= 0 or volume <= 0:
        raise ValueError("threshold must be >= 0 and contract_size/volume must be > 0")
    return threshold_usd / (contract_size * volume)


def pip_distance_to_price(pips, pip_size_price):
    if pips <= 0 or pip_size_price <= 0:
        raise ValueError("pips and pip_size_price must be > 0")
    return pips * pip_size_price


def add_excursions(bars, candidate, entry_idx, row, usd_per_price_unit):
    entry, direction = float(candidate["theoretical_entry"]), candidate["direction"]
    end_idx = len(bars) - 1
    if row.get("exit_time") is not None:
        matches = np.flatnonzero(bars["time"] == int(row["exit_time"]))
        if len(matches):
            end_idx = int(matches[0])
    adverse = 0.0
    for k in range(entry_idx + 1, end_idx + 1):
        bar = bars[k]
        move = entry - float(bar["low"]) if direction == "BUY" else float(bar["high"]) - entry
        adverse = max(adverse, move)
    row["mfe_usd_gross"] = float(row["max_favorable_price"]) * usd_per_price_unit
    row["mae_usd_gross"] = max(0.0, adverse) * usd_per_price_unit
    row["realized_usd_gross"] = (
        float(row["realized_price"]) * usd_per_price_unit
        if row["realized_price"] is not None else None
    )
    return row


def summarize_usd(rows, usd_per_price_unit):
    decisive = [r for r in rows if not r["ambiguous"] and r["realized_usd_gross"] is not None]
    ordered = sorted(decisive, key=lambda r: (int(r["exit_time"]), int(r["trigger_time"])))
    wins = [r for r in ordered if r["realized_usd_gross"] > 0]
    losses = [r for r in ordered if r["realized_usd_gross"] < 0]
    values = [r["realized_usd_gross"] for r in ordered]
    gross_win = sum(r["realized_usd_gross"] for r in wins)
    gross_loss = abs(sum(r["realized_usd_gross"] for r in losses))
    equity = peak = max_dd = 0.0
    for r in ordered:
        equity += r["realized_usd_gross"]
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    return {
        "net_pnl_usd_gross": sum(values),
        "profit_factor_gross": gross_win / gross_loss if gross_loss else None,
        "max_drawdown_usd_gross": max_dd,
        "average_trade_usd_gross": statistics.mean(values) if values else None,
        "median_trade_usd_gross": statistics.median(values) if values else None,
        "average_winner_usd_gross": statistics.mean([r["realized_usd_gross"] for r in wins]) if wins else None,
        "average_loser_usd_gross": statistics.mean([r["realized_usd_gross"] for r in losses]) if losses else None,
        "largest_winner_usd_gross": max((r["realized_usd_gross"] for r in wins), default=None),
        "largest_loser_usd_gross": min((r["realized_usd_gross"] for r in losses), default=None),
        "positive_exits_below_1_usd": sum(0 < r["realized_usd_gross"] < 1 for r in ordered),
        "reached_1usd_mfe_closed_below_1usd": sum(r["mfe_usd_gross"] >= 1 and r["realized_usd_gross"] < 1 for r in ordered),
        "reached_2usd_mfe_closed_below_2usd": sum(r["mfe_usd_gross"] >= 2 and r["realized_usd_gross"] < 2 for r in ordered),
        "reached_3usd_mfe_closed_below_3usd": sum(r["mfe_usd_gross"] >= 3 and r["realized_usd_gross"] < 3 for r in ordered),
        "mean_mfe_usd_gross": statistics.mean([r["mfe_usd_gross"] for r in rows]) if rows else None,
        "mean_mae_usd_gross": statistics.mean([r["mae_usd_gross"] for r in rows]) if rows else None,
        "trail_sl_exits": sum(r["reason"] == "TRAIL_SL" for r in ordered),
        "original_sl_exits": sum(r["reason"] == "SL" for r in ordered),
        "tp_exits": sum(r["reason"] == "TP" for r in ordered),
        "usd_per_price_unit_gross": usd_per_price_unit,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mt5-path", required=True)
    ap.add_argument("--symbol", default="XAUUSD.ecn")
    ap.add_argument("--start", default="2026-09-15T00:00:00+00:00")
    ap.add_argument("--end", default="2026-10-15T00:00:00+00:00")
    ap.add_argument("--config-module", default="sp2l_v3_rr2_trail4_config")
    ap.add_argument("--activation-usd", default="0,0.25,0.5,0.75,1,1.5,2,3")
    ap.add_argument("--trail-pips", default="4,5,10,15,20,30,40,50")
    args = ap.parse_args()
    thresholds = parse_numbers(args.activation_usd, "activation-usd", True)
    trails = parse_numbers(args.trail_pips, "trail-pips")
    start, end = datetime.fromisoformat(args.start), datetime.fromisoformat(args.end)
    if start.tzinfo is None or end.tzinfo is None or start >= end:
        raise RuntimeError("--start and --end must be timezone-aware and start < end")
    cfg = importlib.import_module(args.config_module)
    if not mt5.initialize(path=args.mt5_path):
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        info, account = mt5.symbol_info(args.symbol), mt5.account_info()
        if info is None:
            raise RuntimeError(f"symbol_info unavailable: {mt5.last_error()}")
        if account is None or str(getattr(account, "currency", "")).upper() != "USD":
            raise RuntimeError("USD activation conversion requires a readable USD-denominated account")
        profit_currency = str(getattr(info, "currency_profit", "")).upper()
        if profit_currency != "USD":
            raise RuntimeError(f"Expected symbol profit currency USD, got {profit_currency!r}; refusing guessed conversion")
        contract_size = float(getattr(info, "trade_contract_size", 0.0) or 0.0)
        volume = float(getattr(cfg, "VOLUME", 0.0) or 0.0)
        pip_size = float(getattr(cfg, "XAU_PIP_SIZE_PRICE", 0.0) or 0.0)
        if contract_size <= 0 or volume <= 0 or pip_size <= 0:
            raise RuntimeError("Missing/invalid contract size, volume or configured pip-price convention")
        usd_per_price = contract_size * volume
        bars = engine.fetch_m1_rates(args.symbol, start, end)
        if len(bars) < 10:
            raise RuntimeError(f"Insufficient M1 data: {mt5.last_error()}")
        bars_sha = hashlib.sha256(bars.tobytes()).hexdigest()
        candidates = engine.collect_candidates(bars, cfg, args.symbol)
        end_time = int(bars[-1]["time"])
        scenarios = [{
            "scenario": "NO_TRAIL_FIXED_SL_TP", "activation_usd": None,
            "activation_price_equivalent": None, "trail_pips": None,
            "trail_distance_price": None, "activation_price": None, "distance_price": None,
        }, {
            "scenario": "CURRENT_LIVE_TRAIL4_EQUIVALENT",
            "activation_usd": cfg.TRAIL_DISTANCE_PRICE * usd_per_price,
            "activation_price_equivalent": cfg.TRAIL_DISTANCE_PRICE,
            "trail_pips": cfg.TRAIL_PIPS, "trail_distance_price": cfg.TRAIL_DISTANCE_PRICE,
            "activation_price": cfg.TRAIL_DISTANCE_PRICE, "distance_price": cfg.TRAIL_DISTANCE_PRICE,
        }]
        for threshold in thresholds:
            activation_move = price_move_for_profit_usd(threshold, contract_size, volume)
            for pips in trails:
                distance = pip_distance_to_price(pips, pip_size)
                scenarios.append({
                    "scenario": "USD_ACTIVATION_TRAIL_DISTANCE", "activation_usd": threshold,
                    "activation_price_equivalent": activation_move, "trail_pips": pips,
                    "trail_distance_price": distance, "activation_price": activation_move,
                    "distance_price": distance,
                })
        matrix, trade_rows = [], []
        for s in scenarios:
            rows = [
                engine.simulate_one(bars, c, idx, s["activation_price"], s["distance_price"])
                for c, idx in candidates
            ]
            enriched = []
            for (candidate, idx), row in zip(candidates, rows):
                row = add_excursions(bars, candidate, idx, dict(row), usd_per_price)
                row["reached_activation_threshold"] = (
                    s["activation_usd"] is not None and
                    row["max_favorable_price"] >= s["activation_price"]
                )
                row["closed_below_activation_threshold_after_reaching"] = (
                    row["reached_activation_threshold"] and row["realized_usd_gross"] is not None
                    and row["realized_usd_gross"] < s["activation_usd"]
                )
                enriched.append(row)
                trade_rows.append({k: s[k] for k in ("scenario", "activation_usd", "activation_price_equivalent", "trail_pips", "trail_distance_price")} | row)
            summary = engine.summarize(enriched, dataset_end_time=end_time)
            summary.update(summarize_usd(enriched, usd_per_price))
            matrix.append({k: s[k] for k in ("scenario", "activation_usd", "activation_price_equivalent", "trail_pips", "trail_distance_price")} | summary)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = OUT / f"SP2L_V3_USD_ACTIVATION_TRAILING_MATRIX_{stamp}"
        payload = {
            "status": "COMPLETE", "research_only": True, "canonical": False,
            "symbol": args.symbol, "timeframe": "M1",
            "window_utc": {"start": start.isoformat(), "end": end.isoformat()},
            "bars": len(bars), "bars_sha256": bars_sha, "candidate_count": len(candidates),
            "config_module": args.config_module, "config_version": cfg.VERSION,
            "volume_lots": volume, "account_currency": str(account.currency),
            "profit_currency": profit_currency, "contract_size": contract_size,
            "usd_per_price_unit_gross": usd_per_price, "pip_price_convention": pip_size,
            "activation_usd_grid": thresholds, "trail_pips_grid": trails,
            "scenario_count": len(matrix),
            "limitations": [
                "USD conversion assumes linear gross XAUUSD P&L: price move × contract size × lots.",
                "Spread, commission, swap, slippage, currency conversion and broker costs are excluded.",
                "Same-bar SL and TP touches are ambiguous; a new trail applies from the next completed M1 bar.",
                "Theoretical entry/price-level fills; pending-order fill realism, gaps and broker stop/freeze rejections are not modeled.",
                "Current-runner-equivalent scenario does not model live bid/ask stop/freeze constraints.",
                "Independent overlapping trades are not a funded portfolio; drawdown is trade-sequence gross USD drawdown.",
            ],
            "matrix": matrix,
        }
        json_path = base.with_suffix(".json")
        json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        matrix_path = base.with_name(base.name + "_matrix.csv")
        with matrix_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(matrix[0].keys())); w.writeheader(); w.writerows(matrix)
        trades_path = base.with_name(base.name + "_trades.csv")
        with trades_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(trade_rows[0].keys()) if trade_rows else ["scenario"]); w.writeheader(); w.writerows(trade_rows)
        snapshot_path = base.with_name(base.name + "_SNAPSHOT.md")
        snapshot_path.write_text(
            "# RR2/TRAIL4 USD Activation Matrix Snapshot\n\n"
            f"- Window UTC: {start.isoformat()} to {end.isoformat()}\n"
            f"- Symbol/timeframe: {args.symbol}/M1; bars/candidates: {len(bars)}/{len(candidates)}\n"
            f"- Bars SHA-256: {bars_sha}\n- Config: {cfg.VERSION}; volume={volume}; contract size={contract_size}\n"
            f"- Gross USD per price unit: {usd_per_price}; pip-price convention={pip_size}\n"
            f"- Activation USD grid: {thresholds}; trailing pips: {trails}\n"
            f"- Scenarios: {len(matrix)} (no-trail + current-runner equivalent + grid)\n"
            "- Research only; costs and broker execution constraints are not modeled.\n"
            f"- JSON: {json_path.name}\n- Matrix CSV: {matrix_path.name}\n- Trade CSV: {trades_path.name}\n",
            encoding="utf-8")
        print(json.dumps({"status":"COMPLETE","json":str(json_path),"matrix_csv":str(matrix_path),
            "trades_csv":str(trades_path),"snapshot":str(snapshot_path),"bars":len(bars),
            "candidates":len(candidates),"matrix_rows":len(matrix),"bars_sha256":bars_sha,
            "research_only":True}, indent=2))
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
