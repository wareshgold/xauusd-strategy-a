"""Research-only SP2L parameter robustness matrix on the existing author-replica MT5 implementation.
This tool does not define canonical Strategy A rules. It varies only existing candidate
implementation parameters to test sensitivity around the current baseline.
"""
from __future__ import annotations
import importlib.util, itertools, json, os
from datetime import datetime, timezone
from pathlib import Path
import MetaTrader5 as mt5
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

SOURCE = Path("scripts/run-author-replica-mt5-nonoverlap-stability.py")
SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
N = int(os.getenv("BARS", "10000"))
WEEKS = [("2026-09-14","2026-09-18"),("2026-09-07","2026-09-11"),("2026-08-31","2026-09-04"),("2026-08-24","2026-08-28")]
P_GAPS = [0.8, 1.0, 1.2]
SPIKE_MULTS = [1.3, 1.5, 1.7]
MAX_SLS = [8.0, 10.0, 12.0]
TP_RS = [0.8, 1.0, 1.2]
OUT = Path("artifacts/SP2L_author_replica_parameter_robustness_matrix.xlsx")
JSON_OUT = OUT.with_suffix(".json")

spec = importlib.util.spec_from_file_location("sp2l_replica", SOURCE)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def dt(s, end=False):
    return datetime.fromisoformat(s + ("T23:59:59+00:00" if end else "T00:00:00+00:00"))
def evaluate_week(rates, start, end, p_gap, spike_mult, max_sl, tp_r):
    c=[{"time":int(r[0]),"open":float(r[1]),"high":float(r[2]),"low":float(r[3]),"close":float(r[4])} for r in rates]
    body=lambda x: abs(x["close"]-x["open"]); rows=[]
    for i in range(4,len(c)):
        a,s,corr,trig=c[i-4],c[i-3],c[i-2],c[i-1]
        buy=(trig["low"]<corr["low"] and corr["close"]>s["close"] and corr["open"]>s["open"] and s["open"]>a["open"] and corr["close"]>corr["open"] and s["close"]>s["open"] and a["close"]>a["open"] and corr["low"]>a["high"]+p_gap and body(s)>spike_mult*body(corr) and body(s)>spike_mult*body(a) and body(s)>spike_mult*body(trig))
        sell=(trig["high"]>corr["high"] and corr["close"]<s["close"] and corr["open"]<s["open"] and s["close"]<a["close"] and s["open"]<a["open"] and corr["close"]<corr["open"] and s["close"]<s["open"] and a["close"]<a["open"] and corr["high"]<a["low"]-p_gap and body(s)>spike_mult*body(corr) and body(s)>spike_mult*body(a) and body(s)>spike_mult*body(trig))
        if not (buy or sell): continue
        direction="BUY" if buy else "SELL"; entry=trig["low"] if buy else trig["high"]; sl=a["low"] if buy else a["high"]; signal_ts=c[i-1]["time"]
        if not (start.timestamp()<=signal_ts<=end.timestamp()): continue
        risk=abs(entry-sl)
        if risk<=0 or risk>max_sl: continue
        tp=entry+tp_r*risk if buy else entry-tp_r*risk; outcome="OPEN_OR_UNRESOLVED"
        for j in range(i+1,len(c)):
            x=c[j]; hit_sl=x["low"]<=sl if buy else x["high"]>=sl; hit_tp=x["high"]>=tp if buy else x["low"]<=tp
            if hit_sl and hit_tp: outcome="AMBIGUOUS"; break
            if hit_sl: outcome="LOSS"; break
            if hit_tp: outcome="WIN"; break
        rows.append((direction,outcome))
    w=sum(o=="WIN" for _,o in rows); l=sum(o=="LOSS" for _,o in rows); a=sum(o=="AMBIGUOUS" for _,o in rows); u=sum(o=="OPEN_OR_UNRESOLVED" for _,o in rows); d=w+l
    return len(rows),w,l,a,u,(w/d if d else None)
def main():
    if not mt5.initialize(): raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        if not mt5.symbol_select(SYMBOL,True): raise SystemExit(f"symbol_select failed: {mt5.last_error()}")
        week_rates=[]
        for a,b in WEEKS:
            rates=mt5.copy_rates_from(SYMBOL,mt5.TIMEFRAME_M1,dt(b,True),N)
            if rates is None or len(rates)==0: raise SystemExit(f"MT5 data unavailable for {a}..{b}: {mt5.last_error()}")
            week_rates.append((a,b,rates))
    finally: mt5.shutdown()
    rows=[]
    for pg,sp,ms,tp in itertools.product(P_GAPS,SPIKE_MULTS,MAX_SLS,TP_RS):
        vals=[evaluate_week(r,dt(a),dt(b,True),pg,sp,ms,tp) for a,b,r in week_rates]
        sig=sum(x[0] for x in vals); w=sum(x[1] for x in vals); l=sum(x[2] for x in vals); amb=sum(x[3] for x in vals); un=sum(x[4] for x in vals); wrs=[x[5] for x in vals if x[5] is not None]; d=w+l
        rows.append({"pGapPrice":pg,"spikeMultiplier":sp,"maxSlPrice":ms,"tpR":tp,"signals":sig,"wins":w,"losses":l,"ambiguous":amb,"open_or_unresolved":un,"decisive_win_rate":w/d if d else None,"total_R":w-l,"profit_factor":w/l if l else None,"min_weekly_decisive_wr":min(wrs) if wrs else None,"max_weekly_decisive_wr":max(wrs) if wrs else None,"weeks_above_60pct":sum(x is not None and x>0.60 for x in [v[5] for v in vals]),"weekly_decisive_wr":[v[5] for v in vals]})
    baseline=next(x for x in rows if (x["pGapPrice"],x["spikeMultiplier"],x["maxSlPrice"],x["tpR"])==(1.0,1.5,10.0,1.0))
    result={"research_only":True,"purpose":"parameter sensitivity around existing author-replica baseline; not canonical rule selection","symbol":SYMBOL,"timeframe":"M1","requested_bars_per_week":N,"weeks":WEEKS,"baseline":baseline,"parameter_grid":{"pGapPrice":P_GAPS,"spikeMultiplier":SPIKE_MULTS,"maxSlPrice":MAX_SLS,"tpR":TP_RS},"combinations":len(rows),"results":rows}
    OUT.parent.mkdir(exist_ok=True); JSON_OUT.write_text(json.dumps(result,indent=2),encoding="utf-8")
    wb=Workbook(); ws=wb.active; ws.title="Parameter Matrix"; headers=["pGapPrice","spikeMultiplier","maxSlPrice","tpR","signals","wins","losses","ambiguous","open_or_unresolved","decisive_win_rate","total_R","profit_factor","min_weekly_decisive_wr","max_weekly_decisive_wr","weeks_above_60pct"]; ws.append(headers)
    for x in rows: ws.append([x[h] for h in headers])
    ws2=wb.create_sheet("Baseline"); ws2.append(["metric","value"])
    for k,v in baseline.items():
        if k!="weekly_decisive_wr": ws2.append([k,v])
    ws2.append(["weekly_decisive_wr",json.dumps(baseline["weekly_decisive_wr"])])
    ws3=wb.create_sheet("Weekly WR"); ws3.append(["pGapPrice","spikeMultiplier","maxSlPrice","tpR"]+[f"{a}_wr" for a,_ in WEEKS])
    for x in rows: ws3.append([x["pGapPrice"],x["spikeMultiplier"],x["maxSlPrice"],x["tpR"]]+x["weekly_decisive_wr"])
    for sh in wb.worksheets:
        sh.freeze_panes="A2"
        for col in sh.columns: sh.column_dimensions[get_column_letter(col[0].column)].width=min(max(len(str(c.value or "")) for c in col)+2,32)
    wb.save(OUT); print(json.dumps({"xlsx":str(OUT),"json":str(JSON_OUT),"combinations":len(rows),"baseline":baseline},indent=2))
if __name__=="__main__": main()
