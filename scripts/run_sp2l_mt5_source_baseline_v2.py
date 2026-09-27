"""Dedicated MT5 source-baseline replay using the V2 research detector.

Research only. This runner intentionally does not reuse the historical Author
Replica detector. Geometry is imported from sp2l_strategy_a_v2_detector and
outcome mechanics are frozen locally for this provenance checkpoint.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5
import numpy as np

from mt5_terminal_resolver import find_mt5_terminal

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "artifacts" / "backtest-mt5-source-baseline"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CONTRACT = ROOT / "docs" / "research" / "SP2L_MT5_SOURCE_BASELINE_LOCK_20260927.md"
DETECTOR = ROOT / "scripts" / "sp2l_strategy_a_v2_detector.py"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def gap_after(a: int, b: int) -> int:
    return max(0, int((b - a) // 60) - 1)


def fetch_rates(symbol: str, start: datetime, end: datetime) -> np.ndarray:
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"symbol_select failed: {symbol} / {mt5.last_error()}")
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start, end)
    if rates is None or len(rates) == 0:
        raise RuntimeError(f"copy_rates_range failed: {symbol} / {mt5.last_error()}")
    rates = rates.copy()
    rates.sort(order="time")
    _, idx = np.unique(rates["time"], return_index=True)
    return rates[np.sort(idx)]


def as_candle(row) -> dict:
    return {
        "time": int(row["time"]),
        "open": float(row["open"]),
        "high": float(row["high"]),
        "low": float(row["low"]),
        "close": float(row["close"]),
    }


def evaluate_after_fill(rates: np.ndarray, fill_index: int, signal: dict):
    direction = signal["direction"]
    entry, sl, tp = signal["entry"], signal["sl"], signal["tp"]

    for k in range(fill_index, len(rates)):
        bar = rates[k]
        high, low = float(bar["high"]), float(bar["low"])

        if direction == "BUY":
            hit_sl, hit_tp = low <= sl, high >= tp
        else:
            hit_sl, hit_tp = high >= sl, low <= tp

        if hit_sl and hit_tp:
            return "AMBIGUOUS", k, None, "BOTH_SL_TP_SAME_BAR"
        if hit_tp:
            return "WIN", k, 1.0, "TP"
        if hit_sl:
            return "LOSS", k, -1.0, "SL"
    return "OPEN_AT_END", None, None, "OPEN_AT_END"


def run(rates: np.ndarray, symbol: str) -> dict:
    from sp2l_strategy_a_v2_detector import detect_setup, find_first_entry

    signals = []
    for i in range(2, len(rates) - 1):
        window = [as_candle(x) for x in rates[: i + 1]]
        setup = detect_setup(window)
        if setup is None:
            continue
        signal = find_first_entry(window, i, setup)
        if signal is None:
            continue
        entry_index = int(signal["entry_index"])
        # The trigger candle itself is not fillable; pending entry starts after it.
        fill_index = None
        for j in range(entry_index + 1, len(rates)):
            if any(
                gap_after(int(rates[k]["time"]), int(rates[k + 1]["time"]))
                for k in range(entry_index, j)
            ):
                break
            high, low = float(rates[j]["high"]), float(rates[j]["low"])
            touched = low <= signal["entry"] if signal["direction"] == "BUY" else high >= signal["entry"]
            if touched:
                fill_index = j
                break
        if fill_index is None:
            result, exit_index, r, reason = "NO_FILL", None, None, "NO_FILL"
        else:
            result, exit_index, r, reason = evaluate_after_fill(rates, fill_index, signal)
        signals.append({
            **signal,
            "signal_time": int(signal["entry_time"]),
            "result": result,
            "r": r,
            "fill_index": fill_index,
            "fill_time": int(rates[fill_index]["time"]) if fill_index is not None else None,
            "exit_index": exit_index,
            "exit_time": int(rates[exit_index]["time"]) if exit_index is not None else None,
            "exit_reason": reason,
        })

    wins = sum(x["result"] == "WIN" for x in signals)
    losses = sum(x["result"] == "LOSS" for x in signals)
    ambiguous = sum(x["result"] == "AMBIGUOUS" for x in signals)
    no_fill = sum(x["result"] == "NO_FILL" for x in signals)
    decisive = wins + losses
    equity = peak = dd = 0.0
    streak = max_streak = 0
    for x in signals:
        if x["result"] not in ("WIN", "LOSS"):
            continue
        r = float(x["r"])
        equity += r
        peak = max(peak, equity)
        dd = max(dd, peak - equity)
        streak = streak + 1 if r < 0 else 0
        max_streak = max(max_streak, streak)

    return {
        "symbol": symbol,
        "bars": int(len(rates)),
        "first_bar_utc": datetime.fromtimestamp(int(rates[0]["time"]), timezone.utc).isoformat(),
        "last_bar_utc": datetime.fromtimestamp(int(rates[-1]["time"]), timezone.utc).isoformat(),
        "signals": len(signals),
        "wins": wins,
        "losses": losses,
        "ambiguous": ambiguous,
        "no_fill": no_fill,
        "decisive": decisive,
        "win_rate_pct": 100 * wins / decisive if decisive else None,
        "net_r": wins - losses,
        "profit_factor_simplified": wins / losses if losses else None,
        "max_drawdown_r": dd,
        "max_consecutive_losses": max_streak,
        "signals_detail": signals,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--start", default="2026-09-14T00:00:00Z")
    p.add_argument("--end", default="2026-09-25T23:59:59Z")
    p.add_argument("--mt5-path", required=False)
    args = p.parse_args()

    print("[BASELINE_V2] starting", flush=True)
    print(f"[BASELINE_V2] mt5_path={args.mt5_path}", flush=True)
    print(f"[BASELINE_V2] window={args.start}..{args.end}", flush=True)
    initialized = (
        mt5.initialize(path=args.mt5_path, timeout=30000)
        if args.mt5_path
        else mt5.initialize(timeout=30000)
    )
    print(f"[BASELINE_V2] mt5_initialize={initialized} last_error={mt5.last_error()}", flush=True)
    if not initialized:
        terminal = find_mt5_terminal() if not args.mt5_path else None
        if terminal is None or not mt5.initialize(path=str(terminal), timeout=30000):
            print(json.dumps({"status": "MT5_INIT_FAILED", "error": mt5.last_error()}, indent=2))
            return 2

    try:
        print("[BASELINE_V2] resolving XAUUSD...", flush=True)
        symbol = "XAUUSD"
        matches = [s.name for s in (mt5.symbols_get() or []) if str(s.name).upper() == "XAUUSD.ECN"]
        if not matches:
            matches = [s.name for s in (mt5.symbols_get() or []) if str(s.name).upper().startswith("XAUUSD")]
        if not matches:
            raise RuntimeError("Could not resolve XAUUSD broker symbol")
        resolved = matches[0]
        print(f"[BASELINE_V2] resolved_symbol={resolved}", flush=True)

        start, end = parse_ts(args.start), parse_ts(args.end)
        print("[BASELINE_V2] downloading M1 history...", flush=True)
        rates = fetch_rates(resolved, start, end)
        print(f"[BASELINE_V2] downloaded bars={len(rates)}", flush=True)
        print("[BASELINE_V2] running V2 detector...", flush=True)
        result = run(rates, resolved)
        print(f"[BASELINE_V2] signals={result["signals"]} decisive={result["decisive"]}", flush=True)

        report = {
            "status": "COMPLETE",
            "research_only": True,
            "baseline_contract_sha256": sha256_file(CONTRACT),
            "detector_sha256": sha256_file(DETECTOR),
            "detector": "sp2l_strategy_a_v2_detector",
            "runner": "run_sp2l_mt5_source_baseline_v2.py",
            "data_source": "CONNECTED_MT5_TERMINAL",
            "symbol_requested": symbol,
            "symbol_resolved": resolved,
            "timeframe": "M1",
            "period": {"start_utc": start.isoformat(), "end_utc": end.isoformat()},
            "geometry_config": {
                "p_gap_price": 1.0,
                "spike_multiplier": 1.5,
                "max_sl_distance": 10.0,
                "tp_r": 1.0,
                "session_filter": False,
                "second_entry_2x": False,
            },
            "outcome_contract": {
                "pending_fill": "later_bar_touch_entry",
                "same_bar_sl_tp": "AMBIGUOUS",
                "trigger_bar_fill": False,
                "data_gap": "quarantine_no_fill",
            },
            "result": result,
        }

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = OUT_DIR / f"SP2L_MT5_SOURCE_BASELINE_V2_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({
            "status": "COMPLETE",
            "report": str(path),
            "symbol": resolved,
            "bars": result["bars"],
            "signals": result["signals"],
            "decisive": result["decisive"],
            "wins": result["wins"],
            "losses": result["losses"],
            "ambiguous": result["ambiguous"],
            "no_fill": result["no_fill"],
            "win_rate_pct": result["win_rate_pct"],
            "net_r": result["net_r"],
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
