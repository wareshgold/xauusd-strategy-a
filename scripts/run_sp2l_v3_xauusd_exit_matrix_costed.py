"""SP2L V3 XAUUSD exit matrix with modeled trading costs + walk-forward split.

Extends run_sp2l_v3_xauusd_exit_matrix: identical frozen signal population and
replay logic, but every realized trade additionally pays:
  - full spread once per trade (BUY at entry / SELL at exit, direction-neutral)
  - slippage on stop-type exits (SL and TRAIL_SL only; TP fills exact)
Summaries are split into TRAIN (before --split-date) and VALIDATE (on/after)
for walk-forward sanity checking. Research only; no production decisioning.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5
import sp2l_v3_config as cfg
import run_sp2l_v3_xauusd_exit_matrix as base

OUT = base.OUT
STOP_REASONS = {"SL", "TRAIL_SL"}


def apply_costs(rows, spread, slippage, contract_size):
    for row in rows:
        if row["realized_R"] is None:
            continue
        price = row["realized_price"]
        slip = slippage if row["reason"] in STOP_REASONS else 0.0
        adjusted = price - spread - slip
        row["realized_R_nocost"] = row["realized_R"]
        row["realized_usd_nocost"] = row["realized_usd"]
        row["realized_R"] = adjusted / row["risk"]
        row["realized_usd"] = adjusted * base.VOLUME * contract_size
        row["cost_price"] = price - adjusted
    return rows


def split_summaries(rows, split_date):
    train = [r for r in rows if (r["signal_time_utc"] or "") < split_date]
    validate = [r for r in rows if (r["signal_time_utc"] or "") >= split_date]
    return {
        "split_date": split_date,
        "train": base.summarize(train),
        "validate": base.summarize(validate),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mt5-path", default=None)
    ap.add_argument("--symbol", default="XAUUSD.ecn")
    ap.add_argument("--start", default="2026-07-01T00:00:00+00:00")
    ap.add_argument("--end", default="2026-10-01T00:00:00+00:00")
    ap.add_argument("--spread", type=float, default=0.20,
                    help="XAUUSD.ecn modeled spread in price units (one full spread per trade)")
    ap.add_argument("--slippage", type=float, default=0.05,
                    help="modeled slippage applied to stop-type exits (SL/TRAIL_SL)")
    ap.add_argument("--split-date", default="2026-09-01T00:00:00+00:00",
                    help="walk-forward boundary: TRAIN < date <= VALIDATE (signal_time_utc frame)")
    args = ap.parse_args()

    start = datetime.fromisoformat(args.start)
    end = datetime.fromisoformat(args.end)

    mt5_path = args.mt5_path
    if not mt5_path:
        try:
            from mt5_terminal_resolver import find_mt5_terminal
            mt5_path = find_mt5_terminal()
        except Exception:
            mt5_path = None
    if not (mt5.initialize(path=str(mt5_path)) if mt5_path else mt5.initialize()):
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        info = mt5.symbol_info(args.symbol)
        if info is None:
            raise RuntimeError(f"Symbol unavailable: {args.symbol}")
        if not mt5.symbol_select(args.symbol, True):
            raise RuntimeError("symbol_select failed")

        bars = base.fetch_m1_rates(args.symbol, start, end)
        if len(bars) < 10:
            raise RuntimeError(f"Insufficient M1 data: {mt5.last_error()}")

        contract_size = float(getattr(info, "trade_contract_size", 100.0) or 100.0)
        population = base.build_population(bars, args.symbol)

        matrix = []
        all_trades = []
        for name, tp_r, trail_pips in base.VARIANTS:
            rows = []
            for candidate in population:
                row = base.replay_trade(candidate, bars, tp_r, trail_pips, contract_size)
                row["variant"] = name
                rows.append(row)
            apply_costs(rows, args.spread, args.slippage, contract_size)

            summary = base.summarize(rows)
            matrix.append({
                "variant": name,
                "tpR": tp_r,
                "trailPips": trail_pips,
                "trailDistancePrice": trail_pips * base.XAU_PIP_SIZE_PRICE,
                **summary,
                "monthly": base.monthly_summary(rows),
                "walk_forward": split_summaries(rows, args.split_date),
            })
            all_trades.extend(rows)

        result = {
            "version": "SP2L_V3_EXIT_MATRIX_COSTED_20261001",
            "research_only": True,
            "symbol": args.symbol,
            "timeframe": "M1",
            "start_utc": start.isoformat(),
            "end_utc": end.isoformat(),
            "bars": len(bars),
            "population": {
                "signals": len(population),
                "population_policy": "FROZEN_ONCE_SHARED_BY_ALL_EXIT_VARIANTS",
                "entry_geometry": {
                    "pGapPrice": cfg.P_GAP_PRICE,
                    "spikeMultiplier": cfg.SPIKE_MULTIPLIER,
                    "maxSlDistance": cfg.MAX_SL_DISTANCE,
                    "entryPolicy": "cfg.find_first_entry",
                    "sessionPolicy": cfg.SESSION_POLICY,
                },
            },
            "execution_assumptions": {
                "volume": base.VOLUME,
                "contractSize": contract_size,
                "usd_per_price_unit_at_volume": base.VOLUME * contract_size,
                "spread_price": args.spread,
                "slippage_price": args.slippage,
                "cost_policy": "FULL_SPREAD_ONCE_PER_TRADE + SLIPPAGE_ON_SL_AND_TRAIL_SL_ONLY",
                "calibration": {
                    "observed_live_spread": "0.18 (bid/ask 4160.51/4160.69)",
                    "observed_live_slippage": "0.06 worst (SL 4162.97 filled 4162.91)",
                },
            },
            "exit_policy": {
                "trailPolicy": "COMPLETED_M1_BAR_HIGH_LOW",
                "sameBarPolicy": "AMBIGUOUS_WHEN_SL_AND_TP_BOTH_TOUCHED",
                "fixedInitialTP": True,
                "trailActivation": "FAVORABLE_MOVE_REACHES_TRAIL_DISTANCE",
            },
            "walk_forward": {
                "split_date": args.split_date,
                "frame": "signal_time_utc (server-clock frame, consistent with monthly buckets)",
            },
            "variants": [
                {"name": n, "tpR": tp, "trailPips": tr,
                 "trailDistancePrice": tr * base.XAU_PIP_SIZE_PRICE}
                for n, tp, tr in base.VARIANTS
            ],
            "matrix": matrix,
            "trades": all_trades,
        }

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base_path = OUT / f"SP2L_V3_EXIT_MATRIX_COSTED_3M_{stamp}"
        raw = json.dumps(result, indent=2, ensure_ascii=False)
        base_path.with_suffix(".json").write_text(raw, encoding="utf-8")

        trades_csv = base_path.with_suffix(".csv")
        with trades_csv.open("w", newline="", encoding="utf-8") as f:
            fields = [
                "variant", "direction", "trigger_time", "signal_time_utc",
                "theoretical_entry", "risk", "initial_sl", "initial_tp", "tp_r",
                "trail_pips", "trail_distance_price", "final_sl",
                "trailing_activated", "max_favorable_price", "exit_time_utc",
                "exit_price", "reason", "ambiguous", "cost_price",
                "realized_R_nocost", "realized_R", "risk_usd", "realized_usd",
            ]
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(all_trades)

        summary_csv = base_path.with_name(base_path.name + "_SUMMARY.csv")
        with summary_csv.open("w", newline="", encoding="utf-8") as f:
            fields = [
                "variant", "tpR", "trailPips", "trailDistancePrice", "signals",
                "decisive", "wins", "losses", "ambiguous", "win_rate_decisive_pct",
                "net_R", "profit_factor", "max_drawdown_R", "max_losing_streak",
                "net_profit_usd", "avg_R_per_decisive",
                "train_net_R", "train_profit_factor", "train_decisive",
                "validate_net_R", "validate_profit_factor",
                "validate_win_rate_decisive_pct", "validate_decisive",
            ]
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            for row in matrix:
                flat = dict(row)
                wf = row["walk_forward"]
                flat["train_net_R"] = wf["train"]["net_R"]
                flat["train_profit_factor"] = wf["train"]["profit_factor"]
                flat["train_decisive"] = wf["train"]["decisive"]
                flat["validate_net_R"] = wf["validate"]["net_R"]
                flat["validate_profit_factor"] = wf["validate"]["profit_factor"]
                flat["validate_win_rate_decisive_pct"] = wf["validate"]["win_rate_decisive_pct"]
                flat["validate_decisive"] = wf["validate"]["decisive"]
                w.writerow({k: flat.get(k) for k in fields})

        sha = hashlib.sha256(raw.encode()).hexdigest()
        snap = f"""# SP2L V3 Exit Matrix (costed) Snapshot

Version: SP2L_V3_EXIT_MATRIX_COSTED_20261001
Window UTC: {start.isoformat()} → {end.isoformat()}
Symbol: {args.symbol}
Timeframe: M1
Bars: {len(bars)}

Frozen signal population: {len(population)} signals (identical to uncased matrix).

Costs modeled:
- spread: {args.spread} price units, full amount once per trade (BUY pays at entry, SELL at exit)
- slippage: {args.slippage} price units on stop-type exits only (SL / TRAIL_SL); TP fills exact
- calibration: live spread observed 0.18, live SL slippage observed 0.06 worst

Walk-forward split (signal_time_utc frame): TRAIN < {args.split_date} <= VALIDATE
- TRAIN = July + August 2026, VALIDATE = September 2026

Trailing: completed M1 bar high/low; same-bar SL+TP ambiguous and excluded.
Volume: {base.VOLUME}, contract size: {contract_size}.

JSON SHA256: {sha}
"""
        snap_path = base_path.with_name(base_path.name + "_SNAPSHOT.md")
        snap_path.write_text(snap, encoding="utf-8")

        print(json.dumps({
            "status": "COMPLETE",
            "version": result["version"],
            "populationSignals": len(population),
            "json": str(base_path.with_suffix(".json")),
            "tradesCsv": str(trades_csv),
            "summaryCsv": str(summary_csv),
            "snapshot": str(snap_path),
            "sha256": sha,
            "matrix": [
                {
                    "variant": m["variant"],
                    "net_R": m["net_R"],
                    "PF": m["profit_factor"],
                    "WR": m["win_rate_decisive_pct"],
                    "train_net_R": m["walk_forward"]["train"]["net_R"],
                    "val_net_R": m["walk_forward"]["validate"]["net_R"],
                    "val_PF": m["walk_forward"]["validate"]["profit_factor"],
                }
                for m in matrix
            ],
        }, indent=2))

    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
