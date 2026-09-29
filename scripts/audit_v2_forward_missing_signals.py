"""Deterministic forensic audit for backtest signals missing from V2 forward events.

Research-only. This tool does not alter detector geometry or execution semantics.

For each backtest signal absent from the forward event log, it reconstructs the
exact runner's 10-bar polling view around the signal trigger and classifies
whether the signal was:

- VISIBLE_AT_TRIGGER: the runner's 10-bar window can produce that signal when
  the trigger bar is the latest completed bar.
- VISIBLE_BUT_LATER_CANDIDATE_REPLACES: the signal is visible after the trigger,
  but find_latest_candidate selects a newer candidate before the signal can be
  observed.
- NOT_VISIBLE_IN_10_BAR_LOOKBACK: the runner's current 10-bar history cannot
  reproduce the backtest signal at the trigger.
- NOT_REPRODUCED_FROM_MT5_HISTORY: the current MT5 history does not reproduce
  the signal under the runner's exact detector.
- NO_POST_TRIGGER_WINDOW: insufficient historical bars were returned.

The tool intentionally does not claim why a live process missed a signal when
the historical reconstruction cannot establish that fact. Runtime polling,
process uptime, and state suppression require forward telemetry evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

TIMEFRAME = mt5.TIMEFRAME_M1
P_GAP_PRICE = 1.0
SPIKE_MULTIPLIER = 1.5
MAX_SL_DISTANCE = 10.0
TP_R = 1.0
LOOKBACK_BARS = 10


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--backtest", required=True)
    p.add_argument("--events", required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--symbol", default="XAUUSD.ecn")
    p.add_argument("--mt5-path", default=os.getenv("MT5_TERMINAL_PATH"))
    return p.parse_args()


def epoch(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def load_backtest(path: str, symbol: str, start: int, end: int):
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    details = (data.get("outcomes") or {}).get("signals_detail") or []
    rows = []
    for row in details:
        if str(row.get("symbol")) != symbol:
            continue
        ts = int(row.get("entry_time", row.get("trigger_time", 0)) or 0)
        if start <= ts < end:
            direction = str(row.get("direction", "")).upper()
            rows.append(
                {
                    "signal_id": f"{symbol}:{ts}:{direction}",
                    "trigger_time": ts,
                    "direction": direction,
                    "result": row.get("result"),
                }
            )
    return rows


def load_forward_ids(path: str):
    ids = set()
    if not Path(path).exists():
        return ids
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("event") in {"CANDIDATE", "ORDER_RESULT"} and event.get("signal_id"):
            ids.add(str(event["signal_id"]))
    return ids


def detect(candles, symbol: str):
    if candles is None or len(candles) < 3:
        return None
    before, spike, after = candles[-3], candles[-2], candles[-1]
    ao, ah, al, ac = map(float, (before["open"], before["high"], before["low"], before["close"]))
    bo, bh, bl, bc = map(float, (spike["open"], spike["high"], spike["low"], spike["close"]))
    co, ch, cl, cc = map(float, (after["open"], after["high"], after["low"], after["close"]))
    before_body = abs(ac - ao)
    spike_body = abs(bc - bo)
    after_body = abs(cc - co)
    buy = (
        cc > bc and co > bo and bc > ac and bo > ao and
        cc > co and bc > bo and ac > ao and
        cl > ah + P_GAP_PRICE and
        spike_body > SPIKE_MULTIPLIER * before_body and
        spike_body > SPIKE_MULTIPLIER * after_body
    )
    sell = (
        cc < bc and co < bo and bc < ac and bo < ao and
        cc < co and bc < bo and ac < ao and
        ch < al - P_GAP_PRICE and
        spike_body > SPIKE_MULTIPLIER * before_body and
        spike_body > SPIKE_MULTIPLIER * after_body
    )
    if buy == sell:
        return None
    return {"direction": "BUY" if buy else "SELL", "setup_end": int(after["time"]), "symbol": symbol}


def find_first_entry(candles, start_index: int, setup: dict):
    direction = setup["direction"]
    for j in range(start_index + 1, len(candles)):
        prev = candles[j - 1]
        cur = candles[j]
        if direction == "BUY":
            if float(cur["low"]) >= float(prev["low"]):
                continue
            entry = float(cur["low"])
            sl = float(candles[start_index - 2]["low"])
            risk = entry - sl
            if risk <= 0 or risk > MAX_SL_DISTANCE:
                return None
            return {
                "direction": "BUY",
                "trigger_time": int(cur["time"]),
                "theoretical_entry": entry,
                "sl": sl,
                "risk": risk,
                "tp": entry + TP_R * risk,
                "symbol": setup["symbol"],
            }
        if float(cur["high"]) <= float(prev["high"]):
            continue
        entry = float(cur["high"])
        sl = float(candles[start_index - 2]["high"])
        risk = sl - entry
        if risk <= 0 or risk > MAX_SL_DISTANCE:
            return None
        return {
            "direction": "SELL",
            "trigger_time": int(cur["time"]),
            "theoretical_entry": entry,
            "sl": sl,
            "risk": risk,
            "tp": entry - TP_R * risk,
            "symbol": setup["symbol"],
        }
    return None


def find_latest_candidate(candles, symbol: str):
    candidates = []
    for setup_end in range(2, len(candles) - 1):
        setup = detect(candles[setup_end - 2:setup_end + 1], symbol)
        if not setup:
            continue
        candidate = find_first_entry(candles, setup_end, setup)
        if candidate is not None:
            candidates.append(candidate)
    return max(candidates, key=lambda x: (int(x["trigger_time"]), x["direction"])) if candidates else None


def candidate_id(candidate):
    return f"{candidate['symbol']}:{candidate['trigger_time']}:{candidate['direction']}"


def classify_signal(rows, target):
    target_ts = target["trigger_time"]
    target_id = target["signal_id"]
    exact = [r for r in rows if candidate_id(r) == target_id]
    if exact:
        return "VISIBLE_AT_TRIGGER", target_id, 0

    newer = [r for r in rows if int(r["trigger_time"]) > target_ts]
    if newer:
        latest = max(newer, key=lambda x: (int(x["trigger_time"]), x["direction"]))
        return "VISIBLE_BUT_LATER_CANDIDATE_REPLACES", candidate_id(latest), int(latest["trigger_time"] - target_ts)

    return "NO_MATCH", None, None


def audit_signal(symbol: str, target_ts: int, target_id: str):
    start_dt = datetime.fromtimestamp(target_ts, timezone.utc) - timedelta(minutes=15)
    end_dt = datetime.fromtimestamp(target_ts, timezone.utc) + timedelta(minutes=12)
    rates = mt5.copy_rates_range(symbol, TIMEFRAME, start_dt, end_dt)
    if rates is None or len(rates) == 0:
        return {
            "classification": "NOT_REPRODUCED_FROM_MT5_HISTORY",
            "target_signal_id": target_id,
            "bars_returned": 0,
        }

    bars = [row for row in rates if int(row["time"]) <= target_ts + 10 * 60]
    at_trigger = [row for row in bars if int(row["time"]) <= target_ts][-LOOKBACK_BARS:]
    target_candidate = find_latest_candidate(at_trigger, symbol)

    if target_candidate is not None and candidate_id(target_candidate) == target_id:
        return {
            "classification": "VISIBLE_AT_TRIGGER",
            "target_signal_id": target_id,
            "bars_returned": len(rates),
            "window_bars_at_trigger": len(at_trigger),
            "selected_at_trigger": candidate_id(target_candidate),
        }

    full_after = [row for row in rates if int(row["time"]) <= target_ts + 10 * 60]
    snapshots = []
    times = sorted({int(row["time"]) for row in full_after if int(row["time"]) >= target_ts})
    for snap_ts in times:
        window = [row for row in full_after if int(row["time"]) <= snap_ts][-LOOKBACK_BARS:]
        selected = find_latest_candidate(window, symbol)
        if selected is not None:
            snapshots.append((snap_ts, selected))

    for snap_ts, selected in snapshots:
        if candidate_id(selected) == target_id:
            return {
                "classification": "VISIBLE_AFTER_TRIGGER",
                "target_signal_id": target_id,
                "bars_returned": len(rates),
                "first_selected_time": snap_ts,
                "first_selected_id": target_id,
            }

    newer = [(ts, c) for ts, c in snapshots if int(c["trigger_time"]) > target_ts]
    if newer:
        ts, selected = newer[0]
        return {
            "classification": "VISIBLE_BUT_LATER_CANDIDATE_REPLACES",
            "target_signal_id": target_id,
            "bars_returned": len(rates),
            "replacement_signal_id": candidate_id(selected),
            "replacement_trigger_time": int(selected["trigger_time"]),
            "replacement_seen_at": ts,
        }

    # Re-run the complete local history through the target time. If the exact
    # target never appears, distinguish missing lookback from geometry/history.
    full_to_trigger = [row for row in rates if int(row["time"]) <= target_ts]
    complete_candidates = []
    for setup_end in range(2, len(full_to_trigger) - 1):
        setup = detect(full_to_trigger[setup_end - 2:setup_end + 1], symbol)
        if not setup:
            continue
        c = find_first_entry(full_to_trigger, setup_end, setup)
        if c is not None:
            complete_candidates.append(c)
    if any(candidate_id(c) == target_id for c in complete_candidates):
        return {
            "classification": "NOT_VISIBLE_IN_10_BAR_LOOKBACK",
            "target_signal_id": target_id,
            "bars_returned": len(rates),
            "complete_history_reproduces": True,
        }

    return {
        "classification": "NOT_REPRODUCED_FROM_MT5_HISTORY",
        "target_signal_id": target_id,
        "bars_returned": len(rates),
        "complete_history_reproduces": False,
    }


def main():
    args = parse_args()
    start = epoch(args.start)
    end = epoch(args.end)
    backtest = load_backtest(args.backtest, args.symbol, start, end)
    forward_ids = load_forward_ids(args.events)
    missing = [r for r in backtest if r["signal_id"] not in forward_ids]

    mt5_path = args.mt5_path
    initialized = mt5.initialize(path=mt5_path) if mt5_path else mt5.initialize()
    if not initialized:
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        rows = []
        for target in missing:
            result = audit_signal(args.symbol, target["trigger_time"], target["signal_id"])
            rows.append({**target, **result})
    finally:
        mt5.shutdown()

    counts = {}
    for row in rows:
        counts[row["classification"]] = counts.get(row["classification"], 0) + 1

    report = {
        "status": "COMPLETE",
        "scope": {
            "symbol": args.symbol,
            "start_utc": args.start,
            "end_utc": args.end,
            "lookback_bars": LOOKBACK_BARS,
            "p_gap_price": P_GAP_PRICE,
            "spike_multiplier": SPIKE_MULTIPLIER,
            "max_sl_distance": MAX_SL_DISTANCE,
            "tp_r": TP_R,
        },
        "population": {
            "backtest_signals": len(backtest),
            "forward_signal_ids": len(forward_ids),
            "missing_signals": len(missing),
        },
        "classification_counts": counts,
        "signals": rows,
        "semantic_limit": (
            "Historical reconstruction only. A VISIBLE_AT_TRIGGER result does not "
            "prove the live process polled at that instant; it establishes that the "
            "runner's exact 10-bar detector could have observed the signal."
        ),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
