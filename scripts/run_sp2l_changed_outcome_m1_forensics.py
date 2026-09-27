"""Inspect result/R-changing common SP2L V2 signals against raw MT5 M1 bars.

Research-only forensic. Does not choose or promote canonical fill/exit semantics.
"""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path
import MetaTrader5 as mt5

FIELDS=["direction","entry_time","entry","sl","tp"]

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def fp(x): return tuple(round(x[k],8) if isinstance(x.get(k),float) else x.get(k) for k in FIELDS)
def ts(x): return datetime.fromtimestamp(int(x),timezone.utc).isoformat()
def gap(a,b): return max(0,int((b-a)//60)-1)

def resolve(req):
    names=[s.name for s in (mt5.symbols_get() or [])]
    u=req.upper()
    if u in names:return u
    for s in names:
        if s.upper().replace(".ECN","")==u: return s
    raise RuntimeError("symbol resolution failed: "+req)

def rates(symbol,start,end):
    r=mt5.copy_rates_range(symbol,mt5.TIMEFRAME_M1,start,end)
    if r is None or len(r)==0: raise RuntimeError(f"history failed {mt5.last_error()}")
    return sorted(list(r),key=lambda x:int(x["time"]))

def bar(x):
    return {"time":int(x["time"]),"time_utc":ts(x["time"]),"open":float(x["open"]),"high":float(x["high"]),"low":float(x["low"]),"close":float(x["close"])}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline-report",required=True); p.add_argument("--reference-report",required=True)
    p.add_argument("--combined-report",required=True); p.add_argument("--mt5-path",required=True)
    p.add_argument("--symbol",default="XAUUSD"); p.add_argument("--context-bars",type=int,default=8)
    p.add_argument("--output",required=True); a=p.parse_args()
    b=load(a.baseline_report); r=load(a.reference_report); c=load(a.combined_report)
    bm={fp(x):x for x in b["result"]["signals_detail"]}; tm={fp(x):x for x in r["results"]["trades_detail"]}
    targets=[x for x in c["all_rows"] if "RESULT" in x.get("differences",[]) or "R" in x.get("differences",[])]
    if not mt5.initialize(path=a.mt5_path): raise RuntimeError(f"MT5 init failed: {mt5.last_error()}")
    try:
        sym=resolve(a.symbol); mt5.symbol_select(sym,True); out=[]
        for z in targets:
            k=tuple(z["fingerprint"]); bs=bm[k]; rt=tm.get(k)
            times=[int(bs["entry_time"])]
            if rt: times += [int(rt["activation_time"]),int(rt["exit_time"])]
            lo=datetime.fromtimestamp(min(times)-a.context_bars*60,timezone.utc)
            hi=datetime.fromtimestamp(max(times)+a.context_bars*60,timezone.utc)
            rr=rates(sym,lo,hi); idx={int(x["time"]):i for i,x in enumerate(rr)}
            def window(t):
                if t not in idx:return []
                i=idx[t]; return [bar(x) for x in rr[max(0,i-a.context_bars):min(len(rr),i+a.context_bars+1)]]
            baseline_fill=int(bs["fill_time"]) if bs.get("fill_time") is not None else None
            ref_fill=int(rt["activation_time"]) if rt else None
            out.append({
                "fingerprint":list(k),"differences":z.get("differences",[]),
                "baseline":{"result":bs.get("result"),"r":bs.get("r"),"fill_time":bs.get("fill_time"),"exit_time":bs.get("exit_time"),"exit_reason":bs.get("exit_reason"),
                            "entry":bs.get("entry"),"sl":bs.get("sl"),"tp":bs.get("tp")},
                "reference":{"r":rt.get("r") if rt else None,"activation_time":rt.get("activation_time") if rt else None,
                             "exit_time":rt.get("exit_time") if rt else None,"exit_reason":rt.get("exit_reason") if rt else None,
                             "entry":rt.get("entry") if rt else None,"sl":rt.get("sl") if rt else None,"tp":rt.get("tp") if rt else None},
                "mt5_context":{
                    "symbol":sym,
                    "bars_from":ts(rr[0]["time"]) if rr else None,"bars_to":ts(rr[-1]["time"]) if rr else None,
                    "gap_between_baseline_fill_and_exit":gap(baseline_fill,int(bs["exit_time"])) if baseline_fill and bs.get("exit_time") else None,
                    "gap_between_reference_fill_and_exit":gap(ref_fill,int(rt["exit_time"])) if ref_fill and rt else None,
                    "baseline_fill_window":window(baseline_fill) if baseline_fill else [],
                    "reference_fill_window":window(ref_fill) if ref_fill else [],
                    "baseline_exit_window":window(int(bs["exit_time"])) if bs.get("exit_time") else [],
                    "reference_exit_window":window(int(rt["exit_time"])) if rt else []
                }
            })
        result={"status":"COMPLETE","research_only":True,"purpose":"m1_forensics_result_and_r_changing_common_signals",
                "target_count":len(targets),"target_definition":"all common rows with RESULT or R difference",
                "r_delta_reported":c["derived"]["r_delta_on_rows_with_both_outcomes"],"rows":out,
                "interpretation_limit":"M1 context is descriptive evidence only; it does not resolve canonical fill or exit semantics."}
        q=Path(a.output); q.parent.mkdir(parents=True,exist_ok=True); q.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
        print(json.dumps({"status":"COMPLETE","target_count":len(targets),"r_delta_reported":result["r_delta_reported"],"output":str(q)},indent=2))
    finally: mt5.shutdown()
if __name__=="__main__": raise SystemExit(main())
