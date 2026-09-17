"""Research-only temporal stability runner for the author-associated SP2L candidate.

Collects identical-size MT5 M1 windows ending at explicit UTC snapshot times.
No trading calls. No geometry changes. Results are descriptive evidence only.
"""
from __future__ import annotations

import hashlib
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
TP_R = float(os.getenv("TP_R", "1"))

DEFAULT_SNAPSHOTS = [
    "2026-09-17T10:45:00+00:00",
    "2026-09-10T10:45:00+00:00",
    "2026-09-03T10:45:00+00:00",
    "2026-08-27T10:45:00+00:00",
    "2026-08-20T10:45:00+00:00",
]


def body(c):
    return abs(c["close"] - c["open"])


def signal(c, i):
    a, s, corr, trig = c[i - 4], c[i - 3], c[i - 2], c[i - 1]
    buy = (
        trig["low"] < corr["low"] and corr["close"] > s["close"]
        and corr["open"] > s["open"] and s["open"] > a["open"]
        and corr["close"] > corr["open"] and s["close"] > s["open"]
        and a["close"] > a["open"] and corr["low"] > a["high"] + P_GAP
        and body(s) > SPIKE_MULT * body(corr)
        and body(s) > SPIKE_MULT * body(a)
        and body(s) > SPIKE_MULT * body(trig)
    )
    sell = (
        trig["high"] > corr["high"] and corr["close"] < s["close"]
        and corr["open"] < s["open"] and s["close"] < a["close"]
        and s["open"] < a["open"] and corr["close"] < corr["open"]
        and s["close"] < s["open"] and a["close"] < a["open"]
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


def run_snapshot(end_utc: str):
    end = datetime.fromisoformat(end_utc.replace("Z", "+00:00")).astimezone(timezone.utc)
    rates = mt5.copy_rates_from(SYMBOL, mt5.TIMEFRAME_M1, end, N)
    if rates is None:
        raise RuntimeError(f"copy_rates_from failed at {end.isoformat()}: {mt5.last_error()}")
    candles = [
        {"time": int(r[0]), "open": float(r[1]), "high": float(r[2]),
         "low": float(r[3]), "close": float(r[4])}
        for r in rates
    ]
    payload = json.dumps(candles, separators=(",", ":"), sort_keys=True).encode()
    sha = hashlib.sha256(payload).hexdigest()
    signals = []
    for i in range(4, len(candles)):
        s = signal(candles, i)
        if not s:
            continue
        direction, entry, sl = s
        risk = abs(entry - sl)
        if risk <= 0 or risk > MAX_SL:
            continue
        tp = entry + TP_R * risk if direction == "BUY" else entry - TP_R * risk
        signals.append({"index": i, "direction": direction, "entry": entry,
                        "sl": sl, "tp": tp, "time": candles[i - 1]["time"]})

    wins = losses = ambiguous = 0
    trades = []
    for sig in signals:
        outcome = None
        for j in range(sig["index"] + 1, len(candles)):
            c = candles[j]
            hit_sl = c["low"] <= sig["sl"] if sig["direction"] == "BUY" else c["high"] >= sig["sl"]
            hit_tp = c["high"] >= sig["tp"] if sig["direction"] == "BUY" else c["low"] <= sig["tp"]
            if hit_sl and hit_tp:
                outcome = "AMBIGUOUS"
                break
            if hit_sl:
                outcome = "LOSS"
                break
            if hit_tp:
                outcome = "WIN"
                break
        if outcome:
            trades.append({**sig, "outcome": outcome})
            wins += outcome == "WIN"
            losses += outcome == "LOSS"
            ambiguous += outcome == "AMBIGUOUS"

    decisive = wins + losses
    return {
        "snapshot_end_utc": end.isoformat(),
        "returned_bars": len(candles),
        "first_utc": datetime.fromtimestamp(candles[0]["time"], timezone.utc).isoformat() if candles else None,
        "last_utc": datetime.fromtimestamp(candles[-1]["time"], timezone.utc).isoformat() if candles else None,
        "candles_sha256": sha,
        "signals_detected": len(signals),
        "trades_closed_or_ambiguous": len(trades),
        "wins": wins, "losses": losses, "ambiguous": ambiguous,
        "open_or_unresolved": len(signals) - len(trades),
        "win_rate_decisive": wins / decisive if decisive else None,
        "totalR": wins - losses,
        "profit_factor": wins / losses if losses else None,
    }


def main():
    raw = os.getenv("MT5_SNAPSHOT_ENDS_UTC")
    snapshots = [x.strip() for x in raw.split(",") if x.strip()] if raw else DEFAULT_SNAPSHOTS
    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"symbol_select failed for {SYMBOL}: {mt5.last_error()}")
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        results = [run_snapshot(x) for x in snapshots]
        output = {
            "research_only": True,
            "source": "MetaTrader5.copy_rates_from",
            "terminal": terminal.name if terminal else None,
            "server": account.server if account else None,
            "symbol": SYMBOL, "timeframe": "M1", "requested_bars": N,
            "config": {"pGapPrice": P_GAP, "spikeMultiplier": SPIKE_MULT,
                       "maxSlPrice": MAX_SL, "tpR": TP_R},
            "snapshots": results,
        }
        print(json.dumps(output, indent=2))
        out = Path("artifacts") / "author-replica-mt5-stability-snapshots.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(output, indent=2), encoding="utf-8")
        print(f"\nWrote {out}")
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
