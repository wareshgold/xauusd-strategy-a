"""Research-only exact V2 XAUUSD replay from the connected MT5 terminal.

This runner is deliberately XAUUSD-only and uses the shared V2 detector:
- P-Gap = 1.0
- spike multiplier = 1.5
- max SL distance = 10.0
- TP = 1R
- no session filter
- M1 history from MT5 copy_rates_range()

It is a comparator, not canonical Strategy A.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5
import numpy as np

from mt5_terminal_resolver import find_mt5_terminal
from sp2l_strategy_a_v2_detector import detect_setup, find_first_entry

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "artifacts" / "backtest-mt5-local"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REQUESTED_SYMBOL = "XAUUSD"
P_GAP_PRICE = 1.0
SPIKE_MULTIPLIER = 1.5
MAX_SL_DISTANCE = 10.0
TP_R = 1.0


def resolve_xauusd() -> str:
    symbols = list(mt5.symbols_get() or [])
    names = {str(s.name): s for s in symbols}
    for name in ("XAUUSD", "XAUUSD.ecn", "XAUUSDm", "XAUUSD_ecn"):
        if name in names:
            return name
    for s in symbols:
        n = str(s.name).upper()
        if n.startswith("XAUUSD"):
            return str(s.name)
    raise RuntimeError("No XAUUSD broker symbol found in the connected MT5 terminal")


def fetch_rates(symbol: str, start: datetime, end: datetime) -> np.ndarray:
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"symbol_select failed for {symbol}: {mt5.last_error()}")

    chunk_days = float(os.getenv("SP2L_MT5_HISTORY_CHUNK_DAYS", "7"))
    retries = int(os.getenv("SP2L_MT5_HISTORY_RETRIES", "3"))
    cursor = start.astimezone(timezone.utc)
    end = end.astimezone(timezone.utc)
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
                f"MT5 history failed: {symbol} {cursor.isoformat()}..{chunk_end.isoformat()} "
                f"after {retries} attempts: {err or mt5.last_error()}"
            )
        chunks.append(rates.copy())
        cursor = chunk_end + timedelta(minutes=1)

    result = np.concatenate(chunks)
    result.sort(order="time")
    _, idx = np.unique(result["time"], return_index=True)
    return result[np.sort(idx)]


def outcome(candles: np.ndarray, entry_index: int, signal: dict):
    """Research-only OHLC replay from the first entry trigger onward.

    Same-bar SL/TP ambiguity is quarantined rather than guessed.
    """
    direction = signal["direction"]
    entry = float(signal["entry"])
    sl = float(signal["sl"])
    tp = float(signal["tp"])

    for j in range(entry_index, len(candles)):
        bar = candles[j]
        high, low = float(bar["high"]), float(bar["low"])

        if direction == "BUY":
            hit_sl, hit_tp = low <= sl, high >= tp
        else:
            hit_sl, hit_tp = high >= sl, low <= tp

        if hit_sl and hit_tp:
            return "AMBIGUOUS", j, None, "BOTH_SL_TP_SAME_BAR"
        if hit_tp:
            return "WIN", j, 1.0, "TP"
        if hit_sl:
            return "LOSS", j, -1.0, "SL"

    return "OPEN_AT_END", None, None, "OPEN_AT_END"


def max_dd(results):
    equity = peak = dd = 0.0
    streak = max_streak = 0
    for r in results:
        equity += r
        peak = max(peak, equity)
        dd = max(dd, peak - equity)
        if r < 0:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return dd, max_streak


def run(rates: np.ndarray) -> dict:
    signals = []
    used_entry_until = -1

    # The detector evaluates the completed three-candle setup ending at i.
    for i in range(2, len(rates)):
        if i <= used_entry_until:
            continue

        setup = detect_setup(rates[: i + 1])
        if setup is None:
            continue

        signal = find_first_entry(rates, i, setup)
        if signal is None:
            continue

        entry_index = int(signal["entry_index"])
        result, exit_index, r, reason = outcome(rates, entry_index, signal)

        signals.append({
            "direction": signal["direction"],
            "setup_time": int(signal["setup_time"]),
            "before_spike_time": int(signal["before_spike_time"]),
            "spike_time": int(signal["spike_time"]),
            "after_spike_time": int(signal["after_spike_time"]),
            "entry_index": entry_index,
            "entry_time": int(signal["entry_time"]),
            "entry": float(signal["entry"]),
            "sl": float(signal["sl"]),
            "risk": float(signal["risk"]),
            "tp": float(signal["tp"]),
            "exit_index": exit_index,
            "exit_time": int(rates[exit_index]["time"]) if exit_index is not None else None,
            "result": result,
            "r": r,
            "exit_reason": reason,
        })
        used_entry_until = entry_index

    wins = sum(x["result"] == "WIN" for x in signals)
    losses = sum(x["result"] == "LOSS" for x in signals)
    ambiguous = sum(x["result"] == "AMBIGUOUS" for x in signals)
    open_end = sum(x["result"] == "OPEN_AT_END" for x in signals)
    decisive = wins + losses
    dd, max_losses = max_dd([float(x["r"]) for x in signals if x["r"] is not None])

    by_direction = {}
    for direction in ("BUY", "SELL"):
        subset = [x for x in signals if x["direction"] == direction]
        w = sum(x["result"] == "WIN" for x in subset)
        l = sum(x["result"] == "LOSS" for x in subset)
        d = w + l
        by_direction[direction] = {
            "signals": len(subset),
            "wins": w,
            "losses": l,
            "ambiguous": sum(x["result"] == "AMBIGUOUS" for x in subset),
            "decisive": d,
            "win_rate_pct": 100 * w / d if d else None,
            "net_r": w - l,
        }

    return {
        "symbol": REQUESTED_SYMBOL,
        "bars": int(len(rates)),
        "first_bar_utc": datetime.fromtimestamp(int(rates[0]["time"]), timezone.utc).isoformat(),
        "last_bar_utc": datetime.fromtimestamp(int(rates[-1]["time"]), timezone.utc).isoformat(),
        "signals": len(signals),
        "wins": wins,
        "losses": losses,
        "ambiguous": ambiguous,
        "open_at_end": open_end,
        "decisive": decisive,
        "win_rate_pct": 100 * wins / decisive if decisive else None,
        "net_r": wins - losses,
        "profit_factor_simplified": wins / losses if losses else None,
        "max_drawdown_r": dd,
        "max_consecutive_losses": max_losses,
        "by_direction": by_direction,
        "signals_detail": signals,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2026-06-28T00:00:00Z")
    parser.add_argument("--end", default="2026-09-25T00:00:00Z")
    parser.add_argument("--mt5-path", default=None)
    args = parser.parse_args()

    initialized = mt5.initialize(path=str(args.mt5_path)) if args.mt5_path else mt5.initialize()
    if not initialized:
        terminal = None if args.mt5_path else find_mt5_terminal()
        if terminal is None or not mt5.initialize(path=str(terminal)):
            print(json.dumps({"status": "MT5_INIT_FAILED", "error": mt5.last_error()}, indent=2))
            return 2

    try:
        symbol = resolve_xauusd()
        start = datetime.fromisoformat(args.start.replace("Z", "+00:00"))
        end = datetime.fromisoformat(args.end.replace("Z", "+00:00"))

        info = mt5.symbol_info(symbol)
        print(f"[MT5] XAUUSD -> {symbol}: downloading M1 history ...", flush=True)
        rates = fetch_rates(symbol, start, end)
        result = run(rates)

        report = {
            "status": "COMPLETE",
            "mode": "RESEARCH_ONLY_SP2L_STRATEGY_A_V2_MT5_XAUUSD",
            "source": "CONNECTED_MT5_TERMINAL",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "requested_symbol": REQUESTED_SYMBOL,
            "resolved_symbol": symbol,
            "broker_symbol_info": {
                "digits": int(info.digits) if info else None,
                "point": float(info.point) if info else None,
                "trade_mode": int(info.trade_mode) if info else None,
            },
            "period": {"start_utc": start.isoformat(), "end_utc": end.isoformat()},
            "timeframe": "M1",
            "geometry": {
                "p_gap_price": P_GAP_PRICE,
                "spike_multiplier": SPIKE_MULTIPLIER,
                "max_sl_distance": MAX_SL_DISTANCE,
                "tp_r": TP_R,
                "trigger": "first_post_setup_lower_low_for_buy_higher_high_for_sell",
                "entry": "trigger_candle_low_for_buy_high_for_sell",
                "sl_anchor": "candle_before_spike",
                "session_filter": False,
                "canonical": False,
            },
            "data_contract": {
                "acquisition": "MT5.copy_rates_range",
                "timestamp_handling": "raw MT5 epoch rendered as UTC; no offset normalization",
                "symbol_scope": "XAUUSD only",
            },
            "outcomes": result,
            "reference_comparison_target": {
                "artifact": "SP2L_STRATEGY_A_V2_MT5_20260928T074842Z.json",
                "expected_reference_bars": 87673,
                "expected_reference_signals": 1472,
                "expected_reference_trades": 1356,
                "expected_reference_wins": 836,
                "expected_reference_losses": 520,
                "expected_reference_win_rate_pct": 61.65191740412979,
                "expected_reference_net_r": 316,
                "expected_reference_pf": 1.6076923076923082,
            },
            "semantic_limits": [
                "Research-only comparator; not canonical Strategy A.",
                "No session filter is applied.",
                "OHLC cannot prove intrabar ordering when both SL and TP are touched on one bar; such cases are AMBIGUOUS.",
                "This report is intended to verify the V2 geometry against the user's live MT5 history, not to authorize production trading.",
            ],
        }

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = OUT_DIR / f"SP2L_STRATEGY_A_V2_XAUUSD_MT5_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        print(f"[DONE] XAUUSD -> {symbol}: bars={result['bars']} signals={result['signals']} "
              f"decisive={result['decisive']} WR={result['win_rate_pct']}", flush=True)
        print(json.dumps({
            "status": report["status"],
            "report": str(path),
            "resolved_symbol": symbol,
            "results": {
                "signals": result["signals"],
                "decisive": result["decisive"],
                "wins": result["wins"],
                "losses": result["losses"],
                "win_rate_pct": result["win_rate_pct"],
                "net_r": result["net_r"],
                "profit_factor_simplified": result["profit_factor_simplified"],
            },
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
