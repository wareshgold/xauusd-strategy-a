""""XAUUSD raw-bar boundary forensic audit (research-only).

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
    p.add_argument("--unique-gaps",action="store_true",help="Deduplicate identical gap intervals repeated across matrix windows.")
    p.add_argument("--output")
    a=p.parse_args()
    d=json.loads(Path(a.matrix).read_text(encoding="utf-8"))
    gaps=[]
    for r in d.get("results",[]):
        if r.get("requested_symbol")!=a.symbol: continue
        for g in r.get("gap_intervals",[]):
            if g.get("non_weekend_minutes",0)>0: gaps.append((r,g))
    if a.unique_gaps:
        seen=set()
        unique=[]
        for r,g in gaps:
            key=(r.get("broker_symbol"),g.get("start_utc"),g.get("end_utc"))
            if key in seen: continue
            seen.add(key)
            unique.append((r,g))
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
        exact_hour_boundary = bool(
            last_before and first_after
            and dt(last_before["time_utc"]).minute == 59
            and dt(first_after["time_utc"]).minute == 0
            and (dt(first_after["time_utc"])-dt(last_before["time_utc"])) == timedelta(minutes=61)
        )
        out.append({"case_id":r["case_id"],"gap":g,"broker_symbol":broker,
                    "last_bar_before":last_before,
                    "first_bar_after":first_after,
                    "observed_boundary_pattern": "EXACT_60_MIN_HOUR_BOUNDARY" if exact_hour_boundary else "OTHER",
                    "bars_returned":len(rows),"boundary_bars":rows})
    mt5.shutdown()
    result={"status":"COMPLETE","research_only":True,"symbol":a.symbol,"cases":len(out),"source_matrix":a.matrix,"results":out}
    text=json.dumps(result,indent=2,ensure_ascii=False)
    if a.output: Path(a.output).write_text(text,encoding="utf-8")

    exact=sum(x["observed_boundary_pattern"]=="EXACT_60_MIN_HOUR_BOUNDARY" for x in out)
    other=[x for x in out if x["observed_boundary_pattern"]!="EXACT_60_MIN_HOUR_BOUNDARY"]
    first=out[0]["gap"].get("start_utc") if out else None
    last=out[-1]["gap"].get("end_utc") if out else None
    print(f"{a.symbol} RAW-BAR FORENSICS")
    print("")
    print(f"unique_gaps={len(out)}")
    print(f"exact_60m_hour_boundary={exact}")
    print(f"other_boundary={len(other)}")
    print(f"first_gap={first}")
    print(f"last_gap={last}")
    if other:
        print("")
        print("OTHER_BOUNDARIES:")
        for x in other[:10]:
            g=x["gap"]
            print(f'- {g.get("start_utc")} -> {g.get("end_utc")} [{x["observed_boundary_pattern"]}]')
        if len(other)>10:
            print(f"... {len(other)-10} more in JSON artifact")
    print("")
    print("status=COMPLETE")
    print("research_only=true")
    print("session_approval=NOT_ESTABLISHED")
    if a.output:
        print(f"artifact={a.output}")

if __name__=="__main__": main()
"