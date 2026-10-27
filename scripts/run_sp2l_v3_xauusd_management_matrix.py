"""Research-only R-scaled trade-management matrix. Does not define canonical Strategy A rules."""
from __future__ import annotations
import argparse, csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
import run_sp2l_v3_xauusd_trailing_matrix as base

OUT = Path(__file__).resolve().parents[1] / "artifacts" / "v3"
OUT.mkdir(parents=True, exist_ok=True)

def simulate(bars, candidate, entry_idx, mode, activation_r=None, distance_r=None, partial_r=None):
    direction = candidate["direction"]
    entry, initial_sl, tp, risk = map(float, (candidate["theoretical_entry"], candidate["sl"], candidate["tp"], candidate["risk"]))
    sl, activated, partial = initial_sl, False, False
    partial_contribution = 0.0
    part_fraction = 0.5 if mode == "PARTIAL_RUNNER" else 0.0
    runner_fraction = 1.0 - part_fraction
    target = entry + (partial_r*risk if direction == "BUY" else -partial_r*risk) if partial_r is not None else None
    out = {"direction": direction, "trigger_time": int(candidate["trigger_time"]), "entry_time": int(candidate["trigger_time"]),
           "exit_time": None, "entry": entry, "initial_sl": initial_sl, "initial_tp": tp, "risk_price": risk,
           "management_mode": mode, "activation_R": activation_r, "trail_distance_R": distance_r, "partial_tp_R": partial_r,
           "final_sl": sl, "trailing_activated": False, "partial_done": False, "exit_price": None,
           "reason": "OPEN_OR_UNRESOLVED", "ambiguous": False, "realized_R": None}
    for k in range(entry_idx+1, len(bars)):
        b=bars[k]; hi,lo,op=map(float,(b["high"],b["low"],b["open"]))
        hit_sl = lo <= sl if direction=="BUY" else hi >= sl
        hit_tp = (hi >= tp if direction=="BUY" else lo <= tp) if mode=="FIXED_TP" else False
        hit_part = target is not None and not partial and (hi >= target if direction=="BUY" else lo <= target)
        if hit_sl and (hit_tp or hit_part):
            out.update(ambiguous=True, reason="SL_AND_TARGET_SAME_BAR", exit_time=int(b["time"])); break
        if hit_sl:
            fill=sl
            if direction=="BUY" and op < sl: fill=op
            if direction=="SELL" and op > sl: fill=op
            stop_r=(fill-entry)/risk if direction=="BUY" else (entry-fill)/risk
            out.update(exit_price=fill, realized_R=partial_contribution+runner_fraction*stop_r,
                       exit_time=int(b["time"]), reason="TRAIL_SL" if activated and sl!=initial_sl else "SL"); break
        if hit_tp:
            out.update(exit_price=tp, realized_R=((tp-entry)/risk if direction=="BUY" else (entry-tp)/risk),
                       exit_time=int(b["time"]), reason="TP"); break
        if hit_part:
            partial_contribution=part_fraction*partial_r; partial=True
            out["partial_done"]=True
            continue
        if mode in ("RUNNER","PARTIAL_RUNNER"):
            favorable=hi-entry if direction=="BUY" else entry-lo
            if favorable >= activation_r*risk:
                offset=distance_r*risk
                proposed=hi-offset if direction=="BUY" else lo+offset
                if direction=="BUY" and sl < proposed < hi: sl=proposed; activated=True
                elif direction=="SELL" and lo < proposed < sl: sl=proposed; activated=True
    out["final_sl"]=sl; out["trailing_activated"]=activated
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv-path",required=True)
    p.add_argument("--symbol",default="XAUUSD.ecn")
    p.add_argument("--start",default="2026-08-21T00:00:00+00:00")
    p.add_argument("--end",default="2026-09-19T00:00:00+00:00")
    p.add_argument("--config-module",default="sp2l_v3_rr2_trail4_config")
    p.add_argument("--activation-r",default="1,1.5,2,2.5")
    p.add_argument("--distance-r",default="0.5,1,1.5,2,3")
    p.add_argument("--partial-r",default="1,1.5")
    a=p.parse_args()
    start,end=datetime.fromisoformat(a.start),datetime.fromisoformat(a.end)
    if start.tzinfo is None or end.tzinfo is None or start>=end: raise ValueError("Use valid timezone-aware UTC bounds")
    cfg=__import__(a.config_module)
    bars=base.load_m1_csv(a.csv_path,start,end)
    candidates=base.collect_candidates(bars,cfg,a.symbol)
    acts=base.parse_prices(a.activation_r,"activation-r")
    dists=base.parse_prices(a.distance_r,"distance-r")
    parts=base.parse_prices(a.partial_r,"partial-r")
    scenarios=[("FIXED_TP",None,None,None)]
    scenarios += [("RUNNER",x,d,None) for x in acts for d in dists]
    scenarios += [("PARTIAL_RUNNER",x,d,r) for r in parts for x in acts for d in dists]
    matrix=[]; trades=[]
    for mode,x,d,r in scenarios:
        rows=[simulate(bars,c,i,mode,x,d,r) for c,i in candidates]
        summary=base.summarize(rows,dataset_end_time=int(bars[-1]["time"]))
        matrix.append({"scenario":mode,"activation_R":x,"trail_distance_R":d,"partial_tp_R":r,**summary})
        trades.extend({"scenario":mode,**t} for t in rows)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root=OUT/f"SP2L_V3_MANAGEMENT_MATRIX_{stamp}"
    payload={"status":"COMPLETE","research_only":True,"canonical":False,"symbol":a.symbol,"timeframe":"M1",
      "window_utc":{"start":a.start,"end":a.end},"bars":len(bars),"bars_sha256":hashlib.sha256(bars.tobytes()).hexdigest(),
      "candidates":len(candidates),"config_module":a.config_module,
      "entry_geometry":{"version":cfg.VERSION,"p_gap_price":cfg.P_GAP_PRICE,"spike_multiplier":cfg.SPIKE_MULTIPLIER,
        "max_sl_distance":cfg.MAX_SL_DISTANCE,"configured_tp_R":cfg.TP_R,"session_policy":cfg.SESSION_POLICY},
      "simulation":{"scenario_count":len(scenarios),"stop_gap_fill":"adverse open","costs":"spread, commission, swap and ordinary slippage excluded",
        "partial_exit":"50% at target R; remainder becomes runner","runner":"no fixed TP; trail offset and activation scaled by original risk",
        "ambiguous":"same-bar stop/target excluded from decisive metrics","data_gaps":"not filled or synthesized; source/session audit pending",
        "holdout":"not fresh holdout; research only"},"matrix":matrix}
    jp=root.with_suffix(".json"); jp.write_text(json.dumps(payload,indent=2),encoding="utf-8")
    for suffix,rows in [("_matrix.csv",matrix),("_trades.csv",trades)]:
        with root.with_name(root.name+suffix).open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    snap=root.with_name(root.name+"_SNAPSHOT.md")
    snap.write_text("# Research-only management matrix\n\nEntry geometry unchanged; alternatives are non-canonical.\n"
      "Fixed TP, no-fixed-TP runners, and 50% partial + runner. Stops use adverse-open sensitivity.\n"
      "Costs excluded; OHLC same-bar ambiguities excluded; no gaps synthesized; not fresh holdout.\n",encoding="utf-8")
    print(json.dumps({"status":"COMPLETE","json":str(jp),"matrix_csv":str(root.with_name(root.name+"_matrix.csv")),
      "trades_csv":str(root.with_name(root.name+"_trades.csv")),"snapshot":str(snap),"bars":len(bars),
      "candidates":len(candidates),"matrix_rows":len(matrix),"research_only":True,"canonical":False},indent=2))
if __name__=="__main__": main()
