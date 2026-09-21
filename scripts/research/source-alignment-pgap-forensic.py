#!/usr/bin/env python3
"""Research-only source-alignment forensic measurements for SP2L P-Gap.

Measures source-confirmed structural concepts without defining new canonical
geometry: 10-30 pressure candles, pause/compression, and following trend-bar.
All compression/body metrics are descriptive measurements; no thresholds are
used for classification and no outcomes are analyzed.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
from statistics import median

def candle(r):
    return {k:float(r[k]) for k in ("open","high","low","close")}
def body(x): return abs(x["close"]-x["open"])
def rng(x): return x["high"]-x["low"]
def direction(xs):
    d=sum(x["close"]-x["open"] for x in xs)
    return "BULLISH" if d>0 else "BEARISH" if d<0 else "FLAT"

def candidate(rows,i):
    # Candidate V1 is used only to partition the observed research population.
    # Its implementation thresholds are not treated as source-confirmed rules.
    if i < 43: return None
    for n in range(10,31):
        start=i-2-n
        pressure=rows[start:start+n]; pause=rows[i-2:i]; trend=rows[i]
        if len(pressure)!=n: continue
        d=direction(pressure)
        if d=="FLAT": continue
        pmed=median(rng(x) for x in pressure)
        pause_mean=sum(rng(x) for x in pause)/2
        bmed=median(body(x) for x in pressure)
        trend_aligned=(trend["close"]>trend["open"]) if d=="BULLISH" else (trend["close"]<trend["open"])
        if pause_mean <= pmed*.75 and trend_aligned and body(trend)>=bmed*1.5:
            return {"index":i,"direction":d,"pressure_length":n}
    return None

def imbalance(rows,i):
    if i<2:return None
    l,r=rows[i-2],rows[i]
    if r["low"]>l["high"]: return "BULLISH"
    if r["high"]<l["low"]: return "BEARISH"
    return None

def describe(rows,i):
    z=candidate(rows,i)
    d=z["direction"] if z else None
    # Descriptive source-observable measurements only. No pass/fail labels.
    result={"index":i,"candidate_v1":bool(z),"candidate_direction":d,
            "candidate_pressure_length":z["pressure_length"] if z else None}
    if z:
        n=z["pressure_length"]; pressure=rows[i-2-n:i-2]; pause=rows[i-2:i]; trend=rows[i]
        result.update({
          "pressure_range_median":median(rng(x) for x in pressure),
          "pause_range_mean":sum(rng(x) for x in pause)/2,
          "pause_to_pressure_range_ratio":(sum(rng(x) for x in pause)/2)/median(rng(x) for x in pressure),
          "pressure_body_median":median(body(x) for x in pressure),
          "trend_body":body(trend),
          "trend_body_to_pressure_body_ratio":body(trend)/median(body(x) for x in pressure) if median(body(x) for x in pressure)>0 else None,
          "trend_direction_aligned":((trend["close"]>trend["open"]) if d=="BULLISH" else (trend["close"]<trend["open"]))
        })
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv",required=True)
    ap.add_argument("--sample-artifact",default="artifacts/research/SP2L_BATCH43_PGAP_CANDLE_FORENSICS_2026-09-21.json")
    ap.add_argument("--out",default="artifacts/research/SP2L_BATCH43_SOURCE_ALIGNMENT_FORENSICS_2026-09-21.json")
    a=ap.parse_args()
    with open(a.csv,encoding="utf-8",newline="") as f: rows=[candle(r) for r in csv.DictReader(f)]
    candidate_idx=[]; imbalance_idx=[]
    for i in range(len(rows)):
        if candidate(rows,i): candidate_idx.append(i)
        if imbalance(rows,i): imbalance_idx.append(i)
    cm=set(candidate_idx); im=set(imbalance_idx)
    cats={"candidate_only":sorted(cm-im),"overlap":sorted(cm&im),"imbalance_only":sorted(im-cm)}
    measurements={k:[describe(rows,i) for i in v] for k,v in cats.items()}
    def summarize(items):
        vals=lambda key:[x[key] for x in items if x.get(key) is not None]
        def med(key):
            v=vals(key); return median(v) if v else None
        return {"n":len(items),
                "pressure_length_median":med("candidate_pressure_length"),
                "pause_to_pressure_range_ratio_median":med("pause_to_pressure_range_ratio"),
                "trend_body_to_pressure_body_ratio_median":med("trend_body_to_pressure_body_ratio"),
                "trend_direction_aligned_count":sum(bool(x.get("trend_direction_aligned")) for x in items if "trend_direction_aligned" in x)}
    out={"research_only":True,"dataset":a.csv,
         "source_confirmed_structural_features":["10-30 candles of trend pressure","pressure pauses/compression","trend-bar after pause","continuation context"],
         "implementation_parameters_not_source_confirmed":{"pause_len":2,"compression_factor":0.75,"trend_body_factor":1.5},
         "counts":{"candidate":len(cm),"imbalance":len(im),"overlap":len(cm&im),"candidate_only":len(cm-im),"imbalance_only":len(im-cm)},
         "descriptive_summaries":{k:summarize(v) for k,v in measurements.items()},
         "sample_artifact":a.sample_artifact,
         "boundary":["No source alignment is inferred from performance.","No new threshold, endpoint, candle index, mirror rule, fill rule, or execution rule is defined.","Measurements describe Candidate V1 populations only.","P-Gap executable geometry remains unresolved; Frozen Geometry remains BLOCKED."]}
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out["counts"],indent=2)); print("OUT:",a.out)
if __name__=="__main__": main()
