#!/usr/bin/env python3
"""Research-only Strategy B exit-management matrix.

This tool replays a FROZEN set of Strategy B entry candidates. It does not
generate signals and is not a full strategy backtest if changed exits would
change later entries or trade overlap.

Candles CSV columns: timestamp, open, high, low, close.
Entries CSV columns: entry_time, side (BUY/SELL), entry_price, sl_price.
Optional entries columns: tp_price (blank means no fixed TP), volume, trade_id.

Timestamps are parsed as UTC. The first candle evaluated is strictly after
entry_time. OHLC cannot reveal intrabar ordering; the conservative deterministic
policy checks the existing stop before TP when both are touched. Trailing-stop
updates take effect from the NEXT candle, not the candle that activates it.

Example (PowerShell):
python scripts/research/strategy_b_trailing_matrix.py --candles artifacts/xauusd_m1.csv --entries artifacts/strategy_b_entry_candidates.csv --out-dir artifacts/strategy_b_trailing_matrix_run1 --pip-price 0.10 --contract-size 100 --volume 0.01 --activation-pips 5,10,15,20,25 --trail-gaps 0.20,0.40,0.60,0.80,1.00

With pip-price=0.10, 10 pips = 1.00 XAUUSD price movement. At contract size
100 and volume 0.01, a 1.00 price move is $1 gross before costs. Verify the
exact broker symbol's contract size and pip convention before interpreting PnL.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import pandas as pd
except ImportError:
    raise SystemExit("Missing dependency: pandas. Install with: python -m pip install pandas")


@dataclass(frozen=True)
class Trade:
    trade_id: str
    entry_time: object
    side: int
    entry_price: float
    sl_price: float
    tp_price: Optional[float]
    volume: float


@dataclass(frozen=True)
class Policy:
    name: str
    activation_price: Optional[float]
    trail_gap_price: Optional[float]
    keep_tp: bool
    breakeven: bool = False


def parse_positive_list(raw: str, label: str) -> list[float]:
    try:
        values = [float(x.strip()) for x in raw.split(",") if x.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{label} must be comma-separated numbers") from exc
    if not values or any(not math.isfinite(x) or x <= 0 for x in values):
        raise argparse.ArgumentTypeError(f"{label} values must all be finite and > 0")
    return sorted(set(values))


def column_map(frame):
    return {str(c).strip().lower(): c for c in frame.columns}


def require_columns(frame, required, label):
    cols = column_map(frame)
    missing = [x for x in required if x not in cols]
    if missing:
        raise ValueError(f"{label} missing columns {missing}; found {list(frame.columns)}")
    return cols


def load_candles(path: Path):
    frame = pd.read_csv(path)
    cols = require_columns(frame, ["timestamp", "open", "high", "low", "close"], "candles CSV")
    frame = frame.rename(columns={cols[k]: k for k in cols})
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
    for key in ("open", "high", "low", "close"):
        frame[key] = pd.to_numeric(frame[key], errors="coerce")
    frame = frame.dropna(subset=["timestamp", "open", "high", "low", "close"])
    frame = frame.sort_values("timestamp", kind="stable").drop_duplicates("timestamp", keep="last")
    if frame.empty:
        raise ValueError("No valid OHLC candles after parsing.")
    bad = (frame["high"] < frame[["open", "close", "low"]].max(axis=1)) | (
        frame["low"] > frame[["open", "close", "high"]].min(axis=1)
    )
    if bad.any():
        raise ValueError(f"Invalid OHLC geometry in {int(bad.sum())} candle(s).")
    return frame.reset_index(drop=True)


def load_trades(path: Path, default_volume: float):
    frame = pd.read_csv(path)
    cols = require_columns(frame, ["entry_time", "side", "entry_price", "sl_price"], "entries CSV")
    frame = frame.rename(columns={cols[k]: k for k in cols})
    if "tp_price" not in frame:
        frame["tp_price"] = float("nan")
    if "volume" not in frame:
        frame["volume"] = default_volume
    if "trade_id" not in frame:
        frame["trade_id"] = [f"T{i+1:05d}" for i in range(len(frame))]
    frame["entry_time"] = pd.to_datetime(frame["entry_time"], utc=True, errors="coerce")
    for key in ("entry_price", "sl_price", "tp_price", "volume"):
        frame[key] = pd.to_numeric(frame[key], errors="coerce")
    frame["volume"] = frame["volume"].fillna(default_volume)
    trades = []
    for row in frame.to_dict("records"):
        side_text = str(row.get("side", "")).strip().upper()
        if side_text not in {"BUY", "SELL", "LONG", "SHORT"}:
            continue
        side = 1 if side_text in {"BUY", "LONG"} else -1
        if pd.isna(row["entry_time"]) or pd.isna(row["entry_price"]) or pd.isna(row["sl_price"]):
            continue
        entry, stop = float(row["entry_price"]), float(row["sl_price"])
        tp_raw = row.get("tp_price")
        tp = None if tp_raw is None or pd.isna(tp_raw) else float(tp_raw)
        volume = float(row["volume"])
        if volume <= 0 or (side == 1 and stop >= entry) or (side == -1 and stop <= entry):
            continue
        if tp is not None and ((side == 1 and tp <= entry) or (side == -1 and tp >= entry)):
            raise ValueError(f"{row['trade_id']}: TP must be above BUY entry / below SELL entry.")
        trades.append(Trade(str(row["trade_id"]), row["entry_time"], side, entry, stop, tp, volume))
    if not trades:
        raise ValueError("No valid entries. Check side values, timestamps, and entry/SL geometry.")
    return trades


def simulate(trade: Trade, candles, policy: Policy, args):
    side = trade.side
    stop = trade.sl_price
    tp = trade.tp_price if policy.keep_tp else None
    favorable = trade.entry_price
    activated = False
    start = int(candles["timestamp"].searchsorted(trade.entry_time, side="right"))
    exit_price = exit_time = None
    exit_reason = "END_OF_DATA"
    bars_held = 0

    for j in range(start, len(candles)):
        bar = candles.iloc[j]
        h, l = float(bar.high), float(bar.low)
        bars_held += 1
        # Conservative deterministic handling of same-candle stop/TP ambiguity.
        stop_hit = (l <= stop) if side == 1 else (h >= stop)
        tp_hit = tp is not None and ((h >= tp) if side == 1 else (l <= tp))
        if stop_hit:
            exit_price, exit_time = stop, bar.timestamp
            exit_reason = "TRAIL_SL" if activated else "ORIGINAL_SL"
            break
        if tp_hit:
            exit_price, exit_time, exit_reason = tp, bar.timestamp, "TP"
            break

        # Trailing updates apply starting on the next candle.
        favorable = max(favorable, h) if side == 1 else min(favorable, l)
        move = (favorable - trade.entry_price) * side
        if policy.activation_price is not None and move >= policy.activation_price:
            activated = True
        if activated and policy.trail_gap_price is not None:
            candidate = favorable - side * policy.trail_gap_price
            stop = max(stop, candidate) if side == 1 else min(stop, candidate)
        if policy.breakeven and policy.activation_price is not None and move >= policy.activation_price:
            stop = max(stop, trade.entry_price) if side == 1 else min(stop, trade.entry_price)

    if exit_price is None:
        last = candles.iloc[-1]
        exit_price, exit_time, exit_reason = float(last.close), last.timestamp, "END_OF_DATA_MARK"
    gross = side * (exit_price - trade.entry_price) * args.contract_size * trade.volume
    costs = (args.spread_price + args.slippage_price) * args.contract_size * trade.volume
    costs += args.commission_per_lot * trade.volume
    net = gross - costs
    initial_risk_cash = abs(trade.entry_price - trade.sl_price) * args.contract_size * trade.volume
    r_multiple = net / initial_risk_cash if initial_risk_cash > 0 else float("nan")
    return {
        "trade_id": trade.trade_id, "entry_time": trade.entry_time.isoformat(),
        "exit_time": exit_time.isoformat(), "side": "BUY" if side == 1 else "SELL",
        "entry_price": trade.entry_price, "initial_sl": trade.sl_price,
        "original_tp": "" if trade.tp_price is None else trade.tp_price,
        "exit_price": round(exit_price, 8), "exit_reason": exit_reason,
        "bars_held": bars_held, "volume": trade.volume,
        "gross_pnl": round(gross, 6), "estimated_costs": round(costs, 6),
        "net_pnl": round(net, 6), "initial_risk_cash": round(initial_risk_cash, 6),
        "net_R": round(r_multiple, 6), "activated": activated,
    }


def summarize(name, rows):
    values = [float(r["net_pnl"]) for r in rows]
    rs = [float(r["net_R"]) for r in rows if math.isfinite(float(r["net_R"]))]
    wins, losses = [x for x in values if x > 0], [x for x in values if x < 0]
    gp, gl = sum(wins), -sum(losses)
    equity = peak = max_dd = 0.0
    for value in values:
        equity += value
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    reasons = {}
    for row in rows:
        reasons[row["exit_reason"]] = reasons.get(row["exit_reason"], 0) + 1
    return {
        "policy": name, "trades": len(values), "wins": len(wins), "losses": len(losses),
        "win_rate_pct": round(100 * len(wins) / len(values), 4) if values else 0,
        "net_pnl": round(sum(values), 6),
        "avg_net_pnl": round(sum(values) / len(values), 6) if values else 0,
        "profit_factor": round(gp / gl, 6) if gl else ("INF" if gp else 0),
        "expectancy_R": round(sum(rs) / len(rs), 6) if rs else 0,
        "max_drawdown_cash_trade_order": round(max_dd, 6),
        "end_of_data_marks": reasons.get("END_OF_DATA_MARK", 0),
        "exit_reasons": json.dumps(reasons, sort_keys=True),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--candles", required=True, type=Path)
    p.add_argument("--entries", required=True, type=Path, help="Frozen entry-candidate CSV; not a trade-close CSV")
    p.add_argument("--out-dir", required=True, type=Path, help="Must not already exist; protects prior evidence")
    p.add_argument("--pip-price", type=float, default=0.10, help="Price units per pip; default 0.10")
    p.add_argument("--contract-size", type=float, default=100.0)
    p.add_argument("--volume", type=float, default=0.01)
    p.add_argument("--activation-pips", default="5,10,15,20,25")
    p.add_argument("--trail-gaps", default="0.20,0.40,0.60,0.80,1.00", help="Gap in XAUUSD price units, not pips")
    p.add_argument("--spread-price", type=float, default=0.0, help="Estimated full round-trip spread in price units")
    p.add_argument("--slippage-price", type=float, default=0.0, help="Estimated full round-trip slippage in price units")
    p.add_argument("--commission-per-lot", type=float, default=0.0, help="Round-trip commission per 1.0 lot")
    args = p.parse_args()
    if min(args.pip_price, args.contract_size, args.volume) <= 0:
        p.error("pip-price, contract-size, and volume must be > 0")
    if min(args.spread_price, args.slippage_price, args.commission_per_lot) < 0:
        p.error("cost inputs must be >= 0")
    if args.out_dir.exists():
        p.error(f"Output directory already exists; refusing to overwrite evidence: {args.out_dir}")
    activations = parse_positive_list(args.activation_pips, "activation-pips")
    gaps = parse_positive_list(args.trail_gaps, "trail-gaps")
    candles = load_candles(args.candles)
    trades = load_trades(args.entries, args.volume)
    args.out_dir.mkdir(parents=True, exist_ok=False)

    policies = [Policy("B0_BASELINE_SL_TP", None, None, True),
                Policy("B1_NO_FIXED_TP_ORIGINAL_SL", None, None, False)]
    for activation in activations:
        price_threshold = activation * args.pip_price
        policies.append(Policy(f"BE_ACT_{activation:g}PIP", price_threshold, None, True, True))
        for gap in gaps:
            policies.append(Policy(f"TRAIL_TP_ACT_{activation:g}PIP_GAP_{gap:g}", price_threshold, gap, True))
            policies.append(Policy(f"TRAIL_NO_TP_ACT_{activation:g}PIP_GAP_{gap:g}", price_threshold, gap, False))
    for gap in gaps:
        policies.append(Policy(f"TRAIL_IMMEDIATE_TP_GAP_{gap:g}", 0.0, gap, True))

    summaries, details = [], []
    for policy in policies:
        rows = [simulate(t, candles, policy, args) for t in trades]
        for row in rows:
            row["policy"] = policy.name
        summaries.append(summarize(policy.name, rows))
        details.extend(rows)

    summary_path = args.out_dir / "matrix_summary.csv"
    detail_path = args.out_dir / "trade_replay_detail.csv"
    manifest_path = args.out_dir / "run_manifest.json"
    pd.DataFrame(summaries).to_csv(summary_path, index=False)
    pd.DataFrame(details).to_csv(detail_path, index=False)
    manifest = {
        "mode": "fixed_entry_exit_replay_not_full_strategy_backtest",
        "candles_path": str(args.candles.resolve()), "entries_path": str(args.entries.resolve()),
        "candle_rows": len(candles), "entry_rows_used": len(trades),
        "candle_start_utc": candles.iloc[0].timestamp.isoformat(),
        "candle_end_utc": candles.iloc[-1].timestamp.isoformat(),
        "pip_price": args.pip_price, "contract_size": args.contract_size, "default_volume": args.volume,
        "activation_pips": activations, "trail_gaps_price": gaps,
        "spread_price_round_trip": args.spread_price, "slippage_price_round_trip": args.slippage_price,
        "commission_per_lot_round_trip": args.commission_per_lot,
        "intrabar_policy": "existing stop checked before TP; trailing updates apply next candle",
        "outputs": [summary_path.name, detail_path.name],
        "warning": "Conditional on supplied frozen entries. END_OF_DATA_MARK is marked to final close, not a realized broker exit."
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Completed: {len(policies)} exit policies x {len(trades)} frozen entries")
    print(f"Summary: {summary_path}")
    print(f"Details: {detail_path}")
    print(f"Manifest: {manifest_path}")
    print("IMPORTANT: this is an exit-policy replay, not a full Strategy B re-simulation.")


if __name__ == "__main__":
    main()
