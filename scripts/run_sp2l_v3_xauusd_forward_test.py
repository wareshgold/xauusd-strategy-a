"""SP2L V3 XAUUSD Demo forward runner: frozen V2 geometry + research Trail 10.

Trailing is evaluated from the latest COMPLETED M1 bar, matching the V3
historical model. The initial TP remains fixed. Broker fills/exits are recorded
as observed facts; no canonical production decision is made here.
"""
from __future__ import annotations
import os
import MetaTrader5 as mt5
import sp2l_v3_config as cfg

os.environ["SP2L_SYMBOLS"]="XAUUSD"
os.environ["SP2L_P_GAP_PRICE"]=str(cfg.P_GAP_PRICE)
os.environ["SP2L_SPIKE_MULTIPLIER"]=str(cfg.SPIKE_MULTIPLIER)
os.environ["SP2L_MAX_SL_DISTANCE"]=str(cfg.MAX_SL_DISTANCE)
os.environ["SP2L_TP_R"]=str(cfg.TP_R)
os.environ["SP2L_VOLUME"]=str(cfg.VOLUME)
os.environ["MT5_FORWARD_ORDER_MODE"]=cfg.ORDER_MODE
os.environ["SP2L_PENDING_TTL_MINUTES"]=str(cfg.PENDING_TTL_MINUTES)
os.environ.setdefault("LIVE_TRADING_ENABLE","true")
os.environ.setdefault("ALLOW_REAL_EXECUTION","true")

import run_sp2l_author_replica_multi_symbol_forward_test as runner

runner.detect=cfg.detect
runner.find_first_entry=cfg.find_first_entry
runner.find_latest_candidate=cfg.find_latest_candidate
runner.EVENTS=runner.ARTIFACTS / "SP2L_V3_XAUUSD_TRAIL10_FORWARD_EVENTS.jsonl"
runner.STATE_FILE=runner.RUNTIME / "sp2l_v3_xauusd_trail10_forward_state.json"
runner.session_gate_status=lambda trigger_ts:(True,"V3_ALL_MARKET_HOURS")
_original_rates=runner.rates
runner.rates=lambda symbol,count=10:_original_rates(symbol,120)

_original_monitor=runner.monitor_position_lifecycle
def trail_positions(cfg_runtime,state):
    _original_monitor(cfg_runtime,state)
    symbol=cfg_runtime["symbol"]; magic=cfg_runtime["magic"]
    info=mt5.symbol_info(symbol)
    if info is None: return
    # Bar 0 is forming; bar 1 is the latest completed M1 candle.
    bars=mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 1, 1)
    if bars is None or len(bars)!=1: return
    b=bars[0]
    completed_bar_time=int(b["time"])
    high=float(b["high"]); low=float(b["low"])
    positions=mt5.positions_get(symbol=symbol) or []
    for p in positions:
        if int(getattr(p,"magic",0) or 0)!=magic: continue
        entry=float(getattr(p,"price_open",0) or 0)
        old_sl=float(getattr(p,"sl",0) or 0)
        tp=float(getattr(p,"tp",0) or 0)
        if entry<=0: continue
        if int(p.type)==mt5.POSITION_TYPE_BUY:
            favorable=high-entry
            if favorable < cfg.TRAIL_DISTANCE_PRICE: continue
            new_sl=cfg.trail_stop("BUY",high)
            if new_sl<=old_sl or new_sl>=high: continue
            direction="BUY"
        else:
            favorable=entry-low
            if favorable < cfg.TRAIL_DISTANCE_PRICE: continue
            new_sl=cfg.trail_stop("SELL",low)
            if old_sl>0 and new_sl>=old_sl: continue
            if new_sl<=low: continue
            direction="SELL"
        request={"action":mt5.TRADE_ACTION_SLTP,"symbol":symbol,
                 "position":int(p.ticket),"sl":float(new_sl),"tp":tp}
        send=mt5.order_send(request)
        ok=bool(send and send.retcode==mt5.TRADE_RETCODE_DONE)
        runner.log_event({
            "event":"TRAIL_UPDATE","version":cfg.VERSION,"symbol":symbol,
            "position":int(p.ticket),"direction":direction,
            "completed_bar_time":completed_bar_time,
            "bar_high":high,"bar_low":low,"entry":entry,
            "old_sl":old_sl,"new_sl":float(new_sl),"tp":tp,
            "trail_pips":cfg.TRAIL_PIPS,
            "trail_distance_price":cfg.TRAIL_DISTANCE_PRICE,
            "success":ok,"retcode":int(send.retcode) if send else None,
            "comment":str(send.comment) if send else None,"canonical":False})
runner.monitor_position_lifecycle=trail_positions

if __name__=="__main__":
    runner.main()
