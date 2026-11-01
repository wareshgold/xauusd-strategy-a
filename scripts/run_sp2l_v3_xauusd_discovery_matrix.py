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
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import MetaTrader5 as mt5
import numpy as np

import sp2l_v3_config as cfg
from strategy_factory.frozen_entry_population import load_frozen_entry_population
from strategy_factory.m1_integrity import m1_gap_detected, validate_m1_artifact

DEFAULT_OUT = ROOT / "artifacts" / "v3_discovery"

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
    timestamps = bars["time"]
    if len(timestamps) > 1 and np.any(np.diff(timestamps) <= 0):
        raise RuntimeError("MT5 M1 history contains duplicate or out-of-order timestamps")
    return bars


BAR_FIELDS = ("time", "open", "high", "low", "close", "tick_volume", "spread", "real_volume")


def load_m1_artifact(path):
    artifact = Path(path)
    if not artifact.is_file():
        raise RuntimeError(f"M1 dataset artifact not found: {artifact}")
    raw = artifact.read_bytes()
    expected = hashlib.sha256(raw).hexdigest()
    if artifact.suffix.lower() == ".csv":
        import io
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
        fields = [
            "time_epoch_seconds", "time_utc_iso", "open", "high", "low", "close",
            "tick_volume", "spread", "real_volume",
        ]
        if reader.fieldnames != fields:
            raise RuntimeError("M1 CSV header does not match the declared source schema")
        dtype = [
            ("time", "i8"), ("open", "f8"), ("high", "f8"), ("low", "f8"),
            ("close", "f8"), ("tick_volume", "i8"), ("spread", "i8"), ("real_volume", "i8"),
        ]
        values = []
        for index, row in enumerate(reader):
            timestamp = int(row["time_epoch_seconds"])
            row_time = datetime.fromisoformat(row["time_utc_iso"].replace("Z", "+00:00"))
            if row_time.tzinfo is None or int(row_time.timestamp()) != timestamp:
                raise RuntimeError(f"M1 CSV row {index} has inconsistent UTC/epoch timestamps")
            values.append((
                timestamp, float(row["open"]), float(row["high"]), float(row["low"]),
                float(row["close"]), int(row["tick_volume"]), int(row["spread"]),
                int(row["real_volume"]),
            ))
        bars = np.array(values, dtype=dtype)
        if not len(bars):
            raise RuntimeError("M1 CSV artifact contains no bars")
        timestamps = bars["time"]
        if np.any(timestamps % 60 != 0) or (len(timestamps) > 1 and np.any(np.diff(timestamps) <= 0)):
            raise RuntimeError("M1 CSV artifact contains invalid, duplicate, or out-of-order timestamps")
        return bars, expected
    payload = json.loads(raw.decode("utf-8"))
    if payload.get("schema_version") != 1:
        raise RuntimeError("unsupported M1 dataset artifact schema")
    rows = payload.get("bars")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("M1 dataset artifact contains no bars")
    dtype = [
        ("time", "i8"),
        ("open", "f8"),
        ("high", "f8"),
        ("low", "f8"),
        ("close", "f8"),
        ("tick_volume", "i8"),
        ("spread", "i8"),
        ("real_volume", "i8"),
    ]
    values = [
        (
            int(row["time"]), float(row["open"]), float(row["high"]),
            float(row["low"]), float(row["close"]), int(row["tick_volume"]),
            int(row["spread"]), int(row["real_volume"]),
        )
        for row in rows
    ]
    bars = np.array(values, dtype=dtype)
    timestamps = bars["time"]
    if len(timestamps) > 1 and np.any(np.diff(timestamps) <= 0):
        raise RuntimeError("M1 artifact contains duplicate or out-of-order timestamps")
    return bars, expected


def write_m1_artifact(path, bars, *, symbol, start, end):
    rows = []
    for bar in bars:
        rows.append({
            "time": int(bar["time"]),
            "open": float(bar["open"]),
            "high": float(bar["high"]),
            "low": float(bar["low"]),
            "close": float(bar["close"]),
            "tick_volume": int(bar["tick_volume"]),
            "spread": int(bar["spread"]),
            "real_volume": int(bar["real_volume"]),
        })
    payload = {
        "schema_version": 1,
        "research_only": True,
        "symbol": symbol,
        "timeframe": "M1",
        "window_utc": {"start": start.isoformat(), "end": end.isoformat()},
        "bars": rows,
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest(), len(raw)


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
    activation_bar_index = None
    trailing_updates = 0
    deferred_trailing_updates = 0
    max_fav = 0.0
    max_adverse = 0.0
    exit_price = None
    exit_time = None
    reason = "OPEN_OR_UNRESOLVED"
    ambiguous = False

    # IMPORTANT: trailing is evaluated only from the just-completed bar and
    # therefore becomes effective on the NEXT M1 bar. The current bar cannot
    # use its own final high/low to move its own stop; doing that is lookahead.
    previous_bar_time = int(bars[entry_idx]["time"])
    for k in range(entry_idx + 1, len(bars)):
        b = bars[k]
        current_bar_time = int(b["time"])
        # A missing M1 interval while the position is open can hide an SL,
        # TP, or trailing event. Do not score a later observed bar as decisive.
        if m1_gap_detected(previous_bar_time, current_bar_time):
            ambiguous = True
            reason = "M1_GAP_WHILE_OPEN"
            exit_time = current_bar_time
            break
        previous_bar_time = current_bar_time
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
                activation_bar_index = k

            if activated:
                candidate_sl = high - distance_price
                # A completed-bar OHLC replay must not assume a BUY stop can be
                # installed above the bar's closing market price. MT5 requires
                # a BUY SL below the current Bid; with M1 OHLC we use close as
                # the conservative bar-end proxy. If the proposed stop is above
                # close, defer the update instead of manufacturing an immediate
                # next-bar stop-out. This is deliberately stricter than the
                # previous implementation.
                if candidate_sl < float(b["close"]):
                    new_sl = max(current_sl, candidate_sl)
                    if new_sl > current_sl:
                        trailing_updates += 1
                    current_sl = new_sl
                else:
                    deferred_trailing_updates += 1

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
                activation_bar_index = k

            if activated:
                candidate_sl = low + distance_price
                # Symmetric SELL rule: a SELL SL must remain above the current
                # Ask. With M1 OHLC, completed-bar close is the conservative
                # bar-end proxy. Defer any stop that would be below close.
                if candidate_sl > float(b["close"]):
                    new_sl = min(current_sl, candidate_sl)
                    if new_sl < current_sl:
                        trailing_updates += 1
                    current_sl = new_sl
                else:
                    deferred_trailing_updates += 1

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
        "activation_bar_index": activation_bar_index,
        "entry_bar_excluded_from_exit_replay": True,
        "trailing_updates": trailing_updates,
        "deferred_trailing_updates": deferred_trailing_updates,
        "exit_after_activation_bars": (
            (int(exit_time) - int(activation_time)) // 60
            if exit_time is not None and activation_time is not None
            else None
        ),
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
        "gap_exposed": sum(1 for r in rows if r["reason"] == "M1_GAP_WHILE_OPEN"),
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
    ap.add_argument("--start", default="2026-09-24T07:57:00+00:00")
    ap.add_argument("--end", default="2026-10-23T23:57:00+00:00")
    ap.add_argument(
        "--bars-artifact",
        default=None,
        help="Byte-preserved M1 JSON or CSV artifact. If supplied, MT5 history is not queried; symbol metadata is still required.",
    )
    ap.add_argument(
        "--write-bars-artifact",
        default=None,
        help="Write the exact MT5 M1 snapshot used by this run to this path.",
    )
    ap.add_argument(
        "--entry-population-artifact",
        default=None,
        help="Frozen Strategy A V3 trade CSV used only for its entry fields.",
    )
    ap.add_argument(
        "--entry-population-sha256",
        default=None,
        help="Expected SHA-256 of the frozen Strategy A V3 trade CSV.",
    )
    ap.add_argument("--output-dir", default=str(DEFAULT_OUT), help="Directory for Discovery JSON/CSV/snapshot outputs.")
    args = ap.parse_args()

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
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

        if args.bars_artifact:
            bars, bars_sha256 = load_m1_artifact(args.bars_artifact)
            m1_integrity_report = validate_m1_artifact(
                args.bars_artifact,
                expected_symbol=args.symbol,
                expected_start=args.start,
                expected_end=args.end,
            ).as_dict()
            dataset_source = "M1_ARTIFACT"
            dataset_artifact = str(Path(args.bars_artifact).resolve())
            dataset_format = Path(args.bars_artifact).suffix.lower().lstrip(".")
            dataset_byte_size = Path(args.bars_artifact).stat().st_size
        else:
            bars = fetch_m1_rates(args.symbol, start, end)
            bars_sha256 = None
            m1_integrity_report = None
            dataset_source = "MT5_LIVE_HISTORY"
            dataset_artifact = None
            dataset_format = "mt5_rates"
            dataset_byte_size = None

        if len(bars) < 10:
            raise RuntimeError(f"Insufficient M1 data: {mt5.last_error()}")

        if args.write_bars_artifact:
            written_sha256, written_bytes = write_m1_artifact(
                Path(args.write_bars_artifact), bars,
                symbol=args.symbol, start=start, end=end,
            )
            bars_sha256 = written_sha256
            dataset_source = "MT5_SNAPSHOT"
            dataset_artifact = str(Path(args.write_bars_artifact).resolve())
            dataset_format = "json"
            dataset_byte_size = written_bytes
            m1_integrity_report = validate_m1_artifact(
                args.write_bars_artifact,
                expected_symbol=args.symbol,
                expected_start=args.start,
                expected_end=args.end,
            ).as_dict()
        else:
            written_bytes = None

        mt5_point = float(getattr(info, "point", 0.01) or 0.01)
        contract_size = float(getattr(info, "trade_contract_size", 100.0) or 100.0)
        if bool(args.entry_population_artifact) != bool(args.entry_population_sha256):
            raise RuntimeError("entry population artifact and SHA-256 must be supplied together")
        if args.entry_population_artifact:
            population, frozen_population_info = load_frozen_entry_population(
                args.entry_population_artifact, bars, args.entry_population_sha256
            )
        else:
            population = build_population(bars, args.symbol)
            frozen_population_info = {
                "source": "REBUILT_FROM_V3_CONFIG",
                "rows": len(population),
                "warning": "No frozen V3 entry CSV was supplied; population was recomputed.",
            }
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
            "dataset_provenance": {
                "source": dataset_source,
                "artifact": dataset_artifact,
                "content_sha256": bars_sha256,
                "byte_size": dataset_byte_size,
                "format": dataset_format,
                "schema_version": 1 if dataset_format == "json" else None,
                "m1_integrity": m1_integrity_report,
            },
            "frozen_population": {
                **frozen_population_info,
                "signals": len(population),
                "policy": "ONE_SHARED_SIGNAL_ENTRY_POPULATION_FOR_ALL_EXIT_VARIANTS",
            },
            "geometry": {
                "source_config": cfg.VERSION,
                "pGapPrice": cfg.P_GAP_PRICE,
                "spikeMultiplier": cfg.SPIKE_MULTIPLIER,
                "maxSlDistance": cfg.MAX_SL_DISTANCE,
                "entryPolicy": "FROZEN_V3_ENTRY_CSV" if args.entry_population_artifact else "cfg.find_first_entry",
                "sessionPolicy": cfg.SESSION_POLICY,
            },
            "execution_assumptions": {
                "volume": VOLUME,
                "contract_size": contract_size,
                "usd_per_price_unit_at_volume": VOLUME * contract_size,
                "spread_slippage_commission": "NOT_MODELED",
                "m1_gap_policy": "OPEN_TRADE_CROSSED_GAP => AMBIGUOUS_NO_REALIZED_EXIT",
                "mt5_point": mt5_point,
                "trailing_units": "MT5_POINT",
            },
            "exit_policy": {
                "trailing": "activate after favorable move reaches ACT points; update SL from completed M1 high/low by D points",
                "sameBarPolicy": "SL_AND_TP_SAME_BAR => AMBIGUOUS",
                "m1GapPolicy": "M1_GAP_WHILE_OPEN => AMBIGUOUS_NO_REALIZED_EXIT",
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

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        base = output_dir / f"SP2L_V3_CONTROLLED_DISCOVERY_{stamp}"
        raw = json.dumps(result, indent=2, ensure_ascii=False)
        json_path = base.with_suffix(".json")
        json_path.write_text(raw, encoding="utf-8")

        summary_csv = base.with_name(base.name + "_SUMMARY.csv")
        fields = [
            "name", "rr", "activation_points", "distance_points",
            "signals", "decisive", "wins", "losses", "ambiguous", "gap_exposed",
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
            f"Dataset source: {dataset_source}",
            f"Dataset artifact: {dataset_artifact}",
            f"Dataset SHA256: {bars_sha256}",
            f"Frozen signal/entry population: {len(population)}",
            f"Entry population source: {frozen_population_info.get('source')}",
            f"Entry population artifact: {frozen_population_info.get('artifact')}",
            f"Entry population SHA256: {frozen_population_info.get('content_sha256')}",
            f"Variants: {len(variants)}",
            f"MT5 point: {mt5_point}",
            f"Volume: {VOLUME}",
            f"Contract size: {contract_size}",
            "",
            "Geometry frozen from sp2l_v3_config.py:",
            f"- pGap={cfg.P_GAP_PRICE}",
            f"- spikeMultiplier={cfg.SPIKE_MULTIPLIER}",
            f"- maxSL={cfg.MAX_SL_DISTANCE}",
            f"- entry={frozen_population_info.get('source')}",
            f"- session={cfg.SESSION_POLICY}",
            "",
            "Trailing uses MT5 point units; TP is recalculated independently for every RR.",
            "SL+TP touched on the same M1 bar => ambiguous and excluded from decisive statistics.",
            "Any missing M1 interval while a trade is open => M1_GAP_WHILE_OPEN, ambiguous and excluded.",
            "",
            "Top 10 by discovery rank (NET USD first):",
        ]
        for i, row in enumerate(top, 1):
            lines.append(
                f"{i}. {row['name']} | USD={row['net_profit_usd']:.4f} | "
                f"R={row['net_R']:.4f} | PF={row['profit_factor']} | "
                f"DD={row['max_drawdown_R']:.4f}R | decisive={row['decisive']} | "
                f"ambiguous={row['ambiguous']} | gap_exposed={row['gap_exposed']}"
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
            "datasetContentSha256": bars_sha256,
            "datasetArtifact": dataset_artifact,
            "top10": top,
        }, indent=2))

    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
