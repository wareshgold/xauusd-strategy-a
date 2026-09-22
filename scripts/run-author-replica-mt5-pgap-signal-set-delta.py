"""Research-only exact P-Gap signal-set delta diagnostics.

Compares the exact candidate signal timestamps/directions admitted at each P-Gap
threshold on the same MT5 M1 window. No canonical geometry is changed.
"""
from __future__ import annotations
import importlib.util, json, os
from datetime import datetime, timezone
from pathlib import Path
import MetaTrader5 as mt5

SOURCE_SCRIPT = Path("scripts/run-author-replica-mt5-nonoverlap-stability.py")
SYMBOL = os.getenv("TRADING_SYMBOL","XAUUSD.ecn")
N = int(os.getenv("BARS","10000"))
START = datetime.fromisoformat(os.getenv("WEEK_START_UTC","2026-09-14T00:00:00+00:00")).astimezone(timezone.utc)
END = datetime.fromisoformat(os.getenv("WEEK_END_UTC","2026-09-18T23:59:59+00:00")).astimezone(timezone.utc)
PGAPS = [float(x) for x in os.getenv("DELTA_PGAPS","0,0.25,0.5,0.75,1,1.25,1.5,2").split(",")]

spec=importlib.util.spec_from_file_location("replica",SOURCE_SCRIPT)
if spec is None or spec.loader is None: raise SystemExit("Cannot load source runner")
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def signal(c,i,p):
    a,s,corr,trig=c[i-4],c[i-3],c[i-2],c[i-1]
    body=lambda x: abs(x["close"]-x["open"])
    buy=(trig["low"]<corr["low"] and corr["close"]>s["close"] and corr["open"]>s["open"]
         and s["open"]>a["open"] and corr["close"]>corr["open"] and s["close"]>s["open"]
         and a["close"]>a["open"] and corr["low"]>a["high"]+p
         and body(s)>mod.SPIKE_MULT*body(corr) and body(s)>mod.SPIKE_MULT*body(a)
         and body(s)>mod.SPIKE_MULT*body(trig))
    sell=(trig["high"]>corr["high"] and corr["close"]<s["close"] and corr["open"]<s["open"]
          and s["close"]<a["close"] and s["open"]<a["open"] and corr["close"]<corr["open"]
          and s["close"]<s["open"] and a["close"]<a["open"] and corr["high"]<a["low"]-p
          and body(s)>mod.SPIKE_MULT*body(corr) and body(s)>mod.SPIKE_MULT*body(a)
          and body(s)>mod.SPIKE_MULT*body(trig))
    if buy:
        risk=trig["low"]-a["low"]
        if 0<risk<=mod.MAX_SL: return ("BUY",c[i-1]["time"],trig["low"],a["low"])
    if sell:
        risk=a["high"]-trig["high"]
        if 0<risk<=mod.MAX_SL: return ("SELL",c[i-1]["time"],trig["high"],a["high"])
    return None

def iso(ts): return datetime.fromtimestamp(ts,timezone.utc).isoformat()

def main():
    if not mt5.initialize(): raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        if not mt5.symbol_select(SYMBOL,True): raise SystemExit(f"symbol_select failed: {mt5.last_error()}")
        rates=mt5.copy_rates_from(SYMBOL,mt5.TIMEFRAME_M1,END,N)
        if rates is None or len(rates)==0: raise SystemExit(f"No MT5 data: {mt5.last_error()}")
        c=[{"time":int(r[0]),"open":float(r[1]),"high":float(r[2]),"low":float(r[3]),"close":float(r[4])} for r in rates]
        start_ts,end_ts=START.timestamp(),END.timestamp()
        sets={}
        for p in PGAPS:
            rows=[]
            for i in range(4,len(c)):
                if not(start_ts<=c[i-1]["time"]<=end_ts): continue
                s=signal(c,i,p)
                if s:
                    d,ts,e,sl=s
                    rows.append({"key":f"{ts}|{d}","time_utc":iso(ts),"direction":d,"entry":e,"sl":sl})
            sets[p]=rows
        base=PGAPS[0]
        basekeys={x["key"] for x in sets[base]}
        pairwise=[]
        for p in PGAPS:
            keys={x["key"] for x in sets[p]}
            added=sorted(keys-basekeys)
            removed=sorted(basekeys-keys)
            pairwise.append({"pGapPrice":p,"signals":len(keys),
                "added_vs_base":len(added),"removed_vs_base":len(removed),
                "added_keys":added,"removed_keys":removed})
        adjacent=[]
        for lo,hi in zip(PGAPS,PGAPS[1:]):
            lk={x["key"] for x in sets[lo]}; hk={x["key"] for x in sets[hi]}
            removed=sorted(lk-hk); added=sorted(hk-lk)
            adjacent.append({"from_pGap":lo,"to_pGap":hi,"from_signals":len(lk),"to_signals":len(hk),
                "removed_count":len(removed),"added_count":len(added),
                "removed_keys":removed,"added_keys":added})
        result={"research_only":True,"symbol":SYMBOL,"timeframe":"M1",
          "window":{"start_utc":START.isoformat(),"end_utc":END.isoformat()},
          "returned_bars":len(c),"pgaps":PGAPS,"baseline_pGap":base,
          "set_counts":{str(p):len(sets[p]) for p in PGAPS},
          "pairwise_vs_baseline":pairwise,"adjacent_deltas":adjacent,
          "note":"Exact timestamp+direction membership only; this is not evidence that any P-Gap threshold is canonical."}
        print(json.dumps(result,indent=2))
        out=Path(os.getenv("DELTA_OUT",f"artifacts/SP2L_{SYMBOL.replace('.','_')}_pgap_signal_set_delta_2026-09-14_2026-09-18.json"))
        out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(f"Wrote {out}")
    finally: mt5.shutdown()
if __name__=="__main__": main()
