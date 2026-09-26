"""Research-only direct MT5 replay of the author-associated SP2L candidate.

This script DOES NOT place or modify trades. It reads M1 bars directly from the
connected MetaTrader 5 terminal and applies the currently documented author
implementation candidate. It intentionally does not promote any rule to
canonical Strategy A geometry.

Interval mode is explicit: --start and --end define the exact requested UTC
window. MT5 bars are fetched ending at --end and then filtered to that interval;
bars outside the requested interval are discarded. No timestamp shifting is
performed.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

from sp2l_author_replica_detector import RESEARCH_DETECTOR_REVISION
from sp2l_research_manifest_gate import assert_manifest_compatible

SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
P_GAP = float(os.getenv("PGAP_PRICE", "1"))
SPIKE_MULT = float(os.getenv("SPIKE_MULTIPLIER", "1.5"))
MAX_SL = float(os.getenv("MAX_SL_PRICE", "10"))
TP_R = float(os.getenv("TP_R", "1"))
MANIFEST_COMPATIBILITY = assert_manifest_compatible(
    p_gap_price=P_GAP,
    spike_multiplier=SPIKE_MULT,
    max_sl_distance=MAX_SL,
    tp_r=TP_R,
    detector_revision=RESEARCH_DETECTOR_REVISION,
)


def parse_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp must include UTC offset")
    return dt.astimezone(timezone.utc).replace(second=0, microsecond=0)


def iso_utc(ts: int) -> str:
    return datetime.fromtimestamp(int(ts), timezone.utc).isoformat()


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
    p = argparse.ArgumentParser(description="Research-only exact-interval MT5 SP2L replay")
    p.add_argument("--start", required=True, help="Inclusive UTC start, e.g. 2026-09-21T00:00:00Z")
    p.add_argument("--end", required=True, help="Inclusive UTC end, e.g. 2026-09-21T08:30:00Z")
    p.add_argument(
        "--output",
        default="artifacts/author-replica-mt5-api-interval-result.json",
        help="Output JSON path",
    )
    args = p.parse_args()

    start = parse_utc(args.start)
    end = parse_utc(args.end)
    if end <= start:
        raise SystemExit("end must be after start")

    expected_minutes = int((end - start).total_seconds() // 60) + 1

    if not mt5.initialize():
        # Non-default terminal install (e.g. Otet Group): resolve explicitly.
        from mt5_terminal_resolver import find_mt5_terminal
        path = find_mt5_terminal()
        if path is None or not mt5.initialize(path=str(path)):
            raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"symbol_select failed for {SYMBOL}: {mt5.last_error()}")

        # Request at least the full minute span. If the terminal has market
        # gaps, MT5 may return bars before start to fill the count; those are
        # explicitly filtered out below.
        rates = mt5.copy_rates_from(SYMBOL, mt5.TIMEFRAME_M1, end, expected_minutes)
        if rates is None:
            raise SystemExit(f"copy_rates_from failed: {mt5.last_error()}")

        raw = [
            {
                "time": int(r[0]),
                "open": float(r[1]),
                "high": float(r[2]),
                "low": float(r[3]),
                "close": float(r[4]),
            }
            for r in rates
        ]

        start_ts = int(start.timestamp())
        end_ts = int(end.timestamp())
        candles = [c for c in raw if start_ts <= c["time"] <= end_ts]
        candles.sort(key=lambda c: c["time"])

        timestamps = [c["time"] for c in candles]
        unique = len(timestamps) == len(set(timestamps))
        chronological = all(b > a for a, b in zip(timestamps, timestamps[1:]))
        gaps = [
            {
                "from_utc": iso_utc(a),
                "to_utc": iso_utc(b),
                "missing_minutes": int((b - a) // 60) - 1,
            }
            for a, b in zip(timestamps, timestamps[1:])
            if b - a > 60
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
            signals.append(
                {
                    "index": i,
                    "direction": direction,
                    "entry": entry,
                    "sl": sl,
                    "tp": tp,
                    "time": candles[i - 1]["time"],
                    "time_utc": iso_utc(candles[i - 1]["time"]),
                }
            )

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
            "timestamp_basis": "epoch rendered as UTC; historical MT5 timestamp mapping remains unresolved",
            "terminal": mt5.terminal_info().name if mt5.terminal_info() else None,
            "server": mt5.account_info().server if mt5.account_info() else None,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "requested_interval_utc": {
                "start": start.isoformat(),
                "end": end.isoformat(),
            },
            "expected_minute_span": expected_minutes,
            "raw_returned_bars": len(raw),
            "filtered_bars_in_interval": len(candles),
            "raw_bars_discarded_outside_interval": len(raw) - len(candles),
            "actual_first_utc": iso_utc(candles[0]["time"]) if candles else None,
            "actual_last_utc": iso_utc(candles[-1]["time"]) if candles else None,
            "unique_timestamps": unique,
            "chronological": chronological,
            "gap_count": len(gaps),
            "gaps": gaps,
            "manifest_compatibility": MANIFEST_COMPATIBILITY,
            "config": {
                "pGapPrice": P_GAP,
                "spikeMultiplier": SPIKE_MULT,
                "maxSlPrice": MAX_SL,
                "tpR": TP_R,
            },
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
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\nWrote {out}")
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
