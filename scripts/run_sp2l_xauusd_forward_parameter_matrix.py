"""Research-only XAUUSD parameter matrix for the current Forward-style replay.

This tool explores parameter sensitivity; it does NOT select or promote a
canonical Strategy A configuration. Source meaning outranks performance.
"""
from __future__ import annotations
import argparse,json,os
from datetime import datetime,timezone,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import MetaTrader5 as mt5
import numpy as np

try:
    from sp2l_strategy_a_v2_detector import _body
except ImportError:
    from scripts.sp2l_strategy_a_v2_detector import _body

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"artifacts"/"parameter-matrix"; OUT.mkdir(parents=True,exist_ok=True)
LONDON=ZoneInfo("Europe/London"); NEW_YORK=ZoneInfo("America/New_York")

def resolve_symbol(requested):
    names={str(s.name) for s in (mt5.symbols_get() or [])}; c=requested.upper()
    for x in (c,c+".ecn",c+".ECN",c+"m",c+".c.ecn"):
        if x in names:return x
    n="".join(ch for ch in c if ch.isalnum())
    m=[x for x in names if "".join(ch for ch in x.upper() if ch.isalnum()).startswith(n)]
    if m:return sorted(m,key=lambda x:(len(x),x))[0]
    raise RuntimeError(f"symbol discovery failed: {requested}")

def fetch_rates(symbol,start,end):
    if not mt5.symbol_select(symbol,True): raise RuntimeError(f"symbol_select failed: {symbol} {mt5.last_error()}")
    chunks=[]; cur=start.astimezone(timezone.utc); end=end.astimezone(timezone.utc)
    while cur<end:
        ce=min(cur+timedelta(days=7),end); r=mt5.copy_rates_range(symbol,mt5.TIMEFRAME_M1,cur,ce)
        if r is None or len(r)==0: raise RuntimeError(f"history failed: {mt5.last_error()}")
        chunks.append(r.copy()); cur=ce+timedelta(minutes=1)
    out=np.concatenate(chunks); out.sort(order="time"); _,idx=np.unique(out["time"],return_index=True)
    return out[np.sort(idx)]

def session_ok(ts,offset):
    broker_dt=datetime.fromtimestamp(int(ts),timezone.utc)-timedelta(hours=offset)
    london=broker_dt.astimezone(LONDON); ny=broker_dt.astimezone(NEW_YORK)
    a=london.replace(hour=8,minute=0,second=0,microsecond=0).astimezone(timezone.utc)
    b=ny.replace(hour=17,minute=0,second=0,microsecond=0).astimezone(timezone.utc)
    return a<=broker_dt<=b

def setup(candles,p_gap,spike_mult):
    before,spike,after=candles[-3],candles[-2],candles[-1]
    def side(d):
        if d=="BUY":
            return (float(after["close"])>float(spike["close"]) and float(after["open"])>float(spike["open"]) and
                    float(spike["close"])>float(before["close"]) and float(spike["open"])>float(before["open"]) and
                    float(after["close"])>float(after["open"]) and float(spike["close"])>float(spike["open"]) and
                    float(before["close"])>float(before["open"]) and float(after["low"])>float(before["high"])+p_gap and
                    _body(spike,"BUY")>spike_mult*_body(before,"BUY") and _body(spike,"BUY")>spike_mult*_body(after,"BUY"))
        return (float(after["close"])<float(spike["close"]) and float(after["open"])<float(spike["open"]) and
                float(spike["close"])<float(before["close"]) and float(spike["open"])<float(before["open"]) and
                float(after["close"])<float(after["open"]) and float(spike["close"])<float(spike["open"]) and
                float(before["close"])<float(before["open"]) and float(after["high"])<float(before["low"])-p_gap and
                _body(spike,"SELL")>spike_mult*_body(before,"SELL") and _body(spike,"SELL")>spike_mult*_body(after,"SELL"))
    buy,sell=side("BUY"),side("SELL")
    if buy==sell:return None
    d="BUY" if buy else "SELL"
    return {"direction":d,"setup_time":int(after["time"]),"before_spike_time":int(before["time"]),"spike_time":int(spike["time"]),"after_spike_time":int(after["time"]),"sl":float(before["low"] if d=="BUY" else before["high"]),"spike_body":_body(spike,d)}

def first_entry(candles,start_index,s,tp_r,max_sl):
    d=s["direction"]; sl=float(s["sl"])
    for j in range(start_index+1,len(candles)):
        cur,prev=candles[j],candles[j-1]
        entry=float(cur["low"] if d=="BUY" else cur["high"])
        qualifies=entry<float(prev["low"]) if d=="BUY" else entry>float(prev["high"])
        if not qualifies: continue
        risk=entry-sl if d=="BUY" else sl-entry
        if risk<=0 or risk>max_sl:return None
        return {**s,"entry_index":j,"entry_time":int(cur["time"]),"entry":entry,"risk":risk,
                "tp":entry+tp_r*risk if d=="BUY" else entry-tp_r*risk}
    return None

def candidate(window,p_gap,spike_mult,tp_r,max_sl,symbol):
    cs=[]
    for k in range(2,len(window)-1):
        s=setup(window[k-2:k+1],p_gap,spike_mult)
        if s:
            e=first_entry(window,k,s,tp_r,max_sl)
            if e:
                e=dict(e); e["symbol"]=symbol; cs.append(e)
    return max(cs,key=lambda x:(x["entry_time"],x["direction"])) if cs else None

def replay(rates,symbol,cfg,volume,ttl,offset):
    pending=[]; open_trades=[]; closed=[]; expired=[]; seen=set()
    for i in range(3,len(rates)):
        ts=int(rates[i]["time"]); hi=float(rates[i]["high"]); lo=float(rates[i]["low"])
        rem=[]
        for p in pending:
            age=(ts-p["trigger_time"])/60
            touch=lo<=p["entry"] if p["direction"]=="BUY" else hi>=p["entry"]
            if touch:
                p["fill_time"]=ts;p["status"]="FILLED";open_trades.append(p)
            elif age>=ttl:
                p["status"]="EXPIRED";p["expiry_time"]=ts;expired.append(p)
            else: rem.append(p)
        pending=rem
        still=[]
        for t in open_trades:
            if ts<t["fill_time"]:still.append(t);continue
            hs=lo<=t["sl"] if t["direction"]=="BUY" else hi>=t["sl"]
            ht=hi>=t["tp"] if t["direction"]=="BUY" else lo<=t["tp"]
            if not(hs or ht):still.append(t);continue
            if hs and ht:t["r"]=None;t["result"]="AMBIGUOUS";t["exit_reason"]="BOTH_SAME_M1"
            elif hs:t["r"]=-1.0;t["result"]="LOSS";t["exit_reason"]="SL_TOUCH"
            else:t["r"]=1.0;t["result"]="WIN";t["exit_reason"]="TP_TOUCH"
            t["exit_time"]=ts;closed.append(t)
        open_trades=still
        c=candidate(rates[max(0,i-9):i+1],cfg["p_gap"],cfg["spike"],cfg["tp_r"],cfg["max_sl"],symbol)
        if not c:continue
        key=f'{symbol}:{c["entry_time"]}:{c["direction"]}'
        if key in seen:continue
        seen.add(key)
        if not session_ok(c["entry_time"],offset):continue
        c["signal_id"]=key;c["volume"]=volume;c["status"]="PENDING";c["trigger_time"]=c["entry_time"];pending.append(c)
    decisive=[t for t in closed if t.get("r") is not None]
    wins=sum(t["r"]>0 for t in decisive); losses=sum(t["r"]<0 for t in decisive)
    return {"candidates":len(seen),"filled":sum(t.get("status")=="FILLED" for t in closed),"closed":len(closed),"wins":wins,"losses":losses,
            "ambiguous":sum(t.get("result")=="AMBIGUOUS" for t in closed),"expired":len(expired),"netR":sum(t["r"] for t in decisive),
            "openAtEnd":len(open_trades),"pendingAtEnd":len(pending)}

def floats(text): return [float(x) for x in text.split(",") if x.strip()]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--start",required=True);ap.add_argument("--end",required=True);ap.add_argument("--symbol",default="XAUUSD");ap.add_argument("--mt5-path",required=True)
    ap.add_argument("--p-gaps",default="0.5,0.75,1.0,1.25,1.5");ap.add_argument("--spikes",default="1.25,1.5,1.75,2.0");ap.add_argument("--max-sls",default="5,7.5,10,12.5,15");ap.add_argument("--tp-rs",default="0.75,1.0,1.25,1.5,2.0");ap.add_argument("--ttls",default="15,30,60")
    ap.add_argument("--volume",type=float,default=.01);ap.add_argument("--server-offset-hours",type=float,default=None);ap.add_argument("--output")
    a=ap.parse_args(); start=datetime.fromisoformat(a.start.replace("Z","+00:00"));end=datetime.fromisoformat(a.end.replace("Z","+00:00"))
    if not mt5.initialize(path=a.mt5_path):raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        symbol=resolve_symbol(a.symbol);rates=fetch_rates(symbol,start,end)
        if a.server_offset_hours is None:
            tick=mt5.symbol_info_tick(symbol)
            if not tick or not tick.time:raise RuntimeError("server offset unavailable")
            a.server_offset_hours=round((int(tick.time)-datetime.now(timezone.utc).timestamp())/3600)
        rows=[]; grid=0
        p_gaps, spikes, max_sls, tp_rs, ttls = map(floats, (a.p_gaps, a.spikes, a.max_sls, a.tp_rs, a.ttls))
        total = len(p_gaps) * len(spikes) * len(max_sls) * len(tp_rs) * len(ttls)
        print(f"[MATRIX] XAUUSD Forward parameter matrix: {total} tests", flush=True)
        for pg in p_gaps:
            for sp in spikes:
                for ms in max_sls:
                    for tp in tp_rs:
                        for ttl in ttls:
                            grid+=1;cfg={"p_gap":pg,"spike":sp,"max_sl":ms,"tp_r":tp}
                            x=replay(rates,symbol,cfg,a.volume,ttl,a.server_offset_hours)
                            rows.append({"pGap":pg,"spikeMultiplier":sp,"maxSL":ms,"tpR":tp,"ttlMinutes":ttl,**x})
                            if grid == 1 or grid % 25 == 0 or grid == total:
                                print(f"[{grid}/{total}] {100.0*grid/total:6.2f}% PGap={pg:g} Spike={sp:g} SL={ms:g} TP={tp:g} TTL={ttl:g} -> Filled={x['filled']} NetR={x['netR']:.1f}", flush=True)
        out={"status":"COMPLETE","canonical":False,"mode":"HISTORICAL_FORWARD_PARAMETER_MATRIX_RESEARCH","symbol":symbol,"timeframe":"M1","window":{"start":start.isoformat(),"end":end.isoformat()},"grid_size":grid,
             "rows":rows,"fixed_semantics":{"trigger":"first post-setup lower-low/higher-high","entry":"trigger candle low/high","slAnchor":"before-spike candle extreme","session":"London 08:00 -> New York 17:00","orderMode":"PENDING_LIMIT_RESEARCH","fillModel":"M1 touch","exitModel":"M1 SL/TP touch; dual touch ambiguous","F13_2X":"relation-only, not executed"},
             "warning":"Research-only sensitivity matrix. It does not define the best or canonical configuration. P-Gap, SL boundary, trigger acceptance and execution semantics remain source/research questions."}
        path=Path(a.output) if a.output else OUT/f"SP2L_XAUUSD_FORWARD_PARAMETER_MATRIX_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,indent=2),encoding="utf-8")
        print(json.dumps({"status":"COMPLETE","symbol":symbol,"bars":len(rates),"grid_size":grid,"output":str(path)},indent=2))
    finally:mt5.shutdown()

if __name__=="__main__":main()
