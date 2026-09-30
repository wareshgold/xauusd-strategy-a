#!/usr/bin/env python3
"""Deterministic forensic mapping: MT5 V2 forward positions -> forward signals -> V2 backtest.

Diagnostic only. No strategy/canonical logic is changed.
"""
from __future__ import annotations
import argparse, json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

def load_jsonl(path):
    with Path(path).open("r", encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]

def iso(ts):
    return None if ts is None else datetime.fromtimestamp(int(ts), timezone.utc).isoformat()

def signal_ts(sid):
    try: return int(sid.split(":")[-2])
    except (AttributeError, ValueError, IndexError): return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--history",required=True); ap.add_argument("--forward",required=True)
    ap.add_argument("--backtest",required=True); ap.add_argument("--magic",type=int,default=26092201)
    ap.add_argument("--run-start",required=True); ap.add_argument("--output",required=True)
    a=ap.parse_args()
    history=json.loads(Path(a.history).read_text(encoding="utf-8"))
    events=load_jsonl(a.forward)
    backtest=json.loads(Path(a.backtest).read_text(encoding="utf-8"))
    run_start=datetime.fromisoformat(a.run_start.replace("Z","+00:00")).timestamp()

    # PRIMARY JOIN: Forward lifecycle carries the real MT5 position id AND signal_id.
    # This is deterministic and does not assume signal time == fill time.
    by_position=defaultdict(list)
    by_signal={}
    for e in events:
        if e.get("symbol")!="XAUUSD.ecn": continue
        sid=e.get("signal_id")
        pos=e.get("position")
        if sid and signal_ts(sid) is not None and signal_ts(sid)>=run_start:
            by_signal[sid]=e
        if pos is not None and sid and signal_ts(sid) is not None and signal_ts(sid)>=run_start:
            by_position[int(pos)].append(e)

    deals=[d for d in history.get("deals",[])
           if d.get("symbol")=="XAUUSD.ecn" and d.get("magic")==a.magic
           and int(d.get("time_msc",d.get("time",0)*1000))/1000>=run_start]
    positions=defaultdict(list)
    for d in deals: positions[int(d["position_id"])].append(d)

    bt_rows=backtest.get("outcomes",{}).get("signals_detail",[])

    results=[]
    for pid,ds in sorted(positions.items()):
        entries=[d for d in ds if d.get("entry")==0]
        exits=[d for d in ds if d.get("entry")==1]
        if not entries: continue
        entry=min(entries,key=lambda x:x.get("time_msc",x.get("time",0)*1000))
        exit_=max(exits,key=lambda x:x.get("time_msc",x.get("time",0)*1000)) if exits else None
        fe=by_position.get(pid,[])
        sids=sorted({e.get("signal_id") for e in fe if e.get("signal_id")})
        sid=sids[0] if len(sids)==1 else None
        sig=by_signal.get(sid) if sid else None
        direction="BUY" if int(entry.get("type",0))==0 else "SELL"

        # Backtest comparison is deliberately NOT fuzzy. First try exact signal/setup
        # timestamps against backtest setup_time; then exact theoretical entry price
        # plus direction. Any remaining ambiguity is reported, not guessed.
        bt_candidates=[]
        if sid:
            st=signal_ts(sid)
            bt_candidates=[r for r in bt_rows if r.get("direction")==direction and
                           (r.get("setup_time")==st or r.get("entry_time")==st)]
        if not bt_candidates and sig and sig.get("theoretical_entry") is not None:
            p=float(sig["theoretical_entry"])
            bt_candidates=[r for r in bt_rows if r.get("direction")==direction and
                           r.get("entry") is not None and abs(float(r["entry"])-p)<1e-9]
        results.append({
            "position_id":pid,"forward_signal_ids":sids,
            "forward_signal_id":sid,
            "forward_events_count":len(fe),
            "forward_signal_event":sig,
            "mt5":{"entry_ticket":entry.get("ticket"),"entry_time_utc":iso(entry.get("time")),
                   "entry_price":entry.get("price"),"exit_ticket":exit_.get("ticket") if exit_ else None,
                   "exit_time_utc":iso(exit_.get("time")) if exit_ else None,
                   "exit_price":exit_.get("price") if exit_ else None,
                   "exit_reason":exit_.get("reason") if exit_ else None,
                   "profit":exit_.get("profit") if exit_ else None,
                   "commission":exit_.get("commission") if exit_ else None},
            "backtest_match_count":len(bt_candidates),
            "backtest_matches":bt_candidates[:10]
        })

    summary={"status":"COMPLETE","diagnostic_only":True,
             "run_start_utc":datetime.fromtimestamp(run_start,timezone.utc).isoformat(),
             "magic":a.magic,"mt5_positions_in_run":len(results),
             "matched_forward_positions":sum(bool(r["forward_signal_id"]) for r in results),
             "ambiguous_forward_positions":sum(len(r["forward_signal_ids"])>1 for r in results),
             "matched_backtest_positions":sum(r["backtest_match_count"]==1 for r in results),
             "ambiguous_backtest_positions":sum(r["backtest_match_count"]>1 for r in results),
             "unmatched_backtest_positions":[r["position_id"] for r in results if r["backtest_match_count"]==0],
             "positions":results}
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
    print(json.dumps({k:summary[k] for k in summary if k!="positions"},ensure_ascii=False,indent=2))
    print(f"SAVED: {out}")

if __name__=="__main__": main()
