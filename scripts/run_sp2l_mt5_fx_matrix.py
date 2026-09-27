"""Research-only MT5 multi-symbol SP2L V2 parameter matrix.

Runs the frozen V2 detector across a deterministic FX symbol/parameter grid.
Performance does not define canonical geometry or production decisions.
"""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from datetime import datetime,timedelta,timezone
from pathlib import Path
import MetaTrader5 as mt5
import numpy as np

try:
    from mt5_terminal_resolver import find_mt5_terminal
    from sp2l_strategy_a_v2_detector import detect_setup
except ImportError:
    from scripts.mt5_terminal_resolver import find_mt5_terminal
    from scripts.sp2l_strategy_a_v2_detector import detect_setup

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"artifacts"/"backtest-mt5-fx-matrix"
OUT.mkdir(parents=True,exist_ok=True)

def resolve_symbol(requested):
    syms=list(mt5.symbols_get() or [])
    names={str(s.name):s for s in syms}; c=requested.upper()
    if c in names:return c,"EXACT"
    for suf in (".ecn",".ECN","m",".m","_ecn","-ECN"):
        if c+suf in names:return c+suf,"SUFFIX:"+suf
    n="".join(x for x in c if x.isalnum())
    m=[x for x in names if "".join(y for y in x.upper() if y.isalnum()).startswith(n)]
    if m:return sorted(m,key=lambda x:(len(x),x))[0],"DISCOVERED_PREFIX"
    raise RuntimeError(f"symbol discovery failed: {requested}")

def fetch(symbol,start,end):
    if not mt5.symbol_select(symbol,True):raise RuntimeError(f"symbol_select failed: {symbol} {mt5.last_error()}")
    chunks=[]; cur=start
    while cur<end:
        ce=min(cur+timedelta(days=7),end)
        x=mt5.copy_rates_range(symbol,mt5.TIMEFRAME_M1,cur,ce)
        if x is None or len(x)==0:raise RuntimeError(f"history failed: {symbol} {mt5.last_error()}")
        chunks.append(x.copy());cur=ce+timedelta(minutes=1)
    x=np.concatenate(chunks);x.sort(order="time")
    _,idx=np.unique(x["time"],return_index=True)
    return x[np.sort(idx)]

def body(r):return abs(float(r["close"])-float(r["open"]))

def signals(rates,pg,spike,maxsl):
    out=[];used=set()
    for i in range(2,len(rates)-1):
        a,b,c=rates[i-2],rates[i-1],rates[i]
        setup=detect_setup_custom(a,b,c,pg,spike)
        if not setup:continue
        direction=setup["direction"]
        for j in range(i+1,len(rates)):
            prev=rates[j-1];cur=rates[j]
            entry=float(cur["low"] if direction=="BUY" else cur["high"])
            trig=(float(cur["low"])<float(prev["low"])) if direction=="BUY" else (float(cur["high"])>float(prev["high"]))
            if not trig:continue
            sl=float(a["low"] if direction=="BUY" else a["high"]);risk=(entry-sl) if direction=="BUY" else (sl-entry)
            if risk<=0:break
            if risk>maxsl:break
            if j in used:break
            used.add(j)
            tp=entry+risk if direction=="BUY" else entry-risk
            out.append({"direction":direction,"entry_index":j,"entry_time":int(cur["time"]),"entry":entry,"sl":sl,"tp":tp,"risk":risk})
            break
    return sorted(out,key=lambda x:(x["entry_index"],x["direction"]))

def detect_setup_custom(a,b,c,pg,spike):
    ao,ah,al,ac=map(float,(a["open"],a["high"],a["low"],a["close"]))
    bo,bh,bl,bc=map(float,(b["open"],b["high"],b["low"],b["close"]))
    co,ch,cl,cc=map(float,(c["open"],c["high"],c["low"],c["close"]))
    bb=body(a);sb=body(b);ab=body(c)
    buy=(cc>bc and co>bo and bc>ac and bo>ao and cc>co and bc>bo and ac>ao and cl>ah+pg and sb>spike*bb and sb>spike*ab)
    sell=(cc<bc and co<bo and bc<ac and bo<ao and cc<co and bc<bo and ac<ao and ch<al-pg and sb>spike*bb and sb>spike*ab)
    return {"direction":"BUY"} if buy else ({"direction":"SELL"} if sell else None)

def backtest(rates,sigs):
    by={s["entry_index"]:s for s in sigs};active=None;tr=[]
    for i,b in enumerate(rates):
        h,l,ts=float(b["high"]),float(b["low"]),int(b["time"])
        if active:
            buy=active["direction"]=="BUY"; hs=l<=active["sl"] if buy else h>=active["sl"];ht=h>=active["tp"] if buy else l<=active["tp"]
            if hs or ht:
                if hs and ht: price,reason=active["sl"],"SL_FIRST_SAME_BAR"
                elif hs: price,reason=active["sl"],"SL"
                else: price,reason=active["tp"],"TP"
                r=((price-active["entry"])/active["risk"]) if buy else ((active["entry"]-price)/active["risk"])
                tr.append({**active,"r":r,"exit_time":ts,"exit_reason":reason});active=None;continue
        if active is None and i in by:
            active=dict(by[i])
            active["activation_time"]=ts
    if active:
        close=float(rates[-1]["close"]);r=((close-active["entry"])/active["risk"]) if active["direction"]=="BUY" else ((active["entry"]-close)/active["risk"])
        tr.append({**active,"r":r,"exit_time":int(rates[-1]["time"]),"exit_reason":"END_OF_DATA_MARK"})
    w=sum(x["r"]>0 for x in tr);l=len(tr)-w;pos=sum(x["r"] for x in tr if x["r"]>0);neg=sum(x["r"] for x in tr if x["r"]<0)
    eq=peak=dd=0.;run=mxrun=0
    for x in tr:
        eq+=x["r"];peak=max(peak,eq);dd=max(dd,peak-eq)
        run=run+1 if x["r"]<=0 else 0;mxrun=max(mxrun,run)
    return {"signals":len(sigs),"trades":len(tr),"wins":w,"losses":l,"win_rate_pct":100*w/len(tr) if tr else None,"net_r":sum(x["r"] for x in tr),
            "profit_factor":pos/abs(neg) if neg else None,"max_drawdown_r":dd,"max_consecutive_losses":mxrun,
            "buy_trades":sum(x["direction"]=="BUY" for x in tr),"sell_trades":sum(x["direction"]=="SELL" for x in tr),
            "exit_reasons":dict(Counter(x["exit_reason"] for x in tr))}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--start",required=True);p.add_argument("--end",required=True);p.add_argument("--mt5-path")
    p.add_argument("--symbols",default="EURUSD,GBPUSD,USDJPY,USDCHF,USDCAD,AUDUSD,NZDUSD")
    p.add_argument("--p-gaps",default="0.5,1.0,1.5");p.add_argument("--spike-multipliers",default="1.25,1.5,1.75")
    p.add_argument("--max-sls",default="5,10,15");p.add_argument("--tp-rs",default="1.0")
    p.add_argument("--output-prefix",default=None)
    a=p.parse_args();start=datetime.fromisoformat(a.start.replace("Z","+00:00"));end=datetime.fromisoformat(a.end.replace("Z","+00:00"))
    vals=lambda s:[float(x.strip()) for x in s.split(",") if x.strip()]
    pgs,spikes,maxsls,tprs=vals(a.p_gaps),vals(a.spike_multipliers),vals(a.max_sls),vals(a.tp_rs)
    ok=mt5.initialize(path=a.mt5_path) if a.mt5_path else mt5.initialize()
    if not ok:
        t=find_mt5_terminal()
        if t is None or not mt5.initialize(path=str(t)):raise RuntimeError(f"MT5 init failed: {mt5.last_error()}")
    try:
        rows=[];errors=[];history={}
        for req in [x.strip() for x in a.symbols.split(",") if x.strip()]:
            try:
                sym,res=resolve_symbol(req);rates=fetch(sym,start,end)
                history[req]={"symbol_used":sym,"resolution":res,"bars":len(rates),"first_bar_utc":datetime.fromtimestamp(int(rates[0]["time"]),timezone.utc).isoformat(),"last_bar_utc":datetime.fromtimestamp(int(rates[-1]["time"]),timezone.utc).isoformat()}
                for pg in pgs:
                    for sm in spikes:
                        for ms in maxsls:
                            for tp_r in tprs:
                                ss=signals(rates,pg,sm,ms)
                                # detector TP is 1R; reject non-1R TP as unsupported rather than silently altering contract
                                if tp_r!=1.0: raise RuntimeError("tp-r other than 1.0 is not supported by frozen V2 runner")
                                z=backtest(rates,ss);rows.append({"symbol_requested":req,"symbol_used":sym,"p_gap":pg,"spike_multiplier":sm,"max_sl":ms,"tp_r":tp_r,**z})
            except Exception as e:errors.append({"symbol_requested":req,"error":str(e)})
        stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ");prefix=a.output_prefix or f"SP2L_MT5_FX_MATRIX_{stamp}"
        report={"status":"COMPLETE" if not errors else "PARTIAL","research_only":True,"mode":"SP2L_MT5_FX_PARAMETER_MATRIX",
                "generated_utc":datetime.now(timezone.utc).isoformat(),"period":{"start_utc":start.isoformat(),"end_utc":end.isoformat()},
                "timeframe":"M1","symbols_requested":[x.strip() for x in a.symbols.split(",") if x.strip()],
                "grid":{"p_gaps":pgs,"spike_multipliers":spikes,"max_sls":maxsls,"tp_rs":tprs},
                "history":history,"errors":errors,"rows":rows,
                "contract":{"frozen_detector_structure":True,"tp_r":1.0,"one_active_trade":True,"entry_trigger":"first post-setup lower-low/higher-high","sl_anchor":"before-spike extreme","canonical":False}}
        jp=OUT/f"{prefix}.json";jp.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
        cp=OUT/f"{prefix}.csv"
        fields=list(rows[0].keys()) if rows else []
        with cp.open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
        print(json.dumps({"status":report["status"],"json":str(jp),"csv":str(cp),"symbols":len(history),"rows":len(rows),"errors":len(errors)},indent=2))
    finally:mt5.shutdown()
if __name__=="__main__":main()
