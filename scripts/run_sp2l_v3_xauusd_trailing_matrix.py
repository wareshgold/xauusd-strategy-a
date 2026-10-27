"""Deterministic XAUUSD V3 trailing-management matrix (research only).

Reuses the selected V3 config's signal geometry and compares independent
activation and trail-offset price distances over one shared MT5 M1 dataset.
A newly calculated stop becomes active on the NEXT completed bar; it is never
tested against the same bar that created it (avoids intrabar look-ahead).
No commissions, spread, slippage, or 2X entries are simulated in this first
isolated trailing comparison; these limitations are recorded in the output.
"""
from __future__ import annotations
import argparse, csv, hashlib, importlib, json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "v3"
OUT.mkdir(parents=True, exist_ok=True)


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



def load_m1_csv(path, start, end):
    """Load existing M1 CSV without connecting to or shutting down any MT5 terminal."""
    rows = []
    with Path(path).open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise RuntimeError("CSV has no header")
        names = {name.strip().lower(): name for name in reader.fieldnames}
        required = {"time", "open", "high", "low", "close"}
        missing = required - set(names)
        if missing:
            raise RuntimeError(f"CSV missing required columns: {sorted(missing)}")
        start_ts, end_ts = int(start.timestamp()), int(end.timestamp())
        for line_no, row in enumerate(reader, 2):
            raw_time = (row.get(names["time"]) or "").strip()
            try:
                if raw_time.isdigit():
                    ts = int(raw_time)
                else:
                    parsed = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
                    if parsed.tzinfo is None:
                        raise ValueError("timestamp lacks timezone")
                    ts = int(parsed.astimezone(timezone.utc).timestamp())
                if not start_ts <= ts < end_ts:
                    continue
                vals = [float(row[names[k]]) for k in ("open", "high", "low", "close")]
                if not all(np.isfinite(v) for v in vals):
                    raise ValueError("non-finite OHLC")
                op, hi, lo, cl = vals
                if hi < max(op, cl, lo) or lo > min(op, cl, hi):
                    raise ValueError("invalid OHLC ordering")
                def integer_field(name, default=0):
                    raw = row.get(names.get(name, ""), "")
                    return int(float(raw)) if raw not in (None, "") else default
                rows.append((ts, op, hi, lo, cl, integer_field("tick_volume"),
                             integer_field("spread"), integer_field("real_volume")))
            except Exception as exc:
                raise RuntimeError(f"Invalid CSV row {line_no}: {exc}") from exc
    dtype = [("time", "<i8"), ("open", "<f8"), ("high", "<f8"),
             ("low", "<f8"), ("close", "<f8"), ("tick_volume", "<u8"),
             ("spread", "<i4"), ("real_volume", "<u8")]
    bars = np.array(rows, dtype=dtype)
    if len(bars) == 0:
        raise RuntimeError("CSV contains no bars in requested UTC interval")
    bars.sort(order="time")
    _, idx = np.unique(bars["time"], return_index=True)
    bars = bars[np.sort(idx)]
    return bars

def parse_prices(raw: str, name: str, allow_zero: bool = False) -> list[float]:
    try:
        values = [float(part.strip()) for part in raw.split(",") if part.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{name} must be comma-separated price distances") from exc
    invalid = any((v < 0) if allow_zero else (v <= 0) for v in values)
    if not values or invalid:
        constraint = ">= 0" if allow_zero else "> 0"
        raise argparse.ArgumentTypeError(f"{name} values must all be {constraint}")
    return sorted(set(values))


def collect_candidates(bars, cfg, symbol):
    trades, seen = [], set()
    for i in range(2, len(bars) - 2):
        setup = cfg.detect(bars[i - 2:i + 1], symbol)
        if not setup:
            continue
        candidate = cfg.find_first_entry(bars, i, setup)
        if not candidate:
            continue
        key = (int(candidate["trigger_time"]), candidate["direction"])
        if key in seen:
            continue
        seen.add(key)
        entry_idx = next(
            (k for k in range(i + 1, len(bars))
             if int(bars[k]["time"]) == int(candidate["trigger_time"])),
            None,
        )
        if entry_idx is not None:
            trades.append((candidate, entry_idx))
    return trades


def simulate_one(bars, candidate, entry_idx, activation_price, trail_distance_price):
    """Simulate one candidate; activation_price=None is the fixed-SL/TP baseline."""
    direction = candidate["direction"]
    entry = float(candidate["theoretical_entry"])
    initial_sl = float(candidate["sl"])
    tp = float(candidate["tp"])
    risk = float(candidate["risk"])
    current_sl = initial_sl
    trailing_activated = False
    max_favorable = 0.0
    exit_price = None
    exit_time = None
    reason = "OPEN_OR_UNRESOLVED"
    ambiguous = False

    for k in range(entry_idx + 1, len(bars)):
        bar = bars[k]
        high, low = float(bar["high"]), float(bar["low"])

        # Evaluate levels that were active BEFORE this bar. A new trailing
        # level derived from this bar is not eligible for a same-bar fill.
        if direction == "BUY":
            hit_sl, hit_tp = low <= current_sl, high >= tp
        else:
            hit_sl, hit_tp = high >= current_sl, low <= tp

        if hit_sl and hit_tp:
            ambiguous, reason = True, "SL_AND_TP_SAME_BAR"
            exit_time = int(bar["time"])
            break
        if hit_sl:
            exit_price = current_sl
            exit_time = int(bar["time"])
            reason = "TRAIL_SL" if trailing_activated and current_sl != initial_sl else "SL"
            break
        if hit_tp:
            # TP reach is known, but OHLC cannot establish any further
            # favorable excursion's order within this exit bar. Record only
            # the guaranteed entry-to-TP movement as the MFE floor.
            tp_favorable = tp - entry if direction == "BUY" else entry - tp
            max_favorable = max(max_favorable, max(0.0, tp_favorable))
            exit_price, reason = tp, "TP"
            exit_time = int(bar["time"])
            break

        if direction == "BUY":
            favorable = high - entry
            max_favorable = max(max_favorable, favorable)
            if activation_price is not None and favorable >= activation_price:
                candidate_sl = high - trail_distance_price
                if candidate_sl > current_sl and candidate_sl < high:
                    current_sl = candidate_sl
                    trailing_activated = True
        else:
            favorable = entry - low
            max_favorable = max(max_favorable, favorable)
            if activation_price is not None and favorable >= activation_price:
                candidate_sl = low + trail_distance_price
                if candidate_sl < current_sl and candidate_sl > low:
                    current_sl = candidate_sl
                    trailing_activated = True

    realized = None
    realized_r = None
    if exit_price is not None:
        realized = exit_price - entry if direction == "BUY" else entry - exit_price
        realized_r = realized / risk if risk > 0 else None

    return {
        "direction": direction,
        "trigger_time": int(candidate["trigger_time"]),
        "entry_time": int(candidate["trigger_time"]),
        "exit_time": exit_time,
        "entry": entry,
        "initial_sl": initial_sl,
        "initial_tp": tp,
        "risk_price": risk,
        "activation_price": activation_price,
        "trail_distance_price": trail_distance_price,
        "final_sl": current_sl,
        "trailing_activated": trailing_activated,
        "max_favorable_price": max_favorable,
        "exit_price": exit_price,
        "reason": reason,
        "ambiguous": ambiguous,
        "realized_price": realized,
        "realized_R": realized_r,
    }


def summarize(rows, dataset_end_time=None):
    decisive = [r for r in rows if not r["ambiguous"] and r["realized_R"] is not None]
    # Trade-level equity diagnostics must be ordered by actual exit time, not
    # candidate discovery order or signal/trigger time.
    exit_order = sorted(
        decisive,
        key=lambda r: (int(r["exit_time"]), int(r["trigger_time"]))
        if r.get("exit_time") is not None
        else (2**63 - 1, int(r["trigger_time"])),
    )
    wins = [r for r in exit_order if r["realized_R"] > 0]
    losses = [r for r in exit_order if r["realized_R"] < 0]
    net_r = sum(r["realized_R"] for r in exit_order)
    gross_win = sum(r["realized_R"] for r in wins)
    gross_loss = abs(sum(r["realized_R"] for r in losses))
    equity = peak = max_dd = 0.0
    for r in exit_order:
        equity += r["realized_R"]
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)

    # Independent trades can overlap. This is a concurrency diagnostic only,
    # not a portfolio equity curve or a claim that all trades could be funded.
    end_time = int(dataset_end_time) if dataset_end_time is not None else None
    events = []
    for row in rows:
        start_time = row.get("entry_time", row.get("trigger_time"))
        finish_time = row.get("exit_time")
        if finish_time is None:
            finish_time = end_time
        if start_time is None or finish_time is None or int(finish_time) < int(start_time):
            continue
        # For equal timestamps, process exits before new entries.
        events.append((int(start_time), 1))
        events.append((int(finish_time), -1))
    events.sort(key=lambda event: (event[0], event[1]))
    active = max_active = 0
    for _, delta in events:
        active += delta
        max_active = max(max_active, active)

    return {
        "signals": len(rows),
        "decisive": len(exit_order),
        "wins": len(wins),
        "losses": len(losses),
        "ambiguous": sum(bool(r["ambiguous"]) for r in rows),
        "open_or_unresolved": sum(r["realized_R"] is None and not r["ambiguous"] for r in rows),
        "win_rate_decisive_pct": 100 * len(wins) / len(exit_order) if exit_order else None,
        "net_R": net_r,
        "profit_factor": gross_win / gross_loss if gross_loss else None,
        "max_drawdown_R": max_dd,
        "drawdown_basis": "decisive trade R ordered by exit_time; independent trades, no portfolio sizing",
        "max_consecutive_losses": max_consecutive_losses(exit_order),
        "max_concurrent_independent_trades": max_active,
        "trail_activated_count": sum(bool(r["trailing_activated"]) for r in rows),
    }


def max_consecutive_losses(rows):
    longest = current = 0
    for row in rows:
        if row["realized_R"] < 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mt5-path", default=None)\n    ap.add_argument("--csv-path", default=None, help="Use an existing M1 CSV offline; MT5 is not initialized or shut down")
    ap.add_argument("--symbol", default="XAUUSD.ecn")
    ap.add_argument("--start", default="2026-07-13T00:00:00+00:00")
    ap.add_argument("--end", default="2026-10-13T00:00:00+00:00")
    ap.add_argument("--config-module", default="sp2l_v3_rr2_trail4_config")
    ap.add_argument("--activation-prices", default="0.00,0.05,0.10,0.20,0.40",
                    help="independent favorable-move thresholds in XAUUSD price units; 0.00 starts at the first eligible completed-bar check")
    ap.add_argument("--trail-distances", default="0.02,0.04,0.10,0.20,0.40",
                    help="independent trailing offsets in XAUUSD price units")
    args = ap.parse_args()
    activations = parse_prices(args.activation_prices, "activation-prices", allow_zero=True)
    distances = parse_prices(args.trail_distances, "trail-distances")
    start, end = datetime.fromisoformat(args.start), datetime.fromisoformat(args.end)
    if start.tzinfo is None or end.tzinfo is None or start >= end:
        raise RuntimeError("--start and --end must be timezone-aware and start < end")

    cfg = importlib.import_module(args.config_module)
    if not args.csv_path and not args.mt5_path:
        raise RuntimeError("Provide --csv-path for offline mode or --mt5-path for MT5 acquisition")
    mt5_initialized = False
    try:
        if args.csv_path:
            bars = load_m1_csv(args.csv_path, start, end)
        else:
            if not mt5.initialize(path=args.mt5_path):
                raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
            mt5_initialized = True
            bars = fetch_m1_rates(args.symbol, start, end)
        if len(bars) < 10:
            raise RuntimeError(f"Insufficient M1 data: {len(bars)} bars")
        bars_sha = hashlib.sha256(bars.tobytes()).hexdigest()
        candidates = collect_candidates(bars, cfg, args.symbol)
        matrix = []
        trade_rows = []

        # Same candidates, entries, initial SL and TP; the baseline disables all stop updates.
        baseline_rows = [simulate_one(bars, c, idx, None, None) for c, idx in candidates]
        matrix.append({
            "scenario": "NO_TRAIL_FIXED_SL_TP",
            "activation_price": None,
            "trail_distance_price": None,
            **summarize(baseline_rows, dataset_end_time=int(bars[-1]["time"])),
        })
        for row in baseline_rows:
            trade_rows.append({
                "scenario": "NO_TRAIL_FIXED_SL_TP",
                "activation_price": None,
                "trail_distance_price": None,
                **row,
            })

        for activation in activations:
            for distance in distances:
                rows = [
                    simulate_one(bars, c, idx, activation, distance)
                    for c, idx in candidates
                ]
                summary = summarize(rows, dataset_end_time=int(bars[-1]["time"]))
                matrix.append({
                    "scenario": "TRAILING",
                    "activation_price": activation,
                    "trail_distance_price": distance,
                    **summary,
                })
                for row in rows:
                    trade_rows.append({
                        "scenario": "TRAILING",
                        "activation_price": activation,
                        "trail_distance_price": distance,
                        **row,
                    })

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = OUT / f"SP2L_V3_TRAILING_MATRIX_{stamp}"
        payload = {
            "status": "COMPLETE",
            "research_only": True,
            "symbol": args.symbol,
            "timeframe": "M1",
            "window_utc": {"start": start.isoformat(), "end": end.isoformat()},
            "bars": len(bars),
            "bars_sha256": bars_sha,
            "config_module": args.config_module,
            "geometry": {
                "version": cfg.VERSION,
                "p_gap_price": cfg.P_GAP_PRICE,
                "spike_multiplier": cfg.SPIKE_MULTIPLIER,
                "max_sl_distance": cfg.MAX_SL_DISTANCE,
                "tp_R": cfg.TP_R,
                "session_policy": cfg.SESSION_POLICY,
            },
            "simulation": {
                "activation_prices": activations,
                "trail_distance_prices": distances,
                "baseline": "same candidates and initial SL/TP, trailing disabled",
                "scenario_count": 1 + len(activations) * len(distances),
                "trailing_policy": "completed M1 bar; updated SL applies starting next bar",
                "tp_policy": "fixed initial TP",
                "same_bar_policy": "SL and TP both touched under pre-bar levels => ambiguous",
                "costs": "spread, commission, swap, and slippage not included",
                "entries": "one primary entry only; 2X secondary entries excluded to isolate trailing parameters",
                "gap_fills": "assumes fill at modeled SL/TP level; broker gap/slippage behavior not modeled",
                "drawdown": "decisive trade R ordered by exit time; independent trades and no portfolio sizing, so not account/portfolio drawdown",
                "overlap": "maximum concurrent independent simulated trades reported; no capital, margin, or execution-capacity constraint",
            },
            "matrix": matrix,
        }
        raw = json.dumps(payload, indent=2, ensure_ascii=False)
        json_path = base.with_suffix(".json")
        json_path.write_text(raw, encoding="utf-8")
        csv_path = base.with_name(base.name + "_matrix.csv")
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(matrix[0].keys()))
            writer.writeheader()
            writer.writerows(matrix)
        trades_path = base.with_name(base.name + "_trades.csv")
        with trades_path.open("w", newline="", encoding="utf-8") as f:
            trade_fields = (list(trade_rows[0].keys()) if trade_rows else [
                "activation_price", "trail_distance_price", "direction", "trigger_time",
                "entry_time", "exit_time", "entry", "initial_sl", "initial_tp", "risk_price", "final_sl",
                "trailing_activated", "max_favorable_price", "exit_price", "reason",
                "ambiguous", "realized_price", "realized_R",
            ])
            writer = csv.DictWriter(f, fieldnames=trade_fields)
            writer.writeheader()
            writer.writerows(trade_rows)
        snapshot_path = base.with_name(base.name + "_SNAPSHOT.md")
        snapshot_path.write_text(
            "# SP2L V3 Trailing Matrix Snapshot\n"
            f"Version: {cfg.VERSION}\nSymbol: {args.symbol}\n"
            f"Window UTC: {start.isoformat()} → {end.isoformat()}\n"
            f"Bars: {len(bars)}\nBars SHA256: {bars_sha}\n"
            f"Config module: {args.config_module}\n"
            "No-trailing baseline included: same entries and initial SL/TP; trailing disabled.\n"
            f"Activation price grid: {activations}\nTrail-distance price grid: {distances}\n"
            "Trailing update applies starting on the next completed M1 bar; no same-bar look-ahead.\n"
            "Trade-level drawdown and consecutive losses are sorted by exit time.\n"
            "Maximum concurrent independent simulated trades is reported; this is not portfolio drawdown.\n"
            "Fixed initial TP; same-bar SL+TP ambiguity excluded from decisive metrics.\n"
            "Costs and 2X entries excluded; results are gross research diagnostics, not production evidence.\n"
            f"JSON: {json_path.name}\nMatrix CSV: {csv_path.name}\nTrade CSV: {trades_path.name}\n",
            encoding="utf-8",
        )
        print(json.dumps({
            "status": "COMPLETE",
            "json": str(json_path),
            "matrix_csv": str(csv_path),
            "trades_csv": str(trades_path),
            "snapshot": str(snapshot_path),
            "bars": len(bars),
            "candidates": len(candidates),
            "matrix_rows": len(matrix),
            "bars_sha256": bars_sha,
            "research_only": True,
        }, indent=2))
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
