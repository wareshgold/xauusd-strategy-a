from __future__ import annotations
"""Offline unified 603-variant management matrix. No MT5 or signal generation."""
import argparse,csv,hashlib,json,math,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from strategy_factory.v3_management_engine import replay_management_trade,normalize_management_spec
from strategy_factory.v3_step_lock_engine import replay_step_lock_no_tp,validate_frozen_risk
from strategy_factory.m1_integrity import m1_gap_detected
ENTRY_SHA="39ED87CD1F0BE3E59B5F064B0BCF97A9787E5266DF6E972AA07E5EA4D3608AB1"
M1_SHA="B0782E716C7ECCBD29EF25E146C088B356F2AADF2CCD5D7EA24E6AC1488AA285"
EF=["strategy","variant","direction","setup_time_utc","entry_time_utc","entry_proxy","sl_initial","target","risk_price","exit_time_utc","exit_price","exit_reason","status","r_multiple"]
MF=["time_epoch_seconds","time_utc_iso","open","high","low","close","tick_volume","spread","real_volume"]
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def dt(s):
 x=datetime.fromisoformat(s.replace("Z","+00:00"))
 if x.tzinfo is None or x.utcoffset() is None:raise ValueError("timezone required")
 return x.astimezone(timezone.utc)
def load(mp,ep):
 ms,es=sha(mp),sha(ep)
 if ms!=M1_SHA or es!=ENTRY_SHA:raise ValueError(f"input SHA mismatch M1={ms} entries={es}")
 bars=[];prev=None
 with mp.open(encoding="utf-8-sig",newline="") as f:
  rd=csv.DictReader(f)
  if rd.fieldnames!=MF:raise ValueError("M1 header mismatch")
  for n,r in enumerate(rd,2):
   t=int(r["time_epoch_seconds"]);v={k:float(r[k]) for k in ("open","high","low","close")}
   if int(dt(r["time_utc_iso"]).timestamp())!=t or t%60 or(prev is not None and t<=prev):raise ValueError(f"M1 timestamp error line {n}")
   if not all(math.isfinite(z) and z>0 for z in v.values()) or v["high"]<max(v.values()) or v["low"]>min(v.values()):raise ValueError(f"OHLC error line {n}")
   bars.append({"time":t,**v});prev=t
 if len(bars)!=29919 or bars[0]["time"]!=int(dt("2026-09-24T07:57:00Z").timestamp()) or bars[-1]["time"]!=int(dt("2026-10-23T23:57:00Z").timestamp()):raise ValueError("M1 coverage mismatch")
 ix={b["time"]:i for i,b in enumerate(bars)};pop=[];seen=set();strategies=set()
 with ep.open(encoding="utf-8-sig",newline="") as f:
  rd=csv.DictReader(f)
  if rd.fieldnames!=EF:raise ValueError("entry header mismatch")
  for n,r in enumerate(rd,2):
   strategies.add(r["strategy"].strip());t=int(dt(r["entry_time_utc"]).timestamp());side=r["direction"].strip().upper()
   if len(strategies)>1 or side not in ("BUY","SELL") or t not in ix:raise ValueError(f"entry invalid line {n}")
   c={"entry_idx":ix[t],"theoretical_entry":float(r["entry_proxy"]),"sl":float(r["sl_initial"]),"risk":float(r["risk_price"]),"direction":side,"trigger_time":t,"signal_time_utc":r["entry_time_utc"],"setup_time_utc":r["setup_time_utc"],"source_variant":r["variant"]}
   validate_frozen_risk(c);key=(t,side,c["theoretical_entry"],c["sl"])
   if key in seen:raise ValueError(f"duplicate entry line {n}")
   seen.add(key);pop.append(c)
 if len(pop)!=462:raise ValueError(f"expected 462 entries, got {len(pop)}")
 gaps=sum(b["time"]-a["time"]>60 for a,b in zip(bars,bars[1:]))
 if gaps!=21:raise ValueError(f"expected 21 gaps, got {gaps}")
 return bars,pop,{"m1":{"sha256":ms,"bars":len(bars),"gaps":gaps},"entries":{"sha256":es,"rows":len(pop),"strategy":next(iter(strategies),None)}}
def step_tp(c,bars,rr,contract,volume):
 e=float(c["theoretical_entry"]);risk=float(c["risk"]);side=c["direction"];tp=e+(rr*risk if side=="BUY" else -rr*risk);sl=float(c["sl"]);mil=0;prev=int(bars[c["entry_idx"]]["time"]);held=0
 o={"direction":side,"trigger_time":c["trigger_time"],"signal_time_utc":c.get("signal_time_utc"),"theoretical_entry":e,"risk":risk,"initial_sl":sl,"initial_tp":tp,"final_sl":sl,"highest_milestone_R":0,"bars_held":0,"exit_price":None,"exit_time_utc":None,"reason":"OPEN_OR_UNRESOLVED","ambiguous":False,"realized_price":None,"realized_R":None,"risk_usd":risk*contract*volume,"realized_usd":None,"management_mode":"STEP_LOCK_WITH_TP"}
 for bi in range(c["entry_idx"]+1,len(bars)):
  b=bars[bi];now=int(b["time"])
  if m1_gap_detected(prev,now):o.update(ambiguous=True,reason="M1_GAP_WHILE_OPEN",exit_time_utc=datetime.fromtimestamp(now,timezone.utc).isoformat());break
  prev=now;held+=1;hi,lo=float(b["high"]),float(b["low"]);sh=lo<=sl if side=="BUY" else hi>=sl;th=hi>=tp if side=="BUY" else lo<=tp;fav=hi-e if side=="BUY" else e-lo;reached=max(0,int(math.floor((fav+1e-6)/risk)));new=reached>mil
  if (sh and th) or (sh and new):o.update(ambiguous=True,reason="MULTIPLE_EVENTS_SAME_BAR",exit_time_utc=datetime.fromtimestamp(now,timezone.utc).isoformat());break
  if sh or th:
   px=sl if sh else tp;gain=px-e if side=="BUY" else e-px;o.update(exit_price=px,reason=("STEP_LOCK_SL" if mil else "SL") if sh else "TP",exit_time_utc=datetime.fromtimestamp(now,timezone.utc).isoformat(),realized_price=gain,realized_R=gain/risk,realized_usd=gain*contract*volume);break
  if new:mil=reached;sl=e+(mil-1)*risk if side=="BUY" else e-(mil-1)*risk
 o.update(final_sl=sl,highest_milestone_R=mil,bars_held=held);return o
def variants():
 acts=(0,.25,.5,.75,1,1.5,2,3,4,6);dists=(.2,.3,.4,.5,.7,1,1.5,2,3,4,6);out=[]
 def add(f,n,s,k="mgmt"):out.append({"family":f,"name":n,"spec":s,"kind":k})
 for rr in (1,1.5,2,3):add("FIXED_RR",f"RR_{rr:g}",{"mode":"FIXED_RR","rr":rr})
 add("NO_TARGET","NO_TARGET",{"mode":"NO_TARGET"})
 for x in (.5,1,1.5):add("BREAK_EVEN",f"BE_{x:g}R",{"mode":"BREAK_EVEN","rr":None,"activation_r":x,"offset_r":0})
 for x in acts:
  for y in dists:add("FIXED_DISTANCE_TRAIL",f"FDT_A{x:g}_D{y:g}",{"mode":"TRAILING_R","rr":None,"activation_r":x,"distance_r":y,"price_units":True})
 add("STEP_LOCK","STEP_LOCK_NO_TP",{},"step_no_tp")
 for rr in (1,1.5,2,3):add("STEP_LOCK_TP",f"STEP_LOCK_TP_RR{rr:g}",{"rr":rr},"step_tp")
 for be in (.5,1,1.5):
  for ta in (1,1.5,2,3):
   for td in (.5,1,1.5):add("BE_PLUS_TRAIL",f"BE{be:g}_TA{ta:g}_TD{td:g}",{"mode":"BREAK_EVEN_TRAILING","rr":None,"be_activation_r":be,"be_offset_r":0,"trail_activation_r":ta,"trail_distance_r":td})
 for rr in (1,1.5,2,3):
  for x in acts:
   for y in dists:add("FIXED_TP_PLUS_TRAIL",f"TP{rr:g}_A{x:g}_D{y:g}",{"mode":"TRAILING_R","rr":rr,"activation_r":x,"distance_r":y,"price_units":True})
 for n in (15,30,60,120):add("TIME_EXIT",f"TIME_{n}",{"mode":"TIME_EXIT","max_bars":n})
 if len(out)!=603:raise AssertionError(len(out))
 return out
def summary(rows):
 dec=[x for x in rows if not x["ambiguous"] and x["realized_R"] is not None];w=[x for x in dec if x["realized_R"]>0];l=[x for x in dec if x["realized_R"]<0];gp=sum(x["realized_usd"] for x in w);gl=abs(sum(x["realized_usd"] for x in l));eq=peak=dd=0
 settled=sorted((x for x in rows if x["realized_R"] is not None and not x["ambiguous"]),key=lambda x:x.get("exit_time_utc") or "")
 for x in settled:
  eq+=x["realized_usd"];peak=max(peak,eq);dd=max(dd,peak-eq)
 return {"signals":len(rows),"decisive":len(dec),"wins":len(w),"losses":len(l),"breakeven":len(dec)-len(w)-len(l),"ambiguous":sum(bool(x["ambiguous"]) for x in rows),"open_unresolved":sum(x["reason"]=="OPEN_OR_UNRESOLVED" for x in rows),"gap_exposed":sum(x["reason"]=="M1_GAP_WHILE_OPEN" for x in rows),"net_R":sum(x["realized_R"] for x in dec),"gross_usd":sum(x["realized_usd"] for x in dec),"gross_profit_usd":gp,"gross_loss_usd":gl,"profit_factor":gp/gl if gl else(None if not gp else "infinity"),"max_drawdown_usd":dd,"average_R":sum(x["realized_R"] for x in dec)/len(dec) if dec else None,"costs_modeled":False}
def main():
 p=argparse.ArgumentParser();p.add_argument("--m1-csv",required=True);p.add_argument("--entry-csv",required=True);p.add_argument("--point",type=float,required=True);p.add_argument("--contract-size",type=float,required=True);p.add_argument("--volume",type=float,required=True);p.add_argument("--output-dir",required=True);p.add_argument("--symbol",default="XAUUSD.ecn");a=p.parse_args()
 if not all(math.isfinite(x) and x>0 for x in(a.point,a.contract_size,a.volume)):raise ValueError("point/contract/volume must be positive")
 mp,ep,out=Path(a.m1_csv).resolve(),Path(a.entry_csv).resolve(),Path(a.output_dir).resolve()
 if out.exists():raise FileExistsError(f"refusing overwrite {out}")
 bars,pop,inputs=load(mp,ep);matrix=variants();ranked=[];alltrades=[]
 for vi,v in enumerate(matrix,1):
  rows=[]
  for ix,c in enumerate(pop):
   if v["kind"]=="step_no_tp":r=replay_step_lock_no_tp(c,bars,contract_size=a.contract_size,volume=a.volume)
   elif v["kind"]=="step_tp":r=step_tp(c,bars,v["spec"]["rr"],a.contract_size,a.volume)
   else:
    sp=dict(v["spec"]);price=sp.pop("price_units",False)
    if price:sp["activation_r"]=sp["activation_r"]/c["risk"];sp["distance_r"]=sp["distance_r"]/c["risk"]
    r=replay_management_trade(c,bars,normalize_management_spec(sp),mt5_point=a.point,contract_size=a.contract_size,volume=a.volume)
   r.update(population_index=ix,variant=v["name"],family=v["family"]);rows.append(r)
  sm=summary(rows);sm.update(variant=v["name"],family=v["family"],spec=v["spec"]);ranked.append(sm);alltrades.extend(rows)
  if vi%50==0:print(f"PROGRESS {vi}/603 variants; {vi*462} replays",flush=True)
 ranked.sort(key=lambda x:(x["gross_usd"],x["profit_factor"] if isinstance(x["profit_factor"],(int,float)) else 1e99,-x["ambiguous"]-x["open_unresolved"]),reverse=True)
 for i,x in enumerate(ranked,1):x["discovery_rank"]=i
 out.mkdir(parents=True,exist_ok=False);stem="SP2L_UNIFIED_MANAGEMENT_MATRIX_"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ");rp=out/(stem+"_RANKED.csv");tp=out/(stem+"_TRADES.csv");mf=out/(stem+"_MANIFEST.json")
 with rp.open("x",encoding="utf-8-sig",newline="") as f:
  wr=csv.DictWriter(f,fieldnames=list(ranked[0]));wr.writeheader()
  for x in ranked:wr.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in x.items()})
 with tp.open("x",encoding="utf-8-sig",newline="") as f:
  trade_fields=list(dict.fromkeys(k for row in alltrades for k in row));wr=csv.DictWriter(f,fieldnames=trade_fields,extrasaction="ignore");wr.writeheader();wr.writerows(alltrades)
 manifest={"research_only":True,"canonical":False,"mt5_accessed":False,"signal_rebuild":False,"variant_count":603,"population_count":462,"trade_replays":278586,"symbol":a.symbol,"timeframe":"M1","execution":{"point_metadata_only":a.point,"contract_size":a.contract_size,"volume":a.volume,"spread_commission_slippage":"NOT_MODELED"},"inputs":inputs,"families":{"fixed_RR":[1,1.5,2,3],"no_target":1,"BE_activation_R":[.5,1,1.5],"fixed_distance_activation_price":[0,.25,.5,.75,1,1.5,2,3,4,6],"fixed_distance_price":[.2,.3,.4,.5,.7,1,1.5,2,3,4,6],"step_lock_no_TP":1,"step_lock_TP_RR":[1,1.5,2,3],"BE_trail_BE_activation_R":[.5,1,1.5],"BE_trail_activation_R":[1,1.5,2,3],"BE_trail_distance_R":[.5,1,1.5],"fixed_TP_trail_RR":[1,1.5,2,3],"time_exit_bars":[15,30,60,120],"partial_close":"EXCLUDED_UNDEFINED_FILL_SEMANTICS"},"semantics":{"entry_bar":"EXCLUDED","stop_update":"NEXT_BAR","same_bar_conflicts":"AMBIGUOUS","M1_gap":"AMBIGUOUS_NO_FILL","zero_trail_activation":"FIRST_COMPLETED_POST_ENTRY_BAR","ranking":"DISCOVERY_ONLY_GROSS_USD_THEN_PF_THEN_UNRESOLVED","costs":"NOT_MODELED"},"top_20":ranked[:20],"artifacts":{}}
 for f in(rp,tp):manifest["artifacts"][f.name]={"sha256":sha(f),"bytes":f.stat().st_size}
 mf.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 sums=out/(stem+"_SHA256SUMS.txt")
 with sums.open("x",encoding="utf-8") as f:
  for q in(rp,tp,mf):f.write(f"{sha(q)}  {q.name}\n")
 print(json.dumps({"status":"COMPLETE","variants":603,"population":462,"trade_replays":278586,"top_10":ranked[:10],"output_dir":str(out),"manifest":str(mf),"research_only":True,"mt5_accessed":False},indent=2,ensure_ascii=False));return 0
if __name__=="__main__":raise SystemExit(main())
