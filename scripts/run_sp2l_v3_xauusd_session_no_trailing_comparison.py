"""Research-only comparison: current RR2/TRAIL4 vs London-to-NY vs no trailing.

Uses the same V3 config, candidate detector, MT5 M1 bars, and next-completed-bar
trailing model as run_sp2l_v3_xauusd_trailing_matrix.py. It does not modify the
forward runner, submit orders, or define canonical Strategy A rules.

Scenarios:
A: all market hours, current configured trailing distance/activation, fixed TP_R.
B: entries only from 08:00 Europe/London through 17:00 America/New_York,
   same trailing and fixed TP_R. Positions may exit after the entry window closes.
C: all market hours, initial SL and fixed TP only, no trailing updates.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import MetaTrader5 as mt5

import run_sp2l_v3_xauusd_trailing_matrix as engine

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "v3"
OUT.mkdir(parents=True, exist_ok=True)

LONDON = ZoneInfo("Europe/London")
NEW_YORK = ZoneInfo("America/New_York")
UTC = timezone.utc


def parse_aware(value: str, name: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{name} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError(f"{name} must include a UTC offset")
    return parsed.astimezone(UTC)


def in_london_to_new_york_entry_window(epoch: int) -> bool:
    """True from 08:00 London local time to 17:00 New York local time.

    Both boundaries are computed with IANA time zones for the London-local
    calendar date, so UK/US daylight-saving transitions are not hard-coded.
    Entry must be >= London open and < New York 17:00. Exit time is unrestricted.
    """
    instant = datetime.fromtimestamp(int(epoch), UTC)
    london_date = instant.astimezone(LONDON).date()
    start_local = datetime.combine(london_date, time(8, 0), tzinfo=LONDON)
    end_local = datetime.combine(london_date, time(17, 0), tzinfo=NEW_YORK)
    return start_local.astimezone(UTC) <= instant < end_local.astimezone(UTC)


def simulate_without_trailing(bars, candidate: dict, entry_idx: int) -> dict:
    direction = candidate["direction"]
    entry = float(candidate["theoretical_entry"])
    initial_sl = float(candidate["sl"])
    tp = float(candidate["tp"])
    risk = float(candidate["risk"])
    exit_price = None
    exit_time = None
    reason = "OPEN_OR_UNRESOLVED"
    ambiguous = False

    for k in range(entry_idx + 1, len(bars)):
        bar = bars[k]
        high, low = float(bar["high"]), float(bar["low"])
        if direction == "BUY":
            hit_sl, hit_tp = low <= initial_sl, high >= tp
        else:
            hit_sl, hit_tp = high >= initial_sl, low <= tp

        if hit_sl and hit_tp:
            ambiguous = True
            reason = "SL_AND_TP_SAME_BAR"
            exit_time = int(bar["time"])
            break
        if hit_sl:
            exit_price = initial_sl
            reason = "SL"
            exit_time = int(bar["time"])
            break
        if hit_tp:
            exit_price = tp
            reason = "TP"
            exit_time = int(bar["time"])
            break

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
        "activation_price": None,
        "trail_distance_price": 0.0,
        "final_sl": initial_sl,
        "trailing_activated": False,
        "max_favorable_price": None,
        "exit_price": exit_price,
        "reason": reason,
        "ambiguous": ambiguous,
        "realized_price": realized,
        "realized_R": realized_r,
    }


def add_scenario(scenario: str, bars, candidate_pairs, activation: float, distance: float,
                 dataset_end_time: int) -> tuple[dict, list[dict]]:
    trades = []
    for candidate, entry_idx in candidate_pairs:
        if scenario == "B_LONDON_TO_NY_RR2_TRAIL4" and not in_london_to_new_york_entry_window(
            int(candidate["trigger_time"])
        ):
            continue
        if scenario == "C_ALL_HOURS_NO_TRAILING":
            result = simulate_without_trailing(bars, candidate, entry_idx)
        else:
            result = engine.simulate_one(
                bars, candidate, entry_idx, activation_price=activation,
                trail_distance_price=distance
            )
        trades.append({"scenario": scenario, **result})

    summary = engine.summarize(trades, dataset_end_time=dataset_end_time)
    summary["scenario"] = scenario
    summary["activation_price"] = None if scenario == "C_ALL_HOURS_NO_TRAILING" else activation
    summary["trail_distance_price"] = 0.0 if scenario == "C_ALL_HOURS_NO_TRAILING" else distance
    summary["session_entry_filter"] = scenario == "B_LONDON_TO_NY_RR2_TRAIL4"
    return summary, trades


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mt5-path", required=True)
    parser.add_argument("--symbol", default="XAUUSD.ecn")
    parser.add_argument("--start", default="2026-07-13T00:00:00+00:00")
    parser.add_argument("--end", default="2026-10-15T00:00:00+00:00")
    parser.add_argument("--config-module", default="sp2l_v3_rr2_trail4_config")
    args = parser.parse_args()

    start = parse_aware(args.start, "--start")
    end = parse_aware(args.end, "--end")
    if start >= end:
        parser.error("--start must be earlier than --end")

    cfg = importlib.import_module(args.config_module)
    current_distance = float(cfg.TRAIL_DISTANCE_PRICE)
    # The live V3 runner activates when the completed bar's favorable extreme
    # reaches cfg.TRAIL_DISTANCE_PRICE and trails that same extreme by the same
    # configured price distance. Keep both values tied to config; do not guess
    # pip conversion or substitute a name like TRAIL4 for a price amount.
    activation = current_distance
    distance = current_distance

    if not mt5.initialize(path=args.mt5_path):
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        bars = engine.fetch_m1_rates(args.symbol, start, end)
        if len(bars) < 10:
            raise RuntimeError(f"Insufficient M1 data: {mt5.last_error()}")
        bars_sha = hashlib.sha256(bars.tobytes()).hexdigest()
        candidates = engine.collect_candidates(bars, cfg, args.symbol)
        dataset_end = int(bars[-1]["time"])

        scenarios = [
            "A_ALL_HOURS_CURRENT_RR2_TRAIL4",
            "B_LONDON_TO_NY_RR2_TRAIL4",
            "C_ALL_HOURS_NO_TRAILING",
        ]
        summaries, all_trades = [], []
        for scenario in scenarios:
            summary, trades = add_scenario(
                scenario, bars, candidates, activation, distance, dataset_end
            )
            summaries.append(summary)
            all_trades.extend(trades)

        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        base = OUT / f"SP2L_V3_SESSION_NO_TRAIL_COMPARISON_{stamp}"
        payload = {
            "status": "COMPLETE",
            "research_only": True,
            "symbol": args.symbol,
            "timeframe": "M1",
            "window_utc": {"start": start.isoformat(), "end": end.isoformat()},
            "bars": len(bars),
            "bars_sha256": bars_sha,
            "candidate_count_before_session_filter": len(candidates),
            "config_module": args.config_module,
            "geometry": {
                "version": cfg.VERSION,
                "p_gap_price": cfg.P_GAP_PRICE,
                "spike_multiplier": cfg.SPIKE_MULTIPLIER,
                "max_sl_distance": cfg.MAX_SL_DISTANCE,
                "tp_R": cfg.TP_R,
                "configured_trail_pips": getattr(cfg, "TRAIL_PIPS", None),
                "configured_trail_distance_price": current_distance,
                "session_policy_in_config": cfg.SESSION_POLICY,
            },
            "scenario_definitions": {
                "A_ALL_HOURS_CURRENT_RR2_TRAIL4": (
                    "All entries; current configured trailing activation and distance; fixed initial TP."
                ),
                "B_LONDON_TO_NY_RR2_TRAIL4": (
                    "Entries only from 08:00 Europe/London inclusive to 17:00 America/New_York "
                    "exclusive; same trailing and TP; positions may exit after 17:00 New York."
                ),
                "C_ALL_HOURS_NO_TRAILING": (
                    "All entries; initial SL and fixed TP only; no trailing stop."
                ),
            },
            "simulation_limitations": {
                "trailing_timing": "completed M1 bar; changed SL becomes eligible from next bar",
                "same_bar_policy": "SL and TP both touched under active levels => ambiguous, excluded from decisive metrics",
                "costs": "spread, commission, swap, and slippage excluded",
                "entries": "one theoretical primary entry only; 2X entries excluded",
                "gap_fills": "fills assumed at modeled SL/TP levels; broker gap/slippage not modeled",
                "portfolio": "independent candidate simulations; no capital, margin, or execution-capacity constraints",
                "entry_fill": "theoretical entry model from config; this is not broker-realistic pending-order replay",
            },
            "scenarios": summaries,
        }

        json_path = base.with_suffix(".json")
        json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        matrix_path = base.with_name(base.name + "_matrix.csv")
        with matrix_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(summaries[0].keys()))
            writer.writeheader()
            writer.writerows(summaries)
        trades_path = base.with_name(base.name + "_trades.csv")
        trade_fields = list(all_trades[0].keys()) if all_trades else [
            "scenario", "direction", "trigger_time", "entry_time", "exit_time",
            "entry", "initial_sl", "initial_tp", "risk_price", "exit_price",
            "reason", "ambiguous", "realized_price", "realized_R"
        ]
        with trades_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=trade_fields)
            writer.writeheader()
            writer.writerows(all_trades)
        snapshot_path = base.with_name(base.name + "_SNAPSHOT.md")
        snapshot_path.write_text(
            "# SP2L V3 Session vs No-Trailing Comparison\n"
            f"Version: {cfg.VERSION}\nSymbol: {args.symbol}\n"
            f"Window UTC: {start.isoformat()} → {end.isoformat()}\n"
            f"Bars: {len(bars)}\nBars SHA256: {bars_sha}\n"
            f"Candidates before session filter: {len(candidates)}\n"
            f"Configured trail distance and activation price: {current_distance}\n"
            "Session entry window: 08:00 Europe/London inclusive to 17:00 America/New_York exclusive.\n"
            "Session filter affects entry time only; positions may exit after the window closes.\n"
            "A=current all-hours RR2/TRAIL4; B=session-filtered RR2/TRAIL4; C=all-hours TP/initial-SL only.\n"
            "Research only. Gross results exclude trading costs, 2X entries, broker-realistic fills and portfolio sizing.\n"
            f"JSON: {json_path.name}\nMatrix CSV: {matrix_path.name}\nTrade CSV: {trades_path.name}\n",
            encoding="utf-8",
        )
        print(json.dumps({
            "status": "COMPLETE",
            "research_only": True,
            "json": str(json_path),
            "matrix_csv": str(matrix_path),
            "trades_csv": str(trades_path),
            "snapshot": str(snapshot_path),
            "bars": len(bars),
            "candidates": len(candidates),
            "scenario_rows": len(summaries),
            "configured_trail_distance_price": current_distance,
            "bars_sha256": bars_sha,
        }, indent=2))
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
