"""XAUUSD raw-bar boundary forensic audit (research-only)."""
from __future__ import annotations
import argparse,json
from datetime import datetime,timedelta,timezone
from pathlib import Path
import MetaTrader5 as mt5

def dt(s): return datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(timezone.utc)
def iso(x): return x.astimezone(timezone.utc).isoformat() if x else None

def main():
    p=argparse.ArgumentParser()
    p.add_argument("matrix"); p.add_argument("--mt5-path",required=True)
    p.add_argument("--symbol",default="XAUUSD"); p.add_argument("--limit",type=int,default=20)
    p.add_argument("--unique-gaps",action="store_true")
    p.add_argument("--output")
    a=p.parse_args()
    d=json.loads(Path(a.matrix).read_text(encoding="utf-8"))
    gaps=[]
    for r in d.get("results",[]):
        if r.get("requested_symbol")!=a.symbol: continue
        for g in r.get("gap_intervals",[]):
            if g.get("non_weekend_minutes",0)>0: gaps.append((r,g))
    if a.unique_gaps:
        seen=set(); unique=[]
        for r,g in gaps:
            key=(r.get("broker_symbol"),g.get("start_utc"),g.get("end_utc"))
            if key in seen: continue
            seen.add(key); unique.append((r,g))
        gaps=unique
    gaps=gaps[:a.limit]
    if not mt5.initialize(path=a.mt5_path):
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    out=[]
    for r,g in gaps:
        s,e=dt(g["start_utc"]),dt(g["end_utc"])
        broker=r["broker_symbol"]
        bars=mt5.copy_rates_range(broker,mt5.TIMEFRAME_M1,s-timedelta(minutes=3),e+timedelta(minutes=3))
        rows=[]
        if bars is not None:
            for b in bars:
                t=datetime.fromtimestamp(int(b["time"]),tz=timezone.utc)
                rows.append({"time_utc":iso(t),"open":float(b["open"]),"high":float(b["high"]),"low":float(b["low"]),"close":float(b["close"]),"volume":int(b["tick_volume"])})
        before=[x for x in rows if dt(x["time_utc"])<s]
        after=[x for x in rows if dt(x["time_utc"])>=e]
        last_before=before[-1] if before else None
        first_after=after[0] if after else None
        lb=dt(last_before["time_utc"]) if last_before else None
        fa=dt(first_after["time_utc"]) if first_after else None
        if lb and fa and lb.minute==59 and fa.minute==0 and fa-lb==timedelta(minutes=61):
            pattern="EXACT_23:59_TO_01:00"
        elif lb and fa and lb.minute==58 and fa.minute==0:
            pattern="23:58_TO_01:00"
        elif lb and fa and lb.minute==59 and fa.minute==59:
            pattern="23:59_TO_00:59"
        else:
            pattern="OTHER"
        out.append({"case_id":r["case_id"],"gap":g,"broker_symbol":broker,"last_bar_before":last_before,"first_bar_after":first_after,"observed_boundary_pattern":pattern,"bars_returned":len(rows),"boundary_bars":rows})
    mt5.shutdown()
    result={"status":"COMPLETE","research_only":True,"symbol":a.symbol,"cases":len(out),"source_matrix":a.matrix,"results":out}
    if a.output: Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    counts={}
    for x in out:
        k=x["observed_boundary_pattern"]; counts[k]=counts.get(k,0)+1
    print(f"{a.symbol} RAW-BAR FORENSICS")
    print("")
    print(f"unique_gaps={len(out)}")
    for k in ("EXACT_23:59_TO_01:00","23:58_TO_01:00","23:59_TO_00:59","OTHER"):
        print(f"{k.lower()}={counts.get(k,0)}")
    print("")
    print("BOUNDARY_OBSERVATIONS:")
    for x in out:
        g=x["gap"]; lb=x["last_bar_before"]["time_utc"] if x["last_bar_before"] else None; fa=x["first_bar_after"]["time_utc"] if x["first_bar_after"] else None
        print(f'- {g.get("start_utc")} -> {g.get("end_utc")} | {lb} -> {fa} | {x["observed_boundary_pattern"]}')
    print("")
    print("status=COMPLETE")
    print("research_only=true")
    print("session_approval=NOT_ESTABLISHED")
    if a.output: print(f"artifact={a.output}")

if __name__=="__main__": main()
