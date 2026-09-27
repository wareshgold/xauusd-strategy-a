"""Research-only SP2L direction-reversal counterfactual replay.

This script keeps the existing signal population unchanged and reverses only
the hypothetical trade direction. It does not modify detector geometry.

For each original signal:
- original BUY -> counterfactual SELL
- original SELL -> counterfactual BUY
- entry price is unchanged
- absolute SL/TP distance is unchanged from the original signal risk
- M1 fill/exit ambiguity treatment matches the existing research replay

This is NOT canonical Strategy A and must not be used for production signals.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = ROOT / "artifacts/backtest-mt5-local/SP2L_MT5_LOCAL_MULTI_SYMBOL_20260926T124056Z.json"
OUT_DIR = ROOT / "artifacts/backtest-mt5-local"


def load_signals(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for base, result in data.get("outcomes", {}).items():
        if result.get("status") == "FAILED":
            continue
        for s in result.get("signals_detail", []):
            out.append({"base": base, **s})
    return sorted(out, key=lambda x: (int(x["signal_time"]), x["base"]))


def fetch_window(symbol: str, start_ts: int, end_ts: int):
    start = datetime.fromtimestamp(start_ts, timezone.utc) - timedelta(minutes=2)
    end = datetime.fromtimestamp(end_ts, timezone.utc) + timedelta(minutes=2)
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start, end)
    if rates is None or len(rates) == 0:
        raise RuntimeError(f"No M1 data for {symbol}: {mt5.last_error()}")
    return rates


def classify(symbol: str, signal: dict, horizon_minutes: int = 24 * 60) -> dict:
    original_direction = signal["direction"]
    direction = "SELL" if original_direction == "BUY" else "BUY"
    entry = float(signal["entry"])
    risk = abs(float(signal["entry"]) - float(signal["sl"]))

    if direction == "BUY":
        sl = entry - risk
        tp = entry + risk
    else:
        sl = entry + risk
        tp = entry - risk

    rates = fetch_window(
        symbol,
        int(signal["signal_time"]),
        int(signal["signal_time"]) + 60 * horizon_minutes,
    )

    outcome = "OPEN_AT_END"
    exit_time = None
    exit_reason = None

    for i, bar in enumerate(rates):
        if int(bar["time"]) <= int(signal["signal_time"]):
            continue

        high, low = float(bar["high"]), float(bar["low"])

        if direction == "BUY":
            touched_entry = low <= entry
            hit_sl = low <= sl
            hit_tp = high >= tp
        else:
            touched_entry = high >= entry
            hit_sl = high >= sl
            hit_tp = low <= tp

        if not touched_entry:
            continue

        if hit_sl and hit_tp:
            outcome = "AMBIGUOUS"
            exit_time = int(bar["time"])
            exit_reason = "BOTH_SL_TP_SAME_BAR"
            break

        if hit_tp:
            outcome = "AMBIGUOUS"
            exit_time = int(bar["time"])
            exit_reason = "ENTRY_TP_SAME_BAR_ORDER_UNRESOLVED"
            break

        if hit_sl:
            outcome = "LOSS"
            exit_time = int(bar["time"])
            exit_reason = "SL_AFTER_ENTRY_SAME_BAR"
            break

        for j in range(i + 1, len(rates)):
            b = rates[j]
            h, l = float(b["high"]), float(b["low"])

            if direction == "BUY":
                hit_sl2 = l <= sl
                hit_tp2 = h >= tp
            else:
                hit_sl2 = h >= sl
                hit_tp2 = l <= tp

            if hit_sl2 and hit_tp2:
                outcome = "AMBIGUOUS"
                exit_time = int(b["time"])
                exit_reason = "BOTH_SL_TP_SAME_BAR"
                break

            if hit_tp2:
                outcome = "WIN"
                exit_time = int(b["time"])
                exit_reason = "TP"
                break

            if hit_sl2:
                outcome = "LOSS"
                exit_time = int(b["time"])
                exit_reason = "SL"
                break
        break

    return {
        "signal_time": int(signal["signal_time"]),
        "original_direction": original_direction,
        "counterfactual_direction": direction,
        "entry": entry,
        "risk_distance": risk,
        "sl": sl,
        "tp": tp,
        "result": outcome,
        "exit_time": exit_time,
        "exit_reason": exit_reason,
    }


def summarize(rows: list[dict]) -> dict:
    decisive = [r for r in rows if r["result"] in ("WIN", "LOSS")]
    wins = sum(r["result"] == "WIN" for r in decisive)
    losses = sum(r["result"] == "LOSS" for r in decisive)
    ambiguous = sum(r["result"] == "AMBIGUOUS" for r in rows)
    open_end = sum(r["result"] == "OPEN_AT_END" for r in rows)
    n = len(decisive)

    by_direction = {}
    for direction in ("BUY", "SELL"):
        sub = [r for r in decisive if r["counterfactual_direction"] == direction]
        w = sum(r["result"] == "WIN" for r in sub)
        l = sum(r["result"] == "LOSS" for r in sub)
        by_direction[direction] = {
            "decisive": len(sub),
            "wins": w,
            "losses": l,
            "win_rate_pct_resolved_only": (100.0 * w / len(sub)) if sub else None,
            "net_r_resolved_only": w - l,
        }

    equity = peak = max_dd = 0.0
    max_losses = current_losses = 0
    for r in rows:
        if r["result"] == "WIN":
            equity += 1.0
            current_losses = 0
        elif r["result"] == "LOSS":
            equity -= 1.0
            current_losses += 1
            max_losses = max(max_losses, current_losses)
        else:
            continue
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)

    return {
        "signals": len(rows),
        "decisive": n,
        "wins": wins,
        "losses": losses,
        "ambiguous": ambiguous,
        "open_at_end": open_end,
        "win_rate_pct_resolved_only": (100.0 * wins / n) if n else None,
        "net_r_resolved_only": wins - losses,
        "profit_factor_resolved_only": (wins / losses) if losses else None,
        "worst_case_all_ambiguous_loss_wr_pct": (100.0 * wins / len(rows)) if rows else None,
        "best_case_all_ambiguous_win_wr_pct": (100.0 * (wins + ambiguous) / len(rows)) if rows else None,
        "max_drawdown_r_resolved_only": max_dd,
        "max_consecutive_losses_resolved_only": max_losses,
        "by_counterfactual_direction_resolved_only": by_direction,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--artifact", default=str(DEFAULT_ARTIFACT))
    p.add_argument("--symbol", default="XAUUSD.ecn")
    p.add_argument("--mt5-path", default=None)
    args = p.parse_args()

    artifact = Path(args.artifact)
    signals = [s for s in load_signals(artifact) if s["base"] == "XAUUSD"]

    init_ok = mt5.initialize(path=args.mt5_path) if args.mt5_path else mt5.initialize()
    if not init_ok:
        print(json.dumps({"status": "MT5_INIT_FAILED", "error": mt5.last_error()}, indent=2))
        return 2

    try:
        rows = [classify(args.symbol, s) for s in signals]
        summary = summarize(rows)
        report = {
            "status": "COMPLETE",
            "research_only": True,
            "experiment": "COUNTERFACTUAL_REVERSE_DIRECTION",
            "source_artifact": str(artifact),
            "symbol": args.symbol,
            "signal_set": {
                "base": "XAUUSD",
                "signals": len(signals),
                "signal_population_unchanged": True,
                "detector_geometry_unchanged": True,
            },
            "counterfactual_definition": {
                "BUY_to_SELL": True,
                "SELL_to_BUY": True,
                "entry_unchanged": True,
                "absolute_risk_distance_unchanged": True,
                "sl_tp_rr": "1:1 relative to original risk distance",
            },
            "summary": summary,
            "rows": rows,
            "semantic_limits": [
                "This is a counterfactual research experiment, not canonical Strategy A.",
                "The signal detector and signal population are unchanged.",
                "Direction alone is reversed; entry price and absolute risk distance are unchanged.",
                "M1 OHLC cannot establish intrabar ordering for same-bar entry/TP or SL/TP, so those cases remain AMBIGUOUS.",
                "Pending-order fill semantics remain unresolved.",
                "No production BUY/SELL rule is inferred from this experiment.",
            ],
        }
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = OUT_DIR / f"SP2L_REVERSE_DIRECTION_COUNTERFACTUAL_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({
            "status": "COMPLETE",
            "report": str(path),
            "summary": summary,
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
