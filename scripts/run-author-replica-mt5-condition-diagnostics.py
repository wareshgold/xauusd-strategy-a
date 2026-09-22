"""Research-only MT5 condition diagnostics for the existing author-replica SP2L candidate.

Does not change canonical geometry. Reports condition-by-condition pass counts and
prefix survivors for a requested UTC week. P-Gap values are diagnostics only.
"""
from __future__ import annotations
import importlib.util, json, os
from datetime import datetime, timezone
from pathlib import Path
import MetaTrader5 as mt5

SOURCE_SCRIPT = Path("scripts/run-author-replica-mt5-nonoverlap-stability.py")
SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
N = int(os.getenv("BARS", "10000"))
START = datetime.fromisoformat(os.getenv("WEEK_START_UTC","2026-09-14T00:00:00+00:00")).astimezone(timezone.utc)
END = datetime.fromisoformat(os.getenv("WEEK_END_UTC","2026-09-18T23:59:59+00:00")).astimezone(timezone.utc)
PGAPS = [float(x) for x in os.getenv("DIAGNOSTIC_PGAPS","0,0.25,0.5,1,1.5,2").split(",")]

spec = importlib.util.spec_from_file_location("sp2l_replica", SOURCE_SCRIPT)
if spec is None or spec.loader is None: raise SystemExit(f"Cannot load {SOURCE_SCRIPT}")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def body(c): return abs(c["close"]-c["open"])

def conditions(c, i, p):
    a,s,corr,trig = c[i-4],c[i-3],c[i-2],c[i-1]
    buy=[
      trig["low"]<corr["low"],
      corr["close"]>s["close"],
      corr["open"]>s["open"],
      s["open"]>a["open"],
      corr["close"]>corr["open"],
      s["close"]>s["open"],
      a["close"]>a["open"],
      corr["low"]>a["high"]+p,
      body(s)>mod.SPIKE_MULT*body(corr),
      body(s)>mod.SPIKE_MULT*body(a),
      body(s)>mod.SPIKE_MULT*body(trig),
    ]
    sell=[
      trig["high"]>corr["high"],
      corr["close"]<s["close"],
      corr["open"]<s["open"],
      s["close"]<a["close"],
      corr["close"]<corr["open"],
      s["close"]<s["open"],
      a["close"]<a["open"],
      corr["high"]<a["low"]-p,
      body(s)>mod.SPIKE_MULT*body(corr),
      body(s)>mod.SPIKE_MULT*body(a),
      body(s)>mod.SPIKE_MULT*body(trig),
    ]
    return buy,sell

LABELS=[
 "trigger breaks correction","correction close beyond spike","correction open beyond spike",
 "spike body directional vs A","correction directional body","spike directional body",
 "A directional body","P-Gap","spike > multiplier correction","spike > multiplier A",
 "spike > multiplier trigger"
]

def summarize(c, side, p):
    total=[0]*len(LABELS); prefix=[0]*len(LABELS); full=0
    start_ts=START.timestamp(); end_ts=END.timestamp()
    evaluated=0
    for i in range(4,len(c)):
        signal_time=c[i-1]["time"]
        if not (start_ts<=signal_time<=end_ts): continue
        evaluated+=1
        x=conditions(c,i,p)[0 if side=="BUY" else 1]
        for j,v in enumerate(x):
            if v: total[j]+=1
            if all(x[:j+1]): prefix[j]+=1
        if all(x): full+=1
    return {"side":side,"pGapPrice":p,"evaluated_candle_positions":evaluated,
            "full_condition_matches":full,
            "conditions":[{"index":j+1,"label":LABELS[j],"pass":total[j],
                          "prefix_survivors":prefix[j]} for j in range(len(LABELS))]}

def main():
    if not mt5.initialize(): raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        if not mt5.symbol_select(SYMBOL,True): raise SystemExit(f"symbol_select failed: {mt5.last_error()}")
        rates=mt5.copy_rates_from(SYMBOL,mt5.TIMEFRAME_M1,END,N)
        if rates is None or len(rates)==0: raise SystemExit(f"No MT5 data: {mt5.last_error()}")
        c=[{"time":int(r[0]),"open":float(r[1]),"high":float(r[2]),"low":float(r[3]),"close":float(r[4])} for r in rates]
        result={"research_only":True,"symbol":SYMBOL,"timeframe":"M1",
                "week_start_utc":START.isoformat(),"week_end_utc":END.isoformat(),
                "returned_bars":len(c),
                "first_returned_utc":datetime.fromtimestamp(c[0]["time"],timezone.utc).isoformat(),
                "last_returned_utc":datetime.fromtimestamp(c[-1]["time"],timezone.utc).isoformat(),
                "config":{"spikeMultiplier":mod.SPIKE_MULT,"maxSlPrice":mod.MAX_SL,"tpR":mod.TP_R},
                "diagnostics":[summarize(c,s,p) for p in PGAPS for s in ("BUY","SELL")]}
        print(json.dumps(result,indent=2))
        out=Path(os.getenv("DIAGNOSTIC_OUT",f"artifacts/SP2L_{SYMBOL.replace('.','_')}_condition_diagnostics_2026-09-14_2026-09-18.json"))
        out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(f"Wrote {out}")
    finally: mt5.shutdown()

if __name__=="__main__": main()
