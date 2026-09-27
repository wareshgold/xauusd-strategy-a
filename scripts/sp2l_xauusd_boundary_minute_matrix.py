"""Build a raw-M1 boundary-minute presence matrix for XAUUSD gap cases.

Research-only. For each XAUUSD gap, inspect T-2..T+2 around both gap start
and gap end for XAUUSD and seven FX controls. Presence is recorded directly
from MT5 raw M1 timestamps; no session inference is performed.
"""
from __future__ import annotations
import argparse,json
from datetime import datetime,timedelta,timezone
from pathlib import Path
import MetaTrader5 as mt5

SYMS={"XAUUSD":"XAUUSD.ecn","USDJPY":"USDJPY.ecn","EURJPY":"EURJPY.ecn","GBPUSD":"GBPUSD.ecn","GBPJPY":"GBPJPY.ecn","EURUSD":"EURUSD.ecn","USDCHF":"USDCHF.ecn","USDCAD":"USDCAD.ecn"}

def dt(s): return datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(timezone.utc)
def iso(x): return x.isoformat()
def fetch(sym,a,b):
    r=mt5.copy_rates_range(sym,mt5.TIMEFRAME_M1,a-timedelta(minutes=3),b+timedelta(minutes=3))
    return {datetime.fromtimestamp(int(x["time"]),tz=timezone.utc) for x in r} if r is not None else set()

def window(present,center):
    return {f"T{n:+d}": int(center+timedelta(minutes=n) in present) for n in range(-2,3)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("input"); p.add_argument("--mt5-path",required=True); p.add_argument("--output",required=True); p.add_argument("--limit",type=int,default=58)
    args=p.parse_args()
    cases=json.loads(Path(args.input).read_text(encoding="utf-8"))["results"][:args.limit]
    if not mt5.initialize(path=args.mt5_path): raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    out=[]
    try:
        for i,c in enumerate(cases,1):
            a,b=dt(c["xau_gap_start_utc"]),dt(c["xau_gap_end_utc"])
            row={"case":i,"gap_start_utc":c["xau_gap_start_utc"],"gap_end_utc":c["xau_gap_end_utc"],"xau_pattern":c.get("xau_pattern"),"symbols":{}}
            for name,sym in SYMS.items():
                present=fetch(sym,a,b)
                row["symbols"][name]={"start_boundary":window(present,a),"end_boundary":window(present,b)}
            out.append(row)
    finally: mt5.shutdown()
    # Aggregate exact-minute agreement across controls.
    agree_start={f"T{n:+d}":0 for n in range(-2,3)}
    agree_end={f"T{n:+d}":0 for n in range(-2,3)}
    xau_start={f"T{n:+d}":0 for n in range(-2,3)}
    xau_end={f"T{n:+d}":0 for n in range(-2,3)}
    control_start={f"T{n:+d}":0 for n in range(-2,3)}
    control_end={f"T{n:+d}":0 for n in range(-2,3)}
    controls=list(SYMS)[1:]
    for row in out:
        for side,aggx,aggc,agga in [("start",xau_start,control_start,agree_start),("end",xau_end,control_end,agree_end)]:
            for k in aggx:
                x=row["symbols"]["XAUUSD"][side+"_boundary"][k]
                vals=[row["symbols"][s][side+"_boundary"][k] for s in controls]
                aggx[k]+=x
                aggc[k]+=sum(vals)
                agga[k]+=sum(v==x for v in vals)
    report={"status":"COMPLETE","research_only":True,"session_cause":"UNRESOLVED","session_approval":"NOT_ESTABLISHED","population":len(out),"symbols":SYMS,
            "aggregate":{"xau_start_presence":xau_start,"xau_end_presence":xau_end,"control_start_presence_total":control_start,"control_end_presence_total":control_end,"control_symbol_agreement_with_xau_start":agree_start,"control_symbol_agreement_with_xau_end":agree_end},"cases":out,
            "interpretation":["Exact raw timestamp presence only.","Agreement does not establish session cause.","No session closure or canonical data rule is inferred."]}
    Path(args.output).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("XAUUSD BOUNDARY-MINUTE MATRIX")
    print(f"population={len(out)}")
    print("START_XAU="," ".join(f"{k}:{v}" for k,v in xau_start.items()))
    print("END_XAU="," ".join(f"{k}:{v}" for k,v in xau_end.items()))
    print("START_CONTROL_AGREEMENT="," ".join(f"{k}:{v}" for k,v in agree_start.items()))
    print("END_CONTROL_AGREEMENT="," ".join(f"{k}:{v}" for k,v in agree_end.items()))
    print("SESSION_CAUSE=UNRESOLVED")
    print("SESSION_APPROVAL=NOT_ESTABLISHED")
    print("research_only=true")
    print("status=COMPLETE")
    print(f"artifact={args.output}")
if __name__=="__main__": main()
