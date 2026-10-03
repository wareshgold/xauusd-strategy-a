"""SP2L V3 XAUUSD Demo forward runner: frozen V2 geometry + research Trail 10.

Trailing is evaluated from the latest COMPLETED M1 bar, matching the V3
historical model. The initial TP remains fixed. Broker fills/exits are recorded
as observed facts; no canonical production decision is made here.
"""
from __future__ import annotations
import os
import time
from datetime import datetime, timezone
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
_original_find_latest_candidate=cfg.find_latest_candidate
# Forward-only freshness gate: never execute a candidate whose trigger candle
# completed before this process started. Historical replay belongs to backtests;
# live forward execution must wait for a newly formed setup after START.
# MT5 bar timestamps are in the broker/server clock. Convert START into the
# same timestamp basis before applying the forward-only freshness gate.
# This deliberately does not infer UTC from the broker clock.
_FORWARD_START_SERVER_TS = None

def _server_now_timestamp():
    tick = mt5.symbol_info_tick("XAUUSD.ecn")
    if tick is None or int(getattr(tick, "time", 0) or 0) <= 0:
        return None
    return int(tick.time)

def _init_forward_start_server_ts():
    global _FORWARD_START_SERVER_TS
    server_now = _server_now_timestamp()
    if server_now is None:
        return
    # The local wall clock and MT5 server clock are sampled at the same instant.
    # Store the server-clock equivalent of process START.
    _FORWARD_START_SERVER_TS = int(server_now - (time.time() - _FORWARD_START_EPOCH))

_FORWARD_START_EPOCH = time.time()
_init_forward_start_server_ts()

def _candidate_is_stale(candidate, watermark):
    """Return True when a candidate belongs to the pre-startup replay window."""
    if candidate is None or watermark is None:
        return False
    trigger_ts = int(candidate.get("trigger_time", 0) or 0)
    return trigger_ts <= int(watermark)


def _forward_find_latest_candidate(candles, symbol):
    candidate = _original_find_latest_candidate(candles, symbol)
    if candidate is None:
        return None

    # MT5 is initialized by runner.main(), so retry watermark initialization
    # lazily on the first post-initialize candidate scan.
    if _FORWARD_START_SERVER_TS is None:
        _init_forward_start_server_ts()

    # Fail closed: without a server-clock watermark, do not execute anything.
    if _FORWARD_START_SERVER_TS is None:
        runner.log_event({
            "event": "STARTUP_WATERMARK_UNAVAILABLE",
            "symbol": symbol,
            "executed": False,
            "reason": "MT5_SERVER_TICK_UNAVAILABLE",
            "canonical": False,
        })
        return None

    if _candidate_is_stale(candidate, _FORWARD_START_SERVER_TS):
        runner.log_event({
            "event": "STALE_STARTUP_CANDIDATE_BLOCKED",
            "symbol": symbol,
            "trigger_time": int(candidate.get("trigger_time", 0) or 0),
            "startup_watermark_server_ts": _FORWARD_START_SERVER_TS,
            "reason": "TRIGGER_AT_OR_BEFORE_FORWARD_START",
            "executed": False,
            "canonical": False,
        })
        return None
    return candidate
runner.find_latest_candidate=_forward_find_latest_candidate
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

    # V3 trailing is evaluated once per completed M1 bar per tracked position.
    # A broker-invalid candidate must never be retried every poll cycle.
    trail_seen = state.setdefault("trail_seen", {})

    # Bar 0 is forming; bar 1 is the latest completed M1 candle.
    bars=mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 1, 1)
    if bars is None or len(bars)!=1: return
    b=bars[0]
    completed_bar_time=int(b["time"])
    high=float(b["high"]); low=float(b["low"])

    tick=mt5.symbol_info_tick(symbol)
    if tick is None: return
    bid=float(getattr(tick,"bid",0.0) or 0.0)
    ask=float(getattr(tick,"ask",0.0) or 0.0)
    point=float(getattr(info,"point",0.0) or 0.0)
    stops_level_points=int(getattr(info,"trade_stops_level",0) or 0)
    min_stop_distance=stops_level_points*point

    positions=mt5.positions_get(symbol=symbol) or []
    for p in positions:
        if int(getattr(p,"magic",0) or 0)!=magic: continue
        ticket=int(getattr(p,"ticket",0) or 0)
        entry=float(getattr(p,"price_open",0) or 0)
        old_sl=float(getattr(p,"sl",0) or 0)
        tp=float(getattr(p,"tp",0) or 0)
        if ticket<=0 or entry<=0: continue

        # Hard de-duplication: one trail decision per position per completed bar.
        seen_key=f"{ticket}:{completed_bar_time}"
        if seen_key in trail_seen:
            continue

        if int(p.type)==mt5.POSITION_TYPE_BUY:
            favorable=high-entry
            if favorable < cfg.TRAIL_DISTANCE_PRICE: continue
            new_sl=cfg.trail_stop("BUY",high)
            if new_sl<=old_sl or new_sl>=high: continue
            # BUY SL must remain below the current Bid and broker stop level.
            max_valid_sl=bid-min_stop_distance
            if new_sl >= max_valid_sl:
                trail_seen[seen_key]={"status":"SKIPPED_INVALID_STOPS","new_sl":float(new_sl)}
                runner.log_event({
                    "event":"TRAIL_SKIP","version":cfg.VERSION,"symbol":symbol,
                    "position":ticket,"direction":"BUY",
                    "completed_bar_time":completed_bar_time,
                    "bar_high":high,"bar_low":low,"entry":entry,
                    "old_sl":old_sl,"proposed_sl":float(new_sl),
                    "bid":bid,"ask":ask,"min_stop_distance":min_stop_distance,
                    "reason":"BROKER_STOP_CONSTRAINT","canonical":False})
                continue
            direction="BUY"
        else:
            favorable=entry-low
            if favorable < cfg.TRAIL_DISTANCE_PRICE: continue
            new_sl=cfg.trail_stop("SELL",low)
            if old_sl>0 and new_sl>=old_sl: continue
            if new_sl<=low: continue
            # SELL SL must remain above the current Ask and broker stop level.
            min_valid_sl=ask+min_stop_distance
            if new_sl <= min_valid_sl:
                trail_seen[seen_key]={"status":"SKIPPED_INVALID_STOPS","new_sl":float(new_sl)}
                runner.log_event({
                    "event":"TRAIL_SKIP","version":cfg.VERSION,"symbol":symbol,
                    "position":ticket,"direction":"SELL",
                    "completed_bar_time":completed_bar_time,
                    "bar_high":high,"bar_low":low,"entry":entry,
                    "old_sl":old_sl,"proposed_sl":float(new_sl),
                    "bid":bid,"ask":ask,"min_stop_distance":min_stop_distance,
                    "reason":"BROKER_STOP_CONSTRAINT","canonical":False})
                continue
            direction="SELL"

        request={"action":mt5.TRADE_ACTION_SLTP,"symbol":symbol,
                 "position":ticket,"sl":float(new_sl),"tp":tp}
        send=mt5.order_send(request)
        ok=bool(send and send.retcode==mt5.TRADE_RETCODE_DONE)

        # Regardless of success/failure, consume this position/bar attempt.
        # A failed broker modification must wait for the next completed bar.
        trail_seen[seen_key]={
            "status":"UPDATED" if ok else "FAILED",
            "new_sl":float(new_sl),
            "retcode":int(send.retcode) if send else None,
        }

        runner.log_event({
            "event":"TRAIL_UPDATE","version":cfg.VERSION,"symbol":symbol,
            "position":ticket,"direction":direction,
            "completed_bar_time":completed_bar_time,
            "bar_high":high,"bar_low":low,"entry":entry,
            "old_sl":old_sl,"new_sl":float(new_sl),"tp":tp,
            "trail_pips":cfg.TRAIL_PIPS,
            "trail_distance_price":cfg.TRAIL_DISTANCE_PRICE,
            "success":ok,"retcode":int(send.retcode) if send else None,
            "comment":str(send.comment) if send else None,"canonical":False})

runner.monitor_position_lifecycle=trail_positions

# V3 RUN-ISOLATION: never replay pre-existing broker history into Telegram or
# Forward-Test statistics. Only broker objects created/tracked by THIS process
# are eligible for lifecycle reporting/cancellation.
from datetime import datetime, timezone
_RUN_STARTED_UTC = datetime.now(timezone.utc)
_original_main = runner.main
_original_enforce_pending_order_expiry = runner.enforce_pending_order_expiry

def _fresh_v3_state():
    return {"seen": {}, "notified": set(), "deals": set(), "orders": set(),
            "positions": set(), "order_states": set(), "position_orders": {},
            "signal_orders": {}, "pending_signal_notifications": {}}

def _run_scoped_pending(cfg_runtime, state):
    # Reuse the base runner's TTL guard. The previous V3 override cancelled
    # every tracked pending order on every poll, ignoring PENDING_TTL_MINUTES.
    # The base implementation already scopes expiry to this runner's tracked
    # orders and uses the monotonic creation timestamp, so there is no wall-clock
    # or broker-server timezone ambiguity.
    _original_enforce_pending_order_expiry(cfg_runtime, state)

def _run_scoped_pending_lifecycle(cfg_runtime, state):
    symbol = cfg_runtime["symbol"]
    tracked = set(state["orders"])
    orders = (mt5.history_orders_get(_RUN_STARTED_UTC, datetime.now(timezone.utc), group=symbol) or [])
    orders += list(mt5.orders_get(symbol=symbol) or [])
    for order in orders:
        ticket = int(getattr(order, "ticket", 0) or 0)
        if ticket not in tracked:
            continue
        state_name = runner.order_state_name(order)
        marker = f"{ticket}:{state_name}"
        if marker in state["order_states"]:
            continue
        state["order_states"].add(marker)
        runner.log_event({
            "event":"PENDING_ORDER_LIFECYCLE","version":cfg.VERSION,
            "symbol":symbol,"order":ticket,"state":state_name,
            "state_code":int(getattr(order,"state",-1)),
            "type":int(getattr(order,"type",-1)),
            "time_setup":int(getattr(order,"time_setup",0) or 0),
            "time_done":int(getattr(order,"time_done",0) or 0),
            "magic":int(getattr(order,"magic",0) or 0),
            "position_id":int(getattr(order,"position_id",0) or 0),
            "volume_initial":float(getattr(order,"volume_initial",0.0) or 0.0),
            "volume_current":float(getattr(order,"volume_current",0.0) or 0.0),
            "price_open":float(getattr(order,"price_open",0.0) or 0.0),
            "price_current":float(getattr(order,"price_current",0.0) or 0.0),
            "sl":float(getattr(order,"sl",0.0) or 0.0),
            "tp":float(getattr(order,"tp",0.0) or 0.0),
            "canonical":False})

def _run_scoped_position_lifecycle(cfg_runtime, state):
    symbol, magic = cfg_runtime["symbol"], cfg_runtime["magic"]
    for position in (mt5.positions_get(symbol=symbol) or []):
        position_id = int(getattr(position,"ticket",0) or 0)
        if position_id not in state["positions"] or int(getattr(position,"magic",0) or 0) != magic:
            continue
        marker=f"POSITION:{position_id}:{float(getattr(position,'sl',0.0) or 0.0)}:{float(getattr(position,'tp',0.0) or 0.0)}"
        if marker in state["order_states"]:
            continue
        state["order_states"].add(marker)
        runner.log_event({
            "event":"POSITION_LIFECYCLE","version":cfg.VERSION,"symbol":symbol,
            "position":position_id,"magic":magic,
            "type":int(getattr(position,"type",-1)),
            "volume":float(getattr(position,"volume",0.0) or 0.0),
            "price_open":float(getattr(position,"price_open",0.0) or 0.0),
            "price_current":float(getattr(position,"price_current",0.0) or 0.0),
            "sl":float(getattr(position,"sl",0.0) or 0.0),
            "tp":float(getattr(position,"tp",0.0) or 0.0),
            "profit":float(getattr(position,"profit",0.0) or 0.0),
            "canonical":False})

def _run_scoped_symbol_lifecycle(cfg_runtime, state):
    symbol, magic, pip = cfg_runtime["symbol"], cfg_runtime["magic"], cfg_runtime["pip_size"]
    tracked_orders, tracked_positions = set(state["orders"]), set(state["positions"])
    if not tracked_orders and not tracked_positions:
        return
    deals = mt5.history_deals_get(_RUN_STARTED_UTC, datetime.now(timezone.utc), group=symbol) or []
    for deal in sorted(deals, key=lambda x:(int(x.time), int(x.ticket))):
        ticket=int(deal.ticket)
        if ticket in state["deals"]:
            continue
        order=int(getattr(deal,"order",0) or 0)
        position=int(getattr(deal,"position_id",0) or 0)
        if order not in tracked_orders and position not in tracked_positions:
            continue
        runner._remember_position_links(state, deal)
        is_entry = int(getattr(deal,"entry",-1)) == mt5.DEAL_ENTRY_IN
        entry_price=float(deal.price) if is_entry else runner.position_entry_price(deal, magic)
        if not is_entry and entry_price is None:
            continue
        execution_meta={}
        for linked_order in state.get("position_orders",{}).get(str(position),set()):
            execution_meta=state.get("signal_orders",{}).get(str(linked_order),{})
            if execution_meta: break
        tg=runner.gateway.send_telegram_message(
            runner.lifecycle_message(deal,symbol,pip,magic), parse_mode="HTML")
        profit=float(getattr(deal,"profit",0.0) or 0.0)
        commission=float(getattr(deal,"commission",0.0) or 0.0)
        swap=float(getattr(deal,"swap",0.0) or 0.0)
        runner.log_event({
            "event":"TELEGRAM_DEAL_LIFECYCLE","version":cfg.VERSION,
            "symbol":symbol,"deal":ticket,"order":order,"position":position,
            "signal_id":execution_meta.get("signal_id"),
            "entry":int(getattr(deal,"entry",-1)),
            "reason":int(getattr(deal,"reason",-1)),
            "entry_price":entry_price,
            "theoretical_entry":execution_meta.get("theoretical_entry"),
            "theoretical_sl":execution_meta.get("sl"),
            "theoretical_tp":execution_meta.get("tp"),
            "exit_price":float(deal.price),"profit":profit,
            "commission":commission,"swap":swap,"net":profit+commission+swap,
            "telegram":{"success":bool(getattr(tg,"success",False)),"detail":getattr(tg,"detail",None)},
            "canonical":False})
        if getattr(tg,"success",False):
            state["deals"].add(ticket)

runner.enforce_pending_order_expiry=_run_scoped_pending
runner.monitor_pending_order_lifecycle=_run_scoped_pending_lifecycle
runner.monitor_position_lifecycle=trail_positions
runner.monitor_symbol_lifecycle=_run_scoped_symbol_lifecycle

def _v3_main():
    # Every V3 start gets a clean session ledger. Existing broker
    # orders/positions are never attributed to this run.
    original_load, original_reconcile = runner.load_state, runner.reconcile_state_from_events
    runner.load_state, runner.reconcile_state_from_events = _fresh_v3_state, lambda state: None
    try:
        _original_main()
    finally:
        runner.load_state, runner.reconcile_state_from_events = original_load, original_reconcile

runner.main=_v3_main

if __name__=="__main__":
    runner.main()
