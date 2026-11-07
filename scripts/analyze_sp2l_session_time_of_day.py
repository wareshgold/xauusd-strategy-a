#!/usr/bin/env python
"""Privacy-safe session/time-of-day diagnostics for the weekly SP2L paired audit.

Reads the private audit ZIP and the existing anonymized paired CSV. It does
not query MT5 or touch the live runner. Emits aggregate results only; no
calendar dates, clock timestamps, prices, tickets, or position identifiers.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np

SYMBOL="XAUUSD.ecn"
MAGIC=26092301
RRS=range(1,7)
LONDON=ZoneInfo("Europe/London")
NEW_YORK=ZoneInfo("America/New_York")
TOKYO=ZoneInfo("Asia/Tokyo")

def utc(v):
    if not v: return None
    try: return datetime.fromisoformat(str(v).replace("Z","+00:00")).astimezone(timezone.utc)
    except (TypeError,ValueError): return None

def load_trade_times(bundle):
    with zipfile.ZipFile(bundle) as z:
        deals=json.load(z.open("raw/mt5_history_deals.json"))
        events=[]
        with z.open("raw/runner_files/forward_events.jsonl") as f:
            for line in f:
                try: events.append(json.loads(line))
                except Exception: continue
    bypos=defaultdict(list)
    for d in deals:
        if d.get("symbol")==SYMBOL and d.get("position_id") is not None:
            bypos[str(d["position_id"])].append(d)
    theoretical=defaultdict(set); lifecycle={}
    for e in events:
        p=str(e.get("position","") or "")
        if not p: continue
        if e.get("event")=="TELEGRAM_DEAL_LIFECYCLE":
            try: s=float(e.get("theoretical_sl") or 0)
            except (TypeError,ValueError): s=0
            if s: theoretical[p].add(round(s,8))
        elif e.get("event")=="POSITION_LIFECYCLE":
            try: s=float(e.get("sl") or 0)
            except (TypeError,ValueError): s=0
            t=utc(e.get("ts_utc"))
            if s and t and (p not in lifecycle or t<lifecycle[p][0]):
                lifecycle[p]=(t,s)
    selected=[]
    for p,ds in bypos.items():
        en=[d for d in ds if int(d.get("entry",-1))==0]
        ex=[d for d in ds if int(d.get("entry",-1))==1]
        if len(en)!=1 or len(ex)!=1: continue
        a=en[0]
        if str(a.get("magic"))!=str(MAGIC) or int(a.get("type",-1)) not in (0,1): continue
        vals=theoretical.get(p,set()); life=lifecycle.get(p)
        if len(vals)!=1 or life is None or abs(next(iter(vals))-life[1])>1e-7: continue
        ms=int(a.get("time_msc") or int(a.get("time",0))*1000)
        if life[0].timestamp()*1000>ms: continue
        selected.append((ms,p,datetime.fromtimestamp(ms/1000,timezone.utc)))
    selected.sort(key=lambda x:(x[0],x[1]))
    if len(selected)!=66: raise SystemExit(f"POPULATION_GATE_FAILED expected=66 actual={len(selected)}")
    return [x[2] for x in selected]

def summarize(rows):
    out={"n":len(rows)}
    if not rows: return out
    out["actual_net_mean_usd"]=round(float(np.mean([float(r["actual_net_usd"]) for r in rows])),4)
    for rr in RRS:
        vals=[float(r[f"actual_minus_rr{rr}_usd"]) for r in rows if r.get(f"actual_minus_rr{rr}_usd") not in ("",None)]
        out[f"RR{rr}"]={"paired_n":len(vals),
            "mean_delta_usd":round(float(np.mean(vals)),4) if vals else None,
            "sum_delta_usd":round(float(np.sum(vals)),4) if vals else None,
            "actual_better_n":sum(x>0.005 for x in vals),
            "fixed_rr_better_n":sum(x<-.005 for x in vals)}
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("bundle")
    ap.add_argument("csv")
    ap.add_argument("--output-dir",default="")
    a=ap.parse_args()
    times=load_trade_times(Path(a.bundle).expanduser().resolve())
    csv_path=Path(a.csv).expanduser().resolve()
    with csv_path.open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
    if len(rows)!=66: raise SystemExit(f"CSV_POPULATION_GATE_FAILED expected=66 actual={len(rows)}")
    if any(r.get("trade_key")!=f"T{i:03d}" for i,r in enumerate(rows,1)):
        raise SystemExit("TRADE_ORDER_GATE_FAILED")
    out=Path(a.output_dir).expanduser().resolve() if a.output_dir else csv_path.parent/"SP2L_SESSION_TIME_QC"
    out.mkdir(parents=True,exist_ok=True)

    groups=defaultdict(list)
    utc_hours=defaultdict(list); london_hours=defaultdict(list); ny_hours=defaultdict(list)
    session_counts=defaultdict(int)
    for i,(r,t) in enumerate(zip(rows,times)):
        lo=t.astimezone(LONDON); ny=t.astimezone(NEW_YORK); tk=t.astimezone(TOKYO)
        london=8<=lo.hour<17
        newyork=8<=ny.hour<17
        tokyo=9<=tk.hour<18
        overlap=london and newyork
        groups["LONDON"].append(r) if london else None
        groups["NEW_YORK"].append(r) if newyork else None
        groups["LONDON_NEW_YORK_OVERLAP"].append(r) if overlap else None
        groups["TOKYO"].append(r) if tokyo else None
        groups["OUTSIDE_LONDON_NEW_YORK"].append(r) if not london and not newyork else None
        groups["LONDON_ONLY"].append(r) if london and not newyork else None
        groups["NEW_YORK_ONLY"].append(r) if newyork and not london else None
        groups["OUTSIDE_CORE_SESSIONS"].append(r) if not london and not newyork and not tokyo else None
        utc_hours[t.hour].append(r)
        london_hours[lo.hour].append(r)
        ny_hours[ny.hour].append(r)
        session_counts["LONDON"]+=int(london)
        session_counts["NEW_YORK"]+=int(newyork)
        session_counts["OVERLAP"]+=int(overlap)
        session_counts["TOKYO"]+=int(tokyo)

    def hour_report(d):
        return {f"{h:02d}":summarize(d[h]) for h in sorted(d)}
    report={
      "status":"SESSION_AND_TIME_OF_DAY_QC_COMPLETE",
      "population":66,
      "timezone_method":"IANA zoneinfo: Europe/London, America/New_York, Asia/Tokyo; DST applied per entry instant.",
      "session_definitions":{
        "London":"08:00-16:59 Europe/London local time",
        "New_York":"08:00-16:59 America/New_York local time",
        "Tokyo":"09:00-17:59 Asia/Tokyo local time",
        "overlap":"Entry instant is inside both London and New York definitions"
      },
      "session_trade_counts":dict(session_counts),
      "session_groups":{k:summarize(v) for k,v in groups.items()},
      "utc_hourly":hour_report(utc_hours),
      "london_local_hourly":hour_report(london_hours),
      "new_york_local_hourly":hour_report(ny_hours),
      "privacy":"Aggregate-only output. No calendar dates, exact clock times, prices, tickets, or position identifiers.",
      "limitations":[
        "Only 66 in-sample trades across four relative days; session/hour subgroups may be very small.",
        "Session hours are explicit research conventions, not canonical SP2L rules.",
        "A trade is assigned by entry time only; this does not imply the full trade occurred within that session.",
        "Overlapping session flags are intentional; group counts are not mutually exclusive.",
        "Hourly and session comparisons are descriptive, not statistically validated edge claims.",
        "Multiple subgroup comparisons increase false-discovery risk; no filter or production rule is selected.",
        "Fixed-RR counterfactuals retain the prior barrier-price and cost assumptions."
      ]
    }
    p=out/"session_time_qc_report.json"
    p.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    print("SESSION_AND_TIME_OF_DAY_QC_COMPLETE")
    print("TRADES=66")
    print("SESSION_COUNTS=",dict(session_counts))
    print("SESSION_SUMMARIES")
    for k,v in report["session_groups"].items():
        print(k,"N=",v["n"],"ACTUAL_NET_MEAN=",v.get("actual_net_mean_usd"),
              " ".join(f"RR{rr}={v.get(f'RR{rr}',{}).get('mean_delta_usd')}" for rr in RRS))
    print("UTC_HOURLY_SUMMARIES")
    for h,v in report["utc_hourly"].items():
        print("UTC_HOUR",h,"N=",v["n"]," ".join(f"RR{rr}={v.get(f'RR{rr}',{}).get('mean_delta_usd')}" for rr in RRS))
    print("REPORT=",p)
    print("REPORT_SHA256=",digest)

if __name__=="__main__": main()
