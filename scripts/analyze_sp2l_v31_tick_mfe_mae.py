#!/usr/bin/env python
"""Read-only tick-based MFE/MAE aggregates for the private SP2L V3.1 audit ZIP.

Connects to the already installed MT5 terminal only to read historical ticks.
Never sends/modifies orders and never writes raw ticks or identifiers to disk.
Output contains aggregate statistics only.
"""
from __future__ import annotations
import argparse, json, zipfile, statistics
from collections import Counter
from datetime import datetime, timezone, timedelta
import MetaTrader5 as mt5

SYMBOL="XAUUSD.ecn"
MAGIC=26092301

def load(z,n):
    with z.open(n) as f: return json.load(f)

def n(v):
    try: return float(v) if v is not None else 0.0
    except (TypeError,ValueError): return 0.0

def summary(xs):
    xs=list(xs)
    if not xs: return {"count":0}
    return {"count":len(xs),"mean":round(statistics.mean(xs),3),
            "median":round(statistics.median(xs),3),
            "min":round(min(xs),3),"max":round(max(xs),3)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("bundle")
    ap.add_argument("--mt5-terminal-path",default=r"C:\Program Files\Otet Group MT5 Terminal\terminal64.exe")
    a=ap.parse_args()
    with zipfile.ZipFile(a.bundle) as z:
        deals=load(z,"raw/mt5_history_deals.json")
    ds=[d for d in deals if d.get("symbol")==SYMBOL and str(d.get("magic"))==str(MAGIC)]
    positions={}
    for d in ds:
        pid=d.get("position_id")
        if pid is None: continue
        p=positions.setdefault(str(pid),{"ins":[],"outs":[]})
        e=int(d.get("entry",-1))
        if e==0: p["ins"].append(d)
        elif e==1: p["outs"].append(d)
    eligible=[]
    excluded=Counter()
    for p in positions.values():
        if not p["ins"] or not p["outs"]:
            excluded["missing_entry_or_exit"]+=1; continue
        if len(p["ins"])!=1 or len(p["outs"])!=1:
            excluded["multiple_entry_or_exit_deals"]+=1; continue
        ent,ex=p["ins"][0],p["outs"][0]
        if int(ent.get("type",-1)) not in (0,1):
            excluded["unknown_direction"]+=1; continue
        if int(ex.get("time",0)) < int(ent.get("time",0)):
            excluded["invalid_time_order"]+=1; continue
        eligible.append((ent,ex))
    terminal=str(a.mt5_terminal_path)
    if not mt5.initialize(path=terminal):
        print(json.dumps({"status":"MT5_INIT_FAILED","last_error":mt5.last_error()},indent=2)); return
    try:
        info=mt5.symbol_info(SYMBOL)
        if info is None:
            print(json.dumps({"status":"SYMBOL_INFO_UNAVAILABLE","last_error":mt5.last_error()},indent=2)); return
        contract=n(info.trade_contract_size)
        results=[]
        tick_total=0
        no_ticks=0
        bad_quotes=0
        partial=0
        for ent,ex in eligible:
            t0=int(ent.get("time",0)); t1=int(ex.get("time",0))
            t0ms=int(ent.get("time_msc",t0*1000)); t1ms=int(ex.get("time_msc",t1*1000))
            start=datetime.fromtimestamp(max(0,t0-1),timezone.utc).replace(tzinfo=None)
            end=datetime.fromtimestamp(t1+1,timezone.utc).replace(tzinfo=None)
            ticks=mt5.copy_ticks_range(SYMBOL,start,end,mt5.COPY_TICKS_INFO)
            if ticks is None or len(ticks)==0:
                no_ticks+=1; continue
            tick_total+=len(ticks)
            direction=int(ent["type"])
            entry_price=n(ent.get("price"))
            volume=n(ent.get("volume"))
            if entry_price<=0 or volume<=0 or contract<=0:
                excluded["invalid_entry_or_contract"]+=1; continue
            valid=[]
            for q in ticks:
                qms=int(q["time_msc"]) if "time_msc" in q.dtype.names else int(q["time"])*1000
                if qms < t0ms or qms > t1ms: continue
                bid=n(q["bid"]); ask=n(q["ask"])
                mark=bid if direction==0 else ask
                if mark<=0:
                    bad_quotes+=1; continue
                move=(mark-entry_price) if direction==0 else (entry_price-mark)
                valid.append(move*contract*volume)
            if not valid:
                no_ticks+=1; continue
            if t0==t1: partial+=1
            results.append({"mfe":max(0.0,max(valid)),"mae":min(0.0,min(valid)),
                            "final_mark":valid[-1],"ticks":len(valid)})
        mfe=[x["mfe"] for x in results]
        mae=[x["mae"] for x in results]
        final=[x["final_mark"] for x in results]
        result={
          "scope":{"symbol":SYMBOL,"magic":MAGIC,"price_basis":"BUY marked at bid; SELL marked at ask",
                   "unit":"account-currency estimate using symbol contract size and entry volume",
                   "privacy":"aggregate_only"},
          "population":{"positions_in_zip":len(positions),"simple_single_entry_single_exit_positions":len(eligible),
                        "tick_coverage_positions":len(results),"no_tick_positions":no_ticks,
                        "excluded_counts":dict(excluded)},
          "tick_data":{"total_ticks_examined":tick_total,"invalid_side_quotes_skipped":bad_quotes,
                       "contract_size_used":contract,"same_second_entry_exit_cases":partial},
          "mfe_currency":summary(mfe),
          "mae_currency":summary(mae),
          "final_tick_mark_currency":summary(final),
          "threshold_reach_counts":{
             "mfe_at_least_0_40":sum(x>=0.40 for x in mfe),
             "mfe_at_least_0_80":sum(x>=0.80 for x in mfe),
             "mfe_at_least_1_00":sum(x>=1.00 for x in mfe),
             "mae_at_least_1_00_adverse":sum(x<=-1.00 for x in mae),
             "mae_at_least_2_00_adverse":sum(x<=-2.00 for x in mae)},
          "limitations":[
            "MFE/MAE use historical bid/ask ticks between recorded entry and exit deal times (millisecond fields when available); missing history is reported, not imputed.",
            "Single-entry/single-exit positions only; multi-deal position lifecycles are excluded pending dedicated handling.",
            "MFE/MAE are gross mark-to-market excursions, not realized P/L and do not include commissions.",
            "This does not infer or change canonical entry, P-Gap, AB=CD, SL-anchor, fill, or execution rules.",
            "The script reads historical data only; it does not submit, modify, or close orders."
          ]
        }
        print(json.dumps(result,indent=2,ensure_ascii=False))
    finally:
        mt5.shutdown()

if __name__=="__main__": main()
