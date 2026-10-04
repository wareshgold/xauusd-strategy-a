"""MT5-only SP2L V3 actual-trade trailing/2X research matrix."""
from __future__ import annotations
import argparse,csv,json,hashlib
from datetime import datetime,timedelta,timezone
from pathlib import Path
import MetaTrader5 as mt5
import numpy as np
import sp2l_v3_config as cfg

TRAILS=(2,3,4,5,6,8,10,12,15,20); ACTS=(0,5,10,15,20,30)
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"artifacts"/"v3_matrix"; OUT.mkdir(parents=True,exist_ok=True)
PIP=float(cfg.XAU_PIP_SIZE_PRICE); DEFAULT_MAGIC=26092201

def utc(s): return datetime.fromisoformat(s).astimezone(timezone.utc)
def m1(symbol,a,b):
    out=[]; cur=a
    while cur<b:
        z=min(cur+timedelta(days=7),b); x=mt5.copy_rates_range(symbol,mt5.TIMEFRAME_M1,cur,z)
        if x is None or not len(x): raise RuntimeError(f"M1 history failed {cur}..{z}: {mt5.last_error()}")
        out.append(x.copy()); cur=z+timedelta(minutes=1)
    x=np.concatenate(out); x.sort(order="time"); _,i=np.unique(x["time"],return_index=True); return x[np.sort(i)]

def trades(symbol,a,b,magic):
    ds=mt5.history_deals_get(a,b,group=symbol)
    if ds is None: raise RuntimeError(f"history_deals_get failed: {mt5.last_error()}")
    g={}
    for d in ds:
        if getattr(d,"symbol","")!=symbol or int(getattr(d,"magic",0) or 0)!=magic: continue
        p=int(getattr(d,"position_id",0) or 0)
        if p: g.setdefault(p,[]).append(d)
    out=[]
    for p,ls in g.items():
        ls=sorted(ls,key=lambda d:int(d.time)); ins=[d for d in ls if int(d.entry)==mt5.DEAL_ENTRY_IN]; outs=[d for d in ls if int(d.entry) in (mt5.DEAL_ENTRY_OUT,mt5.DEAL_ENTRY_OUT_BY)]
        if not ins or not outs: continue
        e,x=ins[0],outs[-1]; side="BUY" if int(e.type)==mt5.DEAL_TYPE_BUY else "SELL"
        out.append(dict(position_id=p,direction=side,entry_time=int(e.time),exit_time=int(x.time),entry=float(e.price),exit_observed=float(x.price),volume=float(e.volume),sl=float(getattr(e,"sl",0) or 0),tp=float(getattr(e,"tp",0) or 0),profit_usd=sum(float(getattr(d,"profit",0) or 0) for d in ls),entry_deals=len(ins)))
    return sorted(out,key=lambda z:z["entry_time"])

def finish(t,reason,ep,e2,active,final_sl,mfe):
    r=abs(t["entry"]-t["sl"])
    if ep is None: rr=usd=None; we=t["entry"]
    else:
        e2p=(t["entry"]-.5*r if t["direction"]=="BUY" else t["entry"]+.5*r)
        we=(t["entry"]+e2p)/2 if e2 else t["entry"]
        pnl=(ep-we if t["direction"]=="BUY" else we-ep); rr=pnl/r; usd=pnl*t["volume"]*100*(2 if e2 else 1)
    return dict(position_id=t["position_id"],direction=t["direction"],reason=reason,exit_price=ep,entry2_filled=e2,total_entries=2 if e2 else 1,weighted_entry=we,trailing_activated=active,final_sl=final_sl,max_favorable_price=mfe,realized_R=rr,realized_usd=usd,observed_profit_usd=t["profit_usd"],entry_time=t["entry_time"],exit_time=t["exit_time"])

def replay(t,bars,act,trail,two):
    if not t["sl"]: return dict(position_id=t["position_id"],reason="MISSING_INITIAL_SL",realized_R=None,realized_usd=None,entry2_filled=False,total_entries=1)
    t=dict(t); risk=abs(t["entry"]-t["sl"]); t["sl"]=t["sl"]; tp=t["tp"] or (t["entry"]+risk*cfg.TP_R if t["direction"]=="BUY" else t["entry"]-risk*cfg.TP_R)
    si=next((i for i,b in enumerate(bars) if int(b["time"])>=t["entry_time"]),None); ei=next((i for i,b in enumerate(bars) if int(b["time"])>=t["exit_time"]),len(bars)-1)
    if si is None: return dict(position_id=t["position_id"],reason="MISSING_M1_ENTRY",realized_R=None,realized_usd=None,entry2_filled=False,total_entries=1)
    d=trail*PIP; activation=act*PIP; sl=t["sl"]; active=False; e2=False; mfe=0
    e2p=t["entry"]-.5*risk if t["direction"]=="BUY" else t["entry"]+.5*risk
    for b in bars[si+1:min(ei+1,len(bars))]:
        hi,lo=float(b["high"]),float(b["low"])
        if t["direction"]=="BUY":
            mfe=max(mfe,hi-t["entry"])
            if two and not e2 and lo<=e2p: e2=True
            if hi-t["entry"]>=activation: active=True; sl=max(sl,hi-d)
            hs,ht=lo<=sl,hi>=tp
        else:
            mfe=max(mfe,t["entry"]-lo)
            if two and not e2 and hi>=e2p: e2=True
            if t["entry"]-lo>=activation: active=True; sl=min(sl,lo+d)
            hs,ht=hi>=sl,lo<=tp
        if hs and ht: return finish(t,"AMBIGUOUS",None,e2,active,sl,mfe)
        if hs: return finish(t,"TRAIL_SL" if active else "SL",sl,e2,active,sl,mfe)
        if ht: return finish(t,"TP",tp,e2,active,sl,mfe)
    return finish(t,"UNRESOLVED",None,e2,active,sl,mfe)

def summary(rows):
    d=[x for x in rows if x.get("realized_R") is not None and x["reason"]!="AMBIGUOUS"]; w=[x for x in d if x["realized_R"]>0]; l=[x for x in d if x["realized_R"]<0]
    gp=sum(x["realized_R"] for x in w); gl=abs(sum(x["realized_R"] for x in l)); eq=peak=dd=0
    for x in sorted(d,key=lambda z:z["entry_time"]): eq+=x["realized_R"]; peak=max(peak,eq); dd=max(dd,peak-eq)
    return dict(trades=len(rows),decisive=len(d),wins=len(w),losses=len(l),ambiguous=len(rows)-len(d),win_rate=100*len(w)/len(d) if d else None,net_R=sum(x["realized_R"] for x in d),net_USD=sum((x["realized_usd"] or 0) for x in d),profit_factor=gp/gl if gl else None,max_drawdown_R=dd,avg_R=sum(x["realized_R"] for x in d)/len(d) if d else None,tp_hits=sum(x["reason"]=="TP" for x in rows),sl_hits=sum(x["reason"]=="SL" for x in rows),trail_exits=sum(x["reason"]=="TRAIL_SL" for x in rows),entry2_filled=sum(bool(x.get("entry2_filled")) for x in rows),total_entries=sum(x.get("total_entries",1) for x in rows))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--mt5-path",required=True); ap.add_argument("--symbol",default="XAUUSD.ecn"); ap.add_argument("--magic",type=int,default=DEFAULT_MAGIC); ap.add_argument("--start",default="2026-10-01T10:37:00+00:00"); ap.add_argument("--end"); ap.add_argument("--expected-trades",type=int,default=None); a=ap.parse_args()
    end=utc(a.end) if a.end else datetime.now(timezone.utc); start=utc(a.start)
    if not mt5.initialize(path=a.mt5_path): raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        ts=trades(a.symbol,start,end,a.magic)
        if not a.allow_count_diff and len(ts)!=a.expected_trades: raise RuntimeError(f"Expected {a.expected_trades} completed positions, found {len(ts)}. Inspect history first; use --allow-count-diff only deliberately.")
        if not ts: raise RuntimeError("No completed trades found.")
        bars=m1(a.symbol,datetime.fromtimestamp(min(x["entry_time"] for x in ts),timezone.utc)-timedelta(minutes=2),datetime.fromtimestamp(max(x["exit_time"] for x in ts),timezone.utc)+timedelta(minutes=2))
        matrix=[]; detail=[]
        for act in ACTS:
            for trail in TRAILS:
                for two in (False,True):
                    rows=[replay(x,bars,act,trail,two) for x in ts]; s=summary(rows); name=f"ACT{act}_TRAIL{trail}_2X{'ON' if two else 'OFF'}"; matrix.append(dict(method=name,activation_pips=act,trail_pips=trail,two_x=two,**s))
                    for r in rows: detail.append(dict(method=name,activation_pips=act,trail_pips=trail,two_x=two,**r))
        stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"); base=OUT/f"SP2L_TRAILING_2X_MATRIX_{stamp}"
        for path,rows in ((base.with_suffix(".csv"),matrix),(base.with_name(base.name+"_TRADES.csv"),detail)):
            with open(path,"w",newline="",encoding="utf-8") as f: w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        payload=dict(version="SP2L_V3_MT5_ACTUAL_TRAILING_MATRIX_20261003",research_only=True,symbol=a.symbol,magic=a.magic,start_utc=start.isoformat(),end_utc=end.isoformat(),actual_positions=len(ts),m1_bars=len(bars),pip_size_price=PIP,pip_source="MT5_SYMBOL_POINT",symbol_point=float(info.point),symbol_digits=int(info.digits),v3=dict(pGapPrice=cfg.P_GAP_PRICE,spikeMultiplier=cfg.SPIKE_MULTIPLIER,maxSlDistance=cfg.MAX_SL_DISTANCE,tpR=cfg.TP_R,trailMechanics="completed M1 high/low"),matrix=matrix)
        raw=json.dumps(payload,indent=2); base.with_suffix(".json").write_text(raw,encoding="utf-8"); sha=hashlib.sha256(raw.encode()).hexdigest()
        base.with_name(base.name+"_SNAPSHOT.md").write_text(f"# SP2L V3 MT5 Actual Trailing Matrix\nResearch-only; no canonical decision.\nPositions: {len(ts)} | M1 bars: {len(bars)} | pip size: {PIP} (MT5 symbol point)\nVariants: 120 (6 activation × 10 trail × 2X ON/OFF).\n2X fill: M1 touch counterfactual; same-bar ordering is not inferred.\nJSON SHA256: {sha}\n",encoding="utf-8")
        print(json.dumps(dict(status="COMPLETE",positions=len(ts),m1_bars=len(bars),csv=str(base.with_suffix(".csv")),trades_csv=str(base.with_name(base.name+"_TRADES.csv")),json=str(base.with_suffix(".json")),snapshot=str(base.with_name(base.name+"_SNAPSHOT.md")),sha256=sha),indent=2))
    finally: mt5.shutdown()
if __name__=="__main__": main()
