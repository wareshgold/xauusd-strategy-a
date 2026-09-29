"""Research-only V2 reference-population compatibility replay.

Reconstructs the historical non-overlap suppression used by the 2026-09-28
V2 reference runner. It does NOT change the shared detector or canonical rules.

Historical compatibility behavior:
- evaluate completed three-candle setups;
- skip a setup while its prior valid entry is still active;
- after accepting an entry, suppress setup indices <= that entry index.

This exists only to test whether the old reference population can be reproduced.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import MetaTrader5 as mt5

from mt5_terminal_resolver import find_mt5_terminal
from run_sp2l_strategy_a_v2_xauusd_mt5_backtest import fetch_rates, resolve_xauusd
from sp2l_strategy_a_v2_detector import detect_setup, find_first_entry


REFERENCE = {
    "bars": 87673,
    "signals": 1472,
    "trades": 1356,
    "wins": 836,
    "losses": 520,
}


def outcome(candles, entry_index: int, signal: dict) -> str:
    direction = signal["direction"]
    sl = float(signal["sl"])
    tp = float(signal["tp"])
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
    raw_setup_candidates = 0
    accepted = []
    suppressed = 0
    used_entry_until = -1

    for i in range(2, len(rates)):
        setup = detect_setup(rates[: i + 1])
        if setup is None:
            continue

        raw_setup_candidates += 1

        # Historical reference behavior from commit
        # 482ab68a5ae9aaf46e80e021dc8652578af334fc.
        if i <= used_entry_until:
            suppressed += 1
            continue

        signal = find_first_entry(rates, i, setup)
        if signal is None:
            continue

        result = outcome(rates, int(signal["entry_index"]), signal)
        accepted.append({
            "setup_index": i,
            "entry_index": int(signal["entry_index"]),
            "direction": signal["direction"],
            "result": result,
        })
        used_entry_until = int(signal["entry_index"])

    wins = sum(x["result"] == "WIN" for x in accepted)
    losses = sum(x["result"] == "LOSS" for x in accepted)
    ambiguous = sum(x["result"] == "AMBIGUOUS" for x in accepted)
    open_at_end = sum(x["result"] == "OPEN_AT_END" for x in accepted)
    decisive = wins + losses

    return {
        "raw_setup_candidates": raw_setup_candidates,
        "suppressed_by_overlap": suppressed,
        "accepted_valid_entries": len(accepted),
        "wins": wins,
        "losses": losses,
        "ambiguous": ambiguous,
        "open_at_end": open_at_end,
        "decisive": decisive,
        "win_rate_pct": 100.0 * wins / decisive if decisive else None,
        "net_r": wins - losses,
        "reference": REFERENCE,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2026-06-29T01:00:00Z")
    parser.add_argument("--end", default="2026-09-24T20:30:00Z")
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
        result = run(rates)
        report = {
            "status": "COMPLETE",
            "mode": "RESEARCH_ONLY_V2_REFERENCE_POPULATION_COMPAT",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "resolved_symbol": symbol,
            "period": {
                "start_utc": start.isoformat(),
                "end_utc": end.isoformat(),
            },
            "bars": int(len(rates)),
            "first_bar_utc": datetime.fromtimestamp(int(rates[0]["time"]), timezone.utc).isoformat(),
            "last_bar_utc": datetime.fromtimestamp(int(rates[-1]["time"]), timezone.utc).isoformat(),
            "contract": {
                "p_gap_price": 1.0,
                "spike_multiplier": 1.5,
                "max_sl_distance": 10.0,
                "tp_r": 1.0,
                "overlap_suppression": "historical_reference_used_entry_until",
                "canonical": False,
            },
            "results": result,
            "semantic_limits": [
                "Compatibility reconstruction only; overlap suppression is not promoted to canonical Strategy A.",
                "The historical reference ledger is not embedded; matching aggregate counts is necessary but not sufficient for exact provenance.",
                "Same-bar SL/TP is quarantined as AMBIGUOUS.",
            ],
        }
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = f"artifacts/forensic/2026-09-29/V2_REFERENCE_POPULATION_COMPAT_{stamp}.json"
        import pathlib
        out = pathlib.Path(__file__).resolve().parents[1] / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({
            "status": report["status"],
            "report": str(out),
            "bars": report["bars"],
            "results": result,
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
