"""Research-only A/B forensic for the V2 XAUUSD overlap-suppression change.

Purpose:
- Replay the SAME MT5 M1 array through the SAME detector.
- Compare the pre-63cf0a1 population rule (used_entry_until suppression)
  with the post-63cf0a1 rule (no overlap suppression).
- Attribute population and outcome differences to that implementation change.

This script never places orders and never changes canonical Strategy A.
It is intentionally separate from the production/forward runner.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from run_sp2l_strategy_a_v2_xauusd_mt5_backtest import (
    MAX_SL_DISTANCE,
    P_GAP_PRICE,
    SPIKE_MULTIPLIER,
    TP_R,
    fetch_rates,
    outcome,
    resolve_xauusd,
)
from sp2l_strategy_a_v2_detector import detect_setup, find_first_entry

import MetaTrader5 as mt5

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "artifacts" / "forensic" / "2026-09-29" / "backtest"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def replay(rates: np.ndarray, suppress_overlap: bool) -> dict:
    rows = []
    used_entry_until = -1

    for i in range(2, len(rates)):
        if suppress_overlap and i <= used_entry_until:
            continue

        setup = detect_setup(rates[: i + 1])
        if setup is None:
            continue

        signal = find_first_entry(rates, i, setup)
        if signal is None:
            continue

        entry_index = int(signal["entry_index"])
        result, exit_index, r, reason = outcome(rates, entry_index, signal)

        rows.append({
            "setup_index": i,
            "setup_time": int(signal["setup_time"]),
            "direction": signal["direction"],
            "entry_index": entry_index,
            "entry_time": int(signal["entry_time"]),
            "entry": float(signal["entry"]),
            "sl": float(signal["sl"]),
            "tp": float(signal["tp"]),
            "result": result,
            "r": r,
            "exit_index": exit_index,
            "exit_reason": reason,
        })

        if suppress_overlap:
            used_entry_until = entry_index

    wins = sum(x["result"] == "WIN" for x in rows)
    losses = sum(x["result"] == "LOSS" for x in rows)
    ambiguous = sum(x["result"] == "AMBIGUOUS" for x in rows)
    open_end = sum(x["result"] == "OPEN_AT_END" for x in rows)
    decisive = wins + losses

    return {
        "suppress_overlap": suppress_overlap,
        "signals": len(rows),
        "wins": wins,
        "losses": losses,
        "ambiguous": ambiguous,
        "open_at_end": open_end,
        "decisive": decisive,
        "win_rate_pct": 100.0 * wins / decisive if decisive else None,
        "net_r": wins - losses,
        "profit_factor_simplified": wins / losses if losses else None,
        "rows": rows,
    }


def compare(old: dict, new: dict) -> dict:
    old_keys = {(x["setup_index"], x["entry_index"], x["direction"]) for x in old["rows"]}
    new_keys = {(x["setup_index"], x["entry_index"], x["direction"]) for x in new["rows"]}

    suppressed = sorted(old_keys - new_keys)
    # New-only should normally be empty because suppression only removes candidates.
    new_only = sorted(new_keys - old_keys)

    old_by_key = {(x["setup_index"], x["entry_index"], x["direction"]): x for x in old["rows"]}
    new_by_key = {(x["setup_index"], x["entry_index"], x["direction"]): x for x in new["rows"]}

    suppressed_rows = [
        old_by_key[k]
        for k in suppressed
    ]

    common = sorted(old_keys & new_keys)
    outcome_changed = []
    for k in common:
        a, b = old_by_key[k], new_by_key[k]
        if (a["result"], a["r"]) != (b["result"], b["r"]):
            outcome_changed.append({
                "key": k,
                "suppressed_version": {"result": a["result"], "r": a["r"]},
                "unsuppressed_version": {"result": b["result"], "r": b["r"]},
            })

    return {
        "signal_delta": new["signals"] - old["signals"],
        "decisive_delta": new["decisive"] - old["decisive"],
        "win_delta": new["wins"] - old["wins"],
        "loss_delta": new["losses"] - old["losses"],
        "net_r_delta": new["net_r"] - old["net_r"],
        "win_rate_delta_pct_points": (
            new["win_rate_pct"] - old["win_rate_pct"]
            if old["win_rate_pct"] is not None and new["win_rate_pct"] is not None
            else None
        ),
        "suppressed_by_old_rule": len(suppressed),
        "new_only_under_unsuppressed_rule": len(new_only),
        "common_signal_count": len(common),
        "outcome_changed_on_common_signals": len(outcome_changed),
        "suppressed_signal_rows": suppressed_rows,
        "unexpected_new_only_keys": new_only,
        "outcome_changed_rows": outcome_changed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2026-06-28T00:00:00Z")
    parser.add_argument("--end", default="2026-09-25T00:00:00Z")
    parser.add_argument("--mt5-path", default=None)
    args = parser.parse_args()

    initialized = (
        mt5.initialize(path=str(args.mt5_path))
        if args.mt5_path
        else mt5.initialize()
    )
    if not initialized:
        print(json.dumps({
            "status": "MT5_INIT_FAILED",
            "error": mt5.last_error(),
        }, indent=2))
        return 2

    try:
        symbol = resolve_xauusd()
        start = datetime.fromisoformat(args.start.replace("Z", "+00:00"))
        end = datetime.fromisoformat(args.end.replace("Z", "+00:00"))
        rates = fetch_rates(symbol, start, end)

        old = replay(rates, suppress_overlap=True)
        new = replay(rates, suppress_overlap=False)
        diff = compare(old, new)

        report = {
            "status": "COMPLETE",
            "mode": "RESEARCH_ONLY_V2_OVERLAP_SUPPRESSION_AB",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "resolved_symbol": symbol,
            "period": {
                "start_utc": start.isoformat(),
                "end_utc": end.isoformat(),
            },
            "bars": int(len(rates)),
            "geometry_constants": {
                "p_gap_price": P_GAP_PRICE,
                "spike_multiplier": SPIKE_MULTIPLIER,
                "max_sl_distance": MAX_SL_DISTANCE,
                "tp_r": TP_R,
            },
            "comparison": {
                "A_pre_63cf0a1": {
                    "rule": "used_entry_until suppression",
                    "commit": "482ab68a5ae9aaf46e80e021dc8652578af334fc",
                    "summary": {k: v for k, v in old.items() if k != "rows"},
                },
                "B_post_63cf0a1": {
                    "rule": "no overlap suppression",
                    "commit": "63cf0a11efa548472f45f3db36a0fa87ab25c3ea",
                    "summary": {k: v for k, v in new.items() if k != "rows"},
                },
                "attribution": diff,
            },
            "semantic_limits": [
                "Same MT5 rates and same detector are used for both sides.",
                "The only intended population difference is the overlap-suppression branch.",
                "This is forensic attribution, not a canonical Strategy A decision.",
                "No orders are placed.",
            ],
        }

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = OUT_DIR / f"V2_OVERLAP_SUPPRESSION_AB_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        print(json.dumps({
            "status": report["status"],
            "report": str(path),
            "bars": len(rates),
            "pre_63cf0a1": report["comparison"]["A_pre_63cf0a1"]["summary"],
            "post_63cf0a1": report["comparison"]["B_post_63cf0a1"]["summary"],
            "attribution": {
                "signal_delta": diff["signal_delta"],
                "decisive_delta": diff["decisive_delta"],
                "win_delta": diff["win_delta"],
                "loss_delta": diff["loss_delta"],
                "net_r_delta": diff["net_r_delta"],
                "win_rate_delta_pct_points": diff["win_rate_delta_pct_points"],
                "suppressed_by_old_rule": diff["suppressed_by_old_rule"],
                "new_only_under_unsuppressed_rule": diff["new_only_under_unsuppressed_rule"],
                "outcome_changed_on_common_signals": diff["outcome_changed_on_common_signals"],
            },
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
