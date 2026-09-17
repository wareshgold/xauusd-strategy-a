"""Research-only direct MT5 replay of the author-associated SP2L candidate.

This script DOES NOT place or modify trades. It reads M1 bars directly from the
connected MetaTrader 5 terminal and applies the currently documented author
implementation candidate. It intentionally does not promote any rule to
canonical Strategy A geometry.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
N = int(os.getenv("BARS", "10000"))
P_GAP = float(os.getenv("PGAP_PRICE", "1"))
SPIKE_MULT = float(os.getenv("SPIKE_MULTIPLIER", "1.5"))
MAX_SL = float(os.getenv("MAX_SL_PRICE", "10"))
TP_R = float(os.getenv("TP_R", "1"))
FIXED_FROM_UTC = os.getenv("FIXED_FROM_UTC")


def body(c):
    return abs(c["close"] - c["open"])


def signal(c, i):
    a, s, corr, trig = c[i - 4], c[i - 3], c[i - 2], c[i - 1]
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
    if buy:
        return "BUY", trig["low"], a["low"]
    if sell:
        return "SELL", trig["high"], a["high"]
    return None


def main():
    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"symbol_select failed for {SYMBOL}: {mt5.last_error()}")
        if FIXED_FROM_UTC:
            from_date = datetime.fromisoformat(FIXED_FROM_UTC.replace("Z", "+00:00"))
            if from_date.tzinfo is None:
                from_date = from_date.replace(tzinfo=timezone.utc)
            from_date = from_date.astimezone(timezone.utc)
        else:
            from_date = datetime.now(timezone.utc) + timedelta(hours=3)
        rates = mt5.copy_rates_from(SYMBOL, mt5.TIMEFRAME_M1, from_date, N)
        if rates is None:
            raise SystemExit(f"copy_rates_from failed: {mt5.last_error()}")
        candles = [
            {"time": int(r[0]), "open": float(r[1]), "high": float(r[2]),
             "low": float(r[3]), "close": float(r[4])}
            for r in rates
        ]
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
                if sig["direction"] == "BUY":
                    hit_sl, hit_tp = c["low"] <= sig["sl"], c["high"] >= sig["tp"]
                else:
                    hit_sl, hit_tp = c["high"] >= sig["sl"], c["low"] <= sig["tp"]
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
        total_r = wins - losses
        result = {
            "research_only": True,
            "source": "MetaTrader5.copy_rates_from",
            "terminal": mt5.terminal_info().name if mt5.terminal_info() else None,
            "server": mt5.account_info().server if mt5.account_info() else None,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "request_from_utc": from_date.isoformat(),
            "requested_bars": N,
            "returned_bars": len(candles),
            "first_utc": datetime.fromtimestamp(candles[0]["time"], timezone.utc).isoformat() if candles else None,
            "last_utc": datetime.fromtimestamp(candles[-1]["time"], timezone.utc).isoformat() if candles else None,
            "config": {"pGapPrice": P_GAP, "spikeMultiplier": SPIKE_MULT, "maxSlPrice": MAX_SL, "tpR": TP_R},
            "signals_detected": len(signals),
            "trades_closed_or_ambiguous": len(trades),
            "wins": wins,
            "losses": losses,
            "ambiguous": ambiguous,
            "open_or_unresolved": len(signals) - len(trades),
            "win_rate_decisive": wins / decisive if decisive else None,
            "totalR": total_r,
            "profit_factor": wins / losses if losses else None,
            "signals": signals,
            "trades": trades,
        }
        print(json.dumps(result, indent=2))
        out = Path("artifacts") / "author-replica-mt5-api-result.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\nWrote {out}")
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
