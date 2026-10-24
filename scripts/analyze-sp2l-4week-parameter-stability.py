"""Research-only 4-week x 81 SP2L parameter stability matrix.

Uses the existing non-canonical author-replica signal logic, but evaluates the
declared 4-week partitions under every combination of the pre-registered grid.
No canonical rule or production parameter is selected.
"""
from __future__ import annotations
import importlib.util, json, math, os
from datetime import datetime, timezone
from pathlib import Path
import MetaTrader5 as mt5

BASE=Path("scripts/run-author-replica-mt5-nonoverlap-stability.py")
spec=importlib.util.spec_from_file_location("base",BASE); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
SYMBOL=os.getenv("TRADING_SYMBOL","XAUUSD.ecn"); N=int(os.getenv("BARS","10000"))
WEEKS=[("2026-09-14","2026-09-18"),("2026-09-07","2026-09-11"),("2026-08-31","2026-09-04"),("2026-08-24","2026-08-28")]
PGAPS=[0.8,1.0,1.2]; SPIKES=[1.3,1.5,1.7]; MAXSLS=[8.0,10.0,12.0]; TPS=[0.8,1.0,1.2]

def dt(s,end=False): return datetime.fromisoformat(s+("T23:59:59+00:00" if end else "T00:00:00+00:00"))
def outcome(c,i,d,entry,sl,tp):
    for j in range(i+1,len(c)):
        x=c[j]
        hs=x["low"]<=sl if d=="BUY" else x["high"]>=sl
        ht=x["high"]>=tp if d=="BUY" else x["low"]<=tp
        if hs and ht:return "AMBIGUOUS"
        if hs:return "LOSS"
        if ht:return "WIN"
    return "OPEN_OR_UNRESOLVED"

def run(c,start,end,pg,sm,maxsl,tpr):
    old=(mod.P_GAP,mod.SPIKE_MULT,mod.MAX_SL,mod.TP_R)
    mod.P_GAP,mod.SPIKE_MULT,mod.MAX_SL,mod.TP_R=pg,sm,maxsl,tpr
    rows=[]
    try:
        for i in range(4,len(c)):
            s=mod.signal(c,i)
            if not s: continue
            d,e,sl=s; ts=c[i-1]["time"]
            if not (start.timestamp()<=ts<=end.timestamp()): continue
            risk=abs(e-sl)
            if risk<=0 or risk>maxsl: continue
            tp=e+tpr*risk if d=="BUY" else e-tpr*risk
            rows.append(outcome(c,i,d,e,sl,tp))
    finally: mod.P_GAP,mod.SPIKE_MULT,mod.MAX_SL,mod.TP_R=old
    w=rows.count("WIN"); l=rows.count("LOSS"); a=rows.count("AMBIGUOUS"); u=rows.count("OPEN_OR_UNRESOLVED")
    dec=w+l; eq=peak=dd=0
    for x in rows:
        if x=="WIN":eq+=1
        elif x=="LOSS":eq-=1
        peak=max(peak,eq);dd=max(dd,peak-eq)
    return {"signals":len(rows),"wins":w,"losses":l,"ambiguous":a,"open_or_unresolved":u,
            "decisive_wr":w/dec if dec else None,"total_R":w-l,"profit_factor":w/l if l else None,"max_drawdown_R":dd}

if not mt5.initialize(): raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
try:
    if not mt5.symbol_select(SYMBOL,True): raise SystemExit(f"symbol_select failed: {mt5.last_error()}")
    datasets={}
    for a,b in WEEKS:
        end=dt(b,True); rates=mt5.copy_rates_from(SYMBOL,mt5.TIMEFRAME_M1,end,N)
        if rates is None or len(rates)==0: raise SystemExit(f"No data for {a}: {mt5.last_error()}")
        datasets[(a,b)]=[{"time":int(r[0]),"open":float(r[1]),"high":float(r[2]),"low":float(r[3]),"close":float(r[4])} for r in rates]
finally: mt5.shutdown()

results=[]
for pg in PGAPS:
 for sm in SPIKES:
  for ms in MAXSLS:
   for tp in TPS:
    weeks=[run(c,dt(a),dt(b,True),pg,sm,ms,tp) for (a,b),c in datasets.items()]
    w=sum(x["wins"] for x in weeks); l=sum(x["losses"] for x in weeks); dec=w+l
    results.append({"pGap":pg,"spikeMultiplier":sm,"maxSL":ms,"tpR":tp,"weeks":weeks,
      "signals":sum(x["signals"] for x in weeks),"wins":w,"losses":l,
      "ambiguous":sum(x["ambiguous"] for x in weeks),"open_or_unresolved":sum(x["open_or_unresolved"] for x in weeks),
      "decisive_wr":w/dec if dec else None,"total_R":w-l,"profit_factor":w/l if l else None,
      "max_weekly_drawdown_R":max(x["max_drawdown_R"] for x in weeks)})

def stats(vals):
    vals=sorted(x for x in vals if x is not None); n=len(vals)
    q=lambda p: vals[min(n-1,int(p*(n-1)))]
    return {"min":vals[0],"q1":q(.25),"median":q(.5),"q3":q(.75),"max":vals[-1]}
wr=[x["decisive_wr"] for x in results]; rr=[x["total_R"] for x in results]
base=next(x for x in results if (x["pGap"],x["spikeMultiplier"],x["maxSL"],x["tpR"])==(1.0,1.5,10.0,1.0))
agg={"combinations":81,"wr_stats":stats(wr),"total_R_stats":stats(rr),
     "positive_total_R_count":sum(x["total_R"]>0 for x in results),
     "above_60pct_wr_count":sum(x["decisive_wr"]>0.60 for x in results),
     "baseline":{k:base[k] for k in ["pGap","spikeMultiplier","maxSL","tpR","signals","wins","losses","ambiguous","decisive_wr","total_R","profit_factor"]}}
# One-parameter neighbors around baseline.
neighbors=[]
for key,levels in [("pGap",PGAPS),("spikeMultiplier",SPIKES),("maxSL",MAXSLS),("tpR",TPS)]:
    for v in levels:
        if v=={"pGap":1.0,"spikeMultiplier":1.5,"maxSL":10.0,"tpR":1.0}[key]: continue
        cond={k:{"pGap":1.0,"spikeMultiplier":1.5,"maxSL":10.0,"tpR":1.0}[k] for k in ["pGap","spikeMultiplier","maxSL","tpR"]}; cond[key]=v
        z=next(x for x in results if all(x[k]==cond[k] for k in cond))
        neighbors.append({"parameter":key,"level":v,"delta_WR":z["decisive_wr"]-base["decisive_wr"],"delta_R":z["total_R"]-base["total_R"],"delta_PF":(z["profit_factor"] or 0)-(base["profit_factor"] or 0)})
agg["baseline_neighbors"]=neighbors
out=Path("artifacts/SP2L_parameter_stability_4week_81_matrix_2026-09-19.json"); out.parent.mkdir(exist_ok=True)
payload={"research_only":True,"symbol":SYMBOL,"timeframe":"M1","weeks":WEEKS,"grid":{"pGap":PGAPS,"spikeMultiplier":SPIKES,"maxSL":MAXSLS,"tpR":TPS},"aggregate":agg,"combinations":results}
out.write_text(json.dumps(payload,indent=2),encoding="utf-8")
print(json.dumps({"output":str(out),"aggregate":agg},indent=2))
