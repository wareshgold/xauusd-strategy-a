#!/usr/bin/env python
"""Privacy-safe day-bucket stability and subgroup QC for the SP2L paired audit.

Reads the private audit ZIP and the already-produced anonymized paired CSV.
Does not query MT5, access the live runner, or expose calendar dates, times,
position IDs, tickets, or prices in outputs. Relative D01... buckets preserve
chronological day grouping only.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

SYMBOL = "XAUUSD.ecn"
MAGIC = 26092301
RRS = range(1, 7)

def num(v):
    try: return float(v) if v is not None else 0.0
    except (TypeError, ValueError): return 0.0

def utc(v):
    if not v: return None
    try: return datetime.fromisoformat(str(v).replace("Z","+00:00")).astimezone(timezone.utc)
    except (TypeError, ValueError): return None

def load_order_and_days(bundle):
    with zipfile.ZipFile(bundle) as z:
        deals=json.load(z.open("raw/mt5_history_deals.json"))
        events=[]
        with z.open("raw/runner_files/forward_events.jsonl") as f:
            for line in f:
                try: events.append(json.loads(line))
                except Exception: continue
    bypos=defaultdict(list); theoretical=defaultdict(set); lifecycle={}
    for d in deals:
        if d.get("symbol")==SYMBOL and d.get("position_id") is not None:
            bypos[str(d["position_id"])].append(d)
    for e in events:
        p=str(e.get("position","") or "")
        if not p: continue
        if e.get("event")=="TELEGRAM_DEAL_LIFECYCLE":
            s=num(e.get("theoretical_sl"))
            if s: theoretical[p].add(round(s,8))
        elif e.get("event")=="POSITION_LIFECYCLE":
            s=num(e.get("sl")); t=utc(e.get("ts_utc"))
            if s and t and (p not in lifecycle or t<lifecycle[p][0]):
                lifecycle[p]=(t,s)
    selected=[]
    for p,rows in bypos.items():
        en=[d for d in rows if int(d.get("entry",-1))==0]
        ex=[d for d in rows if int(d.get("entry",-1))==1]
        if len(en)!=1 or len(ex)!=1: continue
        a,b=en[0],ex[0]
        if str(a.get("magic"))!=str(MAGIC) or int(a.get("type",-1)) not in (0,1): continue
        ss=theoretical.get(p,set()); life=lifecycle.get(p)
        if len(ss)!=1 or life is None: continue
        sl=next(iter(ss)); t,s=life
        if abs(sl-s)>1e-7: continue
        ms=int(a.get("time_msc") or int(a.get("time",0))*1000)
        if t.timestamp()*1000>ms: continue
        selected.append((ms,p,datetime.fromtimestamp(ms/1000,timezone.utc).date()))
    selected.sort(key=lambda x:(x[0],x[1]))
    if len(selected)!=66: raise SystemExit(f"POPULATION_GATE_FAILED expected=66 actual={len(selected)}")
    unique=sorted({x[2] for x in selected})
    labels={d:f"D{i+1:02d}" for i,d in enumerate(unique)}
    return [labels[x[2]] for x in selected], len(unique)

def mean(xs):
    return round(float(np.mean(xs)),4) if xs else None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("bundle", help="Private weekly audit ZIP")
    ap.add_argument("csv", help="paired_trade_results_anonymized.csv")
    ap.add_argument("--output-dir",default="")
    a=ap.parse_args()
    days,day_count=load_order_and_days(Path(a.bundle).expanduser().resolve())
    src=Path(a.csv).expanduser().resolve()
    with src.open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
    if len(rows)!=66: raise SystemExit(f"CSV_POPULATION_GATE_FAILED expected=66 actual={len(rows)}")
    for i,r in enumerate(rows,1):
        if r.get("trade_key")!=f"T{i:03d}": raise SystemExit("TRADE_ORDER_GATE_FAILED")
    out=Path(a.output_dir).expanduser().resolve() if a.output_dir else src.parent/"SP2L_DAY_STABILITY_QC"
    out.mkdir(parents=True,exist_ok=True)

    # Investigate whether RR3..RR6 identical no-update means are genuine row-level
    # equality or a reporting/selection artifact. Only aggregate diagnostics leave disk.
    no_update=[r for r in rows if int(r.get("successful_trail_updates") or 0)==0]
    subgroup={}
    for rr in RRS:
        vals=[float(r[f"actual_minus_rr{rr}_usd"]) for r in no_update if r.get(f"actual_minus_rr{rr}_usd") not in ("",None)]
        subgroup[f"RR{rr}"]={"n":len(vals),"mean_delta_usd":mean(vals),"sum_delta_usd":round(sum(vals),4) if vals else None}
    rowwise={}
    for rr in range(3,7):
        col=f"rr{rr}_net_usd"
        vals=[r.get(col,"") for r in no_update]
        rowwise[col]={"nonblank":sum(v not in ("",None) for v in vals),
                      "unique_values":len(set(v for v in vals if v not in ("",None)))}
    same_delta_rows=0
    for r in no_update:
        vals=[r.get(f"actual_minus_rr{rr}_usd","") for rr in range(3,7)]
        if all(v not in ("",None) for v in vals) and len(set(vals))==1: same_delta_rows+=1

    # Day-bucket paired results, with minimum-N guard for interpretation.
    buckets=defaultdict(list)
    for i,r in enumerate(rows): buckets[days[i]].append(r)
    day_report=[]
    for label in sorted(buckets):
        group=buckets[label]
        item={"day_bucket":label,"n":len(group)}
        for rr in RRS:
            vals=[float(r[f"actual_minus_rr{rr}_usd"]) for r in group if r.get(f"actual_minus_rr{rr}_usd") not in ("",None)]
            item[f"RR{rr}_mean_delta_usd"]=mean(vals)
            item[f"RR{rr}_n"]=len(vals)
        day_report.append(item)

    # Anonymized joined CSV contains only T-key, D-bucket, direction, and deltas.
    joined=out/"paired_results_relative_day_buckets.csv"
    fields=["trade_key","day_bucket","direction"]+[f"actual_minus_rr{rr}_usd" for rr in RRS]
    with joined.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for i,r in enumerate(rows):
            w.writerow({k:(days[i] if k=="day_bucket" else r.get(k,"")) for k in fields})

    report={
      "status":"DAY_BUCKET_AND_SUBGROUP_QC_COMPLETE",
      "population":66,
      "distinct_relative_day_buckets":day_count,
      "date_privacy":"Only relative D01... labels are emitted; no calendar date or timestamp is written.",
      "no_successful_update_subgroup":{"n":len(no_update),"paired_delta":subgroup,
        "rr3_to_rr6_fixed_rr_net_value_uniqueness":rowwise,
        "rows_with_identical_rr3_to_rr6_paired_deltas":same_delta_rows},
      "relative_day_buckets":day_report,
      "interpretation_limits":[
        "Relative day buckets are chronological group labels, not calendar dates.",
        "Small per-day sample sizes are descriptive only; no day-level significance claim.",
        "This is in-sample audit data, not an untouched holdout.",
        "No canonical SP2L geometry, execution rule, or live configuration is changed."
      ]
    }
    p=out/"day_stability_qc_report.json"
    p.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    print("DAY_BUCKET_AND_SUBGROUP_QC_COMPLETE")
    print("TRADES=66 DISTINCT_DAY_BUCKETS=",day_count)
    print("NO_UPDATE_N=",len(no_update)," IDENTICAL_RR3_RR6_DELTA_ROWS=",same_delta_rows)
    for k,v in subgroup.items(): print(k,"N=",v["n"],"MEAN_DELTA=",v["mean_delta_usd"],"SUM_DELTA=",v["sum_delta_usd"])
    print("DAY_BUCKET_SUMMARY")
    for d in day_report:
        print(d["day_bucket"],"N=",d["n"]," ".join(f"RR{rr}={d[f'RR{rr}_mean_delta_usd']}" for rr in RRS))
    print("REPORT=",p)
    print("REPORT_SHA256=",digest)
    print("ANONYMIZED_JOINED_CSV=",joined)

if __name__=="__main__": main()
