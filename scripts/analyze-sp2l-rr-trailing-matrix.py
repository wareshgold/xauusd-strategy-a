#!/usr/bin/env python3
"""Research-only 3x4 R:R x trailing-SL sensitivity matrix.

Frozen candle evidence; Entry/initial SL unchanged. TP is reconstructed at
1R/2R/3R. Trailing SL is M1-safe: favorable extreme in candle N updates the
SL only for candle N+1. Same-candle SL+TP touch is AMBIGUOUS. No TP extension.
No canonical rule/parameter promotion.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

PIP_SIZE = 0.10

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def simulate(mapping, candles, rr, trail_pips):
    entry=float(mapping["entry"])
    initial_sl=float(mapping["sl"])
    direction=mapping["direction"]
    risk=abs(entry-initial_sl)
    tp=entry + rr*risk if direction=="BUY" else entry - rr*risk
    trail=trail_pips*PIP_SIZE
    current_sl=initial_sl
    best=entry
    active=False
    i=int(mapping["outcome_scan_start_index"])

    while i < len(candles):
        c=candles[i]
        high=float(c["high"]); low=float(c["low"])

        if direction=="BUY":
            sl_hit=low<=current_sl
            tp_hit=high>=tp
            if sl_hit and tp_hit:
                return {
                    "result":"AMBIGUOUS","realized_r":None,
                    "exit_price":None,"final_sl":current_sl,
                    "trailing_activated":active,"reason":"SL_AND_TP_SAME_BAR","tp":tp
                }
            if sl_hit:
                realized=(current_sl-entry)/risk
                return {
                    "result":"WIN" if realized>0 else ("LOSS" if realized<0 else "BREAKEVEN"),
                    "realized_r":realized,"exit_price":current_sl,
                    "final_sl":current_sl,"trailing_activated":active,
                    "reason":"TRAIL_SL" if active and current_sl>initial_sl else "SL","tp":tp
                }
            if tp_hit:
                return {
                    "result":"WIN","realized_r":rr,"exit_price":tp,
                    "final_sl":current_sl,"trailing_activated":active,
                    "reason":"TP","tp":tp
                }
            best=max(best,high)
            if not active and best>=entry+trail:
                active=True
            if active:
                current_sl=max(current_sl,best-trail)
        else:
            sl_hit=high>=current_sl
            tp_hit=low<=tp
            if sl_hit and tp_hit:
                return {
                    "result":"AMBIGUOUS","realized_r":None,
                    "exit_price":None,"final_sl":current_sl,
                    "trailing_activated":active,"reason":"SL_AND_TP_SAME_BAR","tp":tp
                }
            if sl_hit:
                realized=(entry-current_sl)/risk
                return {
                    "result":"WIN" if realized>0 else ("LOSS" if realized<0 else "BREAKEVEN"),
                    "realized_r":realized,"exit_price":current_sl,
                    "final_sl":current_sl,"trailing_activated":active,
                    "reason":"TRAIL_SL" if active and current_sl<initial_sl else "SL","tp":tp
                }
            if tp_hit:
                return {
                    "result":"WIN","realized_r":rr,"exit_price":tp,
                    "final_sl":current_sl,"trailing_activated":active,
                    "reason":"TP","tp":tp
                }
            best=min(best,low)
            if not active and best<=entry-trail:
                active=True
            if active:
                current_sl=min(current_sl,best+trail)
        i+=1

    return {
        "result":"OPEN_OR_UNRESOLVED","realized_r":None,"exit_price":None,
        "final_sl":current_sl,"trailing_activated":active,
        "reason":"OPEN_OR_UNRESOLVED","tp":tp
    }

def summarize(rows):
    decisive=[r for r in rows if r["result"] in ("WIN","LOSS","BREAKEVEN")]
    wins=[r for r in decisive if r["result"]=="WIN"]
    losses=[r for r in decisive if r["result"]=="LOSS"]
    gp=sum(r["realized_r"] for r in wins)
    gl=abs(sum(r["realized_r"] for r in losses))
    net=sum(r["realized_r"] for r in decisive)
    equity=peak=dd=0.0
    for r in rows:
        if r["realized_r"] is None: continue
        equity+=r["realized_r"]; peak=max(peak,equity); dd=max(dd,peak-equity)
    return {
        "signals":len(rows),
        "decisive":len(decisive),
        "wins":len(wins),
        "losses":len(losses),
        "breakeven":sum(r["result"]=="BREAKEVEN" for r in rows),
        "ambiguous":sum(r["result"]=="AMBIGUOUS" for r in rows),
        "open_or_unresolved":sum(r["result"]=="OPEN_OR_UNRESOLVED" for r in rows),
        "win_rate_decisive_pct":len(wins)/len(decisive)*100 if decisive else None,
        "gross_profit_R":gp,
        "gross_loss_R_abs":gl,
        "net_R":net,
        "profit_factor":gp/gl if gl else None,
        "max_drawdown_R":dd,
        "avg_win_R":gp/len(wins) if wins else None,
        "avg_loss_R_abs":gl/len(losses) if losses else None,
        "trailing_activated_count":sum(r["trailing_activated"] for r in rows)
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candle-evidence",default="artifacts/SP2L_candle_level_evidence_2026-09-14_2026-09-18.json")
    ap.add_argument("--rr",nargs="+",type=float,default=[1.0,2.0,3.0])
    ap.add_argument("--trail-pips",nargs="+",type=float,default=[5.0,10.0,15.0,20.0])
    ap.add_argument("--output",default="artifacts/SP2L_rr_trailing_3x4_matrix_2026-09-14_2026-09-18.json")
    args=ap.parse_args()

    cp=Path(args.candle_evidence)
    evidence=json.loads(cp.read_text(encoding="utf-8"))
    variants=[]
    for rr in args.rr:
        for trail in args.trail_pips:
            trades=[]
            for m in evidence["signal_mappings"]:
                sim=simulate(m,evidence["candles"],rr,trail)
                trades.append({
                    "archived_signal_index":m["archived_signal_index"],
                    "signal_time_utc":m["signal_time_utc"],
                    "direction":m["direction"],
                    "entry":float(m["entry"]),
                    "initial_sl":float(m["sl"]),
                    "rr":rr,"trail_pips":trail,**sim
                })
            variants.append({"rr":rr,"trail_pips":trail,
                             "summary":summarize(trades),"trades":trades})

    result={
        "research_only":True,
        "experiment":"RR_X_TRAILING_SL_3X4_MATRIX",
        "canonicalization_guard":"RESEARCH_ONLY; NO_STRATEGY_RULE_OR_PARAMETER_PROMOTION",
        "frozen_window_utc":"2026-09-14T00:00:00Z/2026-09-18T23:59:59Z",
        "method":{
            "entry_policy":"ARCHIVED_ENTRY_UNCHANGED",
            "initial_sl_policy":"ARCHIVED_SL_UNCHANGED",
            "tp_policy":"ENTRY_PLUS_R_MULTIPLE",
            "rr_values":args.rr,
            "trailing_values_pips":args.trail_pips,
            "trailing_policy":"FAVORABLE_EXTREME_UPDATES_SL_FOR_NEXT_CANDLE_ONLY",
            "same_bar_policy":"AMBIGUOUS_WHEN_SL_AND_TP_BOTH_TOUCHED",
            "intrabar_order":"NOT_INFERRED_FROM_M1_OHLC",
            "tp_extension":"NOT_SIMULATED"
        },
        "input_sha256":sha256_file(cp),
        "variants":variants
    }
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({
        "status":"ANALYZED","output":str(out),
        "input_sha256":result["input_sha256"],
        "variants":[{"rr":v["rr"],"trail_pips":v["trail_pips"],**v["summary"]} for v in variants]
    },indent=2))

if __name__=="__main__":
    main()
