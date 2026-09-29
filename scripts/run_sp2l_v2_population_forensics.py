"""Deterministic V2 population forensic harness.

Purpose:
- Separate raw setup population from entry population.
- Attribute first-trigger outcomes without changing V2 geometry.
- Make the 2026-09-29 68.04% observation directly comparable at the
  setup -> trigger -> valid-entry boundary.

This is research/forensics only. It does not define canonical Strategy A.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

from mt5_terminal_resolver import find_mt5_terminal
from run_sp2l_strategy_a_v2_xauusd_mt5_backtest import fetch_rates, resolve_xauusd
from sp2l_strategy_a_v2_detector import detect_setup, MAX_SL_DISTANCE, TP_R


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "artifacts" / "forensic" / "2026-09-29"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REFERENCE = {
    "bars": 87673,
    "signals": 1472,
    "trades": 1356,
    "wins": 836,
    "losses": 520,
    "win_rate_pct": 61.65191740412979,
    "net_r": 316,
    "profit_factor_simplified": 1.6076923076923082,
}


def classify_first_entry(candles, start_index: int, setup: dict) -> dict:
    """Reproduce find_first_entry semantics, but expose why None occurs."""
    direction = setup["direction"]
    sl = float(setup["sl"])

    for entry_index in range(start_index + 1, len(candles)):
        current = candles[entry_index]
        previous = candles[entry_index - 1]

        if direction == "BUY":
            trigger = float(current["low"]) < float(previous["low"])
            entry = float(current["low"])
            risk = entry - sl
        else:
            trigger = float(current["high"]) > float(previous["high"])
            entry = float(current["high"])
            risk = sl - entry

        if not trigger:
            continue

        if risk <= 0:
            return {
                "status": "INVALID_RISK",
                "reason": "RISK_NON_POSITIVE",
                "entry_index": int(entry_index),
                "entry_time": int(current["time"]),
                "entry": entry,
                "risk": risk,
            }

        if risk > MAX_SL_DISTANCE:
            return {
                "status": "INVALID_RISK",
                "reason": "RISK_ABOVE_MAX_SL_DISTANCE",
                "entry_index": int(entry_index),
                "entry_time": int(current["time"]),
                "entry": entry,
                "risk": risk,
            }

        tp = entry + TP_R * risk if direction == "BUY" else entry - TP_R * risk
        return {
            "status": "VALID_ENTRY",
            "reason": "FIRST_TRIGGER_VALID",
            "entry_index": int(entry_index),
            "entry_time": int(current["time"]),
            "entry": entry,
            "risk": risk,
            "tp": tp,
        }

    return {
        "status": "NO_TRIGGER",
        "reason": "NO_POST_SETUP_TRIGGER_IN_AVAILABLE_HISTORY",
        "entry_index": None,
        "entry_time": None,
        "entry": None,
        "risk": None,
    }


def outcome(candles, entry_index: int, direction: str, entry: float, sl: float, tp: float):
    for j in range(entry_index, len(candles)):
        high = float(candles[j]["high"])
        low = float(candles[j]["low"])
        if direction == "BUY":
            hit_sl, hit_tp = low <= sl, high >= tp
        else:
            hit_sl, hit_tp = high >= sl, low <= tp

        if hit_sl and hit_tp:
            return "AMBIGUOUS"
        if hit_tp:
            return "WIN"
        if hit_sl:
            return "LOSS"
    return "OPEN_AT_END"


def run(rates):
    setups = []
    for i in range(2, len(rates)):
        setup = detect_setup(rates[: i + 1])
        if setup is None:
            continue

        entry = classify_first_entry(rates, i, setup)
        row = {
            "direction": setup["direction"],
            "setup_time": int(setup["setup_time"]),
            "before_spike_time": int(setup["before_spike_time"]),
            "spike_time": int(setup["spike_time"]),
            "after_spike_time": int(setup["after_spike_time"]),
            "setup_index": i,
            **entry,
        }

        if entry["status"] == "VALID_ENTRY":
            row["result"] = outcome(
                rates,
                entry["entry_index"],
                setup["direction"],
                entry["entry"],
                setup["sl"],
                entry["tp"],
            )
        else:
            row["result"] = None

        setups.append(row)

    counts = {
        "setup_candidates": len(setups),
        "valid_entries": sum(x["status"] == "VALID_ENTRY" for x in setups),
        "invalid_risk": sum(x["status"] == "INVALID_RISK" for x in setups),
        "no_trigger": sum(x["status"] == "NO_TRIGGER" for x in setups),
        "wins": sum(x["result"] == "WIN" for x in setups),
        "losses": sum(x["result"] == "LOSS" for x in setups),
        "ambiguous": sum(x["result"] == "AMBIGUOUS" for x in setups),
        "open_at_end": sum(x["result"] == "OPEN_AT_END" for x in setups),
    }
    decisive = counts["wins"] + counts["losses"]
    counts["decisive"] = decisive
    counts["win_rate_pct"] = 100.0 * counts["wins"] / decisive if decisive else None
    counts["net_r"] = counts["wins"] - counts["losses"]
    counts["profit_factor_simplified"] = (
        counts["wins"] / counts["losses"] if counts["losses"] else None
    )

    return counts, setups


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
        rates = fetch_rates(symbol, start, end)
        counts, ledger = run(rates)

        report = {
            "status": "COMPLETE",
            "mode": "RESEARCH_FORENSIC_V2_POPULATION",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "requested_symbol": "XAUUSD",
            "resolved_symbol": symbol,
            "period": {"start_utc": start.isoformat(), "end_utc": end.isoformat()},
            "timeframe": "M1",
            "bars": int(len(rates)),
            "first_bar_utc": datetime.fromtimestamp(int(rates[0]["time"]), timezone.utc).isoformat(),
            "last_bar_utc": datetime.fromtimestamp(int(rates[-1]["time"]), timezone.utc).isoformat(),
            "contract": {
                "p_gap_price": 1.0,
                "spike_multiplier": 1.5,
                "max_sl_distance": MAX_SL_DISTANCE,
                "tp_r": TP_R,
                "trigger": "first_post_setup_lower_low_for_buy_higher_high_for_sell",
                "entry": "trigger_candle_low_for_buy_high_for_sell",
                "sl_anchor": "candle_before_spike",
                "session_filter": False,
                "canonical": False,
            },
            "population_counts": counts,
            "reference_target": REFERENCE,
            "deltas_vs_reference": {
                "bars": int(len(rates)) - REFERENCE["bars"],
                "setup_candidates_vs_reference_signals": counts["setup_candidates"] - REFERENCE["signals"],
                "valid_entries_vs_reference_trades": counts["valid_entries"] - REFERENCE["trades"],
                "wins": counts["wins"] - REFERENCE["wins"],
                "losses": counts["losses"] - REFERENCE["losses"],
            },
            "semantic_limits": [
                "This harness exposes the existing V2 detector and first-entry semantics; it does not modify them.",
                "Reference signal/trade ledger is not embedded here, so count deltas identify reconciliation targets but do not prove causality.",
                "OHLC same-bar SL/TP ordering remains ambiguous.",
                "Research-only; no production authorization.",
            ],
            "ledger": ledger,
        }

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = OUT_DIR / f"V2_POPULATION_FORENSIC_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        print(json.dumps({
            "status": report["status"],
            "report": str(path),
            "bars": report["bars"],
            "population_counts": counts,
            "deltas_vs_reference": report["deltas_vs_reference"],
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
