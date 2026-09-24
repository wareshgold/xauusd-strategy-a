"""Research-only SP2L tick-execution replay on real MT5 history.

Signal geometry is intentionally identical to the existing author-replica M1
detector. M1 bars define signals; real historical MT5 ticks define pending
fills and SL/TP exits. This is NOT canonical and does not alter live runner
state.

Six independent runs are produced: 3 symbols x 2 windows (24H and
London-open -> New-York-close). Session filtering applies to signal eligibility
only; a filled trade may exit after the session window. Pending orders use the
current forward-test research TTL (default 30 minutes).
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import MetaTrader5 as mt5
import numpy as np

from mt5_terminal_resolver import find_mt5_terminal

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "artifacts" / "backtest-mt5-local"
OUT_DIR.mkdir(parents=True, exist_ok=True)

P_GAP_PRICE = float(os.getenv("SP2L_P_GAP_PRICE", "1.0"))
SPIKE_MULTIPLIER = float(os.getenv("SP2L_SPIKE_MULTIPLIER", "1.5"))
MAX_SL_DISTANCE = float(os.getenv("SP2L_MAX_SL_DISTANCE", "10.0"))
TP_R = float(os.getenv("SP2L_TP_R", "1.0"))
PENDING_TTL_MINUTES = float(os.getenv("SP2L_PENDING_TTL_MINUTES", "30"))

LONDON_TZ = ZoneInfo("Europe/London")
NEW_YORK_TZ = ZoneInfo("America/New_York")
LONDON_OPEN = (8, 0)
NEW_YORK_CLOSE = (17, 0)

ALIASES = {
    "XAUUSD": ["XAUUSD"],
    "DJ30": ["DJ30", "DAWJONES", "DOWJONES", "US30", "DJI", "DOW"],
    "DAWJONES": ["DAWJONES", "DJ30", "DOWJONES", "US30", "DJI", "DOW"],
    "USTEC100": ["USTEC100", "USTEC", "NASDAQ", "NAS100", "US100", "NDX"],
    "USTEC": ["USTEC", "USTEC100", "NASDAQ", "NAS100", "US100", "NDX"],
}

REQUESTED = ("XAUUSD", "DJ30", "USTEC100")


def normalize(s: str) -> str:
    return "".join(c for c in s.upper() if c.isalnum())


def resolve_symbols(bases: tuple[str, ...]) -> dict[str, str]:
    all_symbols = [str(x.name) for x in (mt5.symbols_get() or [])]
    exact = set(all_symbols)
    out: dict[str, str] = {}
    for base in bases:
        chosen = None
        for candidate in ALIASES.get(base, [base]):
            for name in (candidate, candidate + ".ecn", candidate + ".ECN",
                         candidate + ".c.ecn", candidate + "m", candidate + ".m"):
                if name in exact:
                    chosen = name
                    break
            if chosen:
                break
        if not chosen:
            nc = {normalize(x) for x in ALIASES.get(base, [base])}
            matches = [x for x in all_symbols
                       if any(normalize(x) == c or normalize(x).startswith(c) for c in nc)]
            if matches:
                chosen = sorted(matches, key=lambda x: (len(x), x))[0]
        if chosen:
            out[base] = chosen
    return out


def in_session(ts: int) -> bool:
    dt = datetime.fromtimestamp(int(ts), timezone.utc)
    london = dt.astimezone(LONDON_TZ).replace(
        hour=LONDON_OPEN[0], minute=LONDON_OPEN[1], second=0, microsecond=0
    )
    ny = dt.astimezone(NEW_YORK_TZ).replace(
        hour=NEW_YORK_CLOSE[0], minute=NEW_YORK_CLOSE[1], second=0, microsecond=0
    )
    return london.astimezone(timezone.utc) <= dt <= ny.astimezone(timezone.utc)


def detect(candles: np.ndarray) -> dict | None:
    a, spike, correction, trigger = candles[-5], candles[-4], candles[-3], candles[-2]
    buy_body = float(spike["close"] - spike["open"])
    sell_body = float(spike["open"] - spike["close"])

    buy = (
        trigger["low"] < correction["low"]
        and correction["close"] > spike["close"]
        and correction["open"] > spike["open"]
        and spike["close"] > a["close"]
        and spike["open"] > a["open"]
        and correction["close"] > correction["open"]
        and spike["close"] > spike["open"]
        and a["close"] > a["open"]
        and correction["low"] > a["high"] + P_GAP_PRICE
        and buy_body > SPIKE_MULTIPLIER * (correction["close"] - correction["open"])
        and buy_body > SPIKE_MULTIPLIER * (a["close"] - a["open"])
        and buy_body > SPIKE_MULTIPLIER * (trigger["close"] - trigger["open"])
    )
    sell = (
        trigger["high"] > correction["high"]
        and correction["close"] < spike["close"]
        and correction["open"] < spike["open"]
        and spike["close"] < a["close"]
        and spike["open"] < a["open"]
        and correction["close"] < correction["open"]
        and spike["close"] < spike["open"]
        and a["close"] < a["open"]
        and correction["high"] < a["low"] - P_GAP_PRICE
        and sell_body > SPIKE_MULTIPLIER * (correction["open"] - correction["close"])
        and sell_body > SPIKE_MULTIPLIER * (a["open"] - a["close"])
        and sell_body > SPIKE_MULTIPLIER * (trigger["open"] - trigger["close"])
    )
    if buy == sell:
        return None

    if buy:
        entry, sl = float(trigger["low"]), float(spike["low"])
        risk = entry - sl
        if 0 < risk <= MAX_SL_DISTANCE:
            return {"direction": "BUY", "signal_time": int(trigger["time"]),
                    "entry": entry, "sl": sl, "risk": risk,
                    "tp": entry + TP_R * risk}
    else:
        entry, sl = float(trigger["high"]), float(spike["high"])
        risk = sl - entry
        if 0 < risk <= MAX_SL_DISTANCE:
            return {"direction": "SELL", "signal_time": int(trigger["time"]),
                    "entry": entry, "sl": sl, "risk": risk,
                    "tp": entry - TP_R * risk}
    return None


def fetch_rates(symbol: str, start: datetime, end: datetime) -> np.ndarray:
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"symbol_select failed: {symbol}: {mt5.last_error()}")
    data = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start, end)
    if data is None or len(data) < 10:
        raise RuntimeError(f"M1 history unavailable for {symbol}: {mt5.last_error()}")
    data = data.copy()
    data.sort(order="time")
    _, idx = np.unique(data["time"], return_index=True)
    return data[np.sort(idx)]


def fetch_ticks(symbol: str, start: datetime, end: datetime) -> np.ndarray:
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"symbol_select failed: {symbol}: {mt5.last_error()}")
    data = mt5.copy_ticks_range(symbol, start, end, mt5.COPY_TICKS_ALL)
    if data is None or len(data) == 0:
        raise RuntimeError(f"Tick history unavailable for {symbol}: {mt5.last_error()}")
    data = data.copy()
    if "time_msc" in data.dtype.names:
        data.sort(order="time_msc")
        _, idx = np.unique(data["time_msc"], return_index=True)
        data = data[np.sort(idx)]
    else:
        data.sort(order="time")
    return data


def tick_prices(tick) -> tuple[float, float]:
    bid = float(tick["bid"]) if "bid" in tick.dtype.names else 0.0
    ask = float(tick["ask"]) if "ask" in tick.dtype.names else 0.0
    if bid <= 0 or ask <= 0:
        return 0.0, 0.0
    return bid, ask


def ticks_for_signal(ticks: np.ndarray, start_ts: int) -> np.ndarray:
    if "time_msc" in ticks.dtype.names:
        return ticks[ticks["time_msc"] >= int(start_ts) * 1000]
    return ticks[ticks["time"] >= int(start_ts)]


def replay_signal(ticks: np.ndarray, signal: dict, eligible_ts: int) -> tuple[str, float | None, dict]:
    direction = signal["direction"]
    entry, sl, tp = signal["entry"], signal["sl"], signal["tp"]
    pending_deadline = eligible_ts + int(PENDING_TTL_MINUTES * 60) if PENDING_TTL_MINUTES > 0 else None

    trace = {
        "eligible_from_utc": datetime.fromtimestamp(eligible_ts, timezone.utc).isoformat(),
        "pending_ttl_minutes": PENDING_TTL_MINUTES,
        "fill_time_utc": None, "fill_price": None, "exit_time_utc": None,
        "exit_price": None, "exit_reason": None, "actual_r": None,
        "ticks_scanned": 0, "ticks_missing_bid_ask": 0,
    }
    filled = False
    fill_ms = None

    for tick in ticks_for_signal(ticks, eligible_ts):
        t_ms = int(tick["time_msc"]) if "time_msc" in tick.dtype.names else int(tick["time"]) * 1000
        t = t_ms / 1000.0
        bid, ask = tick_prices(tick)
        if bid <= 0 or ask <= 0:
            trace["ticks_missing_bid_ask"] += 1
            continue
        trace["ticks_scanned"] += 1

        if not filled:
            if pending_deadline is not None and t > pending_deadline:
                trace["exit_reason"] = "NO_FILL_EXPIRED"
                return "NO_FILL", None, trace
            touched = (ask <= entry) if direction == "BUY" else (bid >= entry)
            if not touched:
                continue
            filled = True
            fill_ms = t_ms
            trace["fill_time_utc"] = datetime.fromtimestamp(t, timezone.utc).isoformat()
            trace["fill_price"] = entry

            hit_sl = bid <= sl if direction == "BUY" else ask >= sl
            hit_tp = bid >= tp if direction == "BUY" else ask <= tp
            if hit_sl and hit_tp:
                trace["exit_time_utc"] = trace["fill_time_utc"]
                trace["exit_price"] = None
                trace["exit_reason"] = "AMBIGUOUS_BOTH_ON_FILL_TICK"
                return "AMBIGUOUS", None, trace
            if hit_sl:
                trace["exit_time_utc"] = trace["fill_time_utc"]
                trace["exit_price"] = sl
                trace["actual_r"] = -1.0
                trace["exit_reason"] = "SL_ON_FILL_TICK"
                return "LOSS", -1.0, trace
            if hit_tp:
                trace["exit_time_utc"] = trace["fill_time_utc"]
                trace["exit_price"] = tp
                trace["actual_r"] = 1.0
                trace["exit_reason"] = "TP_ON_FILL_TICK"
                return "WIN", 1.0, trace
            continue

        hit_sl = bid <= sl if direction == "BUY" else ask >= sl
        hit_tp = bid >= tp if direction == "BUY" else ask <= tp
        if hit_sl and hit_tp:
            trace["exit_time_utc"] = datetime.fromtimestamp(t, timezone.utc).isoformat()
            trace["exit_reason"] = "AMBIGUOUS_BOTH_ON_TICK"
            return "AMBIGUOUS", None, trace
        if hit_tp:
            trace["exit_time_utc"] = datetime.fromtimestamp(t, timezone.utc).isoformat()
            trace["exit_price"] = tp
            trace["actual_r"] = 1.0
            trace["exit_reason"] = "TP"
            return "WIN", 1.0, trace
        if hit_sl:
            trace["exit_time_utc"] = datetime.fromtimestamp(t, timezone.utc).isoformat()
            trace["exit_price"] = sl
            trace["actual_r"] = -1.0
            trace["exit_reason"] = "SL"
            return "LOSS", -1.0, trace

    if filled:
        trace["exit_reason"] = "OPEN_AT_END"
        return "OPEN_AT_END", None, trace
    trace["exit_reason"] = "NO_FILL_END_OF_HISTORY"
    return "NO_FILL", None, trace


def wilson(wins: int, decisive: int) -> list[float | None]:
    if decisive <= 0:
        return [None, None]
    z = 1.959963984540054
    p = wins / decisive
    den = 1 + z*z/decisive
    center = (p + z*z/(2*decisive)) / den
    half = z * np.sqrt(p*(1-p)/decisive + z*z/(4*decisive*decisive)) / den
    return [100*(center-half), 100*(center+half)]


def stats(rows: list[dict]) -> dict:
    wins = sum(r["result"] == "WIN" for r in rows)
    losses = sum(r["result"] == "LOSS" for r in rows)
    ambiguous = sum(r["result"] == "AMBIGUOUS" for r in rows)
    no_fill = sum(r["result"] == "NO_FILL" for r in rows)
    open_end = sum(r["result"] == "OPEN_AT_END" for r in rows)
    decisive = wins + losses
    rvals = [float(r["r"]) for r in rows if r["result"] in ("WIN", "LOSS")]
    equity = peak = dd = 0.0
    consec = max_consec = 0
    for rv in rvals:
        equity += rv
        peak = max(peak, equity)
        dd = max(dd, peak-equity)
        if rv < 0:
            consec += 1
            max_consec = max(max_consec, consec)
        else:
            consec = 0
    by_dir = {}
    for direction in ("BUY", "SELL"):
        sub = [r for r in rows if r["direction"] == direction]
        w = sum(r["result"] == "WIN" for r in sub)
        l = sum(r["result"] == "LOSS" for r in sub)
        d = w + l
        by_dir[direction] = {
            "signals": len(sub), "filled": sum(r.get("filled", False) for r in sub),
            "wins": w, "losses": l, "decisive": d,
            "win_rate_pct": 100*w/d if d else None,
            "wilson_95_ci_pct": wilson(w, d), "net_r": w-l,
        }
    return {
        "signals": len(rows), "filled": sum(r.get("filled", False) for r in rows),
        "wins": wins, "losses": losses, "ambiguous": ambiguous,
        "no_fill": no_fill, "open_at_end": open_end, "decisive": decisive,
        "win_rate_pct": 100*wins/decisive if decisive else None,
        "wilson_95_ci_pct": wilson(wins, decisive),
        "net_r": sum(rvals),
        "profit_factor": (sum(x for x in rvals if x > 0) / abs(sum(x for x in rvals if x < 0))
                          if any(x < 0 for x in rvals) else (float("inf") if rvals else None)),
        "max_drawdown_r": dd, "max_consecutive_losses": max_consec,
        "by_direction": by_dir,
    }


def run_case(base: str, symbol: str, rates: np.ndarray, ticks: np.ndarray,
             session: str, period_end_ts: int) -> dict:
    rows = []
    seen = set()
    for i in range(4, len(rates) - 1):
        # Preserve the existing backtest's formation timing exactly:
        # detect on [i-4:i+1], but the trigger is rates[i-1], and execution
        # becomes eligible from rates[i+1].
        formation = rates[:i+1]
        candidate = detect(formation)
        if candidate is None:
            continue
        sid = candidate["signal_time"]
        if sid in seen:
            continue
        seen.add(sid)
        if session == "LONDON_NY" and not in_session(sid):
            continue

        eligible_ts = int(rates[i + 1]["time"])
        result, r, trace = replay_signal(ticks, candidate, eligible_ts)
        row = {**candidate, "base": base, "symbol": symbol, "session": session,
               "eligible_from_utc": datetime.fromtimestamp(eligible_ts, timezone.utc).isoformat(),
               "result": result, "r": r, "filled": trace["fill_time_utc"] is not None,
               "trace": trace}
        rows.append(row)

    s = stats(rows)
    return {
        "base": base, "symbol": symbol, "session": session,
        "period": {"start_utc": datetime.fromtimestamp(int(rates[0]["time"]), timezone.utc).isoformat(),
                   "end_utc": datetime.fromtimestamp(period_end_ts, timezone.utc).isoformat()},
        "m1_bars": len(rates), "historical_ticks": len(ticks),
        "geometry": {"p_gap_price": P_GAP_PRICE, "spike_multiplier": SPIKE_MULTIPLIER,
                     "max_sl_distance": MAX_SL_DISTANCE, "tp_r": TP_R,
                     "canonical": False},
        "execution_replay": {
            "source": "CONNECTED_MT5_TERMINAL",
            "price_source": "HISTORICAL_MT5_TICKS",
            "pending_order_mode": "PENDING_LIMIT_RESEARCH",
            "buy_fill_rule": "ASK <= theoretical_entry",
            "sell_fill_rule": "BID >= theoretical_entry",
            "buy_exit_rule": "BID touches SL/TP",
            "sell_exit_rule": "ASK touches SL/TP",
            "pending_ttl_minutes": PENDING_TTL_MINUTES,
            "canonical": False,
        },
        "session_definition": {
            "session": session,
            "london_open_local": "08:00",
            "new_york_close_local": "17:00",
            "timezones": ["Europe/London", "America/New_York"],
            "signal_filter_only": True,
            "canonical": False,
        },
        "stats": s,
        "signals_detail": rows,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--start", default="2026-09-21T00:00:00Z")
    p.add_argument("--end", default="2026-09-24T23:59:59Z")
    p.add_argument("--symbols", default="XAUUSD,DJ30,USTEC100")
    args = p.parse_args()

    start = datetime.fromisoformat(args.start.replace("Z", "+00:00")).astimezone(timezone.utc)
    end = datetime.fromisoformat(args.end.replace("Z", "+00:00")).astimezone(timezone.utc)

    if not mt5.initialize():
        terminal = find_mt5_terminal()
        if terminal is None or not mt5.initialize(path=str(terminal)):
            print(json.dumps({"status": "MT5_INIT_FAILED", "error": mt5.last_error()}, indent=2))
            return 2

    try:
        bases = tuple(x.strip().upper() for x in args.symbols.split(",") if x.strip())
        resolved = resolve_symbols(bases)
        report = {
            "status": "RESEARCH_ONLY",
            "source": "CONNECTED_MT5_TERMINAL",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "period_requested": {"start_utc": start.isoformat(), "end_utc": end.isoformat()},
            "symbols": resolved,
            "cases": {},
            "notes": [
                "M1 OHLC is used only to reproduce the existing author-replica signal detector.",
                "Historical MT5 ticks are used for pending-limit fills and SL/TP execution replay.",
                "This is research-only; no canonical geometry or execution semantics are promoted.",
                "The 30-minute pending TTL matches the current forward runner research setting and is not a source-confirmed Strategy A rule.",
                "Session gating applies only to signal eligibility; filled trades can exit after session close.",
                "The replay preserves the current local-backtest formation timing: detector window ends at i, trigger is i-1, execution eligibility begins at i+1.",
                "MT5 tick semantics are represented by ASK for BUY entry, BID for SELL entry, BID for BUY exits, and ASK for SELL exits.",
            ],
        }

        for base in bases:
            symbol = resolved.get(base)
            if not symbol:
                report["cases"][base] = {"status": "SYMBOL_NOT_FOUND"}
                continue
            print(f"[MT5] {base} -> {symbol}: fetching M1 + ticks ...", flush=True)
            rates = fetch_rates(symbol, start, end)
            ticks = fetch_ticks(symbol, start, end)
            print(f"[DATA] {symbol}: M1={len(rates):,} ticks={len(ticks):,}", flush=True)
            for session in ("24H", "LONDON_NY"):
                case = run_case(base, symbol, rates, ticks, session, int(end.timestamp()))
                report["cases"][f"{base}:{session}"] = case
                st = case["stats"]
                print(f"[DONE] {base} {session}: signals={st['signals']} filled={st['filled']} "
                      f"decisive={st['decisive']} WR={st['win_rate_pct']} netR={st['net_r']}", flush=True)

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = OUT_DIR / f"SP2L_MT5_TICK_REPLAY_20260921_20260924_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({"status": "COMPLETE", "report": str(path),
                          "cases": {k: v.get("stats") for k, v in report["cases"].items()}},
                         indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
