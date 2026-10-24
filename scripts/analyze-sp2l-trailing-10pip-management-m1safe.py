#!/usr/bin/env python3
"""Research-only M1-safe 10-pip trailing-SL experiment.

Initial TP stays fixed. A candle's favorable extreme updates the trailing
SL only for the NEXT candle. If SL and TP are both touched in one M1 candle,
the result is AMBIGUOUS. TP extension is not inferred from M1 OHLC because
intrabar ordering is required.
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

def simulate(mapping, candles, trail_pips):
    entry=float(mapping["entry"]); initial_sl=float(mapping["sl"])
    initial_tp=float(mapping["tp"]); direction=mapping["direction"]
    i=int(mapping["outcome_scan_start_index"]); trail=trail_pips*PIP_SIZE
    current_sl=initial_sl; best=entry; active=False; exit_price=None
    reason=None; ambiguous=False; max_fav=0.0; min_adv=0.0
    while i < len(candles):
        c=candles[i]; high=float(c["high"]); low=float(c["low"])
        if direction=="BUY":
            sl_hit=low<=current_sl; tp_hit=high>=initial_tp
            if sl_hit and tp_hit:
                ambiguous=True; reason="SL_AND_TP_SAME_BAR"; break
            if sl_hit:
                reason="TRAIL_SL" if active and current_sl>initial_sl else "SL"
                exit_price=current_sl; break
            if tp_hit:
                reason="TP"; exit_price=initial_tp; break
            best=max(best,high)
            max_fav=max(max_fav,(best-entry)/PIP_SIZE)
            min_adv=min(min_adv,(low-entry)/PIP_SIZE)
            if not active and best>=entry+trail: active=True
            if active: current_sl=max(current_sl,best-trail)
        else:
            sl_hit=high>=current_sl; tp_hit=low<=initial_tp
            if sl_hit and tp_hit:
                ambiguous=True; reason="SL_AND_TP_SAME_BAR"; break
            if sl_hit:
                reason="TRAIL_SL" if active and current_sl<initial_sl else "SL"
                exit_price=current_sl; break
            if tp_hit:
                reason="TP"; exit_price=initial_tp; break
            best=min(best,low)
            max_fav=max(max_fav,(entry-best)/PIP_SIZE)
            min_adv=min(min_adv,(entry-high)/PIP_SIZE)
            if not active and best<=entry-trail: active=True
            if active: current_sl=min(current_sl,best+trail)
        i+=1
    if exit_price is None and not ambiguous: reason="OPEN_OR_UNRESOLVED"
    realized=None if exit_price is None else ((exit_price-entry)/PIP_SIZE if direction=="BUY" else (entry-exit_price)/PIP_SIZE)
    return {
        "archived_signal_index":mapping["archived_signal_index"],
        "signal_time_utc":mapping["signal_time_utc"],"direction":direction,
        "entry":entry,"initial_sl":initial_sl,"initial_tp":initial_tp,
        "trail_pips":trail_pips,"final_sl":current_sl,
        "trailing_activated":active,"max_favorable_pips":max_fav,
        "min_adverse_pips":min_adv,"exit_price":exit_price,
        "reason":reason,"ambiguous":ambiguous,"realized_pips":realized}

def summarize(rows):
    decisive=[r for r in rows if r["realized_pips"] is not None and not r["ambiguous"]]
    wins=[r for r in decisive if r["realized_pips"]>0]
    losses=[r for r in decisive if r["realized_pips"]<0]
    gp=sum(r["realized_pips"] for r in wins); gl=abs(sum(r["realized_pips"] for r in losses))
    equity=peak=dd=0.0
    for r in rows:
        if r["realized_pips"] is None: continue
        equity+=r["realized_pips"]; peak=max(peak,equity); dd=max(dd,peak-equity)
    return {
        "signals":len(rows),"decisive":len(decisive),"wins":len(wins),
        "losses":len(losses),"breakeven":sum(r["realized_pips"]==0 for r in decisive),
        "ambiguous":sum(r["ambiguous"] for r in rows),
        "open_or_unresolved":sum(r["reason"]=="OPEN_OR_UNRESOLVED" for r in rows),
        "win_rate_decisive_pct":len(wins)/len(decisive)*100 if decisive else None,
        "gross_profit_pips":gp,"gross_loss_pips_abs":gl,"net_pips":sum(r["realized_pips"] for r in decisive),
        "profit_factor":gp/gl if gl else None,"max_drawdown_pips":dd,
        "avg_win_pips":gp/len(wins) if wins else None,
        "avg_loss_pips_abs":gl/len(losses) if losses else None,
        "trailing_activated_count":sum(r["trailing_activated"] for r in rows)
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candle-evidence",default="artifacts/SP2L_candle_level_evidence_2026-09-14_2026-09-18.json")
    ap.add_argument("--trail-pips",type=float,default=10.0)
    ap.add_argument("--output",default="artifacts/SP2L_trailing_10pip_m1safe_2026-09-14_2026-09-18.json")
    args=ap.parse_args()
    cp=Path(args.candle_evidence); out=Path(args.output)
    evidence=json.loads(cp.read_text(encoding="utf-8"))
    rows=[simulate(m,evidence["candles"],args.trail_pips) for m in evidence["signal_mappings"]]
    result={
        "research_only":True,
        "experiment":"10_PIP_TRAILING_SL_M1_SAFE_FIXED_TP",
        "canonicalization_guard":"RESEARCH_ONLY; NO_STRATEGY_RULE_OR_PARAMETER_PROMOTION",
        "interpretation":{
            "pip_size_price_units":PIP_SIZE,"trail_pips":args.trail_pips,
            "tp_policy":"FIXED_INITIAL_TP",
            "tp_extension":"NOT_SIMULATED_FROM_M1_OHLC; REQUIRES_INTRABAR_ORDER",
            "same_bar_policy":"AMBIGUOUS_WHEN_SL_AND_TP_BOTH_TOUCHED"
        },
        "input_sha256":sha256_file(cp),
        "summary":summarize(rows),"trades":rows
    }
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({"status":"ANALYZED","output":str(out),"summary":result["summary"],"input_sha256":result["input_sha256"]},indent=2))

if __name__=="__main__":
    main()
