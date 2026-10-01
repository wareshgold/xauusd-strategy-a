"""SP2L V3 XAUUSD 3-month fixed-population exit matrix.

The detector and entry population are generated exactly once. Every exit variant
replays that same frozen candidate population; only TP/trailing exit parameters
change. Research only; no production decisioning.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5
import numpy as np
import sp2l_v3_config as cfg

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "v3"
OUT.mkdir(parents=True, exist_ok=True)

VOLUME = cfg.VOLUME
XAU_PIP_SIZE_PRICE = cfg.XAU_PIP_SIZE_PRICE

VARIANTS = [
    ("RR1_NO_TRAIL", 1.0, 0.0),
    ("RR2_NO_TRAIL", 2.0, 0.0),
    ("RR1_TRAIL5", 1.0, 5.0),
    ("RR1_TRAIL10", 1.0, 10.0),
    ("RR1_TRAIL15", 1.0, 15.0),
    ("RR1_TRAIL20", 1.0, 20.0),
    ("RR1_TRAIL30", 1.0, 30.0),
    ("RR2_TRAIL5", 2.0, 5.0),
    ("RR2_TRAIL10", 2.0, 10.0),
    ("RR2_TRAIL15", 2.0, 15.0),
    ("RR2_TRAIL20", 2.0, 20.0),
    ("RR2_TRAIL30", 2.0, 30.0),
]


def iso(ts):
    return datetime.fromtimestamp(int(ts), timezone.utc).isoformat()


def fetch_m1_rates(symbol, start, end):
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"symbol_select failed: {symbol} {mt5.last_error()}")

    chunks = []
    cur = start.astimezone(timezone.utc)
    end = end.astimezone(timezone.utc)
    while cur < end:
        chunk_end = min(cur + timedelta(days=7), end)
        rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, cur, chunk_end)
        if rates is None or len(rates) == 0:
            raise RuntimeError(
                f"history failed {cur.isoformat()}..{chunk_end.isoformat()}: {mt5.last_error()}"
            )
        chunks.append(rates.copy())
        cur = chunk_end + timedelta(minutes=1)

    bars = np.concatenate(chunks)
    bars.sort(order="time")
    _, idx = np.unique(bars["time"], return_index=True)
    return bars[np.sort(idx)]


def build_population(bars, symbol):
    """Build the signal/entry population once; exit variants never alter it."""
    population = []
    seen = set()
    for i in range(2, len(bars) - 2):
        setup = cfg.detect(bars[i - 2:i + 1], symbol)
        if not setup:
            continue
        candidate = cfg.find_first_entry(bars, i, setup)
        if not candidate:
            continue
        key = (candidate["trigger_time"], candidate["direction"])
        if key in seen:
            continue
        seen.add(key)
        entry_idx = next(
            (k for k in range(i + 1, len(bars))
             if int(bars[k]["time"]) == candidate["trigger_time"]),
            None,
        )
        if entry_idx is None:
            continue
        population.append({
            **candidate,
            "entry_idx": entry_idx,
            "signal_time_utc": iso(candidate["trigger_time"]),
        })
    return population


def replay_trade(candidate, bars, tp_r, trail_pips, contract_size):
    entry_idx = candidate["entry_idx"]
    entry = candidate["theoretical_entry"]
    risk = candidate["risk"]
    direction = candidate["direction"]
    initial_sl = candidate["sl"]
    initial_tp = entry + tp_r * risk if direction == "BUY" else entry - tp_r * risk
    trail_distance = trail_pips * XAU_PIP_SIZE_PRICE

    final_sl = initial_sl
    trail_active = False
    max_fav = 0.0
    exit_price = None
    exit_time = None
    reason = "OPEN_OR_UNRESOLVED"
    ambiguous = False

    for k in range(entry_idx + 1, len(bars)):
        b = bars[k]
        high = float(b["high"])
        low = float(b["low"])

        if direction == "BUY":
            favorable = high - entry
            max_fav = max(max_fav, favorable)

            if trail_distance > 0 and favorable >= trail_distance:
                trail_active = True
                final_sl = max(final_sl, high - trail_distance)

            hit_sl = low <= final_sl
            hit_tp = high >= initial_tp

            if hit_sl and hit_tp:
                ambiguous = True
                reason = "SL_AND_TP_SAME_BAR"
                exit_time = int(b["time"])
                break
            if hit_sl:
                exit_price = final_sl
                reason = "TRAIL_SL" if trail_active and final_sl > initial_sl else "SL"
                exit_time = int(b["time"])
                break
            if hit_tp:
                exit_price = initial_tp
                reason = "TP"
                exit_time = int(b["time"])
                break

        else:
            favorable = entry - low
            max_fav = max(max_fav, favorable)

            if trail_distance > 0 and favorable >= trail_distance:
                trail_active = True
                final_sl = min(final_sl, low + trail_distance)

            hit_sl = high >= final_sl
            hit_tp = low <= initial_tp

            if hit_sl and hit_tp:
                ambiguous = True
                reason = "SL_AND_TP_SAME_BAR"
                exit_time = int(b["time"])
                break
            if hit_sl:
                exit_price = final_sl
                reason = "TRAIL_SL" if trail_active and final_sl < initial_sl else "SL"
                exit_time = int(b["time"])
                break
            if hit_tp:
                exit_price = initial_tp
                reason = "TP"
                exit_time = int(b["time"])
                break

    realized_price = None
    realized_r = None
    realized_usd = None
    risk_usd = risk * VOLUME * contract_size

    if exit_price is not None:
        realized_price = (
            exit_price - entry if direction == "BUY" else entry - exit_price
        )
        realized_r = realized_price / risk
        realized_usd = realized_price * VOLUME * contract_size

    return {
        "direction": direction,
        "trigger_time": candidate["trigger_time"],
        "signal_time_utc": candidate["signal_time_utc"],
        "theoretical_entry": entry,
        "risk": risk,
        "initial_sl": initial_sl,
        "initial_tp": initial_tp,
        "tp_r": tp_r,
        "trail_pips": trail_pips,
        "trail_distance_price": trail_distance,
        "final_sl": final_sl,
        "trailing_activated": trail_active,
        "max_favorable_price": max_fav,
        "exit_time_utc": iso(exit_time) if exit_time is not None else None,
        "exit_price": exit_price,
        "reason": reason,
        "ambiguous": ambiguous,
        "realized_price": realized_price,
        "realized_R": realized_r,
        "risk_usd": risk_usd,
        "realized_usd": realized_usd,
    }


def summarize(rows):
    decisive = [r for r in rows if not r["ambiguous"] and r["realized_R"] is not None]
    wins = [r for r in decisive if r["realized_R"] > 0]
    losses = [r for r in decisive if r["realized_R"] < 0]
    gross_profit_r = sum(r["realized_R"] for r in wins)
    gross_loss_r = abs(sum(r["realized_R"] for r in losses))
    net_r = sum(r["realized_R"] for r in decisive)
    gross_profit_usd = sum(r["realized_usd"] for r in wins)
    gross_loss_usd = abs(sum(r["realized_usd"] for r in losses))
    net_usd = sum(r["realized_usd"] for r in decisive)

    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    losing_streak = 0
    max_losing_streak = 0
    for r in sorted(decisive, key=lambda x: x["trigger_time"]):
        equity += r["realized_R"]
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
        if r["realized_R"] < 0:
            losing_streak += 1
            max_losing_streak = max(max_losing_streak, losing_streak)
        else:
            losing_streak = 0

    return {
        "signals": len(rows),
        "decisive": len(decisive),
        "wins": len(wins),
        "losses": len(losses),
        "ambiguous": len(rows) - len(decisive),
        "win_rate_decisive_pct": 100.0 * len(wins) / len(decisive) if decisive else None,
        "net_R": net_r,
        "profit_factor": gross_profit_r / gross_loss_r if gross_loss_r else None,
        "max_drawdown_R": max_dd,
        "max_losing_streak": max_losing_streak,
        "gross_profit_usd": gross_profit_usd,
        "gross_loss_usd": gross_loss_usd,
        "net_profit_usd": net_usd,
        "avg_R_per_decisive": net_r / len(decisive) if decisive else None,
        "avg_usd_per_decisive": net_usd / len(decisive) if decisive else None,
    }


def monthly_summary(rows):
    out = {}
    for month in ("2026-07", "2026-08", "2026-09"):
        subset = [
            r for r in rows
            if r["signal_time_utc"] and r["signal_time_utc"].startswith(month)
        ]
        out[month] = summarize(subset)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mt5-path", required=True)
    ap.add_argument("--symbol", default="XAUUSD.ecn")
    ap.add_argument("--start", default="2026-07-01T00:00:00+00:00")
    ap.add_argument("--end", default="2026-10-01T00:00:00+00:00")
    args = ap.parse_args()

    start = datetime.fromisoformat(args.start)
    end = datetime.fromisoformat(args.end)

    if not mt5.initialize(path=args.mt5_path):
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        info = mt5.symbol_info(args.symbol)
        if info is None:
            raise RuntimeError(f"Symbol unavailable: {args.symbol}")
        if not mt5.symbol_select(args.symbol, True):
            raise RuntimeError("symbol_select failed")

        bars = fetch_m1_rates(args.symbol, start, end)
        if len(bars) < 10:
            raise RuntimeError(f"Insufficient M1 data: {mt5.last_error()}")

        contract_size = float(getattr(info, "trade_contract_size", 100.0) or 100.0)
        population = build_population(bars, args.symbol)

        matrix = []
        all_trades = []
        for name, tp_r, trail_pips in VARIANTS:
            rows = []
            for candidate in population:
                row = replay_trade(candidate, bars, tp_r, trail_pips, contract_size)
                row["variant"] = name
                rows.append(row)

            summary = summarize(rows)
            matrix.append({
                "variant": name,
                "tpR": tp_r,
                "trailPips": trail_pips,
                "trailDistancePrice": trail_pips * XAU_PIP_SIZE_PRICE,
                **summary,
                "monthly": monthly_summary(rows),
            })
            all_trades.extend(rows)

        result = {
            "version": "SP2L_V3_EXIT_MATRIX_20261001",
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
                "volume": VOLUME,
                "contractSize": contract_size,
                "usd_per_price_unit_at_volume": VOLUME * contract_size,
                "spread_slippage_commission": "NOT_MODELED",
            },
            "exit_policy": {
                "trailPolicy": "COMPLETED_M1_BAR_HIGH_LOW",
                "sameBarPolicy": "AMBIGUOUS_WHEN_SL_AND_TP_BOTH_TOUCHED",
                "fixedInitialTP": True,
                "trailActivation": "FAVORABLE_MOVE_REACHES_TRAIL_DISTANCE",
            },
            "variants": [
                {"name": n, "tpR": tp, "trailPips": tr, "trailDistancePrice": tr * XAU_PIP_SIZE_PRICE}
                for n, tp, tr in VARIANTS
            ],
            "matrix": matrix,
            "trades": all_trades,
        }

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = OUT / f"SP2L_V3_EXIT_MATRIX_3M_{stamp}"
        raw = json.dumps(result, indent=2, ensure_ascii=False)
        base.with_suffix(".json").write_text(raw, encoding="utf-8")

        csv_path = base.with_suffix(".csv")
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            fields = [
                "variant", "direction", "trigger_time", "signal_time_utc", "theoretical_entry",
                "risk", "initial_sl", "initial_tp", "tp_r", "trail_pips",
                "trail_distance_price", "final_sl", "trailing_activated",
                "max_favorable_price", "exit_time_utc", "exit_price", "reason",
                "ambiguous", "realized_price", "realized_R", "risk_usd", "realized_usd",
            ]
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(all_trades)

        matrix_csv = base.with_name(base.name + "_SUMMARY.csv")
        with matrix_csv.open("w", newline="", encoding="utf-8") as f:
            fields = [
                "variant", "tpR", "trailPips", "trailDistancePrice", "signals",
                "decisive", "wins", "losses", "ambiguous", "win_rate_decisive_pct",
                "net_R", "profit_factor", "max_drawdown_R", "max_losing_streak",
                "gross_profit_usd", "gross_loss_usd", "net_profit_usd",
                "avg_R_per_decisive", "avg_usd_per_decisive",
            ]
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for row in matrix:
                w.writerow({k: row[k] for k in fields})

        sha = hashlib.sha256(raw.encode()).hexdigest()
        snap = f"""# SP2L V3 Exit Matrix Snapshot

Version: SP2L_V3_EXIT_MATRIX_20261001
Window UTC: {start.isoformat()} → {end.isoformat()}
Symbol: {args.symbol}
Timeframe: M1
Bars: {len(bars)}

Frozen signal population: {len(population)} signals
All exit variants replay exactly this same population.

Geometry:
- pGap={cfg.P_GAP_PRICE}
- spikeMultiplier={cfg.SPIKE_MULTIPLIER}
- maxSL={cfg.MAX_SL_DISTANCE}
- entry policy={cfg.__name__}.find_first_entry
- session={cfg.SESSION_POLICY}

Volume: {VOLUME}
Contract size: {contract_size}
USD per 1.00 XAU price movement at 0.01 lot: {VOLUME * contract_size:.4f}
Spread/slippage/commission: not modeled

Variants:
- RR1_NO_TRAIL
- RR2_NO_TRAIL
- RR1_TRAIL5
- RR1_TRAIL10
- RR1_TRAIL15
- RR1_TRAIL20
- RR1_TRAIL30
- RR2_TRAIL5
- RR2_TRAIL10
- RR2_TRAIL15
- RR2_TRAIL20
- RR2_TRAIL30

Trailing: completed M1 bar high/low.
Same-bar SL + TP: ambiguous and excluded from decisive win rate.
Trailing is research-only and not source-confirmed canonical Strategy A.

JSON SHA256: {sha}
"""
        snap_path = base.with_name(base.name + "_SNAPSHOT.md")
        snap_path.write_text(snap, encoding="utf-8")

        print(json.dumps({
            "status": "COMPLETE",
            "version": result["version"],
            "populationSignals": len(population),
            "json": str(base.with_suffix(".json")),
            "tradesCsv": str(csv_path),
            "summaryCsv": str(matrix_csv),
            "snapshot": str(snap_path),
            "sha256": sha,
            "matrix": matrix,
        }, indent=2))

    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
