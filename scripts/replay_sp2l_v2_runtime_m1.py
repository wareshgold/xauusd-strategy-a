#!/usr/bin/env python3
"""Deterministic non-canonical SP2L V2 replay on runtime-generated MT5 M1 CSV.

This intentionally mirrors the legacy forensic MT5 tester contract in
experts/forensic/Sp2lV2Mt5Tester/Sp2lV2Mt5Tester.mq5.

It does NOT define canonical Strategy A geometry.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Bar:
    epoch: int
    open: float
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class Signal:
    setup_index: int
    entry_index: int
    setup_epoch: int
    entry_epoch: int
    direction: str
    entry: float
    sl: float
    risk: float


def body(c: Bar, direction: str) -> float:
    return c.close - c.open if direction == "BUY" else c.open - c.close


def setup(rates: list[Bar], i: int, direction: str, pgap: float, spike_mult: float) -> bool:
    if i < 2:
        return False
    before, spike, after = rates[i - 2], rates[i - 1], rates[i]

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


def build_signal(
    rates: list[Bar], setup_index: int, pgap: float, spike_mult: float, max_sl: float
) -> Signal | None:
    buy = setup(rates, setup_index, "BUY", pgap, spike_mult)
    sell = setup(rates, setup_index, "SELL", pgap, spike_mult)
    if buy == sell:
        return None

    direction = "BUY" if buy else "SELL"
    sl = rates[setup_index - 2].low if buy else rates[setup_index - 2].high

    for j in range(setup_index + 1, len(rates)):
        entry = rates[j].low if buy else rates[j].high
        trigger = entry < rates[j - 1].low if buy else entry > rates[j - 1].high
        if not trigger:
            continue

        risk = entry - sl if buy else sl - entry
        if risk <= 0.0 or risk > max_sl:
            return None

        return Signal(
            setup_index=setup_index,
            entry_index=j,
            setup_epoch=rates[setup_index].epoch,
            entry_epoch=rates[j].epoch,
            direction=direction,
            entry=entry,
            sl=sl,
            risk=risk,
        )

    return None


def result_for_signal(
    rates: list[Bar], s: Signal, rr: float, trail_pips: float
) -> tuple[str, float, int | None, bool]:
    risk = abs(s.entry - s.sl)
    tp = s.entry + rr * risk if s.direction == "BUY" else s.entry - rr * risk
    current_sl = s.sl
    best = s.entry
    trail = trail_pips * 0.10
    trailing_enabled = trail_pips > 0.0
    trail_active = False

    for i in range(s.entry_index, len(rates)):
        high, low = rates[i].high, rates[i].low

        if s.direction == "BUY":
            sl_hit = low <= current_sl
            tp_hit = high >= tp
            if sl_hit and tp_hit:
                return "AMBIGUOUS", 0.0, i, trail_active
            if sl_hit:
                r = (current_sl - s.entry) / risk
                if r > 0:
                    return "WIN", r, i, trail_active
                if r < 0:
                    return "LOSS", r, i, trail_active
                return "BREAKEVEN", 0.0, i, trail_active
            if tp_hit:
                return "WIN", rr, i, trail_active

            if trailing_enabled:
                best = max(best, high)
                if not trail_active and best >= s.entry + trail:
                    trail_active = True
                if trail_active:
                    current_sl = max(current_sl, best - trail)

        else:
            sl_hit = high >= current_sl
            tp_hit = low <= tp
            if sl_hit and tp_hit:
                return "AMBIGUOUS", 0.0, i, trail_active
            if sl_hit:
                r = (s.entry - current_sl) / risk
                if r > 0:
                    return "WIN", r, i, trail_active
                if r < 0:
                    return "LOSS", r, i, trail_active
                return "BREAKEVEN", 0.0, i, trail_active
            if tp_hit:
                return "WIN", rr, i, trail_active

            if trailing_enabled:
                best = min(best, low)
                if not trail_active and best <= s.entry - trail:
                    trail_active = True
                if trail_active:
                    current_sl = min(current_sl, best + trail)

    return "OPEN_OR_UNRESOLVED", 0.0, None, trail_active


def load_csv(path: Path) -> tuple[list[Bar], str]:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)

    rates: list[Bar] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"epoch_utc", "time_utc", "open", "high", "low", "close"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise RuntimeError(f"missing columns: {sorted(missing)}")

        for row in reader:
            rates.append(
                Bar(
                    epoch=int(row["epoch_utc"]),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                )
            )

    return rates, digest.hexdigest()


def utc(epoch: int | None) -> str:
    if epoch is None:
        return ""
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, type=Path)
    ap.add_argument("--output-dir", type=Path, default=Path("artifacts/forensic/runtime-m1-replay"))
    ap.add_argument("--pgap", type=float, default=1.0)
    ap.add_argument("--spike-mult", type=float, default=1.5)
    ap.add_argument("--max-sl", type=float, default=10.0)
    ap.add_argument("--rr", type=float, default=1.0)
    ap.add_argument("--trail-pips", type=float, default=0.0)
    args = ap.parse_args()

    rates, sha256 = load_csv(args.csv)
    if not rates:
        raise RuntimeError("empty CSV")

    signals: list[Signal] = []
    for i in range(2, len(rates)):
        s = build_signal(rates, i, args.pgap, args.spike_mult, args.max_sl)
        if s is not None:
            signals.append(s)

    counts = {"WIN": 0, "LOSS": 0, "BREAKEVEN": 0, "AMBIGUOUS": 0, "OPEN_OR_UNRESOLVED": 0}
    net_r = 0.0
    gross_profit = 0.0
    gross_loss = 0.0
    equity = peak = max_dd = 0.0
    loss_streak = max_loss_streak = 0
    trail_count = 0
    trades = []

    for n, s in enumerate(signals, 1):
        result, r, exit_i, trail_active = result_for_signal(rates, s, args.rr, args.trail_pips)
        counts[result] += 1
        if result in {"WIN", "LOSS", "BREAKEVEN"}:
            net_r += r
            if r > 0:
                gross_profit += r
                loss_streak = 0
            elif r < 0:
                gross_loss += -r
                loss_streak += 1
                max_loss_streak = max(max_loss_streak, loss_streak)
            else:
                loss_streak = 0
            equity += r
            peak = max(peak, equity)
            max_dd = max(max_dd, peak - equity)
        else:
            loss_streak = 0

        if trail_active:
            trail_count += 1

        trades.append(
            {
                "signal_id": n,
                "setup_time_utc": utc(s.setup_epoch),
                "entry_time_utc": utc(s.entry_epoch),
                "direction": s.direction,
                "entry": s.entry,
                "sl": s.sl,
                "risk": s.risk,
                "rr": args.rr,
                "trail_pips": args.trail_pips,
                "result": result,
                "r": r,
                "exit_time_utc": utc(rates[exit_i].epoch) if exit_i is not None else "",
                "trailing_activated": int(trail_active),
                "setup_index": s.setup_index,
                "entry_index": s.entry_index,
                "exit_index": exit_i,
            }
        )

    decisive = counts["WIN"] + counts["LOSS"] + counts["BREAKEVEN"]
    wr = 100.0 * counts["WIN"] / decisive if decisive else 0.0
    pf = gross_profit / gross_loss if gross_loss else 0.0

    summary = {
        "mode": "NON_CANONICAL_FORENSIC",
        "experiment": "SP2L_V2_RUNTIME_M1_INDEPENDENT_REPLAY",
        "input_file": str(args.csv),
        "input_sha256": sha256,
        "bars": len(rates),
        "first_utc": utc(rates[0].epoch),
        "last_utc": utc(rates[-1].epoch),
        "signals": len(signals),
        "decisive": decisive,
        **counts,
        "win_rate_decisive_pct": wr,
        "net_R": net_r,
        "profit_factor": pf,
        "max_drawdown_R": max_dd,
        "max_losing_streak": max_loss_streak,
        "trailing_activated_count": trail_count,
        "p_gap_price": args.pgap,
        "spike_multiplier": args.spike_mult,
        "max_sl_distance": args.max_sl,
        "rr": args.rr,
        "trail_pips": args.trail_pips,
        "trail_zero_semantics": "OFF",
        "same_bar_policy": "AMBIGUOUS when active SL and TP both touched",
        "intrabar_order": "NOT_INFERRED_FROM_M1_OHLC",
        "canonical": False,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    summary_path = args.output_dir / f"SP2L_RUNTIME_M1_REPLAY_{stamp}.json"
    trades_path = args.output_dir / f"SP2L_RUNTIME_M1_REPLAY_TRADES_{stamp}.csv"

    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with trades_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=trades[0].keys() if trades else [
            "signal_id","setup_time_utc","entry_time_utc","direction","entry","sl","risk",
            "rr","trail_pips","result","r","exit_time_utc","trailing_activated",
            "setup_index","entry_index","exit_index"
        ])
        writer.writeheader()
        writer.writerows(trades)

    print(json.dumps(summary, indent=2))
    print(f"SUMMARY_JSON={summary_path}")
    print(f"TRADES_CSV={trades_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
