#!/usr/bin/env python3
"""Audit forward-process runtime coverage for missing V2 backtest signals.

Research-only forensic tool. It does not alter detector, execution, or canonical
Strategy A rules.

For each backtest signal missing from the forward event ledger, this tool uses
HEARTBEAT telemetry to determine whether the forward process demonstrably had
runtime coverage at/after the signal trigger. A positive coverage result proves
only that the process was alive and had observed a bar at or after the trigger;
it does not prove that candidate selection/polling would have emitted that
signal.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--backtest", required=True)
    p.add_argument("--events", required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--symbol", required=True)
    p.add_argument("--coverage-tolerance-seconds", type=int, default=180)
    return p.parse_args()


def ts(s: str) -> int:
    return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())


def event_ts(ev: dict) -> int:
    return ts(str(ev["ts_utc"]))


def signal_id(row: dict, symbol: str) -> str:
    return f"{symbol}:{int(row['entry_time'])}:{row['direction']}"


def main() -> int:
    args = parse_args()
    start = ts(args.start)
    end = ts(args.end)
    backtest = json.loads(Path(args.backtest).read_text(encoding="utf-8-sig"))
    rows = list(backtest.get("outcomes", {}).get("signals_detail", []))

    selected = []
    for row in rows:
        trigger = int(row.get("entry_time", 0) or 0)
        row_symbol = str(row.get("symbol") or args.symbol)
        if row_symbol != args.symbol or not (start <= trigger < end):
            continue
        selected.append({
            "signal_id": signal_id(row, args.symbol),
            "trigger_time": trigger,
            "direction": str(row.get("direction") or ""),
            "result": row.get("result"),
        })

    events = []
    for line in Path(args.events).read_text(encoding="utf-8-sig").splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        events.append(ev)

    forward_ids = {
        str(ev.get("signal_id"))
        for ev in events
        if ev.get("event") in {"CANDIDATE", "ORDER_RESULT"}
        and ev.get("signal_id")
    }
    missing = [x for x in selected if x["signal_id"] not in forward_ids]

    heartbeats = [
        ev for ev in events
        if ev.get("event") == "HEARTBEAT"
        and args.symbol in dict(ev.get("symbols") or {})
    ]
    heartbeats.sort(key=event_ts)

    starts = [
        ev for ev in events
        if ev.get("event") == "START"
        and start <= event_ts(ev) <= end
    ]

    def heartbeat_observation(hb: dict) -> dict:
        sym = dict(hb.get("symbols") or {}).get(args.symbol) or {}
        last_bar = int(sym.get("last_bar_time") or 0)
        return {
            "heartbeat_ts_utc": hb.get("ts_utc"),
            "heartbeat_time": event_ts(hb),
            "last_bar_time": last_bar or None,
            "last_bar_utc": sym.get("last_bar_utc"),
            "pid": hb.get("pid"),
            "uptime_seconds": hb.get("uptime_seconds"),
        }

    results = []
    counts = {
        "PROCESS_COVERED_BUT_NO_CANDIDATE_EVENT": 0,
        "PROCESS_NOT_COVERED": 0,
        "INSUFFICIENT_RUNTIME_TELEMETRY": 0,
    }

    for item in missing:
        trigger = item["trigger_time"]
        prior = [hb for hb in heartbeats if event_ts(hb) <= trigger + args.coverage_tolerance_seconds]
        subsequent = [hb for hb in heartbeats if event_ts(hb) >= trigger]
        # A heartbeat whose recorded last_bar_time reaches the target trigger
        # is positive evidence that the running process had loaded that bar.
        covering = [
            hb for hb in heartbeats
            if int((dict(hb.get("symbols") or {}).get(args.symbol) or {}).get("last_bar_time") or 0) >= trigger
            and event_ts(hb) <= trigger + args.coverage_tolerance_seconds
        ]

        if covering:
            classification = "PROCESS_COVERED_BUT_NO_CANDIDATE_EVENT"
            evidence = heartbeat_observation(min(covering, key=event_ts))
        elif prior or subsequent:
            classification = "PROCESS_NOT_COVERED"
            nearest = min(
                heartbeats,
                key=lambda hb: abs(event_ts(hb) - trigger),
                default=None,
            )
            evidence = heartbeat_observation(nearest) if nearest else None
        else:
            classification = "INSUFFICIENT_RUNTIME_TELEMETRY"
            evidence = None

        counts[classification] += 1
        results.append({
            **item,
            "classification": classification,
            "coverage_tolerance_seconds": args.coverage_tolerance_seconds,
            "heartbeat_evidence": evidence,
        })

    first_hb = heartbeat_observation(heartbeats[0]) if heartbeats else None
    last_hb = heartbeat_observation(heartbeats[-1]) if heartbeats else None

    payload = {
        "status": "COMPLETE",
        "scope": {
            "symbol": args.symbol,
            "start_utc": args.start,
            "end_utc": args.end,
            "coverage_tolerance_seconds": args.coverage_tolerance_seconds,
        },
        "population": {
            "backtest_signals": len(selected),
            "forward_signal_ids": len(forward_ids),
            "missing_signals": len(missing),
        },
        "runtime_telemetry": {
            "start_events_in_scope": len(starts),
            "heartbeat_count_for_symbol": len(heartbeats),
            "first_heartbeat": first_hb,
            "last_heartbeat": last_hb,
            "heartbeat_event_timespan_seconds": (
                event_ts(heartbeats[-1]) - event_ts(heartbeats[0])
                if len(heartbeats) >= 2 else 0
            ),
        },
        "classification_counts": counts,
        "semantic_limit": (
            "Historical runtime telemetry only. PROCESS_COVERED_BUT_NO_CANDIDATE_EVENT "
            "proves that a forward heartbeat recorded a bar at or after the trigger; "
            "it does not prove that the process polled at the exact instant, selected "
            "the target candidate, or emitted an event. PROCESS_NOT_COVERED means the "
            "available heartbeat telemetry did not demonstrate coverage within the "
            "configured tolerance. This tool does not infer canonical rules."
        ),
        "signals": results,
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
