"""Research-only MT5-local historical replay for SP2L across a requested symbol basket.

IMPORTANT:
- This script MUST run on the user's Windows machine where the MT5 terminal is installed.
- It pulls M1 history directly from the connected MT5 terminal with copy_rates_range.
- It does not use GitHub price data and does not define canonical Strategy A geometry.
- Symbol names are discovered from the broker terminal; the report records the exact names.
- Entry/SL/TP geometry matches the existing author-replica research detector.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5
import numpy as np

from mt5_terminal_resolver import find_mt5_terminal

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "artifacts" / "backtest-mt5-local"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REQUESTED_BASES = (
    "XAUUSD",
    "BTCUSD",
    "DJ30",
    "DAWJONES",
    "NASDAQ",
    "USTEC100",
    "GBPUSD",
    "USDJPY",
    "EURUSD",
    "USDCHF",
)

DEFAULT_DAYS = int(os.getenv("SP2L_MT5_BACKTEST_DAYS", "103"))
P_GAP_PRICE = float(os.getenv("SP2L_P_GAP_PRICE", "1.0"))
SPIKE_MULTIPLIER = float(os.getenv("SP2L_SPIKE_MULTIPLIER", "1.5"))
MAX_SL_DISTANCE = float(os.getenv("SP2L_MAX_SL_DISTANCE", "10.0"))
TP_R = float(os.getenv("SP2L_TP_R", "1.0"))

# Broker aliases. The terminal is still authoritative: these are only search hints.
ALIASES = {
    "XAUUSD": ["XAUUSD"],
    "BTCUSD": ["BTCUSD"],
    "DJ30": ["DJ30", "DAWJONES", "DOWJONES", "US30", "DJI", "DOW"],
    "DAWJONES": ["DAWJONES", "DJ30", "DOWJONES", "US30", "DJI", "DOW"],
    "NASDAQ": ["NASDAQ", "USTEC100", "USTEC", "NAS100", "US100", "NDX"],
    "USTEC100": ["USTEC100", "USTEC", "NASDAQ", "NAS100", "US100", "NDX"],
    "GBPUSD": ["GBPUSD"],
    "USDJPY": ["USDJPY"],
    "EURUSD": ["EURUSD"],
    "USDCHF": ["USDCHF"],
}


def normalize(s: str) -> str:
    return "".join(ch for ch in s.upper() if ch.isalnum())


def discover_symbols(requested: list[str]) -> dict[str, dict]:
    symbols = list(mt5.symbols_get() or [])
    exact = {str(s.name): s for s in symbols}
    normalized = {normalize(str(s.name)): str(s.name) for s in symbols}

    result = {}
    for base in requested:
        candidates = ALIASES.get(base, [base])
        chosen = None
        method = None

        # Exact base first, then common broker suffixes, then prefix/normalized matches.
        for candidate in candidates:
            if candidate in exact:
                chosen, method = candidate, "EXACT"
                break
            for suffix in (".ecn", ".ECN", "m", ".m", "_ecn", "-ECN"):
                if candidate + suffix in exact:
                    chosen, method = candidate + suffix, f"SUFFIX:{suffix}"
                    break
            if chosen:
                break

        if not chosen:
            norm_candidates = {normalize(c) for c in candidates}
            matches = [
                name for name in exact
                if any(normalize(name) == c or normalize(name).startswith(c) for c in norm_candidates)
            ]
            if matches:
                # Prefer the shortest exact-prefix broker symbol.
                chosen = sorted(matches, key=lambda x: (len(x), x))[0]
                method = "DISCOVERED_PREFIX"

        if chosen:
            info = mt5.symbol_info(chosen)
            tick = mt5.symbol_info_tick(chosen)
            result[base] = {
                "requested": base,
                "symbol": chosen,
                "method": method,
                "digits": int(info.digits) if info else None,
                "point": float(info.point) if info else None,
                "trade_mode": int(info.trade_mode) if info else None,
                "bid": float(tick.bid) if tick else None,
                "ask": float(tick.ask) if tick else None,
            }
        else:
            result[base] = {"requested": base, "symbol": None, "method": None}

    return result


def detect(candles: np.ndarray, symbol: str) -> dict | None:
    a, spike, correction, trigger = candles[-5], candles[-4], candles[-3], candles[-2]
    spike_body_buy = float(spike["close"] - spike["open"])
    spike_body_sell = float(spike["open"] - spike["close"])

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
        and spike_body_buy > SPIKE_MULTIPLIER * (correction["close"] - correction["open"])
        and spike_body_buy > SPIKE_MULTIPLIER * (a["close"] - a["open"])
        and spike_body_buy > SPIKE_MULTIPLIER * (trigger["close"] - trigger["open"])
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
        and spike_body_sell > SPIKE_MULTIPLIER * (correction["open"] - correction["close"])
        and spike_body_sell > SPIKE_MULTIPLIER * (a["open"] - a["close"])
        and spike_body_sell > SPIKE_MULTIPLIER * (trigger["open"] - trigger["close"])
    )

    if buy == sell:
        return None

    if buy:
        entry, sl = float(trigger["low"]), float(spike["low"])
        risk = entry - sl
        if 0 < risk <= MAX_SL_DISTANCE:
            return {
                "direction": "BUY",
                "signal_time": int(trigger["time"]),
                "entry": entry,
                "sl": sl,
                "risk": risk,
                "tp": entry + TP_R * risk,
            }

    if sell:
        entry, sl = float(trigger["high"]), float(spike["high"])
        risk = sl - entry
        if 0 < risk <= MAX_SL_DISTANCE:
            return {
                "direction": "SELL",
                "signal_time": int(trigger["time"]),
                "entry": entry,
                "sl": sl,
                "risk": risk,
                "tp": entry - TP_R * risk,
            }
    return None


def outcome(candles: np.ndarray, signal_index: int, signal: dict) -> tuple[str, int | None, float | None]:
    """Theoretical entry replay.

    A signal is eligible from the candle after the trigger. The first later candle
    touching TP or SL decides the outcome. If both are touched in one candle, it is
    AMBIGUOUS rather than guessing intrabar order.
    """
    direction = signal["direction"]
    entry, sl, tp = signal["entry"], signal["sl"], signal["tp"]

    for j in range(signal_index + 1, len(candles)):
        bar = candles[j]
        high, low = float(bar["high"]), float(bar["low"])

        # Pending-limit semantics are unresolved; only bars that actually reach
        # the theoretical entry are eligible for fill.
        if direction == "BUY":
            filled = low <= entry
            if not filled:
                continue
            hit_sl = low <= sl
            hit_tp = high >= tp
        else:
            filled = high >= entry
            if not filled:
                continue
            hit_sl = high >= sl
            hit_tp = low <= tp

        if hit_sl and hit_tp:
            return "AMBIGUOUS", j, None
        if hit_tp:
            return "WIN", j, 1.0
        if hit_sl:
            return "LOSS", j, -1.0

    return "OPEN_AT_END", None, None


def wilson(wins: int, decisive: int, z: float = 1.959963984540054) -> tuple[float | None, float | None]:
    if decisive <= 0:
        return None, None
    p = wins / decisive
    den = 1 + z * z / decisive
    center = (p + z * z / (2 * decisive)) / den
    half = z * np.sqrt((p * (1 - p) / decisive) + (z * z / (4 * decisive * decisive))) / den
    return 100 * (center - half), 100 * (center + half)


def max_drawdown_and_losses(results: list[float]) -> tuple[float, int]:
    equity = peak = 0.0
    dd = 0.0
    run = max_run = 0
    for r in results:
        equity += r
        peak = max(peak, equity)
        dd = max(dd, peak - equity)
        if r < 0:
            run += 1
            max_run = max(max_run, run)
        else:
            run = 0
    return dd, max_run


def _history_coverage_audit(rates: np.ndarray) -> dict:
    """Audit observed M1 coverage without inventing a broker session schedule."""
    times = [datetime.fromtimestamp(int(t), timezone.utc) for t in rates["time"]]
    by_day: dict = defaultdict(list)
    for ts in times:
        by_day[ts.date()].append(ts)

    first_minutes = [v[0].hour * 60 + v[0].minute for v in by_day.values()]
    last_minutes = [v[-1].hour * 60 + v[-1].minute for v in by_day.values()]
    first_mode = Counter(first_minutes).most_common(1)[0][0] if first_minutes else None
    last_mode = Counter(last_minutes).most_common(1)[0][0] if last_minutes else None

    unexpected_same_day_gaps = []
    cross_day_gaps = []
    for prev, curr in zip(times, times[1:]):
        gap_minutes = int((curr - prev).total_seconds() // 60) - 1
        if gap_minutes <= 0:
            continue
        if prev.date() == curr.date():
            unexpected_same_day_gaps.append({
                "from_utc": prev.isoformat(),
                "to_utc": curr.isoformat(),
                "missing_minutes": gap_minutes,
            })
        else:
            cross_day_gaps.append({
                "from_utc": prev.isoformat(),
                "to_utc": curr.isoformat(),
                "missing_minutes": gap_minutes,
            })

    return {
        "observed_trading_dates": len(by_day),
        "observed_first_bar_mode_utc_minute": first_mode,
        "observed_last_bar_mode_utc_minute": last_mode,
        "observed_first_bar_mode_utc": (
            f"{first_mode // 60:02d}:{first_mode % 60:02d}" if first_mode is not None else None
        ),
        "observed_last_bar_mode_utc": (
            f"{last_mode // 60:02d}:{last_mode % 60:02d}" if last_mode is not None else None
        ),
        "unexpected_same_day_gaps": unexpected_same_day_gaps,
        "cross_day_gaps": cross_day_gaps,
    }


def fetch_rates(symbol: str, start: datetime, end: datetime) -> np.ndarray:
    """Fetch M1 history in bounded UTC date ranges and validate MT5 UTC timestamps.

    MT5's copy_rates_range() returns bar timestamps that this terminal exposes
    in UTC epoch form. A separate copy_rates_from_pos() observation showed a
    +3h-looking current-bar timestamp, but that behavior must not be applied to
    range-requested historical bars. This acquisition path therefore uses the
    documented/range-observed UTC timestamps without any broker offset
    transformation. The observation is retained as an audit note only.
    """
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"symbol_select failed for {symbol}: {mt5.last_error()}")

    chunk_days = float(os.getenv("SP2L_MT5_HISTORY_CHUNK_DAYS", "7"))
    max_retries = int(os.getenv("SP2L_MT5_HISTORY_RETRIES", "3"))
    if chunk_days <= 0:
        raise ValueError("SP2L_MT5_HISTORY_CHUNK_DAYS must be > 0")

    start = start.astimezone(timezone.utc)
    end = end.astimezone(timezone.utc)
    cursor = start
    chunks: list[np.ndarray] = []
    diagnostics: list[dict] = []

    while cursor < end:
        chunk_end = min(cursor + timedelta(days=chunk_days), end)
        rates = None
        last_error = None

        for attempt in range(1, max_retries + 1):
            rates = mt5.copy_rates_range(
                symbol,
                mt5.TIMEFRAME_M1,
                cursor,
                chunk_end,
            )
            if rates is not None and len(rates):
                break
            last_error = mt5.last_error()
            time.sleep(0.25 * attempt)

        if rates is None or len(rates) == 0:
            raise RuntimeError(
                f"MT5 history chunk failed for {symbol}: "
                f"{cursor.isoformat()}..{chunk_end.isoformat()} "
                f"after {max_retries} attempts: {last_error or mt5.last_error()}"
            )

        raw_first = int(rates["time"][0])
        raw_last = int(rates["time"][-1])
        diagnostics.append({
            "start_utc": cursor.isoformat(),
            "end_utc": chunk_end.isoformat(),
            "bars": int(len(rates)),
            "timestamp_normalization": "NONE_COPY_RATES_RANGE_UTC",
            "first_bar_observed_utc": datetime.fromtimestamp(raw_first, timezone.utc).isoformat(),
            "last_bar_observed_utc": datetime.fromtimestamp(raw_last, timezone.utc).isoformat(),
        })

        # Do not shift range-requested bar timestamps. Direct observation of
        # copy_rates_range() on XAUUSD.ecn returned exact requested UTC edges.
        chunks.append(rates.copy())

        next_cursor = chunk_end + timedelta(minutes=1)
        if next_cursor <= cursor:
            raise RuntimeError(f"MT5 history pagination made no progress for {symbol}")
        cursor = next_cursor

    if not chunks:
        raise RuntimeError(f"No M1 bars found for {symbol} in {start.isoformat()}..{end.isoformat()}")

    result = np.concatenate(chunks)
    result.sort(order="time")
    _, idx = np.unique(result["time"], return_index=True)
    result = result[np.sort(idx)]

    first_ts = int(result["time"][0])
    last_ts = int(result["time"][-1])
    start_ts = int(start.timestamp())
    end_ts = int(end.timestamp())

    coverage = _history_coverage_audit(result)

    # Do not assume the requested edge must contain a bar. Recurring observed
    # daily edges can explain outside-session request boundaries; this remains
    # descriptive data-quality logic, not a Strategy A session rule.
    first_dt = datetime.fromtimestamp(first_ts, timezone.utc)
    last_dt = datetime.fromtimestamp(last_ts, timezone.utc)
    start_same_day = first_dt.date() == start.date()
    end_same_day = last_dt.date() == end.date()

    if first_dt.date() > start.date():
        raise RuntimeError(
            f"Incomplete MT5 history for {symbol}: first observed trading date "
            f"{first_dt.date().isoformat()} is after requested start date "
            f"{start.date().isoformat()}"
        )
    if start_same_day and first_ts > start_ts:
        observed_first = coverage["observed_first_bar_mode_utc_minute"]
        actual_minute = first_dt.hour * 60 + first_dt.minute
        if observed_first is None or abs(actual_minute - observed_first) > 1:
            raise RuntimeError(
                f"Incomplete MT5 history for {symbol}: first bar "
                f"{first_dt.isoformat()} is later than requested start "
                f"{start.isoformat()} and does not match the recurring observed "
                f"daily opening edge {coverage['observed_first_bar_mode_utc']}"
            )

    if last_dt.date() < end.date():
        raise RuntimeError(
            f"Incomplete MT5 history for {symbol}: last observed trading date "
            f"{last_dt.date().isoformat()} is before requested end date "
            f"{end.date().isoformat()}"
        )
    if end_same_day and last_ts < end_ts:
        observed_last = coverage["observed_last_bar_mode_utc_minute"]
        actual_minute = last_dt.hour * 60 + last_dt.minute
        if observed_last is None or abs(actual_minute - observed_last) > 1:
            raise RuntimeError(
                f"Incomplete MT5 history for {symbol}: last bar "
                f"{last_dt.isoformat()} is before requested end "
                f"{end.isoformat()} and does not match the recurring observed "
                f"daily closing edge {coverage['observed_last_bar_mode_utc']}"
            )

    # Same-day gaps are not a reason to reject the entire symbol history.
    # They are retained in the coverage audit and are handled at signal level:
    # formation gaps suppress the signal, and outcome gaps quarantine the result.
    diagnostics.append({
        "coverage_audit": coverage,
        "history_gate": "OBSERVED_EDGE_AWARE_SIGNAL_LEVEL_INTRADAY_GAPS",
    })
    fetch_rates.last_diagnostics = diagnostics
    return result
def _gap_after(prev_ts: int, curr_ts: int) -> int:
    return max(0, int((curr_ts - prev_ts) // 60) - 1)


def run_symbol(symbol: str, rates: np.ndarray) -> dict:
    rates = np.sort(rates, order="time")
    # Deduplicate timestamps defensively.
    _, idx = np.unique(rates["time"], return_index=True)
    rates = rates[np.sort(idx)]

    signals = []
    data_gap_events = []
    last_signal_time = None
    for i in range(4, len(rates) - 1):
        formation_gap = None
        for j in range(i - 4, i):
            missing = _gap_after(int(rates[j]["time"]), int(rates[j + 1]["time"]))
            if missing:
                formation_gap = True
                break
        if formation_gap:
            continue

        window = rates[: i + 1]
        candidate = detect(window, symbol)
        if candidate is None or candidate["signal_time"] == last_signal_time:
            continue
        last_signal_time = candidate["signal_time"]

        result, exit_index, r = outcome(rates, i, candidate)
        if exit_index is not None:
            for j in range(i, exit_index):
                missing = _gap_after(int(rates[j]["time"]), int(rates[j + 1]["time"]))
                if missing:
                    data_gap_events.append({
                        "from_utc": datetime.fromtimestamp(int(rates[j]["time"]), timezone.utc).isoformat(),
                        "to_utc": datetime.fromtimestamp(int(rates[j + 1]["time"]), timezone.utc).isoformat(),
                        "missing_minutes": missing,
                    })
                    result, exit_index, r = "DATA_GAP", None, None
                    break

        signals.append({
            **candidate,
            "result": result,
            "exit_time": int(rates[exit_index]["time"]) if exit_index is not None else None,
            "r": r,
        })

    wins = sum(x["result"] == "WIN" for x in signals)
    losses = sum(x["result"] == "LOSS" for x in signals)
    ambiguous = sum(x["result"] == "AMBIGUOUS" for x in signals)
    open_end = sum(x["result"] == "OPEN_AT_END" for x in signals)
    data_gap = sum(x["result"] == "DATA_GAP" for x in signals)
    decisive = wins + losses
    net_r = wins - losses
    pf = wins / losses if losses else (float("inf") if wins else None)
    ci_low, ci_high = wilson(wins, decisive)
    dd, max_losses = max_drawdown_and_losses(
        [float(x["r"]) for x in signals if x["result"] in ("WIN", "LOSS")]
    )

    by_direction = {}
    for direction in ("BUY", "SELL"):
        subset = [x for x in signals if x["direction"] == direction]
        w = sum(x["result"] == "WIN" for x in subset)
        l = sum(x["result"] == "LOSS" for x in subset)
        d = w + l
        lo, hi = wilson(w, d)
        by_direction[direction] = {
            "signals": len(subset), "wins": w, "losses": l, "ambiguous": sum(x["result"] == "AMBIGUOUS" for x in subset),
            "decisive": d, "win_rate_pct": (100*w/d if d else None),
            "wilson_95_ci_pct": [lo, hi],
            "net_r": w-l,
        }

    return {
        "symbol": symbol,
        "bars": int(len(rates)),
        "first_bar_utc": datetime.fromtimestamp(int(rates[0]["time"]), timezone.utc).isoformat(),
        "last_bar_utc": datetime.fromtimestamp(int(rates[-1]["time"]), timezone.utc).isoformat(),
        "signals": len(signals),
        "wins": wins,
        "losses": losses,
        "ambiguous": ambiguous,
        "open_at_end": open_end,
        "data_gap": data_gap,
        "data_gap_events_affecting_signals": data_gap_events,
        "decisive": decisive,
        "win_rate_pct": (100 * wins / decisive if decisive else None),
        "wilson_95_ci_pct": [ci_low, ci_high],
        "net_r": net_r,
        "profit_factor_simplified": pf,
        "max_drawdown_r": dd,
        "max_consecutive_losses": max_losses,
        "by_direction": by_direction,
        "signals_detail": signals,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--start", default=None, help="UTC ISO, e.g. 2026-06-12T00:00:00Z")
    parser.add_argument("--end", default=None, help="UTC ISO, e.g. 2026-09-23T23:59:59Z")
    parser.add_argument("--symbols", default=",".join(REQUESTED_BASES))
    args = parser.parse_args()

    if not mt5.initialize():
        terminal = find_mt5_terminal()
        if terminal is None or not mt5.initialize(path=str(terminal)):
            print(json.dumps({
                "status": "MT5_INIT_FAILED",
                "error": mt5.last_error(),
                "terminal_path": str(terminal) if terminal else None,
            }, indent=2))
            return 2

    try:
        discovered = discover_symbols([x.strip().upper() for x in args.symbols.split(",") if x.strip()])
        usable = {k: v for k, v in discovered.items() if v["symbol"]}

        end = datetime.now(timezone.utc) if not args.end else datetime.fromisoformat(args.end.replace("Z", "+00:00"))
        start = (
            end - timedelta(days=args.days)
            if not args.start
            else datetime.fromisoformat(args.start.replace("Z", "+00:00"))
        )

        report = {
            "status": "RESEARCH_ONLY",
            "source": "CONNECTED_MT5_TERMINAL",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "requested_bases": [x.strip().upper() for x in args.symbols.split(",") if x.strip()],
            "resolved_symbols": discovered,
            "period": {"start_utc": start.isoformat(), "end_utc": end.isoformat()},
            "timeframe": "M1",
            "geometry": {
                "p_gap_price": P_GAP_PRICE,
                "spike_multiplier": SPIKE_MULTIPLIER,
                "max_sl_distance": MAX_SL_DISTANCE,
                "tp_r": TP_R,
                "canonical": False,
            },
            "outcomes": {},
            "notes": [
                "Historical bars are pulled directly from the connected MT5 terminal at run time.",
                "This is not a broker-independent tick backtest; it uses MT5 M1 OHLC history.",
                "Pending-limit fill semantics remain unresolved: a bar is eligible only if it reaches the theoretical entry.",
                "History completeness is edge-aware: recurring observed daily data edges may explain outside-session request boundaries; same-day M1 gaps are retained as data-quality events and signals crossing them are excluded from decisive performance.",
                "MT5 Python API does not expose symbol session-trade intervals in this environment; observed history coverage is descriptive only and is not a canonical Strategy A session rule.",
                "If one M1 candle touches both SL and TP, the result is AMBIGUOUS rather than guessed.",
                "The detector is the existing author-replica research detector; this run does not promote geometry to canonical.",
            ],
        }

        combined_results = []
        for base, meta in usable.items():
            symbol = meta["symbol"]
            print(f"[MT5] {base} -> {symbol}: downloading M1 history ...", flush=True)
            try:
                rates = fetch_rates(symbol, start, end)
                result = run_symbol(symbol, rates)
                result["history_chunks"] = fetch_rates.last_diagnostics
                report["outcomes"][base] = result
                combined_results.extend(
                    {"base": base, **x} for x in result["signals_detail"]
                    if x["result"] in ("WIN", "LOSS")
                )
                print(
                    f"[DONE] {base} -> {symbol}: bars={result['bars']} signals={result['signals']} "
                    f"decisive={result['decisive']} WR={result['win_rate_pct']}",
                    flush=True,
                )
            except Exception as exc:
                report["outcomes"][base] = {"status": "FAILED", "symbol": symbol, "error": str(exc)}
                print(f"[FAILED] {base} -> {symbol}: {exc}", flush=True)

        combined_results.sort(key=lambda x: (int(x["signal_time"]), x["base"]))
        wins = sum(x["result"] == "WIN" for x in combined_results)
        losses = sum(x["result"] == "LOSS" for x in combined_results)
        dd, max_losses = max_drawdown_and_losses([1.0 if x["result"] == "WIN" else -1.0 for x in combined_results])
        lo, hi = wilson(wins, wins + losses)
        report["combined"] = {
            "decisive": wins + losses,
            "wins": wins,
            "losses": losses,
            "win_rate_pct": 100 * wins / (wins + losses) if wins + losses else None,
            "wilson_95_ci_pct": [lo, hi],
            "net_r": wins - losses,
            "profit_factor_simplified": wins / losses if losses else None,
            "max_drawdown_r": dd,
            "max_consecutive_losses": max_losses,
        }

        failed = [k for k, v in report["outcomes"].items() if v.get("status") == "FAILED"]
        report["status"] = "COMPLETE" if not failed else "INCOMPLETE_HISTORY"
        report["failed_symbols"] = failed

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = OUT_DIR / f"SP2L_MT5_LOCAL_MULTI_SYMBOL_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        print(json.dumps({
            "status": report["status"],
            "report": str(path),
            "resolved_symbols": {k: v["symbol"] for k, v in discovered.items()},
            "combined": report["combined"],
        }, indent=2))
        return 0 if not failed else 3
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
