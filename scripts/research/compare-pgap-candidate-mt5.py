#!/usr/bin/env python3
"""Research-only comparison of P-Gap Candidate V1 against the existing
three-candle imbalance observation on an archived MT5 M1 CSV.

No trade outcomes, parameter optimization, canonical geometry, or live signals.
"""

from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from statistics import median

def candle(r):
    return {k: float(r[k]) for k in ("open","high","low","close")}

def body(c): return abs(c["close"]-c["open"])
def rng(c): return c["high"]-c["low"]

def candidate(rows, i, min_p=10, max_p=30, pause_len=2, compression=0.75, trend_factor=1.5):
    if i < max_p + pause_len + 1:
        return None
    # evaluate bounded windows so each event is deterministic
    for n in range(min_p, max_p+1):
        start=i-pause_len- n
        pressure=rows[start:start+n]
        pause=rows[i-pause_len:i]
        trend=rows[i]
        if len(pressure)!=n: continue
        displacement=sum(c["close"]-c["open"] for c in pressure)
        direction="BULLISH" if displacement>0 else "BEARISH" if displacement<0 else None
        if not direction: continue
        p_range=median(rng(c) for c in pressure)
        pause_range=sum(rng(c) for c in pause)/len(pause)
        p_body=median(body(c) for c in pressure)
        directional_trend=(trend["close"]>trend["open"]) if direction=="BULLISH" else (trend["close"]<trend["open"])
        if pause_range <= p_range*compression and directional_trend and body(trend)>=p_body*trend_factor:
            return {"index":i,"pressure_length":n,"direction":direction}
    return None

def imbalance(rows,i):
    if i<2: return None
    left,right=rows[i-2],rows[i]
    if right["low"]>left["high"]: return "BULLISH"
    if right["high"]<left["low"]: return "BEARISH"
    return None

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",required=True)
    p.add_argument("--out",default="artifacts/research/SP2L_PGAP_CANDIDATE_MT5_COMPARISON_2026-09-21.json")
    args=p.parse_args()
    rows=[]
    with open(args.csv,encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f):
            rows.append(candle(r))
    candidate_events=[]; imbalance_events=[]
    for i in range(len(rows)):
        c=candidate(rows,i)
        if c: candidate_events.append(c)
        g=imbalance(rows,i)
        if g: imbalance_events.append({"index":i,"direction":g})
    cset={x["index"] for x in candidate_events}
    iset={x["index"] for x in imbalance_events}
    out={
      "research_only":True,
      "dataset":str(args.csv),
      "candidate_parameters":{"pressure_min":10,"pressure_max":30,"pause_len":2,"compression_factor":0.75,"trend_body_factor":1.5},
      "candidate_event_count":len(candidate_events),
      "existing_imbalance_event_count":len(imbalance_events),
      "overlap_count":len(cset & iset),
      "candidate_only_count":len(cset-iset),
      "imbalance_only_count":len(iset-cset),
      "candidate_events":candidate_events,
      "status":"DESCRIPTIVE_ONLY",
      "canonical_geometry_changed":False,
      "live_trading":False
    }
    outpath=Path(args.out); outpath.parent.mkdir(parents=True,exist_ok=True)
    outpath.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:out[k] for k in out if k not in ("candidate_events",)},indent=2))
    print(f"OUT: {outpath}")

if __name__=="__main__": main()
