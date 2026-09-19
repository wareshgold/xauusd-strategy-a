#!/usr/bin/env python3
"""Research-only R:R sensitivity test for SP2L on frozen M1 evidence.

Keeps archived Entry and SL unchanged. Reconstructs TP as 1R/2R/3R and
scans subsequent M1 candles. If SL and TP are both touched in one candle,
the result is AMBIGUOUS because intrabar order is unavailable.
No trailing and no strategy-rule promotion.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def simulate(m, candles, rr):
    entry=float(m["entry"]); sl=float(m["sl"]); direction=m["direction"]
    risk=abs(entry-sl)
    tp=entry + rr*risk if direction=="BUY" else entry - rr*risk
    i=int(m["outcome_scan_start_index"])
    while i<len(candles):
        c=candles[i]; high=float(c["high"]); low=float(c["low"])
        sl_hit=low<=sl if direction=="BUY" else high>=sl
        tp_hit=high>=tp if direction=="BUY" else low<=tp
        if sl_hit and tp_hit:
            return rr, "AMBIGUOUS", None, tp
        if sl_hit:
            return rr, "LOSS", -1.0, tp
        if tp_hit:
            return rr, "WIN", rr, tp
        i+=1
    return rr, "OPEN_OR_UNRESOLVED", None, tp

def summarize(rows):
    decisive=[r for r in rows if r["result"] in ("WIN","LOSS")]
    wins=[r for r in decisive if r["result"]=="WIN"]
    losses=[r for r in decisive if r["result"]=="LOSS"]
    net=sum(r["realized_r"] for r in decisive)
    gp=sum(r["realized_r"] for r in wins)
    gl=abs(sum(r["realized_r"] for r in losses))
    eq=peak=dd=0.0
    for r in decisive:
        eq+=r["realized_r"]; peak=max(peak,eq); dd=max(dd,peak-eq)
    return {
        "signals":len(rows),"decisive":len(decisive),"wins":len(wins),"losses":len(losses),
        "ambiguous":sum(r["result"]=="AMBIGUOUS" for r in rows),
        "open_or_unresolved":sum(r["result"]=="OPEN_OR_UNRESOLVED" for r in rows),
        "win_rate_decisive_pct":len(wins)/len(decisive)*100 if decisive else None,
        "gross_profit_R":gp,"gross_loss_R_abs":gl,"net_R":net,
        "profit_factor":gp/gl if gl else None,"max_drawdown_R":dd,
        "avg_win_R":gp/len(wins) if wins else None,
        "avg_loss_R_abs":gl/len(losses) if losses else None
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candle-evidence",default="artifacts/SP2L_candle_level_evidence_2026-09-14_2026-09-18.json")
    ap.add_argument("--rr",nargs="+",type=float,default=[1.0,2.0,3.0])
    ap.add_argument("--output",default="artifacts/SP2L_rr_sensitivity_1R_2R_3R_2026-09-14_2026-09-18.json")
    args=ap.parse_args()
    cp=Path(args.candle_evidence); evidence=json.loads(cp.read_text(encoding="utf-8"))
    variants=[]
    for rr in args.rr:
        rows=[]
        for m in evidence["signal_mappings"]:
            r,result,realized,tp=simulate(m,evidence["candles"],rr)
            rows.append({"archived_signal_index":m["archived_signal_index"],"signal_time_utc":m["signal_time_utc"],
                         "direction":m["direction"],"entry":float(m["entry"]),"sl":float(m["sl"]),
                         "risk_price_units":abs(float(m["entry"])-float(m["sl"])),"rr":r,"tp":tp,
                         "result":result,"realized_r":realized})
        variants.append({"rr":rr,"summary":summarize(rows),"trades":rows})
    result={"research_only":True,"experiment":"RR_SENSITIVITY_1R_2R_3R",
            "canonicalization_guard":"RESEARCH_ONLY; NO_STRATEGY_RULE_OR_PARAMETER_PROMOTION",
            "method":{"entry_policy":"ARCHIVED_ENTRY_UNCHANGED","sl_policy":"ARCHIVED_SL_UNCHANGED",
                      "tp_policy":"ENTRY_PLUS_R_MULTIPLE","trailing":"NONE",
                      "same_bar_policy":"AMBIGUOUS_WHEN_SL_AND_TP_BOTH_TOUCHED",
                      "intrabar_order":"NOT_INFERRED_FROM_M1_OHLC"},
            "frozen_window_utc":"2026-09-14T00:00:00Z/2026-09-18T23:59:59Z",
            "input_sha256":sha256_file(cp),"variants":variants}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({"status":"ANALYZED","output":str(out),"input_sha256":result["input_sha256"],
                      "variants":[{"rr":v["rr"],**v["summary"]} for v in variants]},indent=2))
if __name__=="__main__": main()
