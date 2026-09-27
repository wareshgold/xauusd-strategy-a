"""Exact timestamp audit for unresolved MT5 matrix gaps.

Research-only. Joins gate classifications to the original matrix artifact and
reports exact intervals plus overlap with documented replay windows.
"""
from __future__ import annotations
import argparse,json
from datetime import datetime,timedelta,timezone
from pathlib import Path
WINDOWS={"W1":(7,17),"W2":(8,17),"W3":(13,17)}
def parse(s): return datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(timezone.utc)
def overlap(start,end,h1,h2):
    total=0; day=start.replace(hour=0,minute=0,second=0,microsecond=0)
    while day<end:
        a=max(start,day.replace(hour=h1)); b=min(end,day.replace(hour=h2))
        if b>a: total+=int((b-a).total_seconds()//60)
        day+=timedelta(days=1)
    return total
def main():
    p=argparse.ArgumentParser(); p.add_argument("matrix"); p.add_argument("gate"); p.add_argument("--symbol",action="append"); a=p.parse_args()
    m=json.loads(Path(a.matrix).read_text(encoding="utf-8")); g=json.loads(Path(a.gate).read_text(encoding="utf-8"))
    bad={r["case_id"] for r in g["rows"] if r["status"]=="DATA_QUALITY_UNRESOLVED"}; wanted=set(a.symbol or [])
    print("MATRIX=",a.matrix); print("GATE=",a.gate)
    for r in m["results"]:
        if r["case_id"] not in bad or r.get("session_start_utc") is not None: continue
        if wanted and r["requested_symbol"] not in wanted: continue
        print(f"\n{r['requested_symbol']} {r['week_start_utc']} -> {r['week_end_utc']}")
        for x in r.get("gap_intervals",[]):
            if x.get("non_weekend_minutes",0)<=0: continue
            s=parse(x["start_utc"]); e=parse(x["end_utc"])
            ov=" ".join(f"{k}={overlap(s,e,*v)}m" for k,v in WINDOWS.items())
            print(f"  {x['start_utc']} -> {x['end_utc']} missing={x['missing_minutes']} nonweekend={x['non_weekend_minutes']} {ov}")
if __name__=="__main__": raise SystemExit(main())
