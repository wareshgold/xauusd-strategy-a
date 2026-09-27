"""Forensic expansion of baseline-only SP2L population rows.

Research-only. Replays the connected MT5 M1 window and expands only the
baseline-only fingerprints found by the population reconciliation. It does
not change detector geometry or infer canonical semantics.
"""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5
import numpy as np

from mt5_terminal_resolver import find_mt5_terminal

def parse_ts(v):
    return datetime.fromisoformat(v.replace("Z","+00:00")).astimezone(timezone.utc)

def fetch_rates(symbol,start,end):
    if not mt5.symbol_select(symbol,True):
        raise RuntimeError(f"symbol_select failed: {symbol} / {mt5.last_error()}")
    r=mt5.copy_rates_range(symbol,mt5.TIMEFRAME_M1,start,end)
    if r is None or len(r)==0:
        raise RuntimeError(f"copy_rates_range failed: {symbol} / {mt5.last_error()}")
    r=r.copy(); r.sort(order="time")
    _,idx=np.unique(r["time"],return_index=True)
    return r[np.sort(idx)]

def candle(r):
    return {"time":int(r["time"]),"utc":datetime.fromtimestamp(int(r["time"]),timezone.utc).isoformat(),
            "open":float(r["open"]),"high":float(r["high"]),"low":float(r["low"]),"close":float(r["close"])}

def fp(x):
    return (x.get("direction"),x.get("entry_time"),x.get("entry"),x.get("sl"),x.get("tp"))

def trigger_condition(direction,current,previous):
    if direction=="BUY":
        return current["low"] < previous["low"]
    return current["high"] > previous["high"]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline-report",required=True)
    p.add_argument("--reference-report",required=True)
    p.add_argument("--mt5-path")
    p.add_argument("--output",required=True)
    a=p.parse_args()

    base=json.loads(Path(a.baseline_report).read_text(encoding="utf-8"))
    ref=json.loads(Path(a.reference_report).read_text(encoding="utf-8"))
    b=base["result"]["signals_detail"]; r=ref["signal_ledger"]
    rf={fp(x) for x in r}
    targets=[x for x in b if fp(x) not in rf]

    symbol=base.get("symbol_resolved") or "XAUUSD.ecn"
    start=parse_ts(base["period"]["start_utc"]); end=parse_ts(base["period"]["end_utc"])
    init=mt5.initialize(path=a.mt5_path,timeout=30000) if a.mt5_path else mt5.initialize(timeout=30000)
    if not init:
        terminal=find_mt5_terminal() if not a.mt5_path else None
        if terminal is None or not mt5.initialize(path=str(terminal),timeout=30000):
            raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        rates=fetch_rates(symbol,start,end)
        by_time={int(x["time"]):i for i,x in enumerate(rates)}
        expanded=[]
        for s in targets:
            ei=int(s["entry_index"])
            lo=max(0,ei-6); hi=min(len(rates),ei+1)
            bars=[candle(rates[i])|{"index":i} for i in range(lo,hi)]
            trigger_checks=[]
            for i in range(max(1,lo),hi):
                cur=bars[i-lo]; prev=bars[i-lo-1]
                trigger_checks.append({"index":i,"time":cur["time"],"utc":cur["utc"],
                    "previous_low":prev["low"],"current_low":cur["low"],
                    "previous_high":prev["high"],"current_high":cur["high"],
                    "trigger_condition":trigger_condition(s["direction"],cur,prev)})
            setup_indices={k:by_time.get(int(s[k])) for k in
                           ("before_spike_time","spike_time","after_spike_time")}
            expanded.append({
                "signal":s,
                "setup_indices":setup_indices,
                "bars_before_and_through_entry":bars,
                "trigger_checks":trigger_checks,
                "reported_entry_index_matches_entry_time": (
                    ei < len(rates) and int(rates[ei]["time"])==int(s["entry_time"])
                ),
            })
        out={"status":"COMPLETE","research_only":True,
             "purpose":"expand_baseline_only_population_delta",
             "baseline_signals":len(b),"reference_signals":len(r),
             "baseline_only_count":len(targets),"symbol":symbol,
             "period":{"start_utc":start.isoformat(),"end_utc":end.isoformat()},
             "rows":expanded,
             "interpretation_limit":"Descriptive replay only; no geometry or outcome rule is promoted."}
        q=Path(a.output); q.parent.mkdir(parents=True,exist_ok=True)
        q.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
        print(json.dumps({"status":"COMPLETE","rows":len(expanded),"output":str(q),
                          "entry_index_time_checks":[x["reported_entry_index_matches_entry_time"] for x in expanded]},
                         indent=2,ensure_ascii=False))
    finally:
        mt5.shutdown()

if __name__=="__main__":
    main()
