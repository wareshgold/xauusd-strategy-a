#!/usr/bin/env python3
"""Research-only same-day reconciliation of MT5 author-replica candidates vs forward-test events.

This answers one narrow question:
Did the same research detector find a BUY/SELL candidate in today's MT5 M1 history
that the running forward-test did not record?

NOT canonical Strategy A. It intentionally reuses the current author-replica
research geometry from run_sp2l_author_replica_forward_test.py:
- completed M1 window
- P_GAP_PRICE=1.0
- SPIKE_MULTIPLIER=1.5
- origin-candle SL
- 1R TP
- max SL distance=10.0

It does not promote geometry, infer fill semantics, or authorize trading.
"""

from __future__ import annotations
import argparse, csv, json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1
P_GAP_PRICE = 1.0
SPIKE_MULTIPLIER = 1.5
MAX_SL_DISTANCE = 10.0
TP_R = 1.0

ROOT = Path(__file__).resolve().parents[1]
FORWARD_EVENTS = ROOT / "artifacts" / "forward-test" / "SP2L_AUTHOR_REPLICA_FORWARD_EVENTS.jsonl"


def detect(window):
    a, spike, correction, trigger = window
    sb = float(spike["close"] - spike["open"])
    ss = float(spike["open"] - spike["close"])
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
        and sb > SPIKE_MULTIPLIER * (correction["close"] - correction["open"])
        and sb > SPIKE_MULTIPLIER * (a["close"] - a["open"])
        and sb > SPIKE_MULTIPLIER * (trigger["close"] - trigger["open"])
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
        and ss > SPIKE_MULTIPLIER * (correction["open"] - correction["close"])
        and ss > SPIKE_MULTIPLIER * (a["open"] - a["close"])
        and ss > SPIKE_MULTIPLIER * (trigger["open"] - trigger["close"])
    )
    if buy == sell:
        return None
    if buy:
        entry, sl = float(trigger["low"]), float(a["low"])
        risk = entry - sl
        if 0 < risk <= MAX_SL_DISTANCE:
            return {"direction":"BUY","trigger_time":int(trigger["time"]),"entry":entry,"sl":sl,"tp":entry+TP_R*risk,"risk":risk}
    if sell:
        entry, sl = float(trigger["high"]), float(a["high"])
        risk = sl - entry
        if 0 < risk <= MAX_SL_DISTANCE:
            return {"direction":"SELL","trigger_time":int(trigger["time"]),"entry":entry,"sl":sl,"tp":entry-TP_R*risk,"risk":risk}
    return None


def load_forward():
    out = {}
    if not FORWARD_EVENTS.exists():
        return out
    for line in FORWARD_EVENTS.read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("event") == "CANDIDATE":
            c = e.get("candidate", {})
            key = (int(c.get("trigger_time")), c.get("direction"))
            out.setdefault(key, {})["candidate"] = e
        elif e.get("event") == "EXECUTION":
            sid = e.get("signal_id")
            for key, value in out.items():
                if value.get("candidate", {}).get("signal_id") == sid:
                    value["execution"] = e
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default=None, help="UTC ISO; default today 00:00Z")
    parser.add_argument("--end", default=None, help="UTC ISO; default now")
    parser.add_argument("--out-dir", default="artifacts/forward-test")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    start = datetime.fromisoformat(args.start.replace("Z","+00:00")) if args.start else datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    end = datetime.fromisoformat(args.end.replace("Z","+00:00")) if args.end else now
    start = start.astimezone(timezone.utc).replace(second=0, microsecond=0)
    end = end.astimezone(timezone.utc)

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"cannot select {SYMBOL}: {mt5.last_error()}")
        rates = mt5.copy_rates_range(SYMBOL, TIMEFRAME, start, end)
        if rates is None or len(rates) < 5:
            raise SystemExit(f"insufficient MT5 bars: {mt5.last_error()}")

        candidates = []
        for i in range(4, len(rates)):
            window = [rates[i-4], rates[i-3], rates[i-2], rates[i-1]]
            c = detect(window)
            if c:
                c["trigger_time"] = int(rates[i-1]["time"])
                candidates.append(c)

        forward = load_forward()
        rows = []
        for c in candidates:
            key = (c["trigger_time"], c["direction"])
            f = forward.get(key)
            status = "FORWARD_MATCH" if f else "FORWARD_MISSED_CANDIDATE"
            if f and "execution" not in f:
                status = "FORWARD_CANDIDATE_NO_EXECUTION_EVENT"
            elif f and f.get("execution", {}).get("result", {}).get("ok") is False:
                status = "FORWARD_EXECUTION_FAILED"
            rows.append({
                "trigger_time_utc": datetime.fromtimestamp(c["trigger_time"], timezone.utc).isoformat(),
                "direction": c["direction"],
                "entry": c["entry"],
                "sl": c["sl"],
                "tp": c["tp"],
                "risk": c["risk"],
                "status": status,
            })

        out = Path(args.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        stamp = f"{start:%Y-%m-%d}_{end:%Y-%m-%dT%H%M%SZ}"
        csv_path = out / f"SP2L_FORWARD_MISSED_SIGNAL_AUDIT_{stamp}.csv"
        json_path = out / f"SP2L_FORWARD_MISSED_SIGNAL_AUDIT_{stamp}.json"
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["trigger_time_utc","direction","entry","sl","tp","risk","status"])
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "status": "ANALYZED",
            "research_only": True,
            "canonical": False,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "requested_interval_utc": {"start": start.isoformat(), "end": end.isoformat()},
            "mt5_returned_bars": len(rates),
            "backtest_candidates": len(candidates),
            "forward_candidate_matches": sum(r["status"]=="FORWARD_MATCH" for r in rows),
            "forward_missed_candidates": sum(r["status"]=="FORWARD_MISSED_CANDIDATE" for r in rows),
            "forward_candidate_no_execution_event": sum(r["status"]=="FORWARD_CANDIDATE_NO_EXECUTION_EVENT" for r in rows),
            "forward_execution_failed": sum(r["status"]=="FORWARD_EXECUTION_FAILED" for r in rows),
            "forward_events_file": str(FORWARD_EVENTS),
            "geometry_note": "Uses current research author-replica only; no canonical Strategy A inference.",
            "result_csv": csv_path.name,
        }
        json_path.write_text(json.dumps({"summary":summary,"rows":rows}, indent=2)+"\n", encoding="utf-8")
        print(json.dumps(summary, indent=2))
        for r in rows:
            print(json.dumps(r, separators=(",",":")))
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
