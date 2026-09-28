"""Research-only FX discovery matrix for SP2L V2.

Purpose:
- identify FX symbols/scales that produce a non-trivial signal population;
- compare descriptive population/outcome diagnostics across normalized FX pip scales;
- do NOT define or promote canonical P-Gap geometry.

P-Gap is expressed in FX pips only as a scale-discovery parameter. This is
not a source-confirmed Strategy A formula. The XAUUSD Forward runner is
intentionally unaffected by this script.
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
except ImportError:
    from scripts.mt5_terminal_resolver import find_mt5_terminal

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"artifacts"/"backtest-mt5-fx-discovery"
OUT.mkdir(parents=True,exist_ok=True)

DEFAULT_SYMBOLS="EURUSD,GBPUSD,USDJPY,USDCHF,USDCAD,AUDUSD,NZDUSD"
DEFAULT_GAPS="1,2,3,5,10"
DEFAULT_SPIKES="1.25,1.5,1.75,2.0"
DEFAULT_MAXSLS="10,20,30,50"

def resolve_symbol(requested):
    syms=list(mt5.symbols_get() or [])
    names={str(s.name):s for s in syms}
    c=requested.upper()
    if c in names:return c,"EXACT"
    for suf in (".ecn",".ECN","m",".m","_ecn","-ECN"):
        if c+suf in names:return c+suf,"SUFFIX:"+suf
    n="".join(x for x in c if x.isalnum())
    matches=[x for x in names if "".join(y for y in x.upper() if y.isalnum()).startswith(n)]
    if matches:return sorted(matches,key=lambda x:(len(x),x))[0],"DISCOVERED_PREFIX"
    raise RuntimeError(f"symbol discovery failed: {requested}")

def pip_size(info):
    point=float(info.point); digits=int(info.digits)
    # Standard FX pip convention: 0.0001 for most pairs and 0.01 for JPY.
    if digits in (3,5):
        return point*10.0,"POINT_X10"
    return point,"POINT"

def fetch(symbol,start,end):
    if not mt5.symbol_select(symbol,True):
        raise RuntimeError(f"symbol_select failed: {symbol} {mt5.last_error()}")
    chunks=[]; cur=start
    while cur<end:
        ce=min(cur+timedelta(days=7),end)
        x=mt5.copy_rates_range(symbol,mt5.TIMEFRAME_M1,cur,ce)
        if x is None or len(x)==0:
            raise RuntimeError(f"history failed: {symbol} {mt5.last_error()}")
        chunks.append(x.copy()); cur=ce+timedelta(minutes=1)
    x=np.concatenate(chunks); x.sort(order="time")
    _,idx=np.unique(x["time"],return_index=True)
    return x[np.sort(idx)]

def body(c): return abs(float(c["close"])-float(c["open"]))

def detect(a,b,c,gap_price,spike):
    ao,ah,al,ac=map(float,(a["open"],a["high"],a["low"],a["close"]))
    bo,bh,bl,bc=map(float,(b["open"],b["high"],b["low"],b["close"]))
    co,ch,cl,cc=map(float,(c["open"],c["high"],c["low"],c["close"]))
    bb,sb,ab=body(a),body(b),body(c)
    buy=(cc>bc and co>bo and bc>ac and bo>ao and cc>co and bc>bo and ac>ao
         and cl>ah+gap_price and sb>spike*bb and sb>spike*ab)
    sell=(cc<bc and co<bo and bc<ac and bo<ao and cc<co and bc<bo and ac<ao
          and ch<al-gap_price and sb>spike*bb and sb>spike*ab)
    if buy==sell:return None
    return "BUY" if buy else "SELL"

def signals(rates,gap_price,spike,maxsl_price):
    out=[]; used=set()
    for i in range(2,len(rates)-1):
        direction=detect(rates[i-2],rates[i-1],rates[i],gap_price,spike)
        if not direction: continue
        before=rates[i-2]
        for j in range(i+1,len(rates)):
            cur,prev=rates[j],rates[j-1]
            triggered=(float(cur["low"])<float(prev["low"])) if direction=="BUY" else (float(cur["high"])>float(prev["high"]))
            if not triggered: continue
            entry=float(cur["low"] if direction=="BUY" else cur["high"])
            sl=float(before["low"] if direction=="BUY" else before["high"])
            risk=(entry-sl) if direction=="BUY" else (sl-entry)
            if risk<=0 or risk>maxsl_price: break
            if j in used: break
            used.add(j)
            tp=entry+risk if direction=="BUY" else entry-risk
            out.append({"direction":direction,"entry_index":j,"entry_time":int(cur["time"]),"entry":entry,"sl":sl,"tp":tp,"risk":risk})
            break
    return sorted(out,key=lambda x:(x["entry_index"],x["direction"]))

def outcomes(rates,sigs):
    by={x["entry_index"]:x for x in sigs}; active=None; trades=[]
    for i,b in enumerate(rates):
        h,l,ts=float(b["high"]),float(b["low"]),int(b["time"])
        if active:
            buy=active["direction"]=="BUY"
            hs=l<=active["sl"] if buy else h>=active["sl"]
            ht=h>=active["tp"] if buy else l<=active["tp"]
            if hs or ht:
                if hs and ht: price,reason=active["sl"],"SL_FIRST_SAME_BAR"
                elif hs: price,reason=active["sl"],"SL"
                else: price,reason=active["tp"],"TP"
                r=((price-active["entry"])/active["risk"]) if buy else ((active["entry"]-price)/active["risk"])
                trades.append({**active,"r":r,"exit_time":ts,"exit_reason":reason}); active=None; continue
        if active is None and i in by:
            active=dict(by[i]); active["activation_time"]=ts
    if active:
        close=float(rates[-1]["close"])
        r=((close-active["entry"])/active["risk"]) if active["direction"]=="BUY" else ((active["entry"]-close)/active["risk"])
        trades.append({**active,"r":r,"exit_time":int(rates[-1]["time"]),"exit_reason":"END_OF_DATA_MARK"})
    wins=sum(x["r"]>0 for x in trades); losses=len(trades)-wins
    pos=sum(x["r"] for x in trades if x["r"]>0); neg=sum(x["r"] for x in trades if x["r"]<0)
    eq=peak=dd=0.0
    for x in trades:
        eq+=x["r"]; peak=max(peak,eq); dd=max(dd,peak-eq)
    return {"signals":len(sigs),"trades":len(trades),"wins":wins,"losses":losses,
            "win_rate_pct":100*wins/len(trades) if trades else None,
            "net_r":sum(x["r"] for x in trades),
            "profit_factor":pos/abs(neg) if neg else None,
            "max_drawdown_r":dd,
            "tp_exits":sum(x["exit_reason"]=="TP" for x in trades),
            "sl_exits":sum(x["exit_reason"]=="SL" for x in trades),
            "same_bar_exits":sum(x["exit_reason"]=="SL_FIRST_SAME_BAR" for x in trades)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--start",required=True); p.add_argument("--end",required=True); p.add_argument("--mt5-path")
    p.add_argument("--symbols",default=DEFAULT_SYMBOLS)
    p.add_argument("--p-gap-pips",default=DEFAULT_GAPS)
    p.add_argument("--spike-multipliers",default=DEFAULT_SPIKES)
    p.add_argument("--max-sl-pips",default=DEFAULT_MAXSLS)
    p.add_argument("--output-prefix")
    a=p.parse_args()
    start=datetime.fromisoformat(a.start.replace("Z","+00:00")); end=datetime.fromisoformat(a.end.replace("Z","+00:00"))
    vals=lambda s:[float(x.strip()) for x in s.split(",") if x.strip()]
    gaps,spikes,maxsls=vals(a.p_gap_pips),vals(a.spike_multipliers),vals(a.max_sl_pips)
    ok=mt5.initialize(path=a.mt5_path) if a.mt5_path else mt5.initialize()
    if not ok:
        t=find_mt5_terminal()
        if t is None or not mt5.initialize(path=str(t)): raise RuntimeError(f"MT5 init failed: {mt5.last_error()}")
    try:
        rows=[]; history={}; errors=[]
        requested=[x.strip() for x in a.symbols.split(",") if x.strip()]
        for req in requested:
            try:
                sym,res=resolve_symbol(req); info=mt5.symbol_info(sym)
                if info is None: raise RuntimeError(f"symbol_info unavailable: {sym}")
                pip,method=pip_size(info); rates=fetch(sym,start,end)
                history[req]={"symbol_used":sym,"resolution":res,"digits":int(info.digits),"point":float(info.point),
                              "pip_size":pip,"pip_method":method,"bars":len(rates),
                              "first_bar_utc":datetime.fromtimestamp(int(rates[0]["time"]),timezone.utc).isoformat(),
                              "last_bar_utc":datetime.fromtimestamp(int(rates[-1]["time"]),timezone.utc).isoformat()}
                for gap in gaps:
                    for spike in spikes:
                        for msl in maxsls:
                            sig=signals(rates,gap*pip,spike,msl*pip)
                            z=outcomes(rates,sig)
                            rows.append({"symbol_requested":req,"symbol_used":sym,"p_gap_pips":gap,
                                         "spike_multiplier":spike,"max_sl_pips":msl,
                                         "p_gap_price":gap*pip,"max_sl_price":msl*pip,**z})
            except Exception as e:
                errors.append({"symbol_requested":req,"error":str(e)})
        stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"); prefix=a.output_prefix or f"SP2L_MT5_FX_DISCOVERY_MATRIX_{stamp}"
        report={"status":"COMPLETE" if not errors else "PARTIAL","research_only":True,
                "mode":"SP2L_MT5_FX_DISCOVERY_MATRIX","generated_utc":datetime.now(timezone.utc).isoformat(),
                "period":{"start_utc":start.isoformat(),"end_utc":end.isoformat()},"timeframe":"M1",
                "symbols_requested":requested,"grid":{"p_gap_pips":gaps,"spike_multipliers":spikes,"max_sl_pips":maxsls},
                "history":history,"errors":errors,"rows":rows,
                "interpretation":{"purpose":"symbol/scale discovery only","canonical":False,
                                  "p_gap_semantics":"UNRESOLVED_SOURCE_GEOMETRY",
                                  "warning":"pip-normalized P-Gap is a research scale parameter, not a canonical Strategy A formula",
                                  "tp_r":1.0,"entry_trigger":"first post-setup lower-low/higher-high",
                                  "sl_anchor":"before-spike extreme","one_active_trade":True}}
        jp=OUT/f"{prefix}.json"; cp=OUT/f"{prefix}.csv"
        jp.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
        fields=list(rows[0].keys()) if rows else []
        with cp.open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
        print(json.dumps({"status":report["status"],"json":str(jp),"csv":str(cp),"symbols":len(history),"rows":len(rows),"errors":len(errors)},indent=2))
    finally:
        mt5.shutdown()

if __name__=="__main__":
    main()
