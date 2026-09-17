"""Research-only non-overlapping stability snapshots for the author-associated SP2L candidate.

Uses fixed MT5 end timestamps and 10,000 M1 bars per window. Endpoints are spaced
12 calendar days apart so the returned windows are intended to be non-overlapping.
This does not define or promote canonical Strategy A geometry.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
import MetaTrader5 as mt5

SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
N = int(os.getenv("BARS", "10000"))
P_GAP = float(os.getenv("PGAP_PRICE", "1"))
SPIKE_MULT = float(os.getenv("SPIKE_MULTIPLIER", "1.5"))
MAX_SL = float(os.getenv("MAX_SL_PRICE", "10"))
TP_R = float(os.getenv("TP_R", "1"))
DEFAULT_ENDS = [
    "2026-09-17T10:45:00+00:00",
    "2026-09-05T10:45:00+00:00",
    "2026-08-24T10:45:00+00:00",
    "2026-08-12T10:45:00+00:00",
    "2026-07-31T10:45:00+00:00",
    "2026-07-19T10:45:00+00:00",
]
ENDS = [x.strip() for x in os.getenv("SNAPSHOT_ENDS_UTC", ",".join(DEFAULT_ENDS)).split(",") if x.strip()]

def body(c): return abs(c["close"] - c["open"])

def signal(c, i):
    a, s, corr, trig = c[i-4], c[i-3], c[i-2], c[i-1]
    buy = (trig["low"] < corr["low"] and corr["close"] > s["close"] and corr["open"] > s["open"]
           and s["open"] > a["open"] and corr["close"] > corr["open"] and s["close"] > s["open"]
           and a["close"] > a["open"] and corr["low"] > a["high"] + P_GAP
           and body(s) > SPIKE_MULT*body(corr) and body(s) > SPIKE_MULT*body(a) and body(s) > SPIKE_MULT*body(trig))
    sell = (trig["high"] > corr["high"] and corr["close"] < s["close"] and corr["open"] < s["open"]
            and s["close"] < a["close"] and s["open"] < a["open"] and corr["close"] < corr["open"]
            and s["close"] < s["open"] and a["close"] < a["open"] and corr["high"] < a["low"] - P_GAP
            and body(s) > SPIKE_MULT*body(corr) and body(s) > SPIKE_MULT*body(a) and body(s) > SPIKE_MULT*body(trig))
    if buy: return "BUY", trig["low"], a["low"]
    if sell: return "SELL", trig["high"], a["high"]
    return None

def run_window(end_dt):
    rates = mt5.copy_rates_from(SYMBOL, mt5.TIMEFRAME_M1, end_dt, N)
    if rates is None or len(rates) == 0: return {"snapshot_end_utc": end_dt.isoformat(), "error": str(mt5.last_error())}
    c = [{"time": int(r[0]), "open": float(r[1]), "high": float(r[2]), "low": float(r[3]), "close": float(r[4])} for r in rates]
    signals = []
    for i in range(4, len(c)):
        s = signal(c, i)
        if not s: continue
        d, entry, sl = s
        risk = abs(entry-sl)
        if risk <= 0 or risk > MAX_SL: continue
        tp = entry + TP_R*risk if d == "BUY" else entry - TP_R*risk
        signals.append({"index": i, "direction": d, "entry": entry, "sl": sl, "tp": tp, "time": c[i-1]["time"]})
    wins = losses = ambiguous = 0
    for sig in signals:
        outcome = None
        for j in range(sig["index"]+1, len(c)):
            x = c[j]
            hit_sl = x["low"] <= sig["sl"] if sig["direction"] == "BUY" else x["high"] >= sig["sl"]
            hit_tp = x["high"] >= sig["tp"] if sig["direction"] == "BUY" else x["low"] <= sig["tp"]
            if hit_sl and hit_tp: outcome = "AMBIGUOUS"; break
            if hit_sl: outcome = "LOSS"; break
            if hit_tp: outcome = "WIN"; break
        if outcome == "WIN": wins += 1
        elif outcome == "LOSS": losses += 1
        elif outcome == "AMBIGUOUS": ambiguous += 1
    decisive = wins + losses
    return {"snapshot_end_utc": end_dt.isoformat(), "returned_bars": len(c),
            "first_utc": datetime.fromtimestamp(c[0]["time"], timezone.utc).isoformat(),
            "last_utc": datetime.fromtimestamp(c[-1]["time"], timezone.utc).isoformat(),
            "signals_detected": len(signals), "wins": wins, "losses": losses, "ambiguous": ambiguous,
            "open_or_unresolved": len(signals)-wins-losses-ambiguous,
            "win_rate_decisive": wins/decisive if decisive else None, "totalR": wins-losses,
            "profit_factor": wins/losses if losses else None,
            "calendar_span_days": (c[-1]["time"]-c[0]["time"])/86400}

def main():
    if not mt5.initialize(): raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        if not mt5.symbol_select(SYMBOL, True): raise SystemExit(f"symbol_select failed: {mt5.last_error()}")
        snapshots = []
        for raw in ENDS:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)
            snapshots.append(run_window(dt))
        result = {"research_only": True, "source": "MetaTrader5.copy_rates_from", "symbol": SYMBOL,
                  "timeframe": "M1", "requested_bars": N,
                  "spacing_days_between_requested_ends": 12,
                  "config": {"pGapPrice": P_GAP, "spikeMultiplier": SPIKE_MULT, "maxSlPrice": MAX_SL, "tpR": TP_R},
                  "snapshots": snapshots}
        print(json.dumps(result, indent=2))
        out = Path("artifacts")/"author-replica-mt5-nonoverlap-stability.json"
        out.parent.mkdir(exist_ok=True); out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\nWrote {out}")
    finally: mt5.shutdown()

if __name__ == "__main__": main()
