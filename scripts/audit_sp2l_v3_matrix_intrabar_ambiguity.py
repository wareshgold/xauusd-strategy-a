#!/usr/bin/env python3
"""Offline M1 intrabar ambiguity audit for the exact historical 36-position SP2L V3 population.

This is a diagnostic, not a trade simulator. It computes no P/L, ranking, fills,
canonical rules, or BUY/SELL decisions. No MT5 package is imported or connected.
"""
from __future__ import annotations
import argparse, csv, json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

PIP = 0.01
EXPECTED_IDS = {
62458477,62466595,62472493,62479760,62483102,62486473,62488249,62491448,
62492610,62497786,62499705,62503253,62506281,62507768,62510782,62511473,
62512516,62516401,62516729,62518329,62521529,62540713,62546910,62552588,
62555855,62585649,62592622,62594268,62598298,62604959,62614431,62615799,
62618151,62623643,62624533,62625703}
RR_GRID=(1,2,4)
ACT_GRID=(0,2,4,6,8,10,20,30,40,50)
TRAIL_GRID=(2,4,6,8,10,12,20,30,40,50)
TWO_X_GRID=(False,True)

@dataclass(frozen=True)
class Trade:
    position_id:int
    direction:str
    entry:float
    initial_sl:float
    entry_time:int
    exit_time:int
    second_entry_price:float

@dataclass(frozen=True)
class Bar:
    time:int
    open:float
    high:float
    low:float
    close:float

def parse_timestamp(value:str)->int:
    raw=value.strip()
    try: return int(float(raw))
    except ValueError:
        dt=datetime.fromisoformat(raw.replace("Z","+00:00"))
        if dt.tzinfo is None: raise ValueError(f"Timestamp has no timezone: {value!r}")
        return int(dt.astimezone(timezone.utc).timestamp())

def load_trades(path:Path)->list[Trade]:
    required={"variant","position_id","direction","weighted_entry","final_sl","entry_time","exit_time","entry2_filled","total_entries"}
    selected={}
    with path.open("r",encoding="utf-8-sig",newline="") as fh:
        reader=csv.DictReader(fh)
        missing=required-set(reader.fieldnames or [])
        if missing: raise ValueError(f"Trade fixture missing columns: {sorted(missing)}")
        for row in reader:
            if row.get("variant")!="NO_TRAILING_RR1": continue
            pid=int(row["position_id"])
            if pid not in EXPECTED_IDS: continue
            if row["entry2_filled"].strip().lower()!="false": raise ValueError(f"{pid}: entry2_filled is not False")
            if row["total_entries"].strip()!="1": raise ValueError(f"{pid}: total_entries is not 1")
            direction=row["direction"].strip().upper()
            if direction not in {"BUY","SELL"}: raise ValueError(f"{pid}: invalid direction {direction!r}")
            entry=float(row["weighted_entry"]); sl=float(row["final_sl"])
            et=int(float(row["entry_time"])); xt=int(float(row["exit_time"]))
            if et<=0 or xt<et or entry==sl: raise ValueError(f"{pid}: invalid time or zero risk")
            risk=abs(entry-sl)
            e2p=entry-0.5*risk if direction=="BUY" else entry+0.5*risk
            if pid in selected: raise ValueError(f"Duplicate baseline row for {pid}")
            selected[pid]=Trade(pid,direction,entry,sl,et,xt,e2p)
    missing=EXPECTED_IDS-set(selected); extra=set(selected)-EXPECTED_IDS
    if missing or extra: raise ValueError(f"Whitelist mismatch; missing={sorted(missing)}, extra={sorted(extra)}")
    if len(selected)!=36: raise ValueError(f"Expected exactly 36 positions, found {len(selected)}")
    return sorted(selected.values(),key=lambda t:t.entry_time)

def load_bars(path:Path)->list[Bar]:
    required={"time","open","high","low","close"}; bars=[]
    with path.open("r",encoding="utf-8-sig",newline="") as fh:
        reader=csv.DictReader(fh); missing=required-set(reader.fieldnames or [])
        if missing: raise ValueError(f"M1 fixture missing columns: {sorted(missing)}")
        for row in reader:
            b=Bar(parse_timestamp(row["time"]),float(row["open"]),float(row["high"]),float(row["low"]),float(row["close"]))
            vals=(b.open,b.high,b.low,b.close)
            if not all(map(lambda x:x==x and abs(x)!=float("inf"),vals)): raise ValueError(f"Non-finite OHLC at {b.time}")
            if b.high<max(b.open,b.close,b.low) or b.low>min(b.open,b.close,b.high): raise ValueError(f"Invalid OHLC at {b.time}")
            bars.append(b)
    bars.sort(key=lambda b:b.time)
    times=[b.time for b in bars]
    if len(times)!=len(set(times)): raise ValueError("Duplicate M1 timestamps")
    if not bars: raise ValueError("M1 fixture is empty")
    return bars

def iso(ts):
    return "" if ts is None else datetime.fromtimestamp(ts,timezone.utc).isoformat()

def bars_for_trade(trade:Trade,bars:list[Bar]):
    # Mirrors legacy scan window only: entry minute excluded, exit minute included.
    em=trade.entry_time-trade.entry_time%60; xm=trade.exit_time-trade.exit_time%60
    chosen=[b for b in bars if em<b.time<=xm]
    expected=max(0,(xm-(em+60))//60+1)
    # Count missing expected minute bars, including gaps at either edge.
    missing=max(0,expected-len(chosen))
    return chosen,missing,any(b.time==em for b in bars),any(b.time==xm for b in bars)

def inspect_variant(t:Trade,bars:list[Bar],rr:int,act_pips:int,trail_pips:int,two_x:bool):
    risk=abs(t.entry-t.initial_sl)
    tp=t.entry+risk*rr if t.direction=="BUY" else t.entry-risk*rr
    sl=t.initial_sl; activation=act_pips*PIP; distance=trail_pips*PIP
    selected,gaps,entry_bar,exit_bar=bars_for_trade(t,bars)
    first_time=None; first_flags=set(); e2_time=None; act_time=None
    sltp_time=None; trail_same_time=None; e2_exit_time=None
    for b in selected:
        if t.direction=="BUY":
            tp_hit=b.high>=tp; old_sl_hit=b.low<=sl
            act_hit=trail_pips>0 and b.high-t.entry>=activation
            candidate_sl=max(sl,b.high-distance) if act_hit else sl
            trail_hit=act_hit and b.low<=candidate_sl
            e2_hit=two_x and b.low<=t.second_entry_price
        else:
            tp_hit=b.low<=tp; old_sl_hit=b.high>=sl
            act_hit=trail_pips>0 and t.entry-b.low>=activation
            candidate_sl=min(sl,b.low+distance) if act_hit else sl
            trail_hit=act_hit and b.high>=candidate_sl
            e2_hit=two_x and b.high>=t.second_entry_price
        if act_hit and act_time is None: act_time=b.time
        if e2_hit and e2_time is None: e2_time=b.time
        flags=set()
        if tp_hit: flags.add("TP_LEVEL_TOUCHED")
        if old_sl_hit: flags.add("PRE_UPDATE_SL_LEVEL_TOUCHED")
        if tp_hit and old_sl_hit:
            flags.add("SAME_BAR_TP_AND_PRE_UPDATE_SL")
            if sltp_time is None: sltp_time=b.time
        if act_hit: flags.add("TRAIL_ACTIVATION_LEVEL_TOUCHED")
        if trail_hit:
            flags.add("UPDATED_TRAIL_SL_TOUCHED_SAME_BAR")
            if trail_same_time is None: trail_same_time=b.time
        if e2_hit: flags.add("2X_LEVEL_TOUCHED")
        if e2_hit and (tp_hit or old_sl_hit or trail_hit):
            flags.add("2X_AND_EXIT_LEVEL_SAME_BAR")
            if e2_exit_time is None: e2_exit_time=b.time
        exit_flags=flags & {"TP_LEVEL_TOUCHED","PRE_UPDATE_SL_LEVEL_TOUCHED","UPDATED_TRAIL_SL_TOUCHED_SAME_BAR"}
        if exit_flags:
            first_time=b.time; first_flags=flags
            break
        # Legacy high/low stop update is mirrored solely to detect path ambiguity.
        if act_hit: sl=candidate_sl
    all_flags=set(first_flags)
    # Preserve a 2X level-touch observed before the first candidate exit, even
    # when it occurred on an earlier bar and is therefore absent from first_flags.
    # This is diagnostic only: it does not imply an order fill or position change.
    if e2_time is not None: all_flags.add("2X_LEVEL_TOUCHED")
    entry_partial=(t.entry_time%60)!=0
    exit_partial=(t.exit_time%60)!=0
    if gaps: all_flags.add("M1_GAP_IN_REPLAY_WINDOW")
    if not entry_bar: all_flags.add("ENTRY_MINUTE_BAR_MISSING")
    if not exit_bar: all_flags.add("EXIT_MINUTE_BAR_MISSING")
    if entry_partial: all_flags.add("ENTRY_MINUTE_PARTIAL_EXCLUDED")
    if exit_partial: all_flags.add("EXIT_MINUTE_PARTIAL_INCLUDED_AS_WHOLE_BAR")
    if first_time is None: all_flags.add("NO_EXIT_LEVEL_TOUCH_IN_OBSERVED_WINDOW")
    if {"SAME_BAR_TP_AND_PRE_UPDATE_SL","UPDATED_TRAIL_SL_TOUCHED_SAME_BAR","2X_AND_EXIT_LEVEL_SAME_BAR"} & all_flags:
        classification="AMBIGUOUS"
    elif {"M1_GAP_IN_REPLAY_WINDOW","ENTRY_MINUTE_BAR_MISSING","EXIT_MINUTE_BAR_MISSING"} & all_flags:
        classification="DATA_GAP_OR_COVERAGE_LIMIT"
    elif first_time is None: classification="NO_LEVEL_TOUCH_OBSERVED"
    else: classification="SINGLE_LEVEL_TOUCH_ORDER_NOT_PROVEN"
    return {
      "position_id":t.position_id,"direction":t.direction,"RR":rr,"ACT_PIPS":act_pips,"TRAIL_PIPS":trail_pips,"2X":"ON" if two_x else "OFF",
      "bars_inspected":len(selected),"missing_minutes":gaps,"entry_minute_bar_present":entry_bar,"exit_minute_bar_present":exit_bar,
      "entry_minute_partial":entry_partial,"exit_minute_partial":exit_partial,
      "first_candidate_bar_utc":iso(first_time),"first_candidate_flags":"|".join(sorted(first_flags)),
      "ambiguity_flags":"|".join(sorted(all_flags)),"classification":classification,
      "has_same_bar_tp_sl":sltp_time is not None,"has_trail_update_and_touch_same_bar":trail_same_time is not None,
      "has_2x_touch_before_first_candidate":e2_time is not None,"2x_touch_first_utc":iso(e2_time),
      "trail_activation_first_utc":iso(act_time),"first_same_bar_tp_sl_utc":iso(sltp_time),
      "first_trail_update_touch_utc":iso(trail_same_time),"first_2x_exit_collision_utc":iso(e2_exit_time)}

def build_report(trades,bars):
    rows=[]
    for t in trades:
      for rr in RR_GRID:
       for act in ACT_GRID:
        for trail in TRAIL_GRID:
         for two_x in TWO_X_GRID: rows.append(inspect_variant(t,bars,rr,act,trail,two_x))
    classes={}; flags={}
    for r in rows:
        classes[r["classification"]]=classes.get(r["classification"],0)+1
        for flag in filter(None,r["ambiguity_flags"].split("|")): flags[flag]=flags.get(flag,0)+1
    summary={
      "purpose":"OFFLINE_INTRABAR_AMBIGUITY_AUDIT_ONLY","research_only":True,"canonical":False,
      "trade_count":len(trades),"buy_count":sum(t.direction=="BUY" for t in trades),"sell_count":sum(t.direction=="SELL" for t in trades),
      "m1_bar_count":len(bars),"m1_first_utc":iso(bars[0].time),"m1_last_utc":iso(bars[-1].time),
      "variant_count":600,"audit_rows":len(rows),"classification_counts":classes,"ambiguity_flag_counts":flags,
      "execution_semantics":"NOT_MODELED","fees_and_slippage":"NOT_MODELED","pnl_or_performance_metrics":"NOT_COMPUTED",
      "intrabar_ordering":"UNRESOLVED_WHERE_MULTIPLE_LEVELS_TOUCH_WITHIN_ONE_M1_BAR",
      "entry_minute_policy":"EXCLUDED_TO_MIRROR_LEGACY_WINDOW; PARTIAL_MINUTE_NOT_RECONSTRUCTED",
      "exit_minute_policy":"WHOLE_EXIT_MINUTE_INCLUDED_FOR_DIAGNOSTIC_ONLY; POST_EXIT_TICKS_CANNOT_BE_SEPARATED",
      "two_x_policy":"LEVEL_TOUCH_ONLY; NO_FILL_OR_SIZE_OR_AVERAGE_PRICE_ASSUMED"}
    return rows,summary

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--trades",required=True,type=Path); ap.add_argument("--m1",required=True,type=Path); ap.add_argument("--out-dir",required=True,type=Path)
    args=ap.parse_args(); trades=load_trades(args.trades); bars=load_bars(args.m1); rows,summary=build_report(trades,bars)
    args.out_dir.mkdir(parents=True,exist_ok=True)
    csv_path=args.out_dir/"SP2L_V3_36_TRADE_INTRABAR_AUDIT.csv"
    json_path=args.out_dir/"SP2L_V3_36_TRADE_INTRABAR_AUDIT_SUMMARY.json"
    with csv_path.open("w",encoding="utf-8",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    json_path.write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print("AUDIT_ONLY=TRUE"); print(f"TRADES={summary['trade_count']} BUY={summary['buy_count']} SELL={summary['sell_count']}")
    print(f"M1_BARS={summary['m1_bar_count']}"); print(f"VARIANTS={summary['variant_count']} AUDIT_ROWS={summary['audit_rows']}")
    print("P_AND_L=NOT_COMPUTED"); print("MT5=NOT_IMPORTED_OR_CONNECTED"); print(f"CSV={csv_path}"); print(f"SUMMARY={json_path}")

if __name__=="__main__": main()
