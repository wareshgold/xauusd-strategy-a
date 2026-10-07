"""SP2L XAUUSD controlled exit-discovery matrix.

Research-only. Freezes one signal/entry population, then replays many exit
variants against the exact same M1 bars. It does not change SP2L geometry.

IMPORTANT:
- pGap/spike/SL/entry geometry come only from sp2l_v3_config.py.
- MT5 symbol point is used for trailing activation/distance.
- No-trailing is an explicit separate variant.
- SL+TP touched on the same completed M1 bar is AMBIGUOUS, never guessed.
- This is a discovery tool, not canonical Strategy A logic and not production
  BUY/SELL decisioning.
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
OUT = ROOT / "artifacts" / "v3_discovery"
OUT.mkdir(parents=True, exist_ok=True)

VOLUME = cfg.VOLUME

# Controlled discovery grid. This is intentionally broad enough to discover
# profitable regions without silently changing signal/entry geometry.
RR_GRID = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0)
ACTIVATION_POINTS_GRID = (3.0, 5.0, 10.0, 15.0, 20.0)
DISTANCE_POINTS_GRID = (1.0, 2.0, 3.0, 4.0, 5.0, 8.0, 10.0)


def iso(ts):
    return datetime.fromtimestamp(int(ts), timezone.utc).isoformat() if ts is not None else None


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
    population = []
    seen = set()

    # Same frozen candidate population for every exit variant.
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
            (
                k for k in range(i + 1, len(bars))
                if int(bars[k]["time"]) == candidate["trigger_time"]
            ),
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


def replay_trade(candidate, bars, rr, activation_points, distance_points, mt5_point, contract_size):
    entry_idx = candidate["entry_idx"]
    entry = candidate["theoretical_entry"]
    risk = candidate["risk"]
    direction = candidate["direction"]
    initial_sl = candidate["sl"]
    initial_tp = (
        entry + rr * risk if direction == "BUY" else entry - rr * risk
    )

    trailing_enabled = activation_points is not None and distance_points is not None
    activation_price = activation_points * mt5_point if trailing_enabled else 0.0
    distance_price = distance_points * mt5_point if trailing_enabled else 0.0

    current_sl = initial_sl
    activated = False
    activation_time = None
    max_fav = 0.0
    max_adverse = 0.0
    exit_price = None
    exit_time = None
    reason = "OPEN_OR_UNRESOLVED"
    ambiguous = False

    # IMPORTANT: trailing is evaluated only from the just-completed bar and
    # therefore becomes effective on the NEXT M1 bar. The current bar cannot
    # use its own final high/low to move its own stop; doing that is lookahead.
    for k in range(entry_idx + 1, len(bars)):
        b = bars[k]
        high = float(b["high"])
        low = float(b["low"])

        if direction == "BUY":
            favorable = high - entry
            adverse = entry - low
            max_fav = max(max_fav, favorable)
            max_adverse = max(max_adverse, adverse)

            hit_sl = low <= current_sl
            hit_tp = high >= initial_tp

            if hit_sl and hit_tp:
                ambiguous = True
                reason = "SL_AND_TP_SAME_BAR"
                exit_time = int(b["time"])
                break
            if hit_sl:
                exit_price = current_sl
                reason = "TRAIL_SL" if activated and current_sl > initial_sl else "SL"
                exit_time = int(b["time"])
                break
            if hit_tp:
                exit_price = initial_tp
                reason = "TP"
                exit_time = int(b["time"])
                break

            # Only after the bar has completed may it activate/update the
            # trailing stop for the next bar.
            if trailing_enabled and not activated and favorable >= activation_price:
                activated = True
                activation_time = int(b["time"])

            if activated:
                candidate_sl = high - distance_price
                current_sl = max(current_sl, candidate_sl)

        else:
            favorable = entry - low
            adverse = high - entry
            max_fav = max(max_fav, favorable)
            max_adverse = max(max_adverse, adverse)

            hit_sl = high >= current_sl
            hit_tp = low <= initial_tp

            if hit_sl and hit_tp:
                ambiguous = True
                reason = "SL_AND_TP_SAME_BAR"
                exit_time = int(b["time"])
                break
            if hit_sl:
                exit_price = current_sl
                reason = "TRAIL_SL" if activated and current_sl < initial_sl else "SL"
                exit_time = int(b["time"])
                break
            if hit_tp:
                exit_price = initial_tp
                reason = "TP"
                exit_time = int(b["time"])
                break

            if trailing_enabled and not activated and favorable >= activation_price:
                activated = True
                activation_time = int(b["time"])

            if activated:
                candidate_sl = low + distance_price
                current_sl = min(current_sl, candidate_sl)

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
        "rr": rr,
        "activation_points": activation_points,
        "activation_price": activation_price,
        "distance_points": distance_points,
        "distance_price": distance_price,
        "trailing_enabled": trailing_enabled,
        "trailing_activated": activated,
        "activation_time_utc": iso(activation_time),
        "final_sl": current_sl,
        "max_favorable_price": max_fav,
        "max_adverse_price": max_adverse,
        "exit_time_utc": iso(exit_time),
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

    activated = sum(1 for r in rows if r["trailing_activated"])
    trail_exits = sum(1 for r in decisive if r["reason"] == "TRAIL_SL")
    tp_exits = sum(1 for r in decisive if r["reason"] == "TP")
    sl_exits = sum(1 for r in decisive if r["reason"] == "SL")

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
        "activation_pct": 100.0 * activated / len(rows) if rows else None,
        "trail_exits": trail_exits,
        "tp_exits": tp_exits,
        "original_sl_exits": sl_exits,
    }


def rank_key(row):
    # Trader-facing discovery rank: dollars first, then R/PF/DD/trade count.
    # This is NOT a production selection rule.
    net = row["net_profit_usd"]
    pf = row["profit_factor"] if row["profit_factor"] is not None else -999.0
    dd = row["max_drawdown_R"]
    return (
        net,
        row["net_R"],
        pf,
        -dd,
        row["decisive"],
        -row["ambiguous"],
    )


def make_variants():
    variants = [{"name": f"RR{rr:g}_NO_TRAIL", "rr": rr, "activation_points": None, "distance_points": None}
                for rr in RR_GRID]
    for rr in RR_GRID:
        for activation in ACTIVATION_POINTS_GRID:
            for distance in DISTANCE_POINTS_GRID:
                variants.append({
                    "name": f"RR{rr:g}_ACT{activation:g}_D{distance:g}",
                    "rr": rr,
                    "activation_points": activation,
                    "distance_points": distance,
                })
    return variants


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mt5-path", required=True)
    ap.add_argument("--symbol", default="XAUUSD.ecn")
    ap.add_argument("--start", default="2026-10-05T00:00:00+00:00")
    ap.add_argument("--end", default="2026-10-07T05:30:00+00:00")
    args = ap.parse_args()

    start = datetime.fromisoformat(args.start)
    end = datetime.fromisoformat(args.end)
    if end <= start:
        raise ValueError("--end must be after --start")

    if not mt5.initialize(path=args.mt5_path):
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        info = mt5.symbol_info(args.symbol)
        if info is None:
            raise RuntimeError(f"Symbol unavailable: {args.symbol}")
        if not mt5.symbol_select(args.symbol, True):
            raise RuntimeError(f"symbol_select failed: {mt5.last_error()}")

        bars = fetch_m1_rates(args.symbol, start, end)
        if len(bars) < 10:
            raise RuntimeError(f"Insufficient M1 data: {mt5.last_error()}")

        mt5_point = float(getattr(info, "point", 0.01) or 0.01)
        contract_size = float(getattr(info, "trade_contract_size", 100.0) or 100.0)
        population = build_population(bars, args.symbol)
        variants = make_variants()

        matrix = []
        all_trades = []

        for variant in variants:
            rows = [
                replay_trade(
                    candidate,
                    bars,
                    variant["rr"],
                    variant["activation_points"],
                    variant["distance_points"],
                    mt5_point,
                    contract_size,
                )
                for candidate in population
            ]
            for row in rows:
                row["variant"] = variant["name"]
            summary = summarize(rows)
            matrix.append({**variant, **summary})
            all_trades.extend(rows)

        ranked = sorted(matrix, key=rank_key, reverse=True)

        result = {
            "version": "SP2L_V3_CONTROLLED_DISCOVERY_20261007",
            "research_only": True,
            "symbol": args.symbol,
            "timeframe": "M1",
            "window_utc": {"start": start.isoformat(), "end": end.isoformat()},
            "bars": len(bars),
            "frozen_population": {
                "signals": len(population),
                "policy": "ONE_SHARED_SIGNAL_ENTRY_POPULATION_FOR_ALL_EXIT_VARIANTS",
            },
            "geometry": {
                "source_config": cfg.VERSION,
                "pGapPrice": cfg.P_GAP_PRICE,
                "spikeMultiplier": cfg.SPIKE_MULTIPLIER,
                "maxSlDistance": cfg.MAX_SL_DISTANCE,
                "entryPolicy": "cfg.find_first_entry",
                "sessionPolicy": cfg.SESSION_POLICY,
            },
            "execution_assumptions": {
                "volume": VOLUME,
                "contract_size": contract_size,
                "usd_per_price_unit_at_volume": VOLUME * contract_size,
                "spread_slippage_commission": "NOT_MODELED",
                "mt5_point": mt5_point,
                "trailing_units": "MT5_POINT",
            },
            "exit_policy": {
                "trailing": "activate after favorable move reaches ACT points; update SL from completed M1 high/low by D points",
                "sameBarPolicy": "SL_AND_TP_SAME_BAR => AMBIGUOUS",
                "tpPolicy": "fixed initial TP = Entry +/- RR * risk",
                "noTrailPolicy": "explicitly disables trailing",
            },
            "discovery_grid": {
                "rr": list(RR_GRID),
                "activation_points": list(ACTIVATION_POINTS_GRID),
                "distance_points": list(DISTANCE_POINTS_GRID),
                "variant_count": len(variants),
            },
            "ranking": "NET_USD, then NET_R, then PROFIT_FACTOR, then lower MAX_DD_R, then decisive count; discovery-only",
            "matrix": ranked,
            "trades": all_trades,
        }

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = OUT / f"SP2L_V3_CONTROLLED_DISCOVERY_{stamp}"
        raw = json.dumps(result, indent=2, ensure_ascii=False)
        json_path = base.with_suffix(".json")
        json_path.write_text(raw, encoding="utf-8")

        summary_csv = base.with_name(base.name + "_SUMMARY.csv")
        fields = [
            "name", "rr", "activation_points", "distance_points",
            "signals", "decisive", "wins", "losses", "ambiguous",
            "win_rate_decisive_pct", "net_R", "profit_factor", "max_drawdown_R",
            "max_losing_streak", "gross_profit_usd", "gross_loss_usd",
            "net_profit_usd", "avg_R_per_decisive", "avg_usd_per_decisive",
            "activation_pct", "trail_exits", "tp_exits", "original_sl_exits",
        ]
        with summary_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(ranked)

        trades_csv = base.with_name(base.name + "_TRADES.csv")
        trade_fields = sorted(all_trades[0].keys()) if all_trades else []
        with trades_csv.open("w", newline="", encoding="utf-8") as f:
            if trade_fields:
                w = csv.DictWriter(f, fieldnames=trade_fields)
                w.writeheader()
                w.writerows(all_trades)

        sha = hashlib.sha256(raw.encode()).hexdigest()
        snapshot = base.with_name(base.name + "_SNAPSHOT.md")
        top = ranked[:10]
        lines = [
            "# SP2L Controlled Discovery Matrix Snapshot",
            "",
            "Research-only. No canonical rule or production decision is created.",
            f"Window UTC: {start.isoformat()} -> {end.isoformat()}",
            f"Symbol: {args.symbol}",
            f"M1 bars: {len(bars)}",
            f"Frozen signal/entry population: {len(population)}",
            f"Variants: {len(variants)}",
            f"MT5 point: {mt5_point}",
            f"Volume: {VOLUME}",
            f"Contract size: {contract_size}",
            "",
            "Geometry frozen from sp2l_v3_config.py:",
            f"- pGap={cfg.P_GAP_PRICE}",
            f"- spikeMultiplier={cfg.SPIKE_MULTIPLIER}",
            f"- maxSL={cfg.MAX_SL_DISTANCE}",
            f"- entry={cfg.__name__}.find_first_entry",
            f"- session={cfg.SESSION_POLICY}",
            "",
            "Trailing uses MT5 point units; TP is recalculated independently for every RR.",
            "SL+TP touched on the same M1 bar => ambiguous and excluded from decisive statistics.",
            "",
            "Top 10 by discovery rank (NET USD first):",
        ]
        for i, row in enumerate(top, 1):
            lines.append(
                f"{i}. {row['name']} | USD={row['net_profit_usd']:.4f} | "
                f"R={row['net_R']:.4f} | PF={row['profit_factor']} | "
                f"DD={row['max_drawdown_R']:.4f}R | decisive={row['decisive']} | "
                f"ambiguous={row['ambiguous']}"
            )
        lines.extend([
            "",
            "This ranking is historical discovery only. A candidate must survive",
            "untouched validation, robustness/stability, and fresh holdout before",
            "it can be considered for any production research gate.",
            f"",
            f"JSON SHA256: {sha}",
        ])
        snapshot.write_text("\n".join(lines) + "\n", encoding="utf-8")

        print(json.dumps({
            "status": "COMPLETE",
            "version": result["version"],
            "window": result["window_utc"],
            "populationSignals": len(population),
            "variantCount": len(variants),
            "json": str(json_path),
            "summaryCsv": str(summary_csv),
            "tradesCsv": str(trades_csv),
            "snapshot": str(snapshot),
            "sha256": sha,
            "top10": top,
        }, indent=2))

    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
