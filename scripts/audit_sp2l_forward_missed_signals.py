#!/usr/bin/env python3
"""Research-only reconciliation of today's MT5 author-replica candidates against
actual forward-run uptime. Historical candidates outside uptime are excluded.
"""
from __future__ import annotations
import argparse, csv, json
from datetime import datetime, timezone
from pathlib import Path
import MetaTrader5 as mt5

SYMBOL="XAUUSD.ecn"; TIMEFRAME=mt5.TIMEFRAME_M1
P_GAP_PRICE=1.0; SPIKE_MULTIPLIER=1.5; MAX_SL_DISTANCE=10.0; TP_R=1.0
ROOT=Path(__file__).resolve().parents[1]
EVENTS=ROOT/"artifacts"/"forward-test"/"SP2L_AUTHOR_REPLICA_FORWARD_EVENTS.jsonl"

def detect(w):
    a,s,c,t=w; sb=float(s["close"]-s["open"]); ss=float(s["open"]-s["close"])
    buy=(t["low"]<c["low"] and c["close"]>s["close"] and c["open"]>s["open"] and s["close"]>a["close"] and s["open"]>a["open"] and c["close"]>c["open"] and s["close"]>s["open"] and a["close"]>a["open"] and c["low"]>a["high"]+P_GAP_PRICE and sb>SPIKE_MULTIPLIER*(c["close"]-c["open"]) and sb>SPIKE_MULTIPLIER*(a["close"]-a["open"]) and sb>SPIKE_MULTIPLIER*(t["close"]-t["open"]))
    sell=(t["high"]>c["high"] and c["close"]<s["close"] and c["open"]<s["open"] and s["close"]<a["close"] and s["open"]<a["open"] and c["close"]<c["open"] and s["close"]<s["open"] and a["close"]<a["open"] and c["high"]<a["low"]-P_GAP_PRICE and ss>SPIKE_MULTIPLIER*(c["open"]-c["close"]) and ss>SPIKE_MULTIPLIER*(a["open"]-a["close"]) and ss>SPIKE_MULTIPLIER*(t["open"]-t["close"]))
    if buy==sell:return None
    if buy:
        e,sl=float(t["low"]),float(a["low"]); r=e-sl
        if 0<r<=MAX_SL_DISTANCE:return {"direction":"BUY","trigger_time":int(t["time"]),"entry":e,"sl":sl,"tp":e+r,"risk":r}
    if sell:
        e,sl=float(t["high"]),float(a["high"]); r=sl-e
        if 0<r<=MAX_SL_DISTANCE:return {"direction":"SELL","trigger_time":int(t["time"]),"entry":e,"sl":sl,"tp":e-r,"risk":r}
    return None

def parse_ts(v): return datetime.fromisoformat(v.replace("Z","+00:00")).astimezone(timezone.utc)

def load_events():
    events=[]
    if not EVENTS.exists(): return events
    for line in EVENTS.read_text(encoding="utf-8").splitlines():
        try: events.append(json.loads(line))
        except json.JSONDecodeError: pass
    return events

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--start",default=None); ap.add_argument("--end",default=None); ap.add_argument("--out-dir",default="artifacts/forward-test"); args=ap.parse_args()
    events=load_events()
    starts=[parse_ts(e["ts_utc"]) for e in events if e.get("event")=="START"]
    stops=[parse_ts(e["ts_utc"]) for e in events if e.get("event")=="STOP"]
    if not starts: raise SystemExit("No START event found in forward event log")
    # Each START is paired with the next STOP; the audit covers all observed uptime intervals.
    intervals=[]
    for st in starts:
        sp=next((x for x in stops if x>=st),None)
        intervals.append((st,sp))
    now=datetime.now(timezone.utc)
    requested_start=parse_ts(args.start) if args.start else min(x[0] for x in intervals)
    requested_end=parse_ts(args.end) if args.end else now
    if requested_end<=requested_start: raise SystemExit("end must be after start")
    mt5.initialize()
    try:
        if not mt5.symbol_select(SYMBOL,True): raise SystemExit(f"cannot select {SYMBOL}: {mt5.last_error()}")
        rates=mt5.copy_rates_range(SYMBOL,TIMEFRAME,requested_start,requested_end)
        if rates is None or len(rates)<5: raise SystemExit(f"insufficient MT5 bars: {mt5.last_error()}")
        candidates=[]
        for i in range(4,len(rates)):
            c=detect([rates[i-4],rates[i-3],rates[i-2],rates[i-1]])
            if c: candidates.append(c)
        candidates=[c for c in candidates if any(st<=datetime.fromtimestamp(c["trigger_time"],timezone.utc) and (sp is None or datetime.fromtimestamp(c["trigger_time"],timezone.utc)<=sp) for st,sp in intervals)]
        forward_candidates={}
        for e in events:
            if e.get("event")=="CANDIDATE":
                c=e.get("candidate",{}); forward_candidates[(int(c.get("trigger_time")),c.get("direction"))]=e
        rows=[]
        for c in candidates:
            key=(c["trigger_time"],c["direction"]); f=forward_candidates.get(key)
            rows.append({"trigger_time_utc":datetime.fromtimestamp(c["trigger_time"],timezone.utc).isoformat(),"direction":c["direction"],"entry":c["entry"],"sl":c["sl"],"tp":c["tp"],"risk":c["risk"],"status":"FORWARD_MATCH" if f else "GENUINE_FORWARD_UPTIME_MISS"})
        out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
        stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        csvp=out/f"SP2L_FORWARD_UPTIME_MISS_AUDIT_{stamp}.csv"; jsonp=out/f"SP2L_FORWARD_UPTIME_MISS_AUDIT_{stamp}.json"
        fields=["trigger_time_utc","direction","entry","sl","tp","risk","status"]
        with csvp.open("w",newline="",encoding="utf-8") as fh:
            w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(rows)
        summary={"status":"ANALYZED","research_only":True,"canonical":False,"symbol":SYMBOL,"timeframe":"M1","forward_uptime_intervals":[{"start":s.isoformat(),"stop":p.isoformat() if p else None} for s,p in intervals],"mt5_returned_bars":len(rates),"candidates_inside_forward_uptime":len(candidates),"forward_matches":sum(r["status"]=="FORWARD_MATCH" for r in rows),"genuine_forward_uptime_misses":sum(r["status"]=="GENUINE_FORWARD_UPTIME_MISS" for r in rows),"result_csv":csvp.name,"geometry_note":"Current research author-replica only; no canonical inference."}
        jsonp.write_text(json.dumps({"summary":summary,"rows":rows},indent=2)+"\n",encoding="utf-8")
        print(json.dumps(summary,indent=2)); [print(json.dumps(r,separators=(",",":"))) for r in rows]
    finally: mt5.shutdown()
if __name__=="__main__": main()
