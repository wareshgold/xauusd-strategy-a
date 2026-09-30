"""Research-only 3-month V2 XAUUSD R:R x trailing-SL matrix.

Uses the SAME V2 detector, MT5 M1 population, entry and initial SL as
run_sp2l_strategy_a_v2_xauusd_mt5_backtest.py. Only exit policy varies.

Matrix defaults:
  RR = 1R, 2R, 3R
  trailing distance = 0 (OFF), 10, 20, 30, 50 pips

Trailing is NON_CANONICAL_FORENSIC:
- favorable M1 extreme activates trailing after price moves by trail distance
- the updated SL is active from the NEXT candle only
- same-M1-bar SL+TP touch is AMBIGUOUS
- no TP extension
- no canonical rule/parameter promotion
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5
import numpy as np

from mt5_terminal_resolver import find_mt5_terminal
from sp2l_strategy_a_v2_detector import detect_setup, find_first_entry

PIP_SIZE = 0.10
DEFAULT_RR = [1.0, 2.0, 3.0]
DEFAULT_TRAIL_PIPS = [0.0, 10.0, 20.0, 30.0, 50.0]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def simulate(rates: np.ndarray, signal: dict, rr: float, trail_pips: float) -> dict:
    direction = signal["direction"]
    entry = signal["entry"]
    initial_sl = signal["sl"]
    risk = abs(entry - initial_sl)
    tp = entry + rr * risk if direction == "BUY" else entry - rr * risk
    trailing_enabled = trail_pips > 0.0
    trail = trail_pips * PIP_SIZE

    current_sl = initial_sl
    best = entry
    active = False
    i = signal["entry_index"]

    while i < len(rates):
        bar = rates[i]
        high = float(bar["high"])
        low = float(bar["low"])

        if direction == "BUY":
            sl_hit = low <= current_sl
            tp_hit = high >= tp
            if sl_hit and tp_hit:
                return {"result": "AMBIGUOUS", "r": None, "exit_index": i,
                        "reason": "SL_AND_TP_SAME_BAR", "trailing_activated": active}
            if sl_hit:
                realized = (current_sl - entry) / risk
                return {"result": "WIN" if realized > 0 else ("LOSS" if realized < 0 else "BREAKEVEN"),
                        "r": realized, "exit_index": i,
                        "reason": "TRAIL_SL" if active and current_sl != initial_sl else "SL",
                        "trailing_activated": active}
            if tp_hit:
                return {"result": "WIN", "r": rr, "exit_index": i,
                        "reason": "TP", "trailing_activated": active}
            if trailing_enabled:
                best = max(best, high)
                if not active and best >= entry + trail:
                    active = True
                if active:
                    current_sl = max(current_sl, best - trail)
        else:
            sl_hit = high >= current_sl
            tp_hit = low <= tp
            if sl_hit and tp_hit:
                return {"result": "AMBIGUOUS", "r": None, "exit_index": i,
                        "reason": "SL_AND_TP_SAME_BAR", "trailing_activated": active}
            if sl_hit:
                realized = (entry - current_sl) / risk
                return {"result": "WIN" if realized > 0 else ("LOSS" if realized < 0 else "BREAKEVEN"),
                        "r": realized, "exit_index": i,
                        "reason": "TRAIL_SL" if active and current_sl != initial_sl else "SL",
                        "trailing_activated": active}
            if tp_hit:
                return {"result": "WIN", "r": rr, "exit_index": i,
                        "reason": "TP", "trailing_activated": active}
            if trailing_enabled:
                best = min(best, low)
                if not active and best <= entry - trail:
                    active = True
                if active:
                    current_sl = min(current_sl, best + trail)
        i += 1

    return {"result": "OPEN_OR_UNRESOLVED", "r": None, "exit_index": None,
            "reason": "OPEN_OR_UNRESOLVED", "trailing_activated": active}


def summarize(rows: list[dict], contract_size: float, volume: float) -> dict:
    decisive = [r for r in rows if r["result"] in {"WIN", "LOSS", "BREAKEVEN"}]
    wins = [r for r in decisive if r["result"] == "WIN"]
    losses = [r for r in decisive if r["result"] == "LOSS"]
    rs = [float(r["r"]) for r in decisive if r["r"] is not None]
    gp = sum(x for x in rs if x > 0)
    gl = -sum(x for x in rs if x < 0)
    equity = peak = dd = 0.0
    streak = max_streak = 0
    for x in rs:
        equity += x
        peak = max(peak, equity)
        dd = max(dd, peak - equity)
        streak = streak + 1 if x < 0 else 0
        max_streak = max(max_streak, streak)
    return {
        "signals": len(rows),
        "decisive": len(decisive),
        "wins": len(wins),
        "losses": len(losses),
        "breakeven": sum(r["result"] == "BREAKEVEN" for r in rows),
        "ambiguous": sum(r["result"] == "AMBIGUOUS" for r in rows),
        "open_or_unresolved": sum(r["result"] == "OPEN_OR_UNRESOLVED" for r in rows),
        "win_rate_decisive_pct": 100 * len(wins) / len(decisive) if decisive else None,
        "net_R": sum(rs),
        "profit_factor": gp / gl if gl else None,
        "max_drawdown_R": dd,
        "max_losing_streak": max_streak,
        "trailing_activated_count": sum(r["trailing_activated"] for r in rows),
        "net_usd": sum(float(r["pnl_usd"]) for r in rows if r["pnl_usd"] is not None),
        "gross_profit_usd": sum(float(r["pnl_usd"]) for r in rows if r["pnl_usd"] is not None and float(r["pnl_usd"]) > 0),
        "gross_loss_usd": -sum(float(r["pnl_usd"]) for r in rows if r["pnl_usd"] is not None and float(r["pnl_usd"]) < 0),
        "average_initial_risk_usd": sum(float(r["risk_usd"]) for r in rows) / len(rows) if rows else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-06-28T00:00:00Z")
    ap.add_argument("--end", default="2026-09-25T00:00:00Z")
    ap.add_argument("--rr", nargs="+", type=float, default=DEFAULT_RR)
    ap.add_argument("--trail-pips", nargs="+", type=float, default=DEFAULT_TRAIL_PIPS,
                    help="Trailing distance in pips; 0 means trailing OFF.")
    ap.add_argument("--mt5-path", default=None)
    ap.add_argument("--output", default=None)
    ap.add_argument("--volume", type=float, default=0.01, help="Lot volume used only for USD P&L reporting.")
    args = ap.parse_args()

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
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            raise RuntimeError(f"symbol_info failed: {symbol}: {mt5.last_error()}")
        contract_size = float(symbol_info.trade_contract_size)
        rates = fetch_rates(symbol, start, end)
        population = build_population(rates)
        variants = []

        for rr in args.rr:
            for trail_pips in args.trail_pips:
                rows = []
                for signal in population:
                    outcome = simulate(rates, signal, rr, trail_pips)
                    rows.append({
                        **signal,
                        "rr": rr,
                        "trail_pips": trail_pips,
                        **outcome,
                        "risk_usd": float(signal["risk"]) * contract_size * args.volume,
                        "pnl_usd": (float(outcome["r"]) * float(signal["risk"]) * contract_size * args.volume) if outcome["r"] is not None else None,
                        "exit_time": (
                            int(rates[outcome["exit_index"]]["time"])
                            if outcome["exit_index"] is not None else None
                        ),
                    })
                variants.append({
                    "rr": rr,
                    "trail_pips": trail_pips,
                    "summary": summarize(rows, contract_size, args.volume),
                    "trades": rows,
                })

        result = {
            "status": "COMPLETE",
            "mode": "NON_CANONICAL_FORENSIC",
            "experiment": "V2_XAUUSD_3MONTH_RR_X_TRAILING_MATRIX",
            "population_contract": {
                "detector": "sp2l_strategy_a_v2_detector.py",
                "p_gap_price": 1.0,
                "spike_multiplier": 1.5,
                "max_sl_distance": 10.0,
                "session_filter": False,
                "entry_policy": "V2 detector first entry",
                "initial_sl_policy": "V2 detector unchanged",
            },
            "period": {"start_utc": start.isoformat(), "end_utc": end.isoformat()},
            "resolved_symbol": symbol,
            "accounting": {
                "volume_lots": args.volume,
                "contract_size": contract_size,
                "usd_pnl_formula": "R * abs(entry-initial_sl) * contract_size * volume",
            },
            "bars": int(len(rates)),
            "population_signals": len(population),
            "matrix": {
                "rr_values": args.rr,
                "trail_pips_values": args.trail_pips,
                "trail_zero_semantics": "OFF",
                "trail_price_multiplier": PIP_SIZE,
                "trailing_policy": "favorable M1 extreme updates SL for next candle only",
                "same_bar_policy": "AMBIGUOUS when active SL and TP both touched",
                "intrabar_order": "NOT_INFERRED_FROM_M1_OHLC",
                "tp_extension": False,
                "canonical": False,
            },
            "variants": variants,
        }

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = Path(args.output) if args.output else Path(
            "artifacts/backtest-mt5-local"
        ) / f"SP2L_V2_XAUUSD_3MONTH_RR_TRAILING_MATRIX_{stamp}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")

        print(json.dumps({
            "status": "COMPLETE",
            "output": str(out),
            "symbol": symbol,
            "bars": len(rates),
            "signals": len(population),
            "variants": [
                {"rr": v["rr"], "trail_pips": v["trail_pips"], **v["summary"]}
                for v in variants
            ],
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
