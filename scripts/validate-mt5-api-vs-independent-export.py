#!/usr/bin/env python3
"""Compare an independent MQL5 CSV export against Python MT5 copy_rates_from.

Research-only. Fails closed on boundary or OHLC mismatch. No timestamp shifting.
"""
from __future__ import annotations
import argparse, csv, json
from datetime import datetime, timezone
import MetaTrader5 as mt5

SYMBOL="XAUUSD.ecn"
TIMEFRAME=mt5.TIMEFRAME_M1

def parse(v):
    return datetime.fromisoformat(v.replace("Z","+00:00")).astimezone(timezone.utc).replace(second=0,microsecond=0)

def epoch(v): return int(v)

p=argparse.ArgumentParser()
p.add_argument("--csv", required=True)
p.add_argument("--start", required=True)
p.add_argument("--end", required=True)
a=p.parse_args()
start,end=parse(a.start),parse(a.end)

with open(a.csv,newline="",encoding="utf-8-sig") as f:
    rows=list(csv.DictReader(f))

csv_ts=[epoch(r["time_epoch"]) for r in rows]
csv_first=datetime.fromtimestamp(csv_ts[0],timezone.utc).isoformat().replace("+00:00","Z") if rows else None
csv_last=datetime.fromtimestamp(csv_ts[-1],timezone.utc).isoformat().replace("+00:00","Z") if rows else None

expected=int((end-start).total_seconds()//60)+1

result={"requested_start":a.start,"requested_end":a.end,"expected_bars":expected,
        "csv_bars":len(rows),"csv_first_utc":csv_first,"csv_last_utc":csv_last}

if not rows or csv_first != a.start or csv_last != a.end or len(rows)!=expected:
    result["status"]="FAIL"
    result["reason"]="independent export boundaries/count do not match request"
    print(json.dumps(result,indent=2)); raise SystemExit(1)

if not mt5.initialize():
    result["status"]="FAIL"; result["reason"]=f"MT5 initialize failed: {mt5.last_error()}"
    print(json.dumps(result,indent=2)); raise SystemExit(1)

try:
    rates=mt5.copy_rates_from(SYMBOL,TIMEFRAME,end,expected)
    if rates is None or len(rates)!=expected:
        result["status"]="FAIL"; result["reason"]="API count mismatch"; result["api_bars"]=None if rates is None else len(rates)
        print(json.dumps(result,indent=2)); raise SystemExit(1)

    api_ts=[int(x["time"]) for x in rates]
    api_first=datetime.fromtimestamp(api_ts[0],timezone.utc).isoformat().replace("+00:00","Z")
    api_last=datetime.fromtimestamp(api_ts[-1],timezone.utc).isoformat().replace("+00:00","Z")
    result.update({"api_bars":len(rates),"api_first_utc":api_first,"api_last_utc":api_last})

    fields=("open","high","low","close","tick_volume","spread","real_volume")
    mismatches=[]
    if api_ts != csv_ts:
        mismatches.append({"field":"timestamp","count":sum(x!=y for x,y in zip(api_ts,csv_ts))})
    for i,(rr,aa) in enumerate(zip(rows,rates)):
        for field in fields:
            cv=float(rr[field]) if field in ("open","high","low","close") else int(float(rr[field]))
            av=float(aa[field])
            if field in ("open","high","low","close"):
                if abs(cv-av)>1e-9:
                    mismatches.append({"row":i,"field":field,"csv":cv,"api":av})
            elif cv != int(av):
                mismatches.append({"row":i,"field":field,"csv":cv,"api":int(av)})
    result["mismatch_count"]=len(mismatches)
    result["first_mismatches"]=mismatches[:10]
    result["status"]="PASS" if api_first==a.start and api_last==a.end and not mismatches else "FAIL"
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result["status"]=="PASS" else 1)
finally:
    mt5.shutdown()
