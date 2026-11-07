#!/usr/bin/env python
"""Aggregate first-passage order for favorable/adverse tick thresholds; read-only."""
from __future__ import annotations
import argparse, json, zipfile
from collections import Counter
from datetime import datetime, timezone
import MetaTrader5 as mt5

SYMBOL="XAUUSD.ecn"
MAGIC=26092301
FAV=(0.40,0.80,1.00)
ADV=(1.00,2.00)
EPS=0.005

def load(z,n):
    with z.open(n) as f: return json.load(f)

def num(v):
    try: return float(v) if v is not None else 0.0
    except (TypeError,ValueError): return 0.0

def classify(x):
    return "winner" if x>EPS else ("loser" if x < -EPS else "flat")

def compare(rows,f,a):
    c=Counter()
    for r in rows:
        i=r["fav"].get(f); j=r["adv"].get(a)
        if i is None and j is None: k="neither_reached"
        elif i is not None and j is None: k="favorable_only"
        elif i is None and j is not None: k="adverse_only"
        elif i<j: k="favorable_first"
        elif j<i: k="adverse_first"
        else: k="same_tick_timestamp"
        c[k]+=1
    n=len(rows)
    return {"favorable_threshold":f,"adverse_threshold":a,"counts":dict(sorted(c.items())),
            "pct_of_group":{k:round(100*v/n,1) if n else None for k,v in sorted(c.items())}}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("bundle")
    ap.add_argument("--mt5-terminal-path",default=r"C:\Program Files\Otet Group MT5 Terminal\terminal64.exe")
    args=ap.parse_args()
    with zipfile.ZipFile(args.bundle) as z: deals=load(z,"raw/mt5_history_deals.json")
    selected=[d for d in deals if d.get("symbol")==SYMBOL and str(d.get("magic"))==str(MAGIC)]
    ps={}
    for d in selected:
        pid=d.get("position_id")
        if pid is None: continue
        p=ps.setdefault(str(pid),{"in":[],"out":[],"net":0.0})
        e=int(d.get("entry",-1))
        if e==0: p["in"].append(d)
        elif e==1: p["out"].append(d)
        p["net"]+=sum(num(d.get(k)) for k in ("profit","commission","swap","fee"))
    eligible=[]; excluded=Counter()
    for p in ps.values():
        if len(p["in"])!=1 or len(p["out"])!=1:
            excluded["not_exactly_one_IN_and_one_OUT"]+=1; continue
        en,ex=p["in"][0],p["out"][0]
        if int(en.get("type",-1)) not in (0,1):
            excluded["unknown_direction"]+=1; continue
        eligible.append((en,ex,p["net"]))
    if not mt5.initialize(path=args.mt5_terminal_path):
        print(json.dumps({"status":"MT5_INIT_FAILED","last_error":mt5.last_error()},indent=2)); return
    try:
        info=mt5.symbol_info(SYMBOL)
        if info is None:
            print(json.dumps({"status":"SYMBOL_INFO_UNAVAILABLE","last_error":mt5.last_error()},indent=2)); return
        contract=num(info.trade_contract_size); rows=[]; no_tick=0; tick_total=0; bad=0
        for en,ex,net in eligible:
            t0=int(en.get("time",0)); t1=int(ex.get("time",0))
            t0ms=int(en.get("time_msc",t0*1000)); t1ms=int(ex.get("time_msc",t1*1000))
            ticks=mt5.copy_ticks_range(SYMBOL,datetime.fromtimestamp(max(0,t0-1),timezone.utc),
                                       datetime.fromtimestamp(t1+1,timezone.utc),mt5.COPY_TICKS_INFO)
            if ticks is None or len(ticks)==0: no_tick+=1; continue
            tick_total+=len(ticks)
            price=num(en.get("price")); vol=num(en.get("volume"))
            if price<=0 or vol<=0 or contract<=0: continue
            buy=int(en["type"])==0; path=[]
            for q in ticks:
                ms=int(q["time_msc"]) if "time_msc" in q.dtype.names else int(q["time"])*1000
                if ms<t0ms or ms>t1ms: continue
                mark=num(q["bid"] if buy else q["ask"])
                if mark<=0: bad+=1; continue
                delta=(mark-price) if buy else (price-mark)
                path.append((ms,delta*contract*vol))
            if not path: no_tick+=1; continue
            path.sort(key=lambda x:x[0])
            fav={x:None for x in FAV}; adv={x:None for x in ADV}
            for ms,v in path:
                for x in FAV:
                    if fav[x] is None and v>=x: fav[x]=ms
                for x in ADV:
                    if adv[x] is None and v<=-x: adv[x]=ms
            rows.append({"outcome":classify(net),"fav":fav,"adv":adv})
        groups={g:[r for r in rows if r["outcome"]==g] for g in ("winner","loser","flat")}
        result={
          "scope":{"symbol":SYMBOL,"magic":MAGIC,"price_basis":"BUY bid; SELL ask",
                   "privacy":"aggregate_only"},
          "population":{"eligible_single_IN_single_OUT":len(eligible),"tick_coverage_positions":len(rows),
                        "no_tick_positions":no_tick,"excluded_counts":dict(excluded)},
          "tick_data":{"total_ticks_returned_before_millisecond_filter":tick_total,
                       "invalid_side_quotes_skipped":bad,"contract_size_used":contract},
          "first_passage_order_by_realized_outcome":{
             g:[compare(rs,f,a) for f in FAV for a in ADV] for g,rs in groups.items()},
          "limitations":[
             "First-passage order compares first gross favorable and adverse threshold hits.",
             "same_tick_timestamp means both first hits share the same time_msc millisecond; no within-millisecond order is inferred.",
             "This is not a stop-fill, trailing, slippage, spread-cost or execution simulation.",
             "Only exactly one IN and one OUT deal positions are included.",
             "No canonical SP2L geometry or execution rules are inferred or changed.",
             "Historical tick reads only; no order is submitted, modified or closed."
          ]}
        print(json.dumps(result,indent=2,ensure_ascii=False))
    finally: mt5.shutdown()

if __name__=="__main__": main()
