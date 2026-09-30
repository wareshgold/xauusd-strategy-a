"""Research-only XAUUSD V2 exit-management matrix.

Frozen signal/entry/initial-SL layer:
- Reuses sp2l_strategy_a_v2_detector.py and its existing MT5 M1 population.
- Does NOT alter Strategy A geometry.
- Volume defaults to 0.01 lot.
- Reports both R and USD P&L.

Exit experiments:
1) Fixed TP RR=1R
2) Fixed TP RR=2R
3) No TP + trailing distance 10/20/30/50 pips

Session experiments:
- ALL_MARKET_HOURS: every detected entry in the requested window.
- LONDON_TO_NEW_YORK: entry allowed only from 08:00 Europe/London
  through 17:00 America/New_York, DST-aware. Open positions are NOT
  force-closed at session end; the session filter applies only to entry.

Trailing semantics are explicitly NON_CANONICAL_FORENSIC:
- trailing activates after a favorable M1 extreme reaches the configured
  distance from entry;
- the new SL becomes active from the NEXT M1 candle;
- for no-TP variants, exit occurs only at initial/trailing SL or when data ends;
- no intrabar order is inferred from M1 OHLC;
- no trailing rule is promoted to canonical Strategy A.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
from datetime import datetime, time as dtime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import MetaTrader5 as mt5
import numpy as np

from mt5_terminal_resolver import find_mt5_terminal
from sp2l_strategy_a_v2_detector import detect_setup, find_first_entry

PIP_SIZE = 0.10
TRAILS_PIPS = [10.0, 20.0, 30.0, 50.0]
LONDON_TZ = ZoneInfo("Europe/London")
NEW_YORK_TZ = ZoneInfo("America/New_York")


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def resolve_xauusd() -> str:
    symbols = list(mt5.symbols_get() or [])
    names = {str(s.name): s for s in symbols}
    for name in ("XAUUSD", "XAUUSD.ecn", "XAUUSDm", "XAUUSD_ecn"):
        if name in names:
            return name
    for s in symbols:
        if str(s.name).upper().startswith("XAUUSD"):
            return str(s.name)
    raise RuntimeError("No XAUUSD broker symbol found")


def fetch_rates(symbol: str, start: datetime, end: datetime) -> np.ndarray:
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"symbol_select failed: {symbol}: {mt5.last_error()}")
    chunk_days = float(os.getenv("SP2L_MT5_HISTORY_CHUNK_DAYS", "7"))
    retries = int(os.getenv("SP2L_MT5_HISTORY_RETRIES", "3"))
    cursor = start
    chunks = []
    while cursor < end:
        chunk_end = min(cursor + timedelta(days=chunk_days), end)
        rates = None
        err = None
        for attempt in range(1, retries + 1):
            rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, cursor, chunk_end)
            if rates is not None and len(rates):
                break
            err = mt5.last_error()
            time.sleep(0.25 * attempt)
        if rates is None or len(rates) == 0:
            raise RuntimeError(
                f"MT5 history failed {cursor.isoformat()}..{chunk_end.isoformat()}: "
                f"{err or mt5.last_error()}"
            )
        chunks.append(rates.copy())
        cursor = chunk_end + timedelta(minutes=1)
    result = np.concatenate(chunks)
    result.sort(order="time")
    _, idx = np.unique(result["time"], return_index=True)
    return result[np.sort(idx)]


def build_population(rates: np.ndarray) -> list[dict]:
    signals = []
    for i in range(2, len(rates)):
        setup = detect_setup(rates[: i + 1])
        if setup is None:
            continue
        signal = find_first_entry(rates, i, setup)
        if signal is None:
            continue
        signals.append({
            "signal_index": len(signals),
            "direction": signal["direction"],
            "setup_time": int(signal["setup_time"]),
            "entry_index": int(signal["entry_index"]),
            "entry_time": int(signal["entry_time"]),
            "entry": float(signal["entry"]),
            "sl": float(signal["sl"]),
            "risk": float(signal["risk"]),
        })
    return signals


def local_clock(ts_epoch: int, tz: ZoneInfo) -> tuple:
    dt = datetime.fromtimestamp(int(ts_epoch), tz=timezone.utc).astimezone(tz)
    return dt.date(), dt.time()


def in_london_to_new_york_session(ts_epoch: int) -> bool:
    # Entry-only session gate. DST is resolved by the IANA time zones.
    london_dt = datetime.fromtimestamp(ts_epoch, tz=timezone.utc).astimezone(LONDON_TZ)
    ny_dt = datetime.fromtimestamp(ts_epoch, tz=timezone.utc).astimezone(NEW_YORK_TZ)
    start_ok = london_dt.time() >= dtime(8, 0)
    end_ok = ny_dt.time() <= dtime(17, 0)
    return start_ok and end_ok


def filter_population(population: list[dict], session: str) -> list[dict]:
    if session == "ALL_MARKET_HOURS":
        return population
    if session == "LONDON_TO_NEW_YORK":
        return [s for s in population if in_london_to_new_york_session(s["entry_time"])]
    raise ValueError(f"unknown session: {session}")


def simulate(
    rates: np.ndarray,
    signal: dict,
    *,
    exit_mode: str,
    rr: float | None = None,
    trail_pips: float | None = None,
) -> dict:
    direction = signal["direction"]
    entry = float(signal["entry"])
    initial_sl = float(signal["sl"])
    risk = abs(entry - initial_sl)
    if risk <= 0:
        return {"result": "INVALID", "r": None, "exit_index": None, "reason": "INVALID_RISK"}

    tp = None
    if exit_mode == "FIXED_TP":
        if rr is None or rr <= 0:
            raise ValueError("FIXED_TP requires rr > 0")
        tp = entry + rr * risk if direction == "BUY" else entry - rr * risk
    elif exit_mode == "NO_TP_TRAILING":
        if trail_pips is None or trail_pips <= 0:
            raise ValueError("NO_TP_TRAILING requires trail_pips > 0")
    else:
        raise ValueError(f"unknown exit_mode: {exit_mode}")

    trail = float(trail_pips or 0.0) * PIP_SIZE
    current_sl = initial_sl
    best = entry
    trailing_active = False

    for i in range(int(signal["entry_index"]), len(rates)):
        bar = rates[i]
        high = float(bar["high"])
        low = float(bar["low"])

        if direction == "BUY":
            sl_hit = low <= current_sl
            tp_hit = tp is not None and high >= tp

            if sl_hit and tp_hit:
                return {
                    "result": "AMBIGUOUS",
                    "r": None,
                    "exit_index": i,
                    "reason": "SL_AND_TP_SAME_BAR",
                    "trailing_activated": trailing_active,
                }
            if sl_hit:
                realized = (current_sl - entry) / risk
                return {
                    "result": "WIN" if realized > 0 else ("LOSS" if realized < 0 else "BREAKEVEN"),
                    "r": realized,
                    "exit_index": i,
                    "reason": "TRAIL_SL" if trailing_active and current_sl != initial_sl else "SL",
                    "trailing_activated": trailing_active,
                }
            if tp_hit:
                return {
                    "result": "WIN",
                    "r": float(rr),
                    "exit_index": i,
                    "reason": "TP",
                    "trailing_activated": trailing_active,
                }

            if exit_mode == "NO_TP_TRAILING":
                old_sl = current_sl
                best = max(best, high)
                if not trailing_active and best >= entry + trail:
                    trailing_active = True
                if trailing_active:
                    current_sl = max(current_sl, best - trail)
                # current_sl is intentionally active only on the next bar.
                _ = old_sl

        else:
            sl_hit = high >= current_sl
            tp_hit = tp is not None and low <= tp

            if sl_hit and tp_hit:
                return {
                    "result": "AMBIGUOUS",
                    "r": None,
                    "exit_index": i,
                    "reason": "SL_AND_TP_SAME_BAR",
                    "trailing_activated": trailing_active,
                }
            if sl_hit:
                realized = (entry - current_sl) / risk
                return {
                    "result": "WIN" if realized > 0 else ("LOSS" if realized < 0 else "BREAKEVEN"),
                    "r": realized,
                    "exit_index": i,
                    "reason": "TRAIL_SL" if trailing_active and current_sl != initial_sl else "SL",
                    "trailing_activated": trailing_active,
                }
            if tp_hit:
                return {
                    "result": "WIN",
                    "r": float(rr),
                    "exit_index": i,
                    "reason": "TP",
                    "trailing_activated": trailing_active,
                }

            if exit_mode == "NO_TP_TRAILING":
                best = min(best, low)
                if not trailing_active and best <= entry - trail:
                    trailing_active = True
                if trailing_active:
                    current_sl = min(current_sl, best + trail)

    return {
        "result": "OPEN_OR_UNRESOLVED",
        "r": None,
        "exit_index": None,
        "reason": "DATA_END",
        "trailing_activated": trailing_active,
    }


def summarize(rows: list[dict], contract_size: float, volume: float) -> dict:
    decisive = [r for r in rows if r["result"] in {"WIN", "LOSS", "BREAKEVEN"}]
    wins = [r for r in decisive if r["result"] == "WIN"]
    losses = [r for r in decisive if r["result"] == "LOSS"]
    rs = [float(r["r"]) for r in decisive if r["r"] is not None]

    equity = peak = dd = 0.0
    loss_streak = max_loss_streak = 0
    for x in rs:
        equity += x
        peak = max(peak, equity)
        dd = max(dd, peak - equity)
        if x < 0:
            loss_streak += 1
            max_loss_streak = max(max_loss_streak, loss_streak)
        else:
            loss_streak = 0

    gross_profit_r = sum(x for x in rs if x > 0)
    gross_loss_r = -sum(x for x in rs if x < 0)
    net_r = sum(rs)

    for r in rows:
        if r["r"] is not None:
            r["risk_usd"] = r["risk"] * contract_size * volume
            r["pnl_usd"] = r["r"] * r["risk_usd"]
        else:
            r["risk_usd"] = r["risk"] * contract_size * volume
            r["pnl_usd"] = None

    realized_usd = [float(r["pnl_usd"]) for r in rows if r["pnl_usd"] is not None]
    return {
        "signals": len(rows),
        "decisive": len(decisive),
        "wins": len(wins),
        "losses": len(losses),
        "breakeven": sum(r["result"] == "BREAKEVEN" for r in rows),
        "ambiguous": sum(r["result"] == "AMBIGUOUS" for r in rows),
        "open_or_unresolved": sum(r["result"] == "OPEN_OR_UNRESOLVED" for r in rows),
        "win_rate_decisive_pct": 100.0 * len(wins) / len(decisive) if decisive else None,
        "net_R": net_r,
        "profit_factor": gross_profit_r / gross_loss_r if gross_loss_r else None,
        "max_drawdown_R": dd,
        "max_losing_streak": max_loss_streak,
        "net_usd": sum(realized_usd),
        "gross_profit_usd": sum(x for x in realized_usd if x > 0),
        "gross_loss_usd": -sum(x for x in realized_usd if x < 0),
        "trailing_activated_count": sum(bool(r["trailing_activated"]) for r in rows),
    }


def variant_name(exit_mode: str, rr: float | None, trail_pips: float | None) -> str:
    if exit_mode == "FIXED_TP":
        return f"RR_{rr:g}_NO_TRAIL"
    return f"NO_TP_TRAIL_{trail_pips:g}P"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-08-26T00:00:00Z")
    ap.add_argument("--end", default="2026-09-25T00:00:00Z")
    ap.add_argument("--rr", nargs="+", type=float, default=[1.0, 2.0])
    ap.add_argument("--trail-pips", nargs="+", type=float, default=TRAILS_PIPS)
    ap.add_argument("--volume", type=float, default=0.01)
    ap.add_argument("--mt5-path", default=None)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    if args.volume != 0.01:
        raise SystemExit("This experiment is frozen at 0.01 lot. Use --volume 0.01.")

    start = parse_ts(args.start)
    end = parse_ts(args.end)

    initialized = mt5.initialize(path=str(args.mt5_path)) if args.mt5_path else mt5.initialize()
    if not initialized:
        terminal = None if args.mt5_path else find_mt5_terminal()
        if terminal is None or not mt5.initialize(path=str(terminal)):
            print(json.dumps({"status": "MT5_INIT_FAILED", "error": mt5.last_error()}, indent=2))
            return 2

    try:
        symbol = resolve_xauusd()
        info = mt5.symbol_info(symbol)
        if info is None:
            raise RuntimeError(f"symbol_info failed: {symbol}: {mt5.last_error()}")

        contract_size = float(info.trade_contract_size)
        rates = fetch_rates(symbol, start, end)
        population = build_population(rates)

        variants = []
        for session in ("ALL_MARKET_HOURS", "LONDON_TO_NEW_YORK"):
            session_population = filter_population(population, session)

            configs = [
                ("FIXED_TP", rr, None) for rr in args.rr
            ] + [
                ("NO_TP_TRAILING", None, trail) for trail in args.trail_pips
            ]

            for exit_mode, rr, trail_pips in configs:
                rows = []
                for signal in session_population:
                    outcome = simulate(
                        rates,
                        signal,
                        exit_mode=exit_mode,
                        rr=rr,
                        trail_pips=trail_pips,
                    )
                    row = {
                        **signal,
                        "session": session,
                        "variant": variant_name(exit_mode, rr, trail_pips),
                        "exit_mode": exit_mode,
                        "rr": rr,
                        "trail_pips": trail_pips,
                        **outcome,
                    }
                    if outcome["exit_index"] is not None:
                        row["exit_time"] = int(rates[outcome["exit_index"]]["time"])
                    else:
                        row["exit_time"] = None
                    rows.append(row)

                variants.append({
                    "session": session,
                    "variant": variant_name(exit_mode, rr, trail_pips),
                    "exit_mode": exit_mode,
                    "rr": rr,
                    "trail_pips": trail_pips,
                    "population_signals": len(session_population),
                    "summary": summarize(rows, contract_size, args.volume),
                    "trades": rows,
                })

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = Path(args.output) if args.output else Path("artifacts/backtest-mt5-local") / (
            f"SP2L_V2_XAUUSD_EXITS_20260826_20260925_{stamp}.json"
        )
        out.parent.mkdir(parents=True, exist_ok=True)

        result = {
            "status": "COMPLETE",
            "mode": "NON_CANONICAL_FORENSIC_EXIT_RESEARCH",
            "experiment": "V2_XAUUSD_EXACT_WINDOW_RR_AND_NO_TP_TRAILING",
            "source_contract": {
                "detector": "sp2l_strategy_a_v2_detector.py",
                "signal_geometry_unchanged": True,
                "initial_sl_unchanged": True,
                "p_gap_price": 1.0,
                "spike_multiplier": 1.5,
                "max_sl_distance": 10.0,
            },
            "period": {
                "start_utc": start.isoformat(),
                "end_utc": end.isoformat(),
                "end_inclusive": False,
            },
            "resolved_symbol": symbol,
            "accounting": {
                "volume_lots": args.volume,
                "contract_size": contract_size,
                "usd_pnl_formula": "R * initial_risk_price * contract_size * volume",
                "spread_commission_swap_included": False,
            },
            "session_contract": {
                "ALL_MARKET_HOURS": "entry allowed for every detected signal in the requested window",
                "LONDON_TO_NEW_YORK": (
                    "entry only when timestamp is >= 08:00 Europe/London and <= 17:00 "
                    "America/New_York; IANA DST-aware"
                ),
                "open_position_policy": "positions are not force-closed at session end",
            },
            "exit_contract": {
                "fixed_tp": "TP = entry +/- RR * initial risk",
                "no_tp_trailing": (
                    "no TP; favorable M1 extreme activates trailing at configured distance; "
                    "new SL becomes active from next candle"
                ),
                "same_bar_sl_tp": "AMBIGUOUS",
                "m1_intrabar_order": "NOT_INFERRED",
                "canonical": False,
            },
            "bars": int(len(rates)),
            "population_signals_all_hours": len(population),
            "variants": variants,
        }

        out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

        summary_csv = out.with_suffix(".csv")
        fields = [
            "session", "variant", "population_signals", "signals", "decisive",
            "wins", "losses", "breakeven", "ambiguous", "open_or_unresolved",
            "win_rate_decisive_pct", "net_R", "net_usd", "profit_factor",
            "max_drawdown_R", "max_losing_streak", "trailing_activated_count",
        ]
        with summary_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for v in variants:
                writer.writerow({
                    "session": v["session"],
                    "variant": v["variant"],
                    "population_signals": v["population_signals"],
                    **{k: v["summary"].get(k) for k in fields if k in v["summary"]},
                })

        print(json.dumps({
            "status": "COMPLETE",
            "symbol": symbol,
            "bars": len(rates),
            "population_signals_all_hours": len(population),
            "output": str(out),
            "summary_csv": str(summary_csv),
            "variants": [
                {
                    "session": v["session"],
                    "variant": v["variant"],
                    **v["summary"],
                }
                for v in variants
            ],
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
