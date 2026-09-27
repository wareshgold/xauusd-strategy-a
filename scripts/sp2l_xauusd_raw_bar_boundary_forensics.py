"""XAUUSD raw-bar boundary forensic audit (research-only).

Reads an existing matrix artifact, selects unresolved non-weekend gaps, and
re-queries MT5 M1 history around each boundary. No session closure is inferred
or approved; this tool only records observed raw-bar boundaries.
"""
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
    p.add_argument("--output")
    a=p.parse_args()
    d=json.loads(Path(a.matrix).read_text(encoding="utf-8"))
    gaps=[]
    for r in d.get("results",[]):
        if r.get("requested_symbol")!=a.symbol: continue
        for g in r.get("gap_intervals",[]):
            if g.get("non_weekend_minutes",0)>0: gaps.append((r,g))
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
        out.append({"case_id":r["case_id"],"gap":g,"broker_symbol":broker,
                    "last_bar_before":before[-1] if before else None,
                    "first_bar_after":after[0] if after else None,
                    "bars_returned":len(rows),"boundary_bars":rows})
    mt5.shutdown()
    result={"status":"COMPLETE","research_only":True,"symbol":a.symbol,"cases":len(out),"source_matrix":a.matrix,"results":out}
    text=json.dumps(result,indent=2,ensure_ascii=False)
    if a.output: Path(a.output).write_text(text,encoding="utf-8")
    print(text)

if __name__=="__main__": main()
