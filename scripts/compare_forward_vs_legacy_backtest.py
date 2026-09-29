"""Research forensic comparator: forward lifecycle vs legacy backtest.

Purpose:
- Do not change strategy logic.
- Match executed forward lifecycle records against backtest signals.
- Identify parity gaps: signal id, entry, SL/TP, result, timing.

Research-only utility.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_jsonl(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--forward-events", required=True)
    p.add_argument("--backtest-report", required=True)
    p.add_argument("--output", default="forward_vs_backtest_comparison.json")
    args = p.parse_args()

    forward = load_jsonl(Path(args.forward_events))
    backtest = json.loads(Path(args.backtest_report).read_text(encoding="utf-8"))

    lifecycle = [
        x for x in forward
        if x.get("event") == "TELEGRAM_DEAL_LIFECYCLE"
        and x.get("actual_r") is not None
    ]

    signals = []
    for symbol_result in backtest.get("outcomes", {}).values():
        signals.extend(symbol_result.get("signals_detail", []))

    report = {
        "status": "COMPLETE",
        "purpose": "forward_execution_vs_legacy_backtest_parity",
        "forward_completed_lifecycles": len(lifecycle),
        "backtest_signals": len(signals),
        "matches": [],
        "unmatched_forward": [],
        "unmatched_backtest": [],
        "notes": [
            "Comparator does not define strategy rules.",
            "Differences are execution/data parity diagnostics only."
        ],
    }

    by_key = {}
    for s in signals:
        key = (s.get("direction"), s.get("signal_time"))
        by_key[key] = s

    used = set()
    for f in lifecycle:
        sid = f.get("signal_id", "")
        direction = "BUY" if sid.endswith(":BUY") else "SELL"
        # MT5 signal ids contain epoch seconds before direction.
        try:
            t = int(sid.split(":")[1])
        except Exception:
            t = None
        b = by_key.get((direction, t))
        if b:
            used.add((direction, t))
            report["matches"].append({
                "forward_signal_id": sid,
                "forward_actual_r": f.get("actual_r"),
                "backtest_result": b.get("result"),
                "backtest_r": b.get("r"),
                "entry_price_forward": f.get("entry_price"),
                "entry_price_backtest": b.get("entry"),
            })
        else:
            report["unmatched_forward"].append(sid)

    report["unmatched_backtest"] = [
        {"direction": k[0], "signal_time": k[1]}
        for k in by_key
        if k not in used
    ]

    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "COMPLETE",
        "output": args.output,
        "matches": len(report["matches"]),
        "unmatched_forward": len(report["unmatched_forward"]),
        "unmatched_backtest": len(report["unmatched_backtest"]),
    }, indent=2))


if __name__ == "__main__":
    main()
