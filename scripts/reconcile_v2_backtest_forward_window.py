"""Research-only reconciliation of one V2 MT5 backtest window against forward events.

This tool does not define canonical Strategy A rules. It compares the already
emitted backtest signal ledger with observational forward-run CANDIDATE and
ORDER_RESULT events using the runner's signal_id:
    <symbol>:<trigger_time>:<direction>

It is intentionally deterministic and attribution-first.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def parse_ts(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def iso(ts: int) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_events(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8-sig") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            row["_line"] = line_no
            rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backtest", required=True, help="V2 backtest JSON report")
    parser.add_argument("--events", required=True, help="Forward JSONL event file")
    parser.add_argument("--start", required=True, help="UTC ISO-8601 inclusive")
    parser.add_argument("--end", required=True, help="UTC ISO-8601 exclusive")
    parser.add_argument("--symbol", default="XAUUSD.ecn")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    start_ts = parse_ts(args.start)
    end_ts = parse_ts(args.end)

    report = load_json(Path(args.backtest))
    details = report["outcomes"]["signals_detail"]
    bt = []
    for row in details:
        if int(row["entry_time"]) < start_ts or int(row["entry_time"]) >= end_ts:
            continue
        direction = str(row["direction"])
        trigger_time = int(row["entry_time"])
        sid = f"{args.symbol}:{trigger_time}:{direction}"
        bt.append({
            "signal_id": sid,
            "direction": direction,
            "entry_time": trigger_time,
            "entry_utc": iso(trigger_time),
            "entry": row["entry"],
            "sl": row["sl"],
            "tp": row["tp"],
            "risk": row["risk"],
            "result": row["result"],
            "r": row["r"],
            "exit_time": row["exit_time"],
        })

    events = load_events(Path(args.events))
    candidates = {}
    order_results = {}
    for row in events:
        if str(row.get("symbol")) != args.symbol:
            continue
        sid = str(row.get("signal_id") or "")
        if not sid:
            continue
        if row.get("event") == "CANDIDATE":
            candidates.setdefault(sid, []).append(row)
        elif row.get("event") == "ORDER_RESULT":
            order_results.setdefault(sid, []).append(row)

    candidate_ids = set(candidates)
    bt_ids = {x["signal_id"] for x in bt}
    matched = sorted(bt_ids & candidate_ids)
    missing_forward = sorted(bt_ids - candidate_ids)
    extra_forward = sorted(candidate_ids - bt_ids)

    outcome_rows = []
    for sid in matched:
        b = next(x for x in bt if x["signal_id"] == sid)
        ors = order_results.get(sid, [])
        last_order = ors[-1] if ors else None
        result = (last_order or {}).get("result") or {}
        outcome_rows.append({
            "signal_id": sid,
            "backtest_result": b["result"],
            "backtest_r": b["r"],
            "forward_order_result_seen": bool(last_order),
            "forward_order_ok": result.get("ok") if last_order else None,
            "forward_order": result.get("order") if last_order else None,
            "forward_error": result.get("error") if last_order else None,
        })

    summary = {
        "status": "COMPLETE",
        "scope": {
            "symbol": args.symbol,
            "start_utc": args.start,
            "end_utc": args.end,
        },
        "backtest": {
            "signals_in_window": len(bt),
            "wins": sum(x["result"] == "WIN" for x in bt),
            "losses": sum(x["result"] == "LOSS" for x in bt),
            "ambiguous": sum(x["result"] == "AMBIGUOUS" for x in bt),
        },
        "forward_observation": {
            "candidate_unique_signals": len(candidate_ids),
            "order_result_unique_signals": len(order_results),
        },
        "population_reconciliation": {
            "matched_signal_ids": len(matched),
            "missing_from_forward": len(missing_forward),
            "extra_in_forward": len(extra_forward),
            "duplicate_candidate_events": sum(max(0, len(v) - 1) for v in candidates.values()),
            "duplicate_order_result_events": sum(max(0, len(v) - 1) for v in order_results.values()),
        },
        "missing_from_forward": [
            {"signal_id": sid} for sid in missing_forward
        ],
        "extra_in_forward": [
            {"signal_id": sid} for sid in extra_forward
        ],
        "matched_outcomes": outcome_rows,
        "semantic_limits": [
            "This is an observational reconciliation, not a canonical rule definition.",
            "A CANDIDATE event proves runner detection, not broker acceptance.",
            "ORDER_RESULT success proves the runner received an accepted order result; fill/close requires lifecycle/deal events.",
            "Signal identity uses the runner's emitted signal_id and therefore does not invent alternate geometry.",
        ],
    }

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if args.out:
        Path(args.out).write_text(
            json.dumps(summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
