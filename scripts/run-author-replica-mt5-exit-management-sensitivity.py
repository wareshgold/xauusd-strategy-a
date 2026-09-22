"""Research-only exit-management sensitivity for the SP2L candidate.

Candidate execution variants only; none are canonical:
- NO_MANAGEMENT: fixed SL/TP.
- BREAKEVEN_1R: after a completed bar reaches +1R, move SL to entry for subsequent bars.
- TRAIL_PREV_BAR_1R: after +1R activation, trail SL to the most recent completed
  candle extreme (BUY previous low / SELL previous high), only in the favorable
  direction.

Intrabar ordering is unresolved in the source, so if a bar touches both the active
SL and TP it is recorded as AMBIGUOUS. Management changes are applied only after
a completed bar, preventing look-ahead within that bar.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
N = int(os.getenv("BARS", "10000"))
P_GAP = float(os.getenv("PGAP_PRICE", "1"))
SPIKE_MULT = float(os.getenv("SPIKE_MULTIPLIER", "1.5"))
MAX_SL = float(os.getenv("MAX_SL_PRICE", "10"))
TP_VALUES = [float(x) for x in os.getenv("TP_R_VALUES", "0.75,1,1.25,1.5,2").split(",") if x.strip()]
ACTIVATE_R = float(os.getenv("MANAGEMENT_ACTIVATE_R", "1"))
DEFAULT_ENDS = [
    "2026-09-17T10:45:00+00:00",
    "2026-09-05T10:45:00+00:00",
    "2026-08-24T10:45:00+00:00",
    "2026-08-12T10:45:00+00:00",
    "2026-07-31T10:45:00+00:00",
    "2026-07-19T10:45:00+00:00",
]
ENDS = [x.strip() for x in os.getenv("SNAPSHOT_ENDS_UTC", ",".join(DEFAULT_ENDS)).split(",") if x.strip()]
MODES = ("NO_MANAGEMENT", "BREAKEVEN_1R", "TRAIL_PREV_BAR_1R")


def body(c):
    return abs(c["close"] - c["open"])


def signal(c, i):
    a, s, corr, trig = c[i-4], c[i-3], c[i-2], c[i-1]
    buy = (
        trig["low"] < corr["low"]
        and corr["close"] > s["close"] and corr["open"] > s["open"]
        and s["open"] > a["open"]
        and corr["close"] > corr["open"] and s["close"] > s["open"] and a["close"] > a["open"]
        and corr["low"] > a["high"] + P_GAP
        and body(s) > SPIKE_MULT * body(corr)
        and body(s) > SPIKE_MULT * body(a)
        and body(s) > SPIKE_MULT * body(trig)
    )
    sell = (
        trig["high"] > corr["high"]
        and corr["close"] < s["close"] and corr["open"] < s["open"]
        and s["close"] < a["close"] and s["open"] < a["open"]
        and corr["close"] < corr["open"] and s["close"] < s["open"] and a["close"] < a["open"]
        and corr["high"] < a["low"] - P_GAP
        and body(s) > SPIKE_MULT * body(corr)
        and body(s) > SPIKE_MULT * body(a)
        and body(s) > SPIKE_MULT * body(trig)
    )
    if buy:
        return "BUY", trig["low"], a["low"]
    if sell:
        return "SELL", trig["high"], a["high"]
    return None


def collect_signals(c):
    out = []
    for i in range(4, len(c)):
        s = signal(c, i)
        if not s:
            continue
        direction, entry, sl = s
        risk = abs(entry - sl)
        if risk <= 0 or risk > MAX_SL:
            continue
        out.append({"index": i, "direction": direction, "entry": entry, "sl": sl, "risk": risk, "time": c[i-1]["time"]})
    return out


def evaluate(c, sig, tp_r, mode):
    entry, risk, direction = sig["entry"], sig["risk"], sig["direction"]
    tp = entry + tp_r * risk if direction == "BUY" else entry - tp_r * risk
    active_sl = sig["sl"]
    activated = False

    for j in range(sig["index"] + 1, len(c)):
        x = c[j]
        hit_sl = x["low"] <= active_sl if direction == "BUY" else x["high"] >= active_sl
        hit_tp = x["high"] >= tp if direction == "BUY" else x["low"] <= tp

        if hit_sl and hit_tp:
            return "AMBIGUOUS"
        if hit_sl:
            return "LOSS"
        if hit_tp:
            return "WIN"

        # Management is applied only after this completed bar; the new stop is
        # therefore active from the next bar onward.
        favorable = (x["high"] >= entry + ACTIVATE_R * risk) if direction == "BUY" else (x["low"] <= entry - ACTIVATE_R * risk)
        if not activated and favorable:
            activated = True
            if mode == "BREAKEVEN_1R":
                active_sl = entry
            elif mode == "TRAIL_PREV_BAR_1R":
                candidate = x["low"] if direction == "BUY" else x["high"]
                if direction == "BUY":
                    active_sl = max(active_sl, candidate)
                else:
                    active_sl = min(active_sl, candidate)
        elif activated and mode == "TRAIL_PREV_BAR_1R":
            candidate = x["low"] if direction == "BUY" else x["high"]
            if direction == "BUY":
                active_sl = max(active_sl, candidate)
            else:
                active_sl = min(active_sl, candidate)

    return "UNRESOLVED"


def evaluate_mode(c, signals, tp_r, mode):
    counts = {"WIN": 0, "LOSS": 0, "AMBIGUOUS": 0, "UNRESOLVED": 0}
    for sig in signals:
        counts[evaluate(c, sig, tp_r, mode)] += 1
    wins, losses = counts["WIN"], counts["LOSS"]
    decisive = wins + losses
    total_r = wins * tp_r - losses
    return {
        "mode": mode,
        "tpR": tp_r,
        "signals": len(signals),
        "wins": wins,
        "losses": losses,
        "ambiguous": counts["AMBIGUOUS"],
        "unresolved": counts["UNRESOLVED"],
        "decisive": decisive,
        "win_rate_decisive": wins / decisive if decisive else None,
        "totalR_decisive": total_r,
        "profit_factor": (wins * tp_r / losses) if losses else None,
        "expectancy_R_per_decisive": total_r / decisive if decisive else None,
    }


def run_window(end_dt):
    rates = mt5.copy_rates_from(SYMBOL, mt5.TIMEFRAME_M1, end_dt, N)
    if rates is None or len(rates) == 0:
        return {"snapshot_end_utc": end_dt.isoformat(), "error": str(mt5.last_error())}
    c = [{"time": int(r[0]), "open": float(r[1]), "high": float(r[2]), "low": float(r[3]), "close": float(r[4])} for r in rates]
    signals = collect_signals(c)
    return {
        "snapshot_end_utc": end_dt.isoformat(),
        "returned_bars": len(c),
        "first_utc": datetime.fromtimestamp(c[0]["time"], timezone.utc).isoformat(),
        "last_utc": datetime.fromtimestamp(c[-1]["time"], timezone.utc).isoformat(),
        "signal_count": len(signals),
        "results": [evaluate_mode(c, signals, tp_r, mode) for mode in MODES for tp_r in TP_VALUES],
    }


def aggregate(snapshots):
    rows = []
    for mode in MODES:
        for tp_r in TP_VALUES:
            agg = {"mode": mode, "tpR": tp_r, "signals": 0, "wins": 0, "losses": 0, "ambiguous": 0, "unresolved": 0}
            for snap in snapshots:
                if "results" not in snap:
                    continue
                row = next(x for x in snap["results"] if x["mode"] == mode and x["tpR"] == tp_r)
                for k in ("signals", "wins", "losses", "ambiguous", "unresolved"):
                    agg[k] += row[k]
            decisive = agg["wins"] + agg["losses"]
            agg["decisive"] = decisive
            agg["win_rate_decisive"] = agg["wins"] / decisive if decisive else None
            agg["totalR_decisive"] = agg["wins"] * tp_r - agg["losses"]
            agg["profit_factor"] = agg["wins"] * tp_r / agg["losses"] if agg["losses"] else None
            agg["expectancy_R_per_decisive"] = agg["totalR_decisive"] / decisive if decisive else None
            rows.append(agg)
    return rows


def main():
    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"symbol_select failed: {mt5.last_error()}")
        snapshots = []
        for raw in ENDS:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)
            snapshots.append(run_window(dt))

        result = {
            "research_only": True,
            "mode": "EXIT_MANAGEMENT_SENSITIVITY",
            "source": "MetaTrader5.copy_rates_from",
            "symbol": SYMBOL,
            "timeframe": "M1",
            "requested_bars": N,
            "config": {
                "pGapPrice": P_GAP,
                "spikeMultiplier": SPIKE_MULT,
                "maxSlPrice": MAX_SL,
                "tpR_values": TP_VALUES,
                "managementActivationR": ACTIVATE_R,
                "management_modes": list(MODES),
                "canonical": False,
                "source_confirmed": False,
                "intrabar_ordering": "AMBIGUOUS_IF_SL_AND_TP_TOUCH_SAME_BAR",
            },
            "snapshots": snapshots,
            "aggregate": aggregate(snapshots),
        }
        print(json.dumps(result, indent=2))
        out = Path("artifacts") / "author-replica-mt5-exit-management-sensitivity.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\nWrote {out}")
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
