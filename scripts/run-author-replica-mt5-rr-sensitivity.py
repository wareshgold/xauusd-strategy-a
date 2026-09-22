"""Research-only RR sensitivity for the author-associated SP2L candidate.

Keeps the current signal geometry and SL candidate fixed, and varies only TP_R.
This is descriptive research and does not define or promote canonical Strategy A
exit rules. It intentionally has no trailing-stop or breakeven logic.
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
DEFAULT_ENDS = [
    "2026-09-17T10:45:00+00:00",
    "2026-09-05T10:45:00+00:00",
    "2026-08-24T10:45:00+00:00",
    "2026-08-12T10:45:00+00:00",
    "2026-07-31T10:45:00+00:00",
    "2026-07-19T10:45:00+00:00",
]
ENDS = [x.strip() for x in os.getenv("SNAPSHOT_ENDS_UTC", ",".join(DEFAULT_ENDS)).split(",") if x.strip()]


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
        out.append({
            "index": i,
            "direction": direction,
            "entry": entry,
            "sl": sl,
            "risk": risk,
            "time": c[i-1]["time"],
        })
    return out


def evaluate(c, signals, tp_r):
    wins = losses = ambiguous = unresolved = 0
    for sig in signals:
        tp = (
            sig["entry"] + tp_r * sig["risk"]
            if sig["direction"] == "BUY"
            else sig["entry"] - tp_r * sig["risk"]
        )
        outcome = None
        for j in range(sig["index"] + 1, len(c)):
            x = c[j]
            hit_sl = x["low"] <= sig["sl"] if sig["direction"] == "BUY" else x["high"] >= sig["sl"]
            hit_tp = x["high"] >= tp if sig["direction"] == "BUY" else x["low"] <= tp
            if hit_sl and hit_tp:
                outcome = "AMBIGUOUS"
                break
            if hit_sl:
                outcome = "LOSS"
                break
            if hit_tp:
                outcome = "WIN"
                break
        if outcome == "WIN":
            wins += 1
        elif outcome == "LOSS":
            losses += 1
        elif outcome == "AMBIGUOUS":
            ambiguous += 1
        else:
            unresolved += 1

    decisive = wins + losses
    total_r = wins * tp_r - losses
    gross_profit = wins * tp_r
    gross_loss = losses
    return {
        "tpR": tp_r,
        "signals": len(signals),
        "wins": wins,
        "losses": losses,
        "ambiguous": ambiguous,
        "unresolved": unresolved,
        "decisive": decisive,
        "win_rate_decisive": wins / decisive if decisive else None,
        "totalR_decisive": total_r,
        "profit_factor": gross_profit / gross_loss if gross_loss else None,
        "expectancy_R_per_decisive": total_r / decisive if decisive else None,
    }


def run_window(end_dt):
    rates = mt5.copy_rates_from(SYMBOL, mt5.TIMEFRAME_M1, end_dt, N)
    if rates is None or len(rates) == 0:
        return {"snapshot_end_utc": end_dt.isoformat(), "error": str(mt5.last_error())}
    c = [
        {"time": int(r[0]), "open": float(r[1]), "high": float(r[2]), "low": float(r[3]), "close": float(r[4])}
        for r in rates
    ]
    signals = collect_signals(c)
    return {
        "snapshot_end_utc": end_dt.isoformat(),
        "returned_bars": len(c),
        "first_utc": datetime.fromtimestamp(c[0]["time"], timezone.utc).isoformat(),
        "last_utc": datetime.fromtimestamp(c[-1]["time"], timezone.utc).isoformat(),
        "signal_count": len(signals),
        "results": [evaluate(c, signals, tp_r) for tp_r in TP_VALUES],
    }


def aggregate(snapshots):
    rows = []
    for tp_r in TP_VALUES:
        agg = {"tpR": tp_r, "signals": 0, "wins": 0, "losses": 0, "ambiguous": 0, "unresolved": 0}
        for snap in snapshots:
            if "results" not in snap:
                continue
            row = next(x for x in snap["results"] if x["tpR"] == tp_r)
            for k in ("signals", "wins", "losses", "ambiguous", "unresolved"):
                agg[k] += row[k]
        decisive = agg["wins"] + agg["losses"]
        agg["decisive"] = decisive
        agg["win_rate_decisive"] = agg["wins"] / decisive if decisive else None
        agg["totalR_decisive"] = agg["wins"] * tp_r - agg["losses"]
        agg["profit_factor"] = (agg["wins"] * tp_r / agg["losses"]) if agg["losses"] else None
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
            "mode": "RR_SENSITIVITY_NO_TRAILING",
            "source": "MetaTrader5.copy_rates_from",
            "symbol": SYMBOL,
            "timeframe": "M1",
            "requested_bars": N,
            "config": {
                "pGapPrice": P_GAP,
                "spikeMultiplier": SPIKE_MULT,
                "maxSlPrice": MAX_SL,
                "tpR_values": TP_VALUES,
                "trailing_stop": False,
                "breakeven": False,
            },
            "snapshots": snapshots,
            "aggregate": aggregate(snapshots),
        }
        print(json.dumps(result, indent=2))
        out = Path("artifacts") / "author-replica-mt5-rr-sensitivity.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\nWrote {out}")
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
