#!/usr/bin/env python3
"""Deterministic forensic mapping: MT5 V2 forward positions -> forward signals -> V2 backtest.

This script is diagnostic only. It does not alter strategy logic or canonical rules.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def load_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def iso(ts: int | float | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(int(ts), timezone.utc).isoformat()


def signal_ts(signal_id: str | None) -> int | None:
    if not signal_id:
        return None
    parts = signal_id.split(":")
    if len(parts) < 3:
        return None
    try:
        return int(parts[-2])
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--history", required=True)
    ap.add_argument("--forward", required=True)
    ap.add_argument("--backtest", required=True)
    ap.add_argument("--magic", type=int, default=26092201)
    ap.add_argument("--run-start", required=True,
                    help="ISO-8601 UTC start of the V2 forward run")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    history = json.loads(Path(args.history).read_text(encoding="utf-8"))
    events = load_jsonl(Path(args.forward))
    backtest = json.loads(Path(args.backtest).read_text(encoding="utf-8"))

    run_start = datetime.fromisoformat(args.run_start.replace("Z", "+00:00")).timestamp()

    # Forward signal metadata. Prefer TELEGRAM_SIGNAL, then lifecycle events.
    signal_meta = {}
    for e in events:
        sid = e.get("signal_id")
        if not sid or e.get("symbol") != "XAUUSD.ecn":
            continue
        if e.get("event") not in {"TELEGRAM_SIGNAL", "TELEGRAM_DEAL_LIFECYCLE"}:
            continue
        ts = signal_ts(sid)
        if ts is None:
            continue
        if ts < run_start:
            continue
        rec = signal_meta.setdefault(sid, {"signal_id": sid, "signal_ts": ts})
        for k in (
            "direction", "theoretical_entry", "theoretical_sl", "theoretical_tp",
            "entry", "sl", "tp", "risk", "trigger_time", "setup_time"
        ):
            if k in e and e[k] is not None:
                rec[k] = e[k]

    # Real MT5 entries/exits for the selected run. The first four 26092201
    # positions in the two-day history predate the V2 run and are excluded.
    deals = [
        d for d in history["deals"]
        if d.get("symbol") == "XAUUSD.ecn"
        and d.get("magic") == args.magic
        and int(d.get("time_msc", d.get("time", 0) * 1000)) / 1000 >= run_start
    ]
    positions = defaultdict(list)
    for d in deals:
        positions[int(d["position_id"])].append(d)

    # Backtest population.
    bt_rows = backtest.get("outcomes", {}).get("signals_detail", [])
    bt_by_entry = defaultdict(list)
    for row in bt_rows:
        et = row.get("entry_time")
        if et is not None:
            bt_by_entry[(int(et), row.get("direction"))].append(row)

    results = []
    for position_id, ds in sorted(positions.items()):
        entries = [d for d in ds if d.get("entry") == 0]
        exits = [d for d in ds if d.get("entry") == 1]
        if not entries:
            continue
        entry = min(entries, key=lambda x: x.get("time_msc", x.get("time", 0) * 1000))
        exit_ = max(exits, key=lambda x: x.get("time_msc", x.get("time", 0) * 1000)) if exits else None

        entry_time = int(entry.get("time", 0))
        direction = "BUY" if int(entry.get("type", 0)) == 0 else "SELL"

        # Deterministic signal match: exact signal timestamp first, then exact
        # MT5 entry second. No fuzzy price matching is used.
        candidates = [
            s for s in signal_meta.values()
            if s.get("direction") == direction and s.get("signal_ts") == entry_time
        ]
        if not candidates:
            candidates = [
                s for s in signal_meta.values()
                if s.get("direction") == direction
                and abs(int(s.get("signal_ts", -10**18)) - entry_time) <= 120
            ]
        sig = min(candidates, key=lambda s: abs(int(s["signal_ts"]) - entry_time)) if candidates else None

        bt = []
        if sig:
            bt = bt_by_entry.get((int(sig["signal_ts"]), direction), [])
            if not bt:
                # Backtest entry_time may be one or more bars after the trigger;
                # use nearest same-direction entry within 120 seconds only.
                nearby = []
                for row in bt_rows:
                    if row.get("direction") != direction or row.get("entry_time") is None:
                        continue
                    delta = abs(int(row["entry_time"]) - int(sig["signal_ts"]))
                    if delta <= 120:
                        nearby.append((delta, row))
                if nearby:
                    bt = [min(nearby, key=lambda x: x[0])[1]]

        results.append({
            "position_id": position_id,
            "signal_id": sig.get("signal_id") if sig else None,
            "signal_time_utc": iso(sig.get("signal_ts")) if sig else None,
            "direction": direction,
            "forward_theoretical": {
                k: sig.get(k) if sig else None
                for k in ("theoretical_entry", "theoretical_sl", "theoretical_tp", "risk")
            },
            "mt5": {
                "entry_ticket": entry.get("ticket"),
                "entry_time_utc": iso(entry.get("time")),
                "entry_price": entry.get("price"),
                "exit_ticket": exit_.get("ticket") if exit_ else None,
                "exit_time_utc": iso(exit_.get("time")) if exit_ else None,
                "exit_price": exit_.get("price") if exit_ else None,
                "exit_reason": exit_.get("reason") if exit_ else None,
                "profit": exit_.get("profit") if exit_ else None,
                "commission": exit_.get("commission") if exit_ else None,
            },
            "backtest_match_count": len(bt),
            "backtest": bt[0] if bt else None,
        })

    summary = {
        "status": "COMPLETE",
        "diagnostic_only": True,
        "run_start_utc": datetime.fromtimestamp(run_start, timezone.utc).isoformat(),
        "magic": args.magic,
        "mt5_positions_in_run": len(results),
        "matched_forward_signals": sum(r["signal_id"] is not None for r in results),
        "matched_backtest_rows": sum(r["backtest"] is not None for r in results),
        "unmatched_forward_signals": [r["position_id"] for r in results if r["signal_id"] is None],
        "unmatched_backtest_positions": [r["position_id"] for r in results if r["backtest"] is None],
        "positions": results,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({
        k: summary[k] for k in (
            "status", "run_start_utc", "magic", "mt5_positions_in_run",
            "matched_forward_signals", "matched_backtest_rows",
            "unmatched_forward_signals", "unmatched_backtest_positions"
        )
    }, ensure_ascii=False, indent=2))
    print(f"SAVED: {out}")


if __name__ == "__main__":
    main()
