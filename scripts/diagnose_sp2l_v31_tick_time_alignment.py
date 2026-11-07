#!/usr/bin/env python
"""Aggregate-only timing diagnostic for SP2L V3.1 historical tick coverage.

Reads the private audit ZIP and historical MT5 ticks only. Does not write raw
market data, disclose timestamps/prices/tickets, or interact with orders.
"""
from __future__ import annotations
import argparse, json, zipfile, statistics
from collections import Counter
from datetime import datetime, timezone
import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
MAGIC = 26092301

def load(z, name):
    with z.open(name) as f:
        return json.load(f)

def pct(xs, p):
    if not xs:
        return None
    ys = sorted(xs)
    return round(ys[min(len(ys)-1, int((len(ys)-1)*p))], 3)

def dist(xs):
    if not xs:
        return {"count": 0}
    return {"count": len(xs), "min": round(min(xs), 3),
            "median": pct(xs, .5), "p90": pct(xs, .9),
            "max": round(max(xs), 3)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle")
    ap.add_argument("--mt5-terminal-path", default=r"C:\\Program Files\\Otet Group MT5 Terminal\\terminal64.exe")
    a = ap.parse_args()

    with zipfile.ZipFile(a.bundle) as z:
        deals = load(z, "raw/mt5_history_deals.json")

    selected = [d for d in deals if d.get("symbol") == SYMBOL and str(d.get("magic")) == str(MAGIC)]
    positions = {}
    for d in selected:
        pid = d.get("position_id")
        if pid is None:
            continue
        p = positions.setdefault(str(pid), {"ins": [], "outs": []})
        e = int(d.get("entry", -1))
        if e == 0:
            p["ins"].append(d)
        elif e == 1:
            p["outs"].append(d)

    eligible = []
    for p in positions.values():
        if len(p["ins"]) == 1 and len(p["outs"]) == 1:
            ent, ex = p["ins"][0], p["outs"][0]
            if int(ent.get("type", -1)) in (0, 1):
                eligible.append((ent, ex))

    if not mt5.initialize(path=str(a.mt5_terminal_path)):
        print(json.dumps({"status": "MT5_INIT_FAILED", "last_error": mt5.last_error()}, indent=2))
        return

    try:
        before, inside, after = [], [], []
        deal_msc_delta, tick_msc_delta = [], []
        returned_ranges, ticks_total = [], 0
        zero_length = 0
        none_ranges = 0
        for ent, ex in eligible:
            t0 = int(ent.get("time", 0))
            t1 = int(ex.get("time", 0))
            t0ms = int(ent.get("time_msc", t0 * 1000))
            t1ms = int(ex.get("time_msc", t1 * 1000))
            deal_msc_delta.extend([t0ms - t0 * 1000, t1ms - t1 * 1000])
            if t1 < t0:
                continue
            if t0 == t1:
                zero_length += 1
            start = datetime.fromtimestamp(max(0, t0 - 1), timezone.utc).replace(tzinfo=None)
            end = datetime.fromtimestamp(t1 + 1, timezone.utc).replace(tzinfo=None)
            ticks = mt5.copy_ticks_range(SYMBOL, start, end, mt5.COPY_TICKS_INFO)
            if ticks is None or len(ticks) == 0:
                none_ranges += 1
                continue
            ticks_total += len(ticks)
            for q in ticks:
                qsec = int(q["time"])
                qms = int(q["time_msc"]) if "time_msc" in q.dtype.names else qsec * 1000
                tick_msc_delta.append(qms - qsec * 1000)
                if qms < t0ms:
                    before.append((t0ms - qms) / 1000.0)
                elif qms > t1ms:
                    after.append((qms - t1ms) / 1000.0)
                else:
                    inside.append(1)

                # Secondary comparison using seconds-only boundaries.
                if qsec < t0:
                    pass
                elif qsec > t1:
                    pass

        out = {
            "status": "OK",
            "scope": {"symbol": SYMBOL, "magic": MAGIC, "privacy": "aggregate_only"},
            "population": {"eligible_single_entry_exit_positions": len(eligible),
                           "positions_with_empty_tick_query": none_ranges,
                           "same_second_entry_exit_positions": zero_length},
            "tick_query": {"total_ticks_returned": ticks_total,
                           "ticks_before_entry_msc_filter": len(before),
                           "ticks_inside_entry_exit_msc_filter": len(inside),
                           "ticks_after_exit_msc_filter": len(after)},
            "deal_time_msc_minus_time_seconds_x1000": dist(deal_msc_delta),
            "tick_time_msc_minus_time_seconds_x1000": dist(tick_msc_delta),
            "nearest_boundary_distance_seconds": {
                "before_entry": dist(before),
                "after_exit": dist(after)
            },
            "interpretation_hint": "If returned ticks are almost entirely before/after, compare the aggregate offsets with the deal/tick millisecond consistency distributions; no timestamps or prices are emitted."
        }
        print(json.dumps(out, indent=2))
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()
