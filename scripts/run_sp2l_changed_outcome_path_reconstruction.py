"""Reconstruct raw M1 price paths for the 18 common SP2L V2 outcome-changing cases.

Research-only evidence tool. It does not choose or promote canonical fill/exit semantics.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from datetime import datetime,timezone
import MetaTrader5 as mt5

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def epoch(s):
    if s is None:return None
    return int(datetime.fromisoformat(s.replace("Z","+00:00")).timestamp())

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--mt5-path",required=True);p.add_argument("--symbol",default="XAUUSD")
    p.add_argument("--output",required=True);p.add_argument("--context-bars",type=int,default=12);a=p.parse_args()
    x=load(a.input); rows=x["rows"]
    if not mt5.initialize(path=a.mt5_path): raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    base=a.symbol
    si=mt5.symbol_info(base)
    if si is None:
        for s in (base+".ecn",base+".ECN"):
            if mt5.symbol_info(s): base=s;break
    if not mt5.symbol_select(base,True): raise RuntimeError(f"symbol_select failed: {base}")
    out=[]
    for row in rows:
        b=row["baseline"]; r=row["reference"]
        times=[t for t in (b.get("fill_time"),b.get("exit_time"),r.get("activation_time"),r.get("exit_time")) if t]
        if not times:
            out.append({"fingerprint":row["fingerprint"],"status":"NO_TIMES"});continue
        lo=min(epoch(t) for t in times)-a.context_bars*60
        hi=max(epoch(t) for t in times)+a.context_bars*60
        rates=mt5.copy_rates_range(base,mt5.TIMEFRAME_M1,datetime.fromtimestamp(lo,tz=timezone.utc),datetime.fromtimestamp(hi,tz=timezone.utc))
        bars=[] if rates is None else [{"time":int(z["time"]),"time_utc":datetime.fromtimestamp(int(z["time"]),tz=timezone.utc).isoformat(),"open":float(z["open"]),"high":float(z["high"]),"low":float(z["low"]),"close":float(z["close"])} for z in rates]
        def around(t):
            if not t:return []
            q=epoch(t); idx=min(range(len(bars)),key=lambda i:abs(bars[i]["time"]-q),default=None)
            return bars[max(0,(idx or 0)-a.context_bars):min(len(bars),(idx or 0)+a.context_bars+1)] if idx is not None else []
        out.append({
            "fingerprint":row["fingerprint"],"differences":row.get("differences",[]),
            "baseline":{"result":b.get("result"),"r":b.get("r"),"fill_time":b.get("fill_time"),"exit_time":b.get("exit_time"),"exit_reason":b.get("exit_reason"),"entry":b.get("entry"),"sl":b.get("sl"),"tp":b.get("tp")},
            "reference":{"r":r.get("r"),"activation_time":r.get("activation_time"),"exit_time":r.get("exit_time"),"exit_reason":r.get("exit_reason"),"entry":r.get("entry"),"sl":r.get("sl"),"tp":r.get("tp")},
            "m1":{"bar_count":len(bars),"first":bars[0] if bars else None,"last":bars[-1] if bars else None,
                  "around_baseline_fill":around(b.get("fill_time")),"around_baseline_exit":around(b.get("exit_time")),
                  "around_reference_activation":around(r.get("activation_time")),"around_reference_exit":around(r.get("exit_time"))}
        })
    mt5.shutdown()
    result={"status":"COMPLETE","research_only":True,"target_count":len(out),
            "source_r_delta":x.get("r_delta_reported"),"rows":out,
            "purpose":"Raw M1 path reconstruction for causal review; no canonical fill/exit semantics inferred."}
    q=Path(a.output);q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"status":"COMPLETE","target_count":len(out),"output":str(q)},indent=2))
if __name__=="__main__":main()
