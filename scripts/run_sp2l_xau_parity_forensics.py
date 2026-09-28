"""Research-only XAUUSD parity forensic: old API candidate vs shared detector.

This script does not define or promote canonical Strategy A rules. It fetches one
common M1 dataset with copy_rates_range(), then applies both research candidates
to the exact same bars so data acquisition cannot explain their divergence.

It reports:
- old-only/current-only/common signal timestamps
- common-signal SL anchor differences
- old outcome vs current pending-fill outcome differences
- the exact OHLC window for first signal-geometry divergences
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

from mt5_terminal_resolver import find_mt5_terminal
from sp2l_author_replica_detector import detect as current_detect

SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
P_GAP = float(os.getenv("PGAP_PRICE", "1"))
SPIKE_MULT = float(os.getenv("SPIKE_MULTIPLIER", "1.5"))
MAX_SL = float(os.getenv("MAX_SL_PRICE", "10"))
TP_R = float(os.getenv("TP_R", "1"))


def iso(ts: int) -> str:
    return datetime.fromtimestamp(int(ts), timezone.utc).isoformat()


def body(c):
    return abs(c["close"] - c["open"])


def old_signal(candles, i):
    a, s, corr, trig = candles[i - 4], candles[i - 3], candles[i - 2], candles[i - 1]
    buy = (
        trig["low"] < corr["low"]
        and corr["close"] > s["close"]
        and corr["open"] > s["open"]
        and s["open"] > a["open"]
        and corr["close"] > corr["open"]
        and s["close"] > s["open"]
        and a["close"] > a["open"]
        and corr["low"] > a["high"] + P_GAP
        and body(s) > SPIKE_MULT * body(corr)
        and body(s) > SPIKE_MULT * body(a)
        and body(s) > SPIKE_MULT * body(trig)
    )
    sell = (
        trig["high"] > corr["high"]
        and corr["close"] < s["close"]
        and corr["open"] < s["open"]
        and s["close"] < a["close"]
        and s["open"] < a["open"]
        and corr["close"] < corr["open"]
        and s["close"] < s["open"]
        and a["close"] < a["open"]
        and corr["high"] < a["low"] - P_GAP
        and body(s) > SPIKE_MULT * body(corr)
        and body(s) > SPIKE_MULT * body(a)
        and body(s) > SPIKE_MULT * body(trig)
    )
    if buy == sell:
        return None
    if buy:
        entry, sl = float(trig["low"]), float(a["low"])
        risk = entry - sl
        if 0 < risk <= MAX_SL:
            return {"direction": "BUY", "signal_time": int(trig["time"]),
                    "entry": entry, "sl": sl, "risk": risk,
                    "tp": entry + TP_R * risk}
    if sell:
        entry, sl = float(trig["high"]), float(a["high"])
        risk = sl - entry
        if 0 < risk <= MAX_SL:
            return {"direction": "SELL", "signal_time": int(trig["time"]),
                    "entry": entry, "sl": sl, "risk": risk,
                    "tp": entry - TP_R * risk}
    return None


def current_signal(candles, i):
    # Shared detector expects the final element to be the forming/current bar.
    # The same four completed bars are therefore candles[i-4:i].
    return current_detect(
        candles[: i + 1],
        p_gap_price=P_GAP,
        spike_multiplier=SPIKE_MULT,
        max_sl_distance=MAX_SL,
        tp_r=TP_R,
    )


def old_outcome(candles, signal, signal_index):
    for j in range(signal_index + 1, len(candles)):
        c = candles[j]
        if signal["direction"] == "BUY":
            hit_sl, hit_tp = c["low"] <= signal["sl"], c["high"] >= signal["tp"]
        else:
            hit_sl, hit_tp = c["high"] >= signal["sl"], c["low"] <= signal["tp"]
        if hit_sl and hit_tp:
            return "AMBIGUOUS", j
        if hit_sl:
            return "LOSS", j
        if hit_tp:
            return "WIN", j
    return "OPEN_AT_END", None


def current_outcome(candles, signal, signal_index):
    direction = signal["direction"]
    entry, sl, tp = signal["entry"], signal["sl"], signal["tp"]
    for j in range(signal_index + 1, len(candles)):
        c = candles[j]
        if direction == "BUY":
            touched_entry = c["low"] <= entry
            if not touched_entry:
                continue
            hit_sl, hit_tp = c["low"] <= sl, c["high"] >= tp
        else:
            touched_entry = c["high"] >= entry
            if not touched_entry:
                continue
            hit_sl, hit_tp = c["high"] >= sl, c["low"] <= tp
        if hit_sl and hit_tp:
            return "AMBIGUOUS", j
        if hit_tp:
            return "AMBIGUOUS", j
        if hit_sl:
            return "LOSS", j
        for k in range(j + 1, len(candles)):
            n = candles[k]
            if direction == "BUY":
                hit_sl, hit_tp = n["low"] <= sl, n["high"] >= tp
            else:
                hit_sl, hit_tp = n["high"] >= sl, n["low"] <= tp
            if hit_sl and hit_tp:
                return "AMBIGUOUS", k
            if hit_tp:
                return "WIN", k
            if hit_sl:
                return "LOSS", k
    return "OPEN_AT_END", None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--mt5-path", default=None)
    p.add_argument("--output", default="artifacts/forensic/2026-09-28/SP2L_XAU_PARITY_FORENSICS.json")
    args = p.parse_args()

    start = datetime.fromisoformat(args.start.replace("Z", "+00:00")).astimezone(timezone.utc)
    end = datetime.fromisoformat(args.end.replace("Z", "+00:00")).astimezone(timezone.utc)

    if args.mt5_path:
        ok = mt5.initialize(path=str(Path(args.mt5_path)))
    else:
        ok = mt5.initialize()
    if not ok:
        terminal = find_mt5_terminal()
        if terminal is None or not mt5.initialize(path=str(terminal)):
            raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"symbol_select failed: {mt5.last_error()}")

        rates = mt5.copy_rates_range(SYMBOL, mt5.TIMEFRAME_M1, start, end)
        if rates is None or len(rates) == 0:
            raise SystemExit(f"copy_rates_range failed: {mt5.last_error()}")

        raw = [
            {"time": int(r[0]), "open": float(r[1]), "high": float(r[2]),
             "low": float(r[3]), "close": float(r[4])}
            for r in rates
        ]
        candles = sorted(raw, key=lambda x: x["time"])
        seen = set()
        candles = [c for c in candles if not (c["time"] in seen or seen.add(c["time"]))]

        old = {}
        current = {}
        old_index = {}
        current_index = {}

        for i in range(4, len(candles) - 1):
            o = old_signal(candles, i)
            if o:
                key = (o["signal_time"], o["direction"])
                old[key] = o
                old_index[key] = i
            c = current_signal(candles, i)
            if c:
                key = (c["signal_time"], c["direction"])
                current[key] = c
                current_index[key] = i

        old_keys, current_keys = set(old), set(current)
        common_keys = old_keys & current_keys
        old_only = sorted(old_keys - current_keys)
        current_only = sorted(current_keys - old_keys)

        sl_diffs = []
        outcome_diffs = []
        for key in sorted(common_keys):
            o, c = old[key], current[key]
            if abs(o["sl"] - c["sl"]) > 1e-9:
                sl_diffs.append({
                    "signal_time": iso(key[0]), "direction": key[1],
                    "old_sl": o["sl"], "current_sl": c["sl"],
                    "entry": o["entry"], "old_risk": o["risk"], "current_risk": c["risk"],
                })
            oo, oj = old_outcome(candles, o, old_index[key])
            co, cj = current_outcome(candles, c, current_index[key])
            if oo != co:
                outcome_diffs.append({
                    "signal_time": iso(key[0]), "direction": key[1],
                    "old_outcome": oo, "current_outcome": co,
                    "old_exit_time": iso(candles[oj]["time"]) if oj is not None else None,
                    "current_exit_time": iso(candles[cj]["time"]) if cj is not None else None,
                })

        def key_rows(keys):
            return [
                {"signal_time": iso(k[0]), "direction": k[1], **(old.get(k) or current.get(k))}
                for k in sorted(keys)
            ]


        # Counterfactual decomposition on the COMMON signal set:
        # hold signal geometry and entry fixed, then vary only SL anchor and
        # outcome semantics. Descriptive forensic analysis only.
        def outcome_old_semantics(signal, signal_index):
            return old_outcome(candles, signal, signal_index)[0]

        def outcome_pending_semantics(signal, signal_index):
            return current_outcome(candles, signal, signal_index)[0]

        anchor_variants = {}
        for key in sorted(common_keys):
            o, c = old[key], current[key]
            entry = o["entry"]
            direction = o["direction"]
            variants = {
                "OLD_SL_OLD_OUTCOME": o,
                "OLD_SL_PENDING_OUTCOME": {
                    **o,
                    "risk": abs(entry - o["sl"]),
                    "tp": entry + TP_R * abs(entry - o["sl"]) if direction == "BUY"
                    else entry - TP_R * abs(entry - o["sl"]),
                },
                "CURRENT_SL_OLD_OUTCOME": {
                    **c,
                    "risk": abs(entry - c["sl"]),
                    "tp": entry + TP_R * abs(entry - c["sl"]) if direction == "BUY"
                    else entry - TP_R * abs(entry - c["sl"]),
                },
                "CURRENT_SL_PENDING_OUTCOME": c,
            }
            for name, sig in variants.items():
                signal_index = old_index[key]
                if name.endswith("OLD_OUTCOME"):
                    outcome = outcome_old_semantics(sig, signal_index)
                else:
                    outcome = outcome_pending_semantics(sig, signal_index)
                anchor_variants.setdefault(name, []).append(outcome)

        def summarize_outcomes(rows):
            wins = rows.count("WIN")
            losses = rows.count("LOSS")
            ambiguous = rows.count("AMBIGUOUS")
            opened = rows.count("OPEN_AT_END")
            decisive = wins + losses
            return {
                "signals": len(rows),
                "wins": wins,
                "losses": losses,
                "ambiguous": ambiguous,
                "open_at_end": opened,
                "decisive": decisive,
                "win_rate_decisive": wins / decisive if decisive else None,
                "totalR_decisive": wins - losses,
            }

        counterfactual_matrix = {
            name: summarize_outcomes(rows)
            for name, rows in anchor_variants.items()
        }

        sl_axis_delta = {
            "old_outcome": {
                "from": "OLD_SL_OLD_OUTCOME",
                "to": "CURRENT_SL_OLD_OUTCOME",
                "win_delta": counterfactual_matrix["CURRENT_SL_OLD_OUTCOME"]["wins"] - counterfactual_matrix["OLD_SL_OLD_OUTCOME"]["wins"],
                "loss_delta": counterfactual_matrix["CURRENT_SL_OLD_OUTCOME"]["losses"] - counterfactual_matrix["OLD_SL_OLD_OUTCOME"]["losses"],
                "wr_delta": counterfactual_matrix["CURRENT_SL_OLD_OUTCOME"]["win_rate_decisive"] - counterfactual_matrix["OLD_SL_OLD_OUTCOME"]["win_rate_decisive"],
                "totalR_delta": counterfactual_matrix["CURRENT_SL_OLD_OUTCOME"]["totalR_decisive"] - counterfactual_matrix["OLD_SL_OLD_OUTCOME"]["totalR_decisive"],
            },
            "pending_vs_old_outcome_with_old_sl": {
                "from": "OLD_SL_OLD_OUTCOME",
                "to": "OLD_SL_PENDING_OUTCOME",
                "win_delta": counterfactual_matrix["OLD_SL_PENDING_OUTCOME"]["wins"] - counterfactual_matrix["OLD_SL_OLD_OUTCOME"]["wins"],
                "loss_delta": counterfactual_matrix["OLD_SL_PENDING_OUTCOME"]["losses"] - counterfactual_matrix["OLD_SL_OLD_OUTCOME"]["losses"],
                "wr_delta": counterfactual_matrix["OLD_SL_PENDING_OUTCOME"]["win_rate_decisive"] - counterfactual_matrix["OLD_SL_OLD_OUTCOME"]["win_rate_decisive"],
                "totalR_delta": counterfactual_matrix["OLD_SL_PENDING_OUTCOME"]["totalR_decisive"] - counterfactual_matrix["OLD_SL_OLD_OUTCOME"]["totalR_decisive"],
            },
        }

        result = {
            "research_only": True,
            "source": "ONE_COMMON_COPY_RATES_RANGE_DATASET",
            "config": {"pGapPrice": P_GAP, "spikeMultiplier": SPIKE_MULT,
                       "maxSlPrice": MAX_SL, "tpR": TP_R},
            "bars": len(candles),
            "first_bar_utc": iso(candles[0]["time"]),
            "last_bar_utc": iso(candles[-1]["time"]),
            "old_api_candidate": {
                "signals": len(old), "old_only_vs_current": len(old_only),
                "common": len(common_keys)
            },
            "shared_detector_candidate": {
                "signals": len(current), "current_only_vs_old": len(current_only),
                "common": len(common_keys)
            },
            "counterfactual_decomposition": {
                "matrix": counterfactual_matrix,
                "axis_deltas": sl_axis_delta,
            },
            "divergence": {
                "old_only_signals": key_rows(old_only),
                "current_only_signals": key_rows(current_only),
                "common_signal_sl_differences": sl_diffs,
                "common_signal_outcome_differences": outcome_diffs,
            },
            "first_geometry_divergences": {
                "old_only": key_rows(old_only[:10]),
                "current_only": key_rows(current_only[:10]),
            },
            "notes": [
                "Old candidate uses spike-start candle a as SL anchor.",
                "Shared detector uses spike candle as SL anchor.",
                "Old BUY does not require spike.close > a.close; shared detector does.",
                "Outcome comparison is descriptive only; neither semantics is canonical.",
                "Counterfactual matrix holds the common signals and their entry fixed, then varies only SL anchor and outcome semantics.",
                "The counterfactual matrix is diagnostic and must not be used to select or promote a canonical rule."
            ],
        }

        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({
            "status": "COMPLETE",
            "bars": len(candles),
            "old_signals": len(old),
            "current_signals": len(current),
            "common": len(common_keys),
            "old_only": len(old_only),
            "current_only": len(current_only),
            "sl_differences": len(sl_diffs),
            "outcome_differences": len(outcome_diffs),
            "report": str(out),
        }, indent=2))
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
