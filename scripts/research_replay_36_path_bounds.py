#!/usr/bin/env python3
"""Offline OHLC path-sensitivity replay for the frozen 36-position SP2L fixture.

Research-only: no MT5 imports, network access, orders, or canonical decisions.
Two intrabar paths are deterministic OHLC sensitivity cases, NOT probabilities,
tick reconstructions, broker fill simulations, or execution rules.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPECTED_IDS = {
62458477,62466595,62472493,62479760,62483102,62486473,62488249,62491448,
62492610,62497786,62499705,62503253,62506281,62507768,62510782,62511473,
62512516,62516401,62516729,62518329,62521529,62540713,62546910,62552588,
62555855,62585649,62592622,62594268,62598298,62604959,62614431,62615799,
62618151,62623643,62624533,62625703}
EXCLUDED_KNOWN={62417157,62429827}
RR_GRID=(1,2,4)
ACTIVATION_PIPS=(0,2,4,6,8,10,20,30,40,50)
TRAIL_PIPS=(2,4,6,8,10,12,20,30,40,50)
PIP_PRICE=0.01
SCENARIOS=("ADVERSE_FIRST","FAVORABLE_FIRST")
CONTRACT_SIZE_ASSUMPTION=100.0
VOLUME_ASSUMPTION=0.01

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def parse_utc(value: str) -> int:
    dt=datetime.fromisoformat(value.strip().replace("Z","+00:00"))
    if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
    return int(dt.astimezone(timezone.utc).timestamp())

def load_trades(path: Path):
    selected={}; baseline_rows=0; excluded=set()
    with path.open("r",encoding="utf-8-sig",newline="") as fh:
        reader=csv.DictReader(fh)
        required={"variant","position_id","direction","weighted_entry","final_sl","entry_time","entry2_filled","total_entries"}
        missing=required-set(reader.fieldnames or [])
        if missing: raise ValueError(f"Trade fixture missing columns: {sorted(missing)}")
        for row in reader:
            if row.get("variant")!="NO_TRAILING_RR1": continue
            baseline_rows+=1; pid=int(row["position_id"])
            if pid in EXCLUDED_KNOWN: excluded.add(pid)
            if pid not in EXPECTED_IDS: continue
            if pid in selected: raise ValueError(f"Duplicate baseline position_id: {pid}")
            direction=row["direction"].upper()
            if direction not in {"BUY","SELL"}: raise ValueError(f"Invalid direction for {pid}")
            if row["entry2_filled"].strip().lower()!="false" or row["total_entries"].strip()!="1":
                raise ValueError(f"Non-single-entry fixture population at {pid}")
            entry=float(row["weighted_entry"]); sl=float(row["final_sl"]); risk=abs(entry-sl)
            if not all(math.isfinite(x) for x in (entry,sl,risk)) or risk<=0:
                raise ValueError(f"Invalid entry/SL/risk for {pid}")
            selected[pid]={"position_id":pid,"direction":direction,"entry":entry,"sl":sl,
                           "risk":risk,"entry_time":int(float(row["entry_time"])),
                           "source_variant":"NO_TRAILING_RR1"}
    if set(selected)!=EXPECTED_IDS:
        raise ValueError(f"Whitelist mismatch; missing={sorted(EXPECTED_IDS-set(selected))}")
    trades=sorted(selected.values(),key=lambda x:(x["entry_time"],x["position_id"]))
    buys=sum(t["direction"]=="BUY" for t in trades); sells=len(trades)-buys
    if (buys,sells)!=(18,18): raise ValueError(f"Expected 18 BUY / 18 SELL, got {buys}/{sells}")
    audit={"baseline_rows_in_source":baseline_rows,"selected_positions":len(trades),"buy":buys,"sell":sells,
           "excluded_known_ids_present":sorted(excluded),
           "selected_ids_sha256":hashlib.sha256(("\n".join(str(t["position_id"]) for t in trades)+"\n").encode()).hexdigest(),
           "entry2_population":"FALSE_ONLY","entry_sl_provenance":"NO_TRAILING_RR1 weighted_entry / final_sl"}
    return trades,audit

def load_m1(path: Path):
    bars=[]
    with path.open("r",encoding="utf-8-sig",newline="") as fh:
        reader=csv.DictReader(fh)
        required={"time","open","high","low","close"}
        missing=required-set(reader.fieldnames or [])
        if missing: raise ValueError(f"M1 fixture missing columns: {sorted(missing)}")
        for line,row in enumerate(reader,start=2):
            ts=parse_utc(row["time"]); o,h,l,c=(float(row[k]) for k in ("open","high","low","close"))
            if not all(math.isfinite(x) for x in (o,h,l,c)): raise ValueError(f"Non-finite OHLC at line {line}")
            if h<max(o,c,l) or l>min(o,c,h): raise ValueError(f"Invalid OHLC at line {line}")
            bars.append({"time":ts,"open":o,"high":h,"low":l,"close":c})
    bars.sort(key=lambda b:b["time"]); times=[int(b["time"]) for b in bars]
    if not bars: raise ValueError("M1 fixture is empty")
    if len(times)!=len(set(times)): raise ValueError("Duplicate M1 timestamps")
    gaps=[{"from_utc":datetime.fromtimestamp(a,timezone.utc).isoformat(),
           "to_utc":datetime.fromtimestamp(b,timezone.utc).isoformat(),
           "missing_minutes":int((b-a)//60-1)}
          for a,b in zip(times,times[1:]) if b-a>60]
    return bars,{"bars":len(bars),"first_utc":datetime.fromtimestamp(times[0],timezone.utc).isoformat(),
                 "last_utc":datetime.fromtimestamp(times[-1],timezone.utc).isoformat(),
                 "gaps":gaps,"ohlc_validation":"PASS","duplicate_timestamps":0}

def _event(q0,q1,stop_q,tp_q):
    if q1>q0 and q0<tp_q<=q1: return "TP"
    if q1<q0 and q1<=stop_q<=q0: return "STOP"
    return None

def simulate_path(trade,bars,rr,activation_pips,trail_pips,scenario):
    side=1.0 if trade["direction"]=="BUY" else -1.0
    entry,risk=trade["entry"],trade["risk"]
    initial_stop=-risk; stop_q=initial_stop; tp_q=rr*risk
    activation_q=activation_pips*PIP_PRICE; trail_q=trail_pips*PIP_PRICE
    active=False; mfe_q=0.0; stop_moved=False
    entry_minute=trade["entry_time"]-(trade["entry_time"]%60)
    started=False; previous_time=None
    for bar in bars:
        ts=int(bar["time"])
        if ts<=entry_minute:
            previous_time=ts
            continue
        if not started:
            # The first complete post-entry minute should immediately follow the
            # excluded entry minute. Never bridge a missing interval.
            if ts-entry_minute>60:
                return {"status":"DATA_GAP_CENSOR","reason":"DATA_GAP_CENSOR","exit_q":None,
                        "exit_price_proxy":None,"realized_R":None,"gross_usd_proxy":None,
                        "active":active,"mfe_price":mfe_q,"gap_seconds":ts-entry_minute}
            started=True
        elif previous_time is not None and ts-previous_time>60:
            return {"status":"DATA_GAP_CENSOR","reason":"DATA_GAP_CENSOR","exit_q":None,
                    "exit_price_proxy":None,"realized_R":None,"gross_usd_proxy":None,
                    "active":active,"mfe_price":mfe_q,"gap_seconds":ts-previous_time}
        # First complete post-entry minute is the first observable bar; no entry-minute path is inferred.
        q_open=(bar["open"]-entry)*side; q_high=(bar["high"]-entry)*side
        q_low=(bar["low"]-entry)*side; q_close=(bar["close"]-entry)*side
        q_fav,q_adv=max(q_high,q_low),min(q_high,q_low)
        if q_open<=stop_q:
            return {"status":"GAP_TRIGGER_UNRESOLVED","reason":"GAP_STOP","exit_q":None,
                    "exit_price_proxy":None,"realized_R":None,"gross_usd_proxy":None,
                    "active":active,"mfe_price":mfe_q,"gap_seconds":None}
        if q_open>=tp_q:
            return {"status":"GAP_TRIGGER_UNRESOLVED","reason":"GAP_TP","exit_q":None,
                    "exit_price_proxy":None,"realized_R":None,"gross_usd_proxy":None,
                    "active":active,"mfe_price":mfe_q,"gap_seconds":None}
        vertices=[q_open,q_adv,q_fav,q_close] if scenario=="ADVERSE_FIRST" else [q_open,q_fav,q_adv,q_close]
        for q0,q1 in zip(vertices,vertices[1:]):
            event=_event(q0,q1,stop_q,tp_q)
            if event:
                exit_q=tp_q if event=="TP" else stop_q
                exit_price=entry+side*exit_q
                reason="TP" if event=="TP" else ("TRAIL_SL" if stop_moved else "SL")
                return {"status":"RESOLVED","reason":reason,"exit_q":exit_q,
                        "exit_price_proxy":exit_price,"realized_R":exit_q/risk,
                        "gross_usd_proxy":(exit_price-entry)*side*CONTRACT_SIZE_ASSUMPTION*VOLUME_ASSUMPTION,
                        "active":active,"mfe_price":mfe_q,"gap_seconds":None}
            if q1>q0:
                mfe_q=max(mfe_q,q1)
                if trail_pips>0 and mfe_q>=activation_q:
                    active=True; candidate=mfe_q-trail_q
                    if candidate>stop_q: stop_q=candidate; stop_moved=True
        previous_time=ts
    return {"status":"END_OF_DATA","reason":"END_OF_DATA","exit_q":None,
            "exit_price_proxy":None,"realized_R":None,"gross_usd_proxy":None,
            "active":active,"mfe_price":mfe_q,"gap_seconds":None}

def summarize(results):
    resolved=[r for r in results if r["status"]=="RESOLVED"]
    wins=[r for r in resolved if r["realized_R"]>0]
    losses=[r for r in resolved if r["realized_R"]<0]
    gp=sum(r["realized_R"] for r in wins); gl=abs(sum(r["realized_R"] for r in losses))
    return {"positions":len(results),"resolved":len(resolved),"wins":len(wins),"losses":len(losses),
            "non_resolved":len(results)-len(resolved),
            "data_gap_censor":sum(r["status"]=="DATA_GAP_CENSOR" for r in results),
            "gap_trigger_unresolved":sum(r["status"]=="GAP_TRIGGER_UNRESOLVED" for r in results),
            "end_of_data":sum(r["status"]=="END_OF_DATA" for r in results),
            "win_rate_resolved_pct":100*len(wins)/len(resolved) if resolved else None,
            "profit_factor_resolved":gp/gl if gl else None,
            "gross_R_resolved":sum(r["realized_R"] for r in resolved),
            "gross_usd_proxy_resolved":sum(r["gross_usd_proxy"] for r in resolved)}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--trades",required=True,type=Path); ap.add_argument("--m1",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path); args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    trades,trade_audit=load_trades(args.trades); bars,m1_audit=load_m1(args.m1)
    trade_sha,m1_sha=sha256_file(args.trades),sha256_file(args.m1)
    trade_results=[]; summaries=[]; ambiguities=[]
    for rr in RR_GRID:
      for act in ACTIVATION_PIPS:
       for trail in TRAIL_PIPS:
        pair={}
        for scenario in SCENARIOS:
         outcomes=[]
         for trade in trades:
          outcome=simulate_path(trade,bars,rr,act,trail,scenario)
          row={"variant":f"RR{rr}_ACT{act}_TRAIL{trail}_2XOFF","rr":rr,
               "activation_pips":act,"trail_pips":trail,"scenario":scenario,**trade,**outcome}
          outcomes.append(row); trade_results.append(row)
         pair[scenario]=outcomes
         summaries.append({"variant":f"RR{rr}_ACT{act}_TRAIL{trail}_2XOFF","rr":rr,
                           "activation_pips":act,"trail_pips":trail,"scenario":scenario,**summarize(outcomes)})
        for i,trade in enumerate(trades):
         a,f=pair["ADVERSE_FIRST"][i],pair["FAVORABLE_FIRST"][i]
         differs=(a["status"]!=f["status"] or a["reason"]!=f["reason"] or
                  (a["exit_q"] is not None and f["exit_q"] is not None and
                   not math.isclose(a["exit_q"],f["exit_q"],abs_tol=1e-9)))
         if differs:
          ambiguities.append({"variant":f"RR{rr}_ACT{act}_TRAIL{trail}_2XOFF",
             "position_id":trade["position_id"],"adverse_first_status":a["status"],
             "adverse_first_reason":a["reason"],"adverse_first_R":a["realized_R"],
             "favorable_first_status":f["status"],"favorable_first_reason":f["reason"],
             "favorable_first_R":f["realized_R"]})
    def write_csv(path,rows):
        fields=list(dict.fromkeys(k for row in rows for k in row))
        with path.open("w",encoding="utf-8",newline="") as fh:
            writer=csv.DictWriter(fh,fieldnames=fields,extrasaction="ignore"); writer.writeheader(); writer.writerows(rows)
    write_csv(args.out/"trade_results.csv",trade_results)
    write_csv(args.out/"scenario_summary.csv",summaries)
    write_csv(args.out/"path_ambiguities.csv",ambiguities)
    manifest={"research_only":True,"canonical":False,"execution_decisions":False,
      "engine":"OFFLINE_OHLC_TWO_PATH_SENSITIVITY_V1",
      "path_semantics":"OHLC_PATH_SENSITIVITY_NOT_PROBABILISTIC",
      "fill_semantics":"UNRESOLVED_PRICE_LEVEL_PROXY_ONLY_GAPS_UNRESOLVED",
      "costs":"OMITTED_GROSS_ONLY",
      "usd_proxy_assumption":{"contract_size":CONTRACT_SIZE_ASSUMPTION,"volume":VOLUME_ASSUMPTION,
        "warning":"Not broker-verified; not net P/L; excludes commission, swap, slippage."},
      "entry_minute":"EXCLUDED_AS_ENTRY_TIME_WITHIN_BAR_IS_UNKNOWN",
      "observed_exit":"NOT_USED_AS_REPLAY_CUTOFF_OR_COUNTERFACTUAL_EXIT",
      "two_x":"EXCLUDED_UNRESOLVED_INTRABAR_AND_SIZE_SEMANTICS",
      "rr_grid":RR_GRID,"activation_pips":ACTIVATION_PIPS,"trail_pips":TRAIL_PIPS,
      "variants":len(RR_GRID)*len(ACTIVATION_PIPS)*len(TRAIL_PIPS),"scenarios":SCENARIOS,
      "trade_fixture":{"path":str(args.trades),"sha256":trade_sha,**trade_audit},
      "m1_fixture":{"path":str(args.m1),"sha256":m1_sha,**m1_audit},
      "outputs":["trade_results.csv","scenario_summary.csv","path_ambiguities.csv","manifest.json"]}
    (args.out/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":"OFFLINE_REPLAY_COMPLETE","positions":len(trades),
      "buy":trade_audit["buy"],"sell":trade_audit["sell"],"variants":manifest["variants"],
      "scenario_rows":len(summaries),"trade_result_rows":len(trade_results),
      "path_ambiguity_rows":len(ambiguities),"trade_sha256":trade_sha,"m1_sha256":m1_sha,
      "out":str(args.out),"research_only":True,"canonical":False},indent=2))

if __name__=="__main__": main()
