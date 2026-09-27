"""Re-fetch complete MT5 M1 paths for changed-outcome cases.

Research-only. Stores raw M1 bars and reconciles first level-touch events.
No canonical execution semantics are inferred.
"""
from __future__ import annotations
import argparse,json
from datetime import datetime,timezone
from pathlib import Path

def ep(v):
    if v is None:return None
    if isinstance(v,(int,float)):return int(v)
    return int(datetime.fromisoformat(str(v).replace("Z","+00:00")).timestamp())

def iso(ts):
    return datetime.fromtimestamp(int(ts),tz=timezone.utc).isoformat()

def first_event(bars,start,end,direction,sl,tp):
    s=ep(start); e=ep(end)
    if s is None or e is None:
        return {"status":"UNRESOLVED","reason":"missing_start_or_end_time"}
    eligible=[b for b in bars if s<=b["time"]<=e]
    for b in eligible:
        sl_hit=b["low"]<=sl if direction=="BUY" else b["high"]>=sl
        tp_hit=b["high"]>=tp if direction=="BUY" else b["low"]<=tp
        if sl_hit and tp_hit: ev="BOTH_SAME_M1"
        elif sl_hit: ev="SL_TOUCH"
        elif tp_hit: ev="TP_TOUCH"
        else: continue
        return {"status":"FOUND","event":ev,"time":b["time_utc"],"bar":b}
    return {"status":"NO_LEVEL_TOUCH","bars_scanned":len(eligible)}

def direction_of(fp):
    if isinstance(fp,list) and fp:return str(fp[0])
    if isinstance(fp,str):return fp.split("|")[0]
    return None

def fetch_mt5(symbol,start,end,path):
    import MetaTrader5 as mt5
    if not mt5.initialize(path=path):
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        info=mt5.symbol_info(symbol)
        if info is None or not info.visible:
            if not mt5.symbol_select(symbol,True):
                raise RuntimeError(f"symbol unavailable: {symbol}")
        rates=mt5.copy_rates_range(symbol,mt5.TIMEFRAME_M1,datetime.fromtimestamp(start,tz=timezone.utc),datetime.fromtimestamp(end,tz=timezone.utc))
        if rates is None:
            raise RuntimeError(f"copy_rates_range returned None: {mt5.last_error()}")
        out=[]
        for x in rates:
            t=int(x["time"])
            out.append({"time":t,"time_utc":iso(t),"open":float(x["open"]),"high":float(x["high"]),"low":float(x["low"]),"close":float(x["close"])})
        return out
    finally:
        mt5.shutdown()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--output",required=True)
    p.add_argument("--mt5-path",required=True);p.add_argument("--symbol",default="XAUUSD.ecn")
    a=p.parse_args()
    x=json.loads(Path(a.input).read_text(encoding="utf-8"));rows=[]
    for row in x.get("rows",[]):
        b=row["baseline"]; r=row["reference"]; direction=direction_of(row.get("fingerprint"))
        starts=[v for v in (ep(b.get("fill_time")),ep(r.get("activation_time"))) if v is not None]
        ends=[v for v in (ep(b.get("exit_time")),ep(r.get("exit_time"))) if v is not None]
        if not starts or not ends:
            rows.append({"fingerprint":row.get("fingerprint"),"status":"UNRESOLVED","reason":"missing_path_boundary"})
            continue
        lo,hi=min(starts),max(ends)
        try: bars=fetch_mt5(a.symbol,lo,hi,a.mt5_path)
        except Exception as ex:
            rows.append({"fingerprint":row.get("fingerprint"),"status":"ERROR","reason":str(ex)})
            continue
        be=first_event(bars,b.get("fill_time"),b.get("exit_time"),direction,b.get("sl"),b.get("tp"))
        re=first_event(bars,r.get("activation_time"),r.get("exit_time"),direction,r.get("sl"),r.get("tp"))
        rows.append({
            "fingerprint":row.get("fingerprint"),"category":row.get("category"),
            "baseline_r":b.get("r"),"reference_r":r.get("r"),"r_delta":row.get("r_delta"),
            "baseline":{"fill_time":b.get("fill_time"),"exit_time":b.get("exit_time"),"sl":b.get("sl"),"tp":b.get("tp"),"first_event":be},
            "reference":{"activation_time":r.get("activation_time"),"exit_time":r.get("exit_time"),"sl":r.get("sl"),"tp":r.get("tp"),"first_event":re},
            "path":{"start":iso(lo),"end":iso(hi),"bars":len(bars),
                    "first_time":bars[0]["time_utc"] if bars else None,
                    "last_time":bars[-1]["time_utc"] if bars else None,
                    "raw_m1":bars}
        })
    result={"status":"COMPLETE","research_only":True,"input_target_count":x.get("target_count"),"rows":rows,
            "note":"Full MT5 M1 re-fetch with raw bars retained for deterministic reconciliation."}
    q=Path(a.output);q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"status":"COMPLETE","rows":len(rows),"errors":sum(r.get("status")=="ERROR" for r in rows),"unresolved":sum(r.get("status")=="UNRESOLVED" for r in rows),"empty_paths":sum(r.get("path",{}).get("bars")==0 for r in rows if "path" in r),"output":str(q)},indent=2,ensure_ascii=False))
if __name__=="__main__":main()
