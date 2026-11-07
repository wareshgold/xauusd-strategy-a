#!/usr/bin/env python
"""Compare naive vs timezone-aware UTC datetime handling in MT5 tick queries.

Aggregate-only, read-only diagnostic. Samples at most 12 eligible positions.
No timestamps, prices, tickets, or raw ticks are printed or written.
"""
from __future__ import annotations
import argparse, json, zipfile
from datetime import datetime, timezone
import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
MAGIC = 26092301

def load(z, name):
    with z.open(name) as f:
        return json.load(f)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle")
    ap.add_argument("--mt5-terminal-path", default=r"C:\Program Files\Otet Group MT5 Terminal\terminal64.exe")
    ap.add_argument("--sample-size", type=int, default=12)
    a = ap.parse_args()

    with zipfile.ZipFile(a.bundle) as z:
        deals = load(z, "raw/mt5_history_deals.json")

    positions = {}
    for d in deals:
        if d.get("symbol") != SYMBOL or str(d.get("magic")) != str(MAGIC):
            continue
        pid = d.get("position_id")
        if pid is None:
            continue
        p = positions.setdefault(str(pid), {"ins": [], "outs": []})
        entry = int(d.get("entry", -1))
        if entry == 0:
            p["ins"].append(d)
        elif entry == 1:
            p["outs"].append(d)

    eligible = []
    for p in positions.values():
        if len(p["ins"]) == 1 and len(p["outs"]) == 1:
            en, ex = p["ins"][0], p["outs"][0]
            if int(en.get("type", -1)) in (0, 1):
                eligible.append((en, ex))

    eligible = eligible[:max(1, min(a.sample_size, 20))]
    if not mt5.initialize(path=str(a.mt5_terminal_path)):
        print(json.dumps({"status": "MT5_INIT_FAILED", "last_error": mt5.last_error()}, indent=2))
        return

    try:
        naive_inside = aware_inside = naive_total = aware_total = 0
        naive_empty = aware_empty = 0
        comparable = 0
        for en, ex in eligible:
            t0 = int(en.get("time", 0))
            t1 = int(ex.get("time", 0))
            t0ms = int(en.get("time_msc", t0 * 1000))
            t1ms = int(ex.get("time_msc", t1 * 1000))
            if t1 < t0:
                continue
            start_epoch = max(0, t0 - 1)
            end_epoch = t1 + 1
            start_aware = datetime.fromtimestamp(start_epoch, timezone.utc)
            end_aware = datetime.fromtimestamp(end_epoch, timezone.utc)
            start_naive = start_aware.replace(tzinfo=None)
            end_naive = end_aware.replace(tzinfo=None)

            tn = mt5.copy_ticks_range(SYMBOL, start_naive, end_naive, mt5.COPY_TICKS_INFO)
            ta = mt5.copy_ticks_range(SYMBOL, start_aware, end_aware, mt5.COPY_TICKS_INFO)

            if tn is None or len(tn) == 0:
                naive_empty += 1
            else:
                naive_total += len(tn)
                for q in tn:
                    qms = int(q["time_msc"]) if "time_msc" in q.dtype.names else int(q["time"]) * 1000
                    if t0ms <= qms <= t1ms:
                        naive_inside += 1

            if ta is None or len(ta) == 0:
                aware_empty += 1
            else:
                aware_total += len(ta)
                for q in ta:
                    qms = int(q["time_msc"]) if "time_msc" in q.dtype.names else int(q["time"]) * 1000
                    if t0ms <= qms <= t1ms:
                        aware_inside += 1
            comparable += 1

        print(json.dumps({
            "status": "OK",
            "scope": {"symbol": SYMBOL, "magic": MAGIC, "privacy": "aggregate_only"},
            "sample": {"eligible_positions_requested": len(eligible), "positions_compared": comparable},
            "naive_datetime_query": {"ticks_returned": naive_total, "ticks_inside_deal_msc_window": naive_inside,
                                     "empty_position_queries": naive_empty},
            "aware_utc_datetime_query": {"ticks_returned": aware_total, "ticks_inside_deal_msc_window": aware_inside,
                                         "empty_position_queries": aware_empty},
            "interpretation": "A materially higher aware_utc inside count supports a datetime timezone interpretation issue; this sample is diagnostic, not a full-population MFE/MAE result."
        }, indent=2))
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()
