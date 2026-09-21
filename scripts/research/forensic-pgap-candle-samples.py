#!/usr/bin/env python3
"""Research-only candle-level forensic sampler for Batch43 P-Gap comparison.

Recomputes Candidate V1 and the existing 3-candle imbalance observation,
then samples candidate-only, overlap, and imbalance-only events. No outcomes,
optimization, canonical promotion, or live trading.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
from statistics import median

def c(r): return {k:float(r[k]) for k in ("open","high","low","close")}
def body(x): return abs(x["close"]-x["open"])
def rng(x): return x["high"]-x["low"]

def candidate(rows,i,min_p=10,max_p=30,pause_len=2,compression=.75,trend_factor=1.5):
    if i < max_p+pause_len+1: return None
    for n in range(min_p,max_p+1):
        start=i-pause_len-n
        pressure=rows[start:start+n]; pause=rows[i-pause_len:i]; trend=rows[i]
        if len(pressure)!=n: continue
        disp=sum(x["close"]-x["open"] for x in pressure)
        direction="BULLISH" if disp>0 else "BEARISH" if disp<0 else None
        if not direction: continue
        pr=median(rng(x) for x in pressure)
        pause_r=sum(rng(x) for x in pause)/len(pause)
        pb=median(body(x) for x in pressure)
        trend_dir=(trend["close"]>trend["open"]) if direction=="BULLISH" else (trend["close"]<trend["open"])
        if pause_r<=pr*compression and trend_dir and body(trend)>=pb*trend_factor:
            return {"index":i,"pressure_length":n,"direction":direction}
    return None

def imbalance(rows,i):
    if i<2:return None
    left,right=rows[i-2],rows[i]
    if right["low"]>left["high"]: return "BULLISH"
    if right["high"]<left["low"]: return "BEARISH"
    return None

def snapshot(rows,i,kind,direction=None,pressure_length=None):
    lo=max(0,i-6); hi=min(len(rows),i+5)
    candles=[]
    for j in range(lo,hi):
        x=rows[j]
        candles.append({"offset":j-i,"open":x["open"],"high":x["high"],"low":x["low"],"close":x["close"],
                        "body":body(x),"range":rng(x)})
    return {"index":i,"kind":kind,"direction":direction,"pressure_length":pressure_length,"window":candles}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",required=True); p.add_argument("--samples",type=int,default=12)
    p.add_argument("--out",default="artifacts/research/SP2L_BATCH43_PGAP_CANDLE_FORENSICS_2026-09-21.json")
    a=p.parse_args()
    rows=[]
    with open(a.csv,encoding="utf-8",newline="") as f:
        rows=[c(r) for r in csv.DictReader(f)]
    ce=[]; ie=[]
    for i in range(len(rows)):
        z=candidate(rows,i)
        if z: ce.append(z)
        g=imbalance(rows,i)
        if g: ie.append({"index":i,"direction":g})
    cm={x["index"]:x for x in ce}; im={x["index"]:x for x in ie}
    cats={"candidate_only":sorted(set(cm)-set(im)),
          "overlap":sorted(set(cm)&set(im)),
          "imbalance_only":sorted(set(im)-set(cm))}
    # Deterministic evenly spaced samples, preserving both directions where possible.
    samples={}
    for k,idxs in cats.items():
        if not idxs: samples[k]=[]; continue
        n=min(a.samples,len(idxs))
        picks=[idxs[round(j*(len(idxs)-1)/(n-1))] for j in range(n)] if n>1 else [idxs[len(idxs)//2]]
        samples[k]=[]
        for i in picks:
            z=cm.get(i); g=im.get(i)
            samples[k].append(snapshot(rows,i,k,(z or g)["direction"],z.get("pressure_length") if z else None))
    out={"research_only":True,"dataset":a.csv,"candidate_parameters":{"pressure_min":10,"pressure_max":30,"pause_len":2,"compression_factor":.75,"trend_body_factor":1.5},
         "counts":{"candidate":len(cm),"imbalance":len(im),"overlap":len(set(cm)&set(im)),
                   "candidate_only":len(cats["candidate_only"]),"imbalance_only":len(cats["imbalance_only"])},
         "samples":samples,
         "interpretation_boundary":["Descriptive candle-level comparison only.","Does not establish source alignment.","Does not tune thresholds or promote geometry.","P-Gap remains executable-geometry unresolved."]}
    Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out["counts"],indent=2)); print("OUT:",a.out)

if __name__=="__main__": main()
