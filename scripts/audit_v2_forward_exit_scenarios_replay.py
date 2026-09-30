"""Research-only forensic replay of historical V2 Forward exits.

This tool NEVER places/modifies broker orders and does not change canonical
Strategy A geometry. It takes historical Forward lifecycle events and MT5 M1
history and compares hypothetical exit policies on the SAME historical trades.

Scenarios:
- 1R target, no trailing
- 1R target + BE after +1R
- 2R target, no trailing
- 2R target + BE after +1R

The trailing rule is explicitly NON_CANONICAL_FORENSIC: once price reaches
+1R, move the stop to entry. No other trailing definition is assumed.

Intrabar ambiguity is fail-closed: if a bar touches both the active stop and
target (or stop and the BE level needed to change state), the scenario is
marked AMBIGUOUS rather than inventing an execution ordering.

The script uses theoretical SL/entry fields recorded by the Forward runner,
while retaining the actual broker entry/exit for the historical baseline.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

TIMEFRAME = mt5.TIMEFRAME_M1
SCENARIOS = (
    ("R1_NO_TRAIL", 1.0, False),
    ("R1_BE_AT_1R", 1.0, True),
    ("R2_NO_TRAIL", 2.0, False),
    ("R2_BE_AT_1R", 2.0, True),
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--events", required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--symbol", default="XAUUSD.ecn")
    p.add_argument("--mt5-path", default=os.getenv("MT5_TERMINAL_PATH"))
    p.add_argument("--output", required=True)
    return p.parse_args()


def parse_ts(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def load_events(path: str, start: int, end: int, symbol: str):
    """Return historical signal lifecycle records keyed by signal_id."""
    rows = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("event") != "TELEGRAM_DEAL_LIFECYCLE":
            continue
        if e.get("symbol") != symbol or not e.get("signal_id"):
            continue
        ts = parse_ts(str(e.get("ts_utc")))
        if not (start <= ts < end):
            continue

        sid = str(e["signal_id"])
        entry_flag = int(e.get("entry", -1))
        rec = rows.setdefault(sid, {"signal_id": sid, "symbol": symbol})
        rec.setdefault("events", []).append(e)
        if entry_flag == 0:
            rec["entry_event"] = e
        elif entry_flag == 1:
            rec["exit_event"] = e

    trades = []
    for sid, rec in rows.items():
        ent = rec.get("entry_event")
        ex = rec.get("exit_event")
        if not ent or not ex:
            continue
        entry_price = ent.get("entry_price")
        theoretical_entry = ent.get("theoretical_entry")
        theoretical_sl = ent.get("theoretical_sl")
        direction = str(sid.rsplit(":", 1)[-1]).upper()
        if direction not in {"BUY", "SELL"}:
            continue
        if not all(isinstance(x, (int, float)) for x in
                   (entry_price, theoretical_entry, theoretical_sl)):
            continue
        entry_ts = parse_ts(str(ent["ts_utc"]))
        exit_ts = parse_ts(str(ex["ts_utc"]))
        if exit_ts < entry_ts:
            continue
        risk = (float(theoretical_entry) - float(theoretical_sl)
                if direction == "BUY"
                else float(theoretical_sl) - float(theoretical_entry))
        if risk <= 0:
            continue
        trades.append({
            "signal_id": sid,
            "direction": direction,
            "entry_ts": entry_ts,
            "exit_ts": exit_ts,
            "actual_entry": float(entry_price),
            "theoretical_entry": float(theoretical_entry),
            "theoretical_sl": float(theoretical_sl),
            "risk": risk,
            "actual_exit": ex.get("exit_price"),
            "actual_net": ex.get("net"),
            "actual_r": ex.get("actual_r"),
        })
    return sorted(trades, key=lambda x: (x["entry_ts"], x["signal_id"]))


def load_bars(symbol: str, start_ts: int, end_ts: int):
    start = datetime.fromtimestamp(start_ts, timezone.utc) - timedelta(minutes=1)
    end = datetime.fromtimestamp(end_ts, timezone.utc) + timedelta(minutes=1)
    rates = mt5.copy_rates_range(symbol, TIMEFRAME, start, end)
    if rates is None or len(rates) == 0:
        return []
    return [
        {
            "time": int(r["time"]),
            "open": float(r["open"]),
            "high": float(r["high"]),
            "low": float(r["low"]),
            "close": float(r["close"]),
        }
        for r in rates
    ]


def simulate(trade, bars, target_r, trailing, analysis_end_ts):
    d = trade["direction"]
    entry = trade["actual_entry"]
    initial_sl = trade["theoretical_sl"]
    risk = abs(trade["theoretical_entry"] - trade["theoretical_sl"])

    if d == "BUY":
        target = entry + target_r * risk
        be_trigger = entry + risk
        active_sl = initial_sl
    else:
        target = entry - target_r * risk
        be_trigger = entry - risk
        active_sl = initial_sl

    be_armed = False
    path_r = None
    exit_time = None
    status = "OPEN_AT_DATA_END"

    for bar in bars:
        if bar["time"] < trade["entry_ts"]:
            continue
        if bar["time"] > analysis_end_ts:
            break

        if d == "BUY":
            stop_hit = bar["low"] <= active_sl
            target_hit = bar["high"] >= target
            be_hit = trailing and not be_armed and bar["high"] >= be_trigger
        else:
            stop_hit = bar["high"] >= active_sl
            target_hit = bar["low"] <= target
            be_hit = trailing and not be_armed and bar["low"] <= be_trigger

        # If stop and target occur in the same bar, chronology is unknowable
        # from OHLC alone. Do not invent a tie-break.
        if stop_hit and target_hit:
            return {
                "status": "AMBIGUOUS_INTRABAR",
                "exit_ts": bar["time"],
                "r": None,
                "reason": "ACTIVE_STOP_AND_TARGET_TOUCHED_IN_SAME_M1_BAR",
            }

        if be_hit and stop_hit:
            # The bar can both reach the BE trigger and revisit the stop;
            # M1 OHLC does not establish which happened first.
            return {
                "status": "AMBIGUOUS_INTRABAR",
                "exit_ts": bar["time"],
                "r": None,
                "reason": "BE_TRIGGER_AND_STOP_TOUCHED_IN_SAME_M1_BAR",
            }

        if trailing and be_hit:
            be_armed = True
            active_sl = entry

        if stop_hit:
            exit_price = active_sl
            path_r = ((exit_price - entry) / risk if d == "BUY"
                      else (entry - exit_price) / risk)
            exit_time = bar["time"]
            status = "STOP"
            break

        if target_hit:
            exit_price = target
            path_r = target_r
            exit_time = bar["time"]
            status = "TARGET"
            break

    if status == "OPEN_AT_DATA_END":
        # For a historical completed trade, the bar replay should normally
        # reach an exit. Keep it explicit instead of using the actual exit
        # price to manufacture a hypothetical scenario result.
        return {
            "status": status,
            "exit_ts": None,
            "r": None,
            "reason": "NO_HYPOTHETICAL_EXIT_BEFORE_ANALYSIS_END",
        }

    return {
        "status": status,
        "exit_ts": exit_time,
        "r": path_r,
        "reason": None,
    }


def summarize(results):
    decisive = [r for r in results if r["status"] in {"STOP", "TARGET"}]
    wins = [r for r in decisive if r["r"] > 0]
    losses = [r for r in decisive if r["r"] < 0]
    rs = [float(r["r"]) for r in decisive]
    gross_win = sum(r for r in rs if r > 0)
    gross_loss = -sum(r for r in rs if r < 0)
    pf = gross_win / gross_loss if gross_loss else None

    max_dd = 0.0
    equity = 0.0
    peak = 0.0
    for r in rs:
        equity += r
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)

    max_losing_streak = 0
    streak = 0
    for r in rs:
        if r < 0:
            streak += 1
            max_losing_streak = max(max_losing_streak, streak)
        else:
            streak = 0

    return {
        "trades": len(results),
        "decisive": len(decisive),
        "ambiguous": sum(r["status"] == "AMBIGUOUS_INTRABAR" for r in results),
        "open_at_data_end": sum(r["status"] == "OPEN_AT_DATA_END" for r in results),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate_pct": (100.0 * len(wins) / len(decisive)) if decisive else None,
        "net_r": sum(rs),
        "profit_factor": pf,
        "max_drawdown_r": max_dd,
        "max_losing_streak": max_losing_streak,
        "avg_r_per_decisive_trade": (sum(rs) / len(rs)) if rs else None,
    }


def main():
    args = parse_args()
    start_ts = parse_ts(args.start)
    end_ts = parse_ts(args.end)

    trades = load_events(args.events, start_ts, end_ts, args.symbol)
    if not trades:
        raise SystemExit("No completed historical Forward lifecycle trades found in requested window.")

    initialized = mt5.initialize(path=args.mt5_path) if args.mt5_path else mt5.initialize()
    if not initialized:
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        scenario_rows = {name: [] for name, _, _ in SCENARIOS}
        for trade in trades:
            bars = load_bars(args.symbol, trade["entry_ts"], end_ts)
            if not bars:
                for name, _, _ in SCENARIOS:
                    scenario_rows[name].append({
                        "signal_id": trade["signal_id"],
                        "status": "NO_MT5_M1_HISTORY",
                        "r": None,
                    })
                continue

            for name, target_r, trailing in SCENARIOS:
                outcome = simulate(trade, bars, target_r, trailing, end_ts)
                scenario_rows[name].append({
                    "signal_id": trade["signal_id"],
                    "direction": trade["direction"],
                    "entry_ts": trade["entry_ts"],
                    "exit_ts_historical": trade["exit_ts"],
                    "actual_r_historical": trade["actual_r"],
                    "actual_net_historical": trade["actual_net"],
                    "theoretical_entry": trade["theoretical_entry"],
                    "theoretical_sl": trade["theoretical_sl"],
                    "actual_entry": trade["actual_entry"],
                    "risk": trade["risk"],
                    **outcome,
                })
    finally:
        mt5.shutdown()

    report = {
        "status": "COMPLETE",
        "mode": "NON_CANONICAL_FORENSIC",
        "scope": {
            "symbol": args.symbol,
            "start_utc": args.start,
            "end_utc": args.end,
            "timeframe": "M1",
            "historical_trades": len(trades),
        },
        "historical_baseline": summarize([
            {
                "status": "TARGET" if (t["actual_r"] is not None and float(t["actual_r"]) > 0)
                          else "STOP",
                "r": float(t["actual_r"]) if t["actual_r"] is not None else 0.0,
            }
            for t in trades if t["actual_r"] is not None
        ]),
        "trailing_definition": {
            "name": "BE_AT_1R",
            "rule": "When price first reaches +1R from actual broker entry, move stop to actual broker entry.",
            "canonical": False,
        },
        "scenarios": {
            name: {
                "policy": {
                    "target_r": target_r,
                    "trailing": trailing,
                    "canonical": False,
                },
                "summary": summarize(rows),
                "trades": rows,
            }
            for (name, target_r, trailing), rows in zip(SCENARIOS, [scenario_rows[n] for n, _, _ in SCENARIOS])
        },
        "limitations": [
            "Historical Forward lifecycle events are the population; this does not discover new signals.",
            "Hypothetical exits use actual broker entry plus the runner-recorded theoretical SL.",
            "M1 OHLC cannot establish intrabar event ordering; ambiguous bars are excluded from decisive results.",
            "The trailing definition is a forensic scenario only and is not a canonical Strategy A rule.",
            "The current live Forward process is not modified by this audit.",
        ],
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "mode": report["mode"],
        "historical_trades": len(trades),
        "output": args.output,
        "scenario_summaries": {
            name: report["scenarios"][name]["summary"] for name, _, _ in SCENARIOS
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
