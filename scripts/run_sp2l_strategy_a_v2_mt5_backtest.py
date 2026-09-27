"""Research-only MT5-local backtest for SP2L Strategy A V2.

V2 contract:
- P-Gap = 1.0 price unit
- three-candle setup: before / spike / after
- first post-setup lower-low / higher-high trigger
- entry = trigger candle Low/High
- SL = candle before Spike Low/High
- TP = 1R
- max SL = 10.0 price units
- no EMA/ATR/ADX/trend/session filters
- no second entry
- same-bar SL+TP => SL-first

This script is intentionally separate from the source-aligned Strategy A runner.
It is research-only and must never emit production BUY/SELL decisions.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "artifacts" / "backtest-mt5-local"
OUT_DIR.mkdir(parents=True, exist_ok=True)

try:
    from mt5_terminal_resolver import find_mt5_terminal
    from sp2l_strategy_a_v2_detector import detect_setup, find_first_entry
except ImportError:
    from scripts.mt5_terminal_resolver import find_mt5_terminal
    from scripts.sp2l_strategy_a_v2_detector import detect_setup, find_first_entry


def fetch_rates(symbol: str, start: datetime, end: datetime) -> np.ndarray:
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"symbol_select failed: {symbol} {mt5.last_error()}")

    chunks = []
    cursor = start.astimezone(timezone.utc)
    end = end.astimezone(timezone.utc)

    while cursor < end:
        chunk_end = min(cursor + timedelta(days=7), end)
        rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, cursor, chunk_end)
        if rates is None or len(rates) == 0:
            raise RuntimeError(
                f"history failed {cursor.isoformat()}..{chunk_end.isoformat()}: {mt5.last_error()}"
            )
        chunks.append(rates.copy())
        cursor = chunk_end + timedelta(minutes=1)

    rates = np.concatenate(chunks)
    rates.sort(order="time")
    _, idx = np.unique(rates["time"], return_index=True)
    return rates[np.sort(idx)]


def gap_minutes(a: int, b: int) -> int:
    return max(0, int((b - a) // 60) - 1)


def mark_to_market_r(direction: str, entry: float, risk: float, close: float) -> float:
    if direction == "BUY":
        return (close - entry) / risk
    return (entry - close) / risk


def build_signals(rates: np.ndarray) -> list[dict]:
    """Reproduce the V2 setup/trigger contract on the full historical array."""
    signals = []
    used_entry_indices: set[int] = set()

    for c_pos in range(2, len(rates) - 1):
        setup = detect_setup(rates[c_pos - 2 : c_pos + 1])
        if setup is None:
            continue

        entry = find_first_entry(rates, c_pos, setup)
        if entry is None:
            continue

        entry_index = int(entry["entry_index"])

        # The reference implementation writes only one position to an entry
        # timestamp. Preserve deterministic single-position behavior.
        if entry_index in used_entry_indices:
            continue

        used_entry_indices.add(entry_index)
        signals.append(entry)

    signals.sort(key=lambda x: (x["entry_index"], x["direction"]))
    return signals


def run_backtest(rates: np.ndarray, signals: list[dict]) -> dict:
    by_entry = {int(s["entry_index"]): s for s in signals}
    active = None
    trades = []
    data_gap_events = []

    for i in range(len(rates)):
        bar = rates[i]
        high = float(bar["high"])
        low = float(bar["low"])
        close = float(bar["close"])
        ts = int(bar["time"])

        # Manage active trade before activating a new signal, matching the
        # reference loop. The entry candle itself is therefore not also used
        # as an exit candle.
        if active is not None:
            direction = active["direction"]
            sl = active["sl"]
            tp = active["tp"]
            entry = active["entry"]
            risk = active["risk"]

            if direction == "BUY":
                hit_sl = low <= sl
                hit_tp = high >= tp
            else:
                hit_sl = high >= sl
                hit_tp = low <= tp

            exit_price = None
            reason = None

            if hit_sl and hit_tp:
                exit_price = sl
                reason = "SL_FIRST_SAME_BAR"
            elif hit_sl:
                exit_price = sl
                reason = "SL"
            elif hit_tp:
                exit_price = tp
                reason = "TP"

            if exit_price is not None:
                r = (
                    (exit_price - entry) / risk
                    if direction == "BUY"
                    else (entry - exit_price) / risk
                )
                trades.append({
                    **active,
                    "exit_time": ts,
                    "exit": float(exit_price),
                    "r": float(r),
                    "exit_reason": reason,
                    "completed": True,
                })
                active = None
                continue

        if active is None and i in by_entry:
            active = dict(by_entry[i])
            active["signal_time"] = active["entry_time"]
            active["activation_time"] = ts

        # Data-quality telemetry: retain missing M1 gaps that occur while a
        # trade is active. They do not invent an exit price.
        if i > 0 and active is not None:
            missing = gap_minutes(int(rates[i - 1]["time"]), ts)
            if missing:
                data_gap_events.append({
                    "from_utc": datetime.fromtimestamp(
                        int(rates[i - 1]["time"]), timezone.utc
                    ).isoformat(),
                    "to_utc": datetime.fromtimestamp(ts, timezone.utc).isoformat(),
                    "missing_minutes": missing,
                })

    if active is not None:
        last = rates[-1]
        close = float(last["close"])
        r = mark_to_market_r(active["direction"], active["entry"], active["risk"], close)
        trades.append({
            **active,
            "exit_time": int(last["time"]),
            "exit": close,
            "r": float(r),
            "exit_reason": "END_OF_DATA_MARK",
            "completed": False,
        })

    wins = sum(t["r"] > 0 for t in trades)
    losses = sum(t["r"] <= 0 for t in trades)
    completed = [t for t in trades if t["completed"]]
    completed_wins = sum(t["r"] > 0 for t in completed)
    completed_losses = sum(t["r"] <= 0 for t in completed)

    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    max_loss_run = 0
    loss_run = 0
    for trade in trades:
        equity += trade["r"]
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
        if trade["r"] <= 0:
            loss_run += 1
            max_loss_run = max(max_loss_run, loss_run)
        else:
            loss_run = 0

    by_direction = {}
    for direction in ("BUY", "SELL"):
        subset = [t for t in trades if t["direction"] == direction]
        w = sum(t["r"] > 0 for t in subset)
        l = sum(t["r"] <= 0 for t in subset)
        by_direction[direction] = {
            "trades": len(subset),
            "wins": w,
            "losses": l,
            "win_rate_pct": 100 * w / len(subset) if subset else None,
            "net_r": sum(t["r"] for t in subset),
        }

    exit_reasons = Counter(t["exit_reason"] for t in trades)

    return {
        "signals": len(signals),
        "trades": len(trades),
        "wins": wins,
        "losses": losses,
        "win_rate_pct": 100 * wins / len(trades) if trades else None,
        "net_r": sum(t["r"] for t in trades),
        "profit_factor_simplified": (
            sum(t["r"] for t in trades if t["r"] > 0)
            / abs(sum(t["r"] for t in trades if t["r"] < 0))
            if any(t["r"] < 0 for t in trades)
            else None
        ),
        "completed_trades": len(completed),
        "completed_wins": completed_wins,
        "completed_losses": completed_losses,
        "completed_win_rate_pct": (
            100 * completed_wins / len(completed) if completed else None
        ),
        "max_drawdown_r": max_dd,
        "max_consecutive_losses": max_loss_run,
        "by_direction": by_direction,
        "exit_reasons": dict(exit_reasons),
        "data_gap_events_during_active_trades": data_gap_events,
        "trades_detail": trades,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="XAUUSD")
    parser.add_argument("--start", required=True, help="UTC ISO")
    parser.add_argument("--end", required=True, help="UTC ISO")
    parser.add_argument("--mt5-path", default=None)
    args = parser.parse_args()

    start = datetime.fromisoformat(args.start.replace("Z", "+00:00"))
    end = datetime.fromisoformat(args.end.replace("Z", "+00:00"))

    initialized = False
    if args.mt5_path:
        initialized = mt5.initialize(path=args.mt5_path)
    else:
        initialized = mt5.initialize()

    if not initialized:
        terminal = find_mt5_terminal()
        if terminal is None or not mt5.initialize(path=str(terminal)):
            print(json.dumps({
                "status": "MT5_INIT_FAILED",
                "error": mt5.last_error(),
                "terminal_path": str(terminal) if terminal else None,
            }, indent=2))
            return 2

    try:
        symbol = args.symbol
        rates = fetch_rates(symbol, start, end)
        signals = build_signals(rates)
        result = run_backtest(rates, signals)

        report = {
            "status": "COMPLETE",
            "mode": "RESEARCH_ONLY_SP2L_STRATEGY_A_V2",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "symbol_requested": symbol,
            "symbol_used": symbol,
            "period": {
                "start_utc": start.isoformat(),
                "end_utc": end.isoformat(),
            },
            "timeframe": "M1",
            "contract": {
                "p_gap_price": 1.0,
                "spike_multiplier": 1.5,
                "max_sl_distance": 10.0,
                "tp_r": 1.0,
                "trigger": "first post-setup lower-low for BUY / higher-high for SELL",
                "entry": "trigger candle Low for BUY / High for SELL",
                "sl_anchor": "candle before Spike Low/High",
                "intrabar_resolution": "SL_FIRST",
                "ema_filter": False,
                "atr_filter": False,
                "adx_filter": False,
                "trend_filter": False,
                "session_filter": False,
                "second_entry": False,
                "canonical": False,
            },
            "history": {
                "bars": int(len(rates)),
                "first_bar_utc": datetime.fromtimestamp(
                    int(rates[0]["time"]), timezone.utc
                ).isoformat(),
                "last_bar_utc": datetime.fromtimestamp(
                    int(rates[-1]["time"]), timezone.utc
                ).isoformat(),
            },
            "results": result,
            "semantic_limits": [
                "V2 is a research comparator, not canonical Strategy A.",
                "The 1.0 P-Gap threshold is an externally observed implementation contract, not source-resolved canonical geometry.",
                "SL-first is an explicit OHLC convention and does not establish true intrabar chronology.",
                "No EMA/ATR/ADX/trend/session/second-entry filter is active in this baseline.",
                "No production BUY/SELL decision is emitted by this script.",
            ],
        }

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = OUT_DIR / f"SP2L_STRATEGY_A_V2_MT5_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        print(json.dumps({
            "status": report["status"],
            "report": str(path),
            "signals": result["signals"],
            "trades": result["trades"],
            "wins": result["wins"],
            "losses": result["losses"],
            "win_rate_pct": result["win_rate_pct"],
            "net_r": result["net_r"],
            "profit_factor_simplified": result["profit_factor_simplified"],
            "completed_win_rate_pct": result["completed_win_rate_pct"],
            "max_drawdown_r": result["max_drawdown_r"],
            "max_consecutive_losses": result["max_consecutive_losses"],
            "by_direction": result["by_direction"],
            "exit_reasons": result["exit_reasons"],
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
