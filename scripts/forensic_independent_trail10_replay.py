#!/usr/bin/env python3
"""
Independent raw-M1 replay audit for the non-canonical SP2L V2 MT5 trail experiment.

This is deliberately separate from the MQL5 EA implementation. It:
1) fetches raw M1 OHLC from MetaTrader 5,
2) reconstructs the same signal population,
3) independently replays RR=1 with trailing,
4) compares every trade against the MT5 tester CSV.

No pandas is required.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Bar:
    time: int
    open: float
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class Signal:
    index: int
    setup_index: int
    entry_index: int
    setup_time: int
    entry_time: int
    direction: str
    entry: float
    sl: float
    risk: float


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="XAUUSD.ecn")
    p.add_argument("--mt5-path", required=True)
    p.add_argument("--csv", required=True)
    p.add_argument("--start", default="2025-09-25T00:00:00Z")
    p.add_argument("--end", default="2026-09-25T00:00:00Z")
    p.add_argument("--pgap", type=float, default=1.0)
    p.add_argument("--spike-mult", type=float, default=1.5)
    p.add_argument("--max-sl", type=float, default=10.0)
    p.add_argument("--rr", type=float, default=1.0)
    p.add_argument("--trail-price", type=float, default=1.0,
                   help="Trailing distance in XAU price. MT5 InpTrailPips=10 => 1.0.")
    p.add_argument("--output-json", default="")
    p.add_argument("--output-csv", default="")
    p.add_argument("--tol", type=float, default=1e-8)
    return p.parse_args()


def parse_utc(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def epoch(value: str) -> int:
    return int(parse_utc(value).timestamp())


def body(c: Bar, direction: str) -> float:
    return c.close - c.open if direction == "BUY" else c.open - c.close


def setup(bars: list[Bar], i: int, direction: str, pgap: float, spike_mult: float) -> bool:
    if i < 2:
        return False
    before, spike, after = bars[i - 2], bars[i - 1], bars[i]

    if direction == "BUY":
        return (
            after.close > spike.close
            and after.open > spike.open
            and spike.close > before.close
            and spike.open > before.open
            and after.close > after.open
            and spike.close > spike.open
            and before.close > before.open
            and after.low > before.high + pgap
            and body(spike, "BUY") > spike_mult * body(before, "BUY")
            and body(spike, "BUY") > spike_mult * body(after, "BUY")
        )

    return (
        after.close < spike.close
        and after.open < spike.open
        and spike.close < before.close
        and spike.open < before.open
        and after.close < after.open
        and spike.close < spike.open
        and before.close < before.open
        and after.high < before.low - pgap
        and body(spike, "SELL") > spike_mult * body(before, "SELL")
        and body(spike, "SELL") > spike_mult * body(after, "SELL")
    )


def build_signals(
    bars: list[Bar], pgap: float, spike_mult: float, max_sl: float
) -> list[Signal]:
    out: list[Signal] = []
    for i in range(2, len(bars)):
        buy = setup(bars, i, "BUY", pgap, spike_mult)
        sell = setup(bars, i, "SELL", pgap, spike_mult)
        if buy == sell:
            continue

        direction = "BUY" if buy else "SELL"
        sl = bars[i - 2].low if buy else bars[i - 2].high

        for j in range(i + 1, len(bars)):
            entry = bars[j].low if buy else bars[j].high
            trigger = entry < bars[j - 1].low if buy else entry > bars[j - 1].high
            if not trigger:
                continue

            risk = entry - sl if buy else sl - entry
            if risk <= 0.0 or risk > max_sl:
                break

            out.append(
                Signal(
                    index=len(out) + 1,
                    setup_index=i,
                    entry_index=j,
                    setup_time=bars[i].time,
                    entry_time=bars[j].time,
                    direction=direction,
                    entry=entry,
                    sl=sl,
                    risk=risk,
                )
            )
            break
    return out


def replay_signal(
    bars: list[Bar], signal: Signal, rr: float, trail_price: float
) -> dict[str, Any]:
    risk = abs(signal.entry - signal.sl)
    tp = (
        signal.entry + rr * risk
        if signal.direction == "BUY"
        else signal.entry - rr * risk
    )
    current_sl = signal.sl
    best = signal.entry
    trail_active = False

    for i in range(signal.entry_index, len(bars)):
        b = bars[i]

        if signal.direction == "BUY":
            sl_hit = b.low <= current_sl
            tp_hit = b.high >= tp

            if sl_hit and tp_hit:
                return {
                    "result": "AMBIGUOUS",
                    "r": 0.0,
                    "exit_index": i,
                    "exit_time": b.time,
                    "trailing_activated": trail_active,
                }
            if sl_hit:
                r = (current_sl - signal.entry) / risk
                result = "WIN" if r > 0 else "LOSS" if r < 0 else "BREAKEVEN"
                return {
                    "result": result,
                    "r": r,
                    "exit_index": i,
                    "exit_time": b.time,
                    "trailing_activated": trail_active,
                }
            if tp_hit:
                return {
                    "result": "WIN",
                    "r": rr,
                    "exit_index": i,
                    "exit_time": b.time,
                    "trailing_activated": trail_active,
                }

            best = max(best, b.high)
            if not trail_active and best >= signal.entry + trail_price:
                trail_active = True
            if trail_active:
                current_sl = max(current_sl, best - trail_price)

        else:
            sl_hit = b.high >= current_sl
            tp_hit = b.low <= tp

            if sl_hit and tp_hit:
                return {
                    "result": "AMBIGUOUS",
                    "r": 0.0,
                    "exit_index": i,
                    "exit_time": b.time,
                    "trailing_activated": trail_active,
                }
            if sl_hit:
                r = (signal.entry - current_sl) / risk
                result = "WIN" if r > 0 else "LOSS" if r < 0 else "BREAKEVEN"
                return {
                    "result": result,
                    "r": r,
                    "exit_index": i,
                    "exit_time": b.time,
                    "trailing_activated": trail_active,
                }
            if tp_hit:
                return {
                    "result": "WIN",
                    "r": rr,
                    "exit_index": i,
                    "exit_time": b.time,
                    "trailing_activated": trail_active,
                }

            best = min(best, b.low)
            if not trail_active and best <= signal.entry - trail_price:
                trail_active = True
            if trail_active:
                current_sl = min(current_sl, best + trail_price)

    return {
        "result": "OPEN_OR_UNRESOLVED",
        "r": 0.0,
        "exit_index": -1,
        "exit_time": None,
        "trailing_activated": trail_active,
    }


def fetch_bars(symbol: str, mt5_path: str, start: int, end: int) -> list[Bar]:
    try:
        import MetaTrader5 as mt5
    except Exception as exc:
        raise RuntimeError(
            "MetaTrader5 Python package is required in the active venv."
        ) from exc

    ok = mt5.initialize(path=mt5_path)
    if not ok:
        raise RuntimeError(f"mt5.initialize failed: {mt5.last_error()}")

    try:
        if not mt5.symbol_select(symbol, True):
            raise RuntimeError(f"symbol_select failed for {symbol}: {mt5.last_error()}")

        dt_from = datetime.fromtimestamp(start, tz=timezone.utc)
        dt_to = datetime.fromtimestamp(end, tz=timezone.utc)
        rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, dt_from, dt_to)
        if rates is None:
            raise RuntimeError(f"copy_rates_range failed: {mt5.last_error()}")
        bars = [
            Bar(
                time=int(r["time"]),
                open=float(r["open"]),
                high=float(r["high"]),
                low=float(r["low"]),
                close=float(r["close"]),
            )
            for r in rates
        ]
        return bars
    finally:
        mt5.shutdown()


def load_csv(path: str) -> list[dict[str, str]]:
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def parse_csv_epoch(value: str) -> int:
    normalized = value.strip().replace(".", "-", 2).replace(" ", "T", 1)
    return int(parse_utc(normalized).timestamp())


def nearly_equal(a: float, b: float, tol: float) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tol)


def compare(
    signals: list[Signal],
    replayed: list[dict[str, Any]],
    csv_rows: list[dict[str, str]],
    tol: float,
) -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
    if len(signals) != len(csv_rows):
        mismatches.append(
            {"type": "COUNT", "signals": len(signals), "csv_rows": len(csv_rows)}
        )

    n = min(len(signals), len(csv_rows), len(replayed))
    for k in range(n):
        s = signals[k]
        r = replayed[k]
        row = csv_rows[k]
        expected_sid = f"{k+1}_{s.entry_time}_{s.direction}"
        checks = {
            "signal_id": row.get("signal_id") == expected_sid,
            "setup_time": parse_csv_epoch(row["setup_time_utc"]) == s.setup_time,
            "entry_time": parse_csv_epoch(row["entry_time_utc"]) == s.entry_time,
            "direction": row["direction"] == s.direction,
            "entry": nearly_equal(float(row["entry"]), s.entry, tol),
            "sl": nearly_equal(float(row["sl"]), s.sl, tol),
            "risk": nearly_equal(float(row["risk"]), s.risk, tol),
            "result": row["result"] == r["result"],
            "r": nearly_equal(float(row["r"]), float(r["r"]), tol),
            "trailing_activated": row["trailing_activated"] == ("1" if r["trailing_activated"] else "0"),
        }
        if not all(checks.values()):
            mismatches.append(
                {
                    "row": k + 1,
                    "signal_id": expected_sid,
                    "checks": checks,
                    "csv": row,
                    "replay": {
                        "result": r["result"],
                        "r": r["r"],
                        "exit_time": r["exit_time"],
                        "trailing_activated": r["trailing_activated"],
                    },
                    "signal": asdict(s),
                }
            )

    expected_counts: dict[str, int] = {}
    for r in replayed:
        expected_counts[r["result"]] = expected_counts.get(r["result"], 0) + 1
    csv_counts: dict[str, int] = {}
    for row in csv_rows:
        csv_counts[row["result"]] = csv_counts.get(row["result"], 0) + 1

    replay_net_r = sum(
        float(r["r"])
        for r in replayed
        if r["result"] in {"WIN", "LOSS", "BREAKEVEN"}
    )
    csv_net_r = sum(
        float(row["r"])
        for row in csv_rows
        if row["result"] in {"WIN", "LOSS", "BREAKEVEN"}
    )

    return {
        "PASS": len(mismatches) == 0,
        "signal_count": len(signals),
        "csv_row_count": len(csv_rows),
        "mismatch_count": len(mismatches),
        "replay_counts": expected_counts,
        "csv_counts": csv_counts,
        "replay_net_R": replay_net_r,
        "csv_net_R": csv_net_r,
        "net_R_delta": replay_net_r - csv_net_r,
        "mismatches": mismatches[:100],
    }


def main() -> int:
    args = parse_args()
    start = epoch(args.start)
    end = epoch(args.end)

    if not os.path.exists(args.csv):
        raise SystemExit(f"CSV not found: {args.csv}")
    if not os.path.exists(args.mt5_path):
        raise SystemExit(f"MT5 terminal not found: {args.mt5_path}")

    print("INDEPENDENT_SP2L_TRAIL_REPLAY")
    print(f"symbol={args.symbol}")
    print(f"start_utc={datetime.fromtimestamp(start, tz=timezone.utc).isoformat()}")
    print(f"end_utc={datetime.fromtimestamp(end, tz=timezone.utc).isoformat()}")
    print(f"trail_price={args.trail_price}")

    bars = fetch_bars(args.symbol, args.mt5_path, start, end)
    print(f"bars={len(bars)}")
    if not bars:
        raise SystemExit("No M1 bars returned.")

    signals = build_signals(bars, args.pgap, args.spike_mult, args.max_sl)
    print(f"signals={len(signals)}")

    replayed = [replay_signal(bars, s, args.rr, args.trail_price) for s in signals]
    csv_rows = load_csv(args.csv)
    report = compare(signals, replayed, csv_rows, args.tol)

    report.update(
        {
            "mode": "NON_CANONICAL_FORENSIC_INDEPENDENT_REPLAY",
            "canonical": False,
            "symbol": args.symbol,
            "start_utc": datetime.fromtimestamp(start, tz=timezone.utc).isoformat(),
            "end_utc": datetime.fromtimestamp(end, tz=timezone.utc).isoformat(),
            "bars": len(bars),
            "pgap": args.pgap,
            "spike_multiplier": args.spike_mult,
            "max_sl": args.max_sl,
            "rr": args.rr,
            "trail_price": args.trail_price,
            "source_csv": os.path.abspath(args.csv),
            "same_bar_policy": "AMBIGUOUS when active SL and TP both touched",
            "intrabar_order": "NOT_INFERRED_FROM_M1_OHLC",
        }
    )

    print(json.dumps(report, indent=2, sort_keys=True))

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=True)

    if args.output_csv:
        with open(args.output_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["row", "signal_id", "result", "r", "exit_time_utc", "trailing_activated"])
            for k, (s, r) in enumerate(zip(signals, replayed), start=1):
                exit_ts = (
                    datetime.fromtimestamp(r["exit_time"], tz=timezone.utc).isoformat()
                    if r["exit_time"] is not None
                    else ""
                )
                w.writerow([
                    k,
                    f"{k}_{s.entry_time}_{s.direction}",
                    r["result"],
                    f'{r["r"]:.12f}',
                    exit_ts,
                    "1" if r["trailing_activated"] else "0",
                ])

    return 0 if report["PASS"] else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
