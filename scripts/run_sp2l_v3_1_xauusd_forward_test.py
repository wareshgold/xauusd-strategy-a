"""SP2L V3.1 XAUUSD Demo forward runner: research RR4 / ACT40 / DIST40.

Trailing is evaluated from the latest COMPLETED M1 bar, matching the V3
historical model. The initial TP remains fixed. Broker fills/exits are recorded
as observed facts; no canonical production decision is made here.
"""
from __future__ import annotations
import os
import time
from datetime import timedelta
from sp2l_trailing_rules import (
    normalize_trailing_sl,
    trailing_sl_is_placeable,
    should_retry_trailing,
)
from sp2l_trailing_state import (
    load_trailing_state,
    save_trailing_state,
    update_favorable_extreme,
    favorable_move,
    trailing_activation_reached,
    trailing_record_matches,
)
import MetaTrader5 as mt5
import sp2l_v3_1_rr4_act40_config as cfg

os.environ["SP2L_SYMBOLS"]="XAUUSD"
os.environ["SP2L_MAGIC_BASE"]="26092300"  # XAUUSD slot => V3.1 magic 26092301; V3 remains 26092201.
os.environ["SP2L_P_GAP_PRICE"]=str(cfg.P_GAP_PRICE)
os.environ["SP2L_SPIKE_MULTIPLIER"]=str(cfg.SPIKE_MULTIPLIER)
os.environ["SP2L_MAX_SL_DISTANCE"]=str(cfg.MAX_SL_DISTANCE)
os.environ["SP2L_TP_R"]=str(cfg.TP_R)
os.environ["SP2L_VOLUME"]=str(cfg.VOLUME)
os.environ["MT5_FORWARD_ORDER_MODE"]=cfg.ORDER_MODE
os.environ["SP2L_PENDING_TTL_MINUTES"]=str(cfg.PENDING_TTL_MINUTES)
# Server UTC offset must be explicitly pinned by the operator for this run.
# No historical/default UTC offset is assumed; expiry and order submission fail closed without it.
os.environ.setdefault("LIVE_TRADING_ENABLE","true")
os.environ.setdefault("ALLOW_REAL_EXECUTION","true")

import run_sp2l_author_replica_multi_symbol_forward_test as runner
from sp2l_history_query_failure_log import HistoryQueryFailureLogGate

_HISTORY_QUERY_FAILURE_LOG_GATE = HistoryQueryFailureLogGate()

# RR4/ACT40 Telegram display convention only: one pip = $0.10 price.
# Do not alter the generic runner's pip_size or execution configuration.
_original_send_signal = runner.send_signal
def _rr2_trail4_send_signal(candidate, pip_size, order_ticket=None):
    return _original_send_signal(
        candidate, float(cfg.XAU_PIP_SIZE_PRICE), order_ticket
    )
runner.send_signal = _rr2_trail4_send_signal

runner.detect=cfg.detect
runner.find_first_entry=cfg.find_first_entry
runner.find_latest_candidate=cfg.find_latest_candidate
runner.EVENTS=runner.ARTIFACTS / "SP2L_V3_1_XAUUSD_RR4_ACT40_FORWARD_EVENTS.jsonl"
runner.STATE_FILE=runner.RUNTIME / "sp2l_v3_1_xauusd_rr4_act40_forward_state.json"
runner.session_gate_status=lambda trigger_ts:(True,"V3_ALL_MARKET_HOURS")
_original_rates=runner.rates
runner.rates=lambda symbol,count=10:_original_rates(symbol,30)

_original_monitor=runner.monitor_position_lifecycle
_TRAIL_MAX_SEND_ATTEMPTS_PER_BAR = 3
_TRAIL_RETRY_COOLDOWN_SECONDS = 2.0
_TRAIL_RETRY_STATE = {}
_TRAIL_DEFERRED_LOGGED = set()
_TRAIL_STATE_FILE = runner.RUNTIME / "sp2l_v3_1_xauusd_rr4_act40_trailing_state.json"
_TRAIL_FAVORABLE_EXTREMES = {}
_TRAIL_STATE_LOADED = False
_TRAIL_STATE_DIRTY = False

def trail_positions(cfg_runtime,state):
    global _TRAIL_STATE_DIRTY
    _original_monitor(cfg_runtime,state)
    symbol=cfg_runtime["symbol"]; magic=cfg_runtime["magic"]
    if mt5.symbol_info(symbol) is None: return
    # Bar 0 is forming; bar 1 is the latest completed M1 candle.
    bars=mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 1, 1)
    if bars is None or len(bars)!=1: return
    b=bars[0]
    completed_bar_time=int(b["time"])
    high=float(b["high"]); low=float(b["low"])
    positions=mt5.positions_get(symbol=symbol)
    if positions is None: return
    if _TRAIL_STATE_DIRTY:
        try:
            save_trailing_state(_TRAIL_STATE_FILE,_TRAIL_FAVORABLE_EXTREMES)
            _TRAIL_STATE_DIRTY = False
        except Exception as exc:
            runner.log_event({
                "event":"TRAIL_STATE_PERSIST_FAILED","version":cfg.VERSION,
                "symbol":symbol,"detail":f"{type(exc).__name__}: {exc}",
                "canonical":False})
            return
    attempts=state.setdefault("trail_attempts", set())
    now=time.monotonic()

    # Keep retry state only for the currently evaluated completed M1 bar.
    for key in list(_TRAIL_RETRY_STATE):
        if not key.endswith(f":{completed_bar_time}"):
            _TRAIL_RETRY_STATE.pop(key,None)
    for key in list(_TRAIL_DEFERRED_LOGGED):
        if not key.endswith(f":{completed_bar_time}"):
            _TRAIL_DEFERRED_LOGGED.discard(key)

    for p in positions:
        if int(getattr(p,"magic",0) or 0)!=magic: continue
        ticket=int(getattr(p,"ticket",0) or 0)
        entry=float(getattr(p,"price_open",0) or 0)
        old_sl=float(getattr(p,"sl",0) or 0)
        tp=float(getattr(p,"tp",0) or 0)
        if entry<=0 or ticket<=0: continue
        position_time=int(getattr(p,"time",0) or 0)
        position_time_msc=int(getattr(p,"time_msc",0) or 0)
        if not cfg.completed_bar_is_after_position(
            completed_bar_time, position_time, position_time_msc
        ):
            continue
        attempt_key=f"{ticket}:{completed_bar_time}"
        if attempt_key in attempts: continue
        retry=_TRAIL_RETRY_STATE.get(attempt_key,{"count":0,"last_attempt":0.0})
        if retry["count"] >= _TRAIL_MAX_SEND_ATTEMPTS_PER_BAR:
            attempts.add(attempt_key)
            continue
        if now-float(retry["last_attempt"]) < _TRAIL_RETRY_COOLDOWN_SECONDS:
            continue

        if int(p.type)==mt5.POSITION_TYPE_BUY:
            direction="BUY"
        else:
            direction="SELL"

        # Preserve the best completed-bar excursion for the full position
        # lifetime. A rejected/deferred SL update must not erase a prior
        # favorable extreme when the next M1 bar starts.
        entry_time_msc = position_time_msc or position_time * 1000
        prior_record = _TRAIL_FAVORABLE_EXTREMES.get(str(ticket))
        record_matches = trailing_record_matches(
            prior_record,
            symbol=symbol,
            magic=magic,
            direction=direction,
            entry=entry,
            position_time_msc=entry_time_msc,
        )
        previous_extreme = (
            float(prior_record["favorable_extreme"]) if record_matches else entry
        )
        favorable_extreme = update_favorable_extreme(
            direction, entry, previous_extreme, high, low
        )
        if not record_matches or favorable_extreme != previous_extreme:
            _TRAIL_FAVORABLE_EXTREMES[str(ticket)] = {
                "symbol": symbol,
                "magic": int(magic),
                "direction": direction,
                "entry": float(entry),
                "position_time_msc": int(entry_time_msc),
                "favorable_extreme": float(favorable_extreme),
                "last_completed_bar_time": int(completed_bar_time),
            }
            _TRAIL_STATE_DIRTY = True
            try:
                # Persist before attempting the broker modification. If MT5
                # rejects/defer the SL, the excursion survives the next bar
                # and a controlled process restart.
                save_trailing_state(_TRAIL_STATE_FILE, _TRAIL_FAVORABLE_EXTREMES)
                _TRAIL_STATE_DIRTY = False
            except Exception as exc:
                runner.log_event({
                    "event":"TRAIL_STATE_PERSIST_FAILED","version":cfg.VERSION,
                    "symbol":symbol,"position":ticket,
                    "completed_bar_time":completed_bar_time,
                    "detail":f"{type(exc).__name__}: {exc}","canonical":False})
                continue

        favorable = favorable_move(direction, entry, favorable_extreme)
        if not trailing_activation_reached(
            direction, entry, favorable_extreme, cfg.TRAIL_DISTANCE_PRICE
        ):
            continue
        raw_sl=cfg.trail_stop(direction,favorable_extreme)

        # Refresh quote and symbol constraints immediately before each SLTP send.
        info_now=mt5.symbol_info(symbol)
        tick_now=mt5.symbol_info_tick(symbol)
        if info_now is None or tick_now is None: continue
        point=float(getattr(info_now,"point",0.0) or 0.0)
        tick_size=float(getattr(info_now,"trade_tick_size",0.0) or 0.0) or point
        digits=int(getattr(info_now,"digits",2) or 0)
        stops_level=int(getattr(info_now,"trade_stops_level",0) or 0)
        freeze_level=int(getattr(info_now,"trade_freeze_level",0) or 0)
        bid=float(getattr(tick_now,"bid",0.0) or 0.0)
        ask=float(getattr(tick_now,"ask",0.0) or 0.0)
        if point<=0 or tick_size<=0: continue
        min_distance=max(stops_level,freeze_level)*point
        new_sl=normalize_trailing_sl(direction,raw_sl,tick_size,digits)
        placeable=trailing_sl_is_placeable(direction,new_sl,bid,ask,min_distance)
        improving=(new_sl>old_sl) if direction=="BUY" else (old_sl<=0 or new_sl<old_sl)
        if not placeable or not improving:
            if attempt_key not in _TRAIL_DEFERRED_LOGGED:
                runner.log_event({
                    "event":"TRAIL_DEFERRED","version":cfg.VERSION,"symbol":symbol,
                    "position":ticket,"direction":direction,
                    "completed_bar_time":completed_bar_time,
                    "raw_sl":float(raw_sl),"normalized_sl":float(new_sl),
                    "old_sl":old_sl,"bid":bid,"ask":ask,
                    "point":point,"tick_size":tick_size,"digits":digits,
                    "stops_level":stops_level,"freeze_level":freeze_level,
                    "min_distance":min_distance,
                    "reason":"CURRENT_QUOTE_OR_BROKER_DISTANCE" if not placeable else "SL_NOT_IMPROVING",
                    "canonical":False})
                _TRAIL_DEFERRED_LOGGED.add(attempt_key)
            continue

        request={"action":mt5.TRADE_ACTION_SLTP,"symbol":symbol,
                 "position":ticket,"sl":float(new_sl),"tp":tp}
        send=mt5.order_send(request)
        retcode=int(send.retcode) if send else None
        ok=bool(send and retcode==mt5.TRADE_RETCODE_DONE)
        retry["count"]+=1
        retry["last_attempt"]=time.monotonic()
        if ok:
            attempts.add(attempt_key)
            _TRAIL_RETRY_STATE.pop(attempt_key,None)
        elif should_retry_trailing(retcode,retry["count"],_TRAIL_MAX_SEND_ATTEMPTS_PER_BAR):
            _TRAIL_RETRY_STATE[attempt_key]=retry
        else:
            attempts.add(attempt_key)
            _TRAIL_RETRY_STATE.pop(attempt_key,None)
        runner.log_event({
            "event":"TRAIL_UPDATE","version":cfg.VERSION,"symbol":symbol,
            "position":ticket,"direction":direction,
            "completed_bar_time":completed_bar_time,
            "bar_high":high,"bar_low":low,"favorable_extreme":favorable_extreme,
            "favorable_move":favorable,"entry":entry,
            "old_sl":old_sl,"new_sl":float(new_sl),"tp":tp,
            "trail_pips":cfg.TRAIL_PIPS,
            "trail_distance_price":cfg.TRAIL_DISTANCE_PRICE,
            "bid":bid,"ask":ask,"point":point,"tick_size":tick_size,
            "digits":digits,"stops_level":stops_level,
            "freeze_level":freeze_level,"min_distance":min_distance,
            "attempt_number":retry["count"],
            "success":ok,"retcode":retcode,
            "comment":str(send.comment) if send else None,"canonical":False})

    # Remove persisted extrema only after a successful broker inventory query.
    # A None result returned above leaves the recovery file untouched.
    active_owned = {
        str(int(getattr(pos,"ticket",0) or 0))
        for pos in positions
        if int(getattr(pos,"magic",0) or 0)==magic
        and int(getattr(pos,"ticket",0) or 0)>0
    }
    stale_keys = set(_TRAIL_FAVORABLE_EXTREMES) - active_owned
    if stale_keys:
        for stale_key in stale_keys:
            _TRAIL_FAVORABLE_EXTREMES.pop(stale_key,None)
        _TRAIL_STATE_DIRTY = True
        try:
            save_trailing_state(_TRAIL_STATE_FILE,_TRAIL_FAVORABLE_EXTREMES)
            _TRAIL_STATE_DIRTY = False
        except Exception as exc:
            runner.log_event({
                "event":"TRAIL_STATE_PERSIST_FAILED","version":cfg.VERSION,
                "symbol":symbol,"detail":f"{type(exc).__name__}: {exc}",
                "canonical":False})

runner.monitor_position_lifecycle=trail_positions

# V3 RUN-ISOLATION: never replay pre-existing broker history into Telegram or
# Forward-Test statistics. Only broker objects created/tracked by THIS process
# are eligible for lifecycle reporting/cancellation.
from datetime import datetime, timezone
from sp2l_deal_lifecycle_dedupe import claim_deal_lifecycle_event
from sp2l_v31_startup_recovery import recover_owned_broker_inventory
_RUN_STARTED_UTC = datetime.now(timezone.utc)
_original_main = runner.main

def _fresh_v3_state():
    return {"seen": {}, "notified": set(), "deals": set(), "deal_events": set(), "orders": set(),
            "positions": set(), "order_states": set(), "position_orders": {},
            "signal_orders": {}, "pending_signal_notifications": {}}

# Pending-expiry clock freshness is deliberately stricter than the shared
# session clock helper: after process start, require the broker tick timestamp
# to advance before using a server offset for cancellation. This prevents a
# cached offset (or an unchanged stale tick) from being treated as fresh after
# a restart. If the market supplies no advancing tick, expiry fails closed.
_PENDING_CLOCK_LAST_TICK_TIME: int | None = None


def _pending_server_offset_strict(symbol: str):
    global _PENDING_CLOCK_LAST_TICK_TIME
    tick = mt5.symbol_info_tick(symbol)
    tick_time = int(getattr(tick, "time", 0) or 0) if tick else 0
    if tick_time <= 0:
        raise RuntimeError("pending expiry clock unavailable: missing tick timestamp")
    previous = _PENDING_CLOCK_LAST_TICK_TIME
    _PENDING_CLOCK_LAST_TICK_TIME = tick_time
    if previous is None:
        raise RuntimeError("pending expiry clock not yet proven fresh since process start")
    if tick_time <= previous:
        raise RuntimeError("pending expiry clock tick has not advanced since previous observation")
    # A tick can advance while remaining exactly one hour stale, which is
    # indistinguishable from a legitimate broker DST offset using tick.time
    # alone. Require an operator-pinned offset and compare the observed value
    # against it. Missing/mismatched configuration must never cancel orders.
    configured = os.getenv("SP2L_PENDING_SERVER_OFFSET_HOURS", "").strip()
    if not configured:
        raise RuntimeError("SP2L_PENDING_SERVER_OFFSET_HOURS is required for pending expiry")
    try:
        configured_hours = float(configured)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("invalid SP2L_PENDING_SERVER_OFFSET_HOURS") from exc
    if not configured_hours.is_integer() or not -12 <= configured_hours <= 14:
        raise RuntimeError("SP2L_PENDING_SERVER_OFFSET_HOURS must be an integer from -12 to +14")
    expected = timedelta(hours=int(configured_hours))
    # A monotonically advancing tick is not necessarily a fresh tick: a
    # delayed feed can advance while remaining minutes/hours behind. Compare
    # its broker timestamp to host UTC shifted by the operator-pinned offset.
    # If the host clock or feed is outside this bounded tolerance, expiry is
    # disabled; this is a safety gate, not a strategy or execution rule.
    expected_tick_epoch = time.time() + expected.total_seconds()
    tick_age_seconds = expected_tick_epoch - tick_time
    if abs(tick_age_seconds) > 120:
        raise RuntimeError(
            "pending expiry tick timestamp outside freshness tolerance: "
            f"age_seconds={tick_age_seconds:.1f} tolerance=120"
        )
    # Compare the shared helper's offset with the independently pinned
    # expectation to catch unreviewed server-clock/DST changes.
    observed = runner.mt5_server_offset_strict()
    if observed != expected:
        raise RuntimeError(
            f"broker offset mismatch: configured={int(configured_hours)}h observed={observed}"
        )
    return observed


def _run_scoped_pending(cfg_runtime, state):
    """Expire only this runner's XAUUSD limit orders using broker-clock age.

    MT5 order.time_setup is expressed on the broker/server clock. Compare it
    with the current time on that same clock, using the strict tick-derived
    server offset. If the offset cannot be established, fail closed and do
    not cancel anything. Matching symbol + this runner's magic scopes ownership
    independently of the intentionally fresh signal state after startup.
    """
    ttl_minutes = float(cfg_runtime.get("pending_ttl_minutes", os.getenv("SP2L_PENDING_TTL_MINUTES", "30")))
    if ttl_minutes <= 0:
        return
    symbol, magic = cfg_runtime["symbol"], int(cfg_runtime["magic"])
    active_orders = mt5.orders_get(symbol=symbol)
    if active_orders is None:
        return
    eligible = []
    for order in active_orders:
        ticket = int(getattr(order, "ticket", 0) or 0)
        if ticket <= 0 or str(getattr(order, "symbol", "") or "") != symbol:
            continue
        if int(getattr(order, "magic", 0) or 0) != magic:
            continue
        if int(getattr(order, "type", -1)) not in (mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_SELL_LIMIT):
            continue
        # Only a confirmed cancellation completes expiry. A failure or
        # dry-run notification must not suppress subsequent cancellation tries.
        if f"{ticket}:EXPIRY_NOTIFIED:CANCELLED" in state.get("order_states", set()):
            continue
        eligible.append(order)
    if not eligible:
        return
    try:
        server_offset = _pending_server_offset_strict(symbol)
        now_server_epoch = time.time() + server_offset.total_seconds()
    except Exception as exc:
        # One diagnostic per ticket per process; a later poll may retry when
        # fresh broker ticks become available. Unknown age must never cancel.
        states = state.setdefault("order_states", set())
        for order in eligible:
            ticket = int(getattr(order, "ticket", 0) or 0)
            diagnostic = f"{ticket}:EXPIRY_CLOCK_UNAVAILABLE"
            if diagnostic not in states:
                states.add(diagnostic)
                runner.log_event({
                    "event": "PENDING_ORDER_TTL_SKIPPED",
                    "version": cfg.VERSION, "symbol": symbol, "order": ticket,
                    "reason": "SERVER_OFFSET_UNAVAILABLE",
                    "detail": f"{type(exc).__name__}: {exc}",
                    "canonical": False,
                })
        return
    for order in eligible:
        ticket = int(getattr(order, "ticket", 0) or 0)
        setup_epoch = int(getattr(order, "time_setup", 0) or 0)
        if setup_epoch <= 0:
            continue
        age_minutes = (now_server_epoch - setup_epoch) / 60.0
        # A negative age indicates an invalid/unavailable clock basis; fail
        # closed rather than treating a future timestamp as an expired order.
        if age_minutes < ttl_minutes:
            continue
        runner._cancel_pending_order(order, state)

def _run_scoped_pending_lifecycle(cfg_runtime, state):
    symbol, magic = cfg_runtime["symbol"], int(cfg_runtime["magic"])
    tracked = set(state["orders"])
    active_orders = list(mt5.orders_get(symbol=symbol) or [])
    # Reconcile only currently active limit orders carrying this runner's
    # symbol + magic. This restores lifecycle ownership after a restart without
    # replaying old signals, candidates, positions, or historical deals.
    for active in active_orders:
        ticket = int(getattr(active, "ticket", 0) or 0)
        if (ticket > 0
                and str(getattr(active, "symbol", "") or "") == symbol
                and int(getattr(active, "magic", 0) or 0) == magic
                and int(getattr(active, "type", -1)) in (mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_SELL_LIMIT)):
            state["orders"].add(ticket)
            tracked.add(ticket)
    orders = list(mt5.history_orders_get(_RUN_STARTED_UTC, datetime.now(timezone.utc), group=symbol) or [])
    orders.extend(active_orders)
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

    # MT5 time-window history can omit recent deals when broker timestamps use
    # a different clock basis from host UTC. Resolve only runner-owned IDs,
    # then query each linked position so its closing deal is not missed.
    from sp2l_tracked_deal_history import (
        DealHistoryQueryError,
        collect_tracked_deals,
    )
    try:
        deals = collect_tracked_deals(
            history_deals_get=mt5.history_deals_get,
            history_orders_get=getattr(mt5, "history_orders_get", None),
            symbol=symbol,
            tracked_orders=tracked_orders,
            tracked_positions=tracked_positions,
            last_error=getattr(mt5, "last_error", None),
        )
    except DealHistoryQueryError as exc:
        # A failed query is not an empty history snapshot. Suppress only
        # duplicate diagnostics; always defer lifecycle processing.
        if _HISTORY_QUERY_FAILURE_LOG_GATE.should_log(
            exc.query, exc.target, exc.detail
        ):
            runner.log_event({
                "event": "MT5_DEAL_HISTORY_QUERY_FAILED",
                "version": cfg.VERSION,
                "symbol": symbol,
                "query": exc.query,
                "target": exc.target,
                "detail": exc.detail,
                "canonical": False,
            })
        runner.save_state(state)
        return

    _HISTORY_QUERY_FAILURE_LOG_GATE.mark_success()
    run_started_epoch = int(_RUN_STARTED_UTC.timestamp())
    for deal in deals:
        ticket=int(deal.ticket)
        if ticket in state["deals"]:
            continue
        deal_epoch = int(getattr(deal, "time", 0) or 0)
        if deal_epoch > 0 and deal_epoch < run_started_epoch:
            # Suppress historical deals even if MT5 unexpectedly returns them
            # outside the requested time bounds. Record the suppression once;
            # a genuinely new close deal has its own post-start timestamp.
            state["deals"].add(ticket)
            runner.log_event({
                "event": "TELEGRAM_STALE_DEAL_SUPPRESSED",
                "version": cfg.VERSION,
                "symbol": symbol,
                "deal": ticket,
                "deal_time": deal_epoch,
                "run_started_epoch": run_started_epoch,
                "canonical": False,
            })
            runner.save_state(state)
            continue
        order=int(getattr(deal,"order",0) or 0)
        position=int(getattr(deal,"position_id",0) or 0)
        runner._remember_position_links(state, deal)
        is_entry = int(getattr(deal,"entry",-1)) == mt5.DEAL_ENTRY_IN
        entry_price=float(deal.price) if is_entry else runner.position_entry_price(deal, magic)
        if not is_entry and entry_price is None:
            # Do not send a close before its actual entry can be linked.
            # Keep polling history; the broker record may become available later.
            continue
        execution_meta={}
        for linked_order in state.get("position_orders",{}).get(str(position),set()):
            execution_meta=state.get("signal_orders",{}).get(str(linked_order),{})
            if execution_meta: break
        # Event observation and Telegram delivery are separate state dimensions.
        # A missing Telegram configuration must not cause the same broker deal
        # to be appended to the event log on every polling cycle.
        first_observation = claim_deal_lifecycle_event(state, ticket)
        tg=runner.gateway.send_telegram_message(
            runner.lifecycle_message(deal,symbol,cfg.XAU_PIP_SIZE_PRICE,magic), parse_mode="HTML")
        delivered=bool(getattr(tg,"success",False))
        profit=float(getattr(deal,"profit",0.0) or 0.0)
        commission=float(getattr(deal,"commission",0.0) or 0.0)
        swap=float(getattr(deal,"swap",0.0) or 0.0)
        if first_observation:
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
                "telegram":{"success":delivered,"detail":getattr(tg,"detail",None)},
                "canonical":False})
        if delivered:
            state["deals"].add(ticket)
            if not first_observation:
                runner.log_event({
                    "event":"TELEGRAM_DEAL_NOTIFICATION_DELIVERED",
                    "version":cfg.VERSION,"symbol":symbol,"deal":ticket,
                    "position":position,"canonical":False})
            runner.save_state(state)
        else:
            # Preserve chronological OPENED -> CLOSED delivery and retry failed sends.
            # The observation event is already de-duplicated in deal_events.
            runner.save_state(state)
            break

runner.enforce_pending_order_expiry=_run_scoped_pending
runner.monitor_pending_order_lifecycle=_run_scoped_pending_lifecycle
runner.monitor_position_lifecycle=trail_positions
runner.monitor_symbol_lifecycle=_run_scoped_symbol_lifecycle


def _v31_startup_recovery(configs, state):
    """Reconcile live broker-owned objects before entering the V3.1 poll loop.

    This is read-only at the broker boundary. Unknown/incomplete inventory
    aborts startup; no signal history or old deal notifications are replayed.
    """
    summaries = []
    for cfg_runtime in configs:
        symbol = str(cfg_runtime["symbol"])
        magic = int(cfg_runtime["magic"])
        # MT5 returns None on query failure and an empty tuple on a valid
        # empty result. Never collapse those two states.
        active_orders = mt5.orders_get(symbol=symbol)
        active_positions = mt5.positions_get(symbol=symbol)
        summary = recover_owned_broker_inventory(
            state,
            symbol=symbol,
            magic=magic,
            orders=active_orders,
            positions=active_positions,
            buy_limit_type=mt5.ORDER_TYPE_BUY_LIMIT,
            sell_limit_type=mt5.ORDER_TYPE_SELL_LIMIT,
        )
        summaries.append(summary)
    # Persist the recovered ownership set before recording recovery success
    # or entering the first management poll. Any write failure aborts startup.
    runner.save_state(state)
    runner.log_event({
        "event": "STARTUP_BROKER_RECOVERY",
        "version": cfg.VERSION,
        "symbol": ",".join(str(item["symbol"]) for item in summaries),
        "orders_recovered": sum(item["orders_recovered"] for item in summaries),
        "positions_recovered": sum(item["positions_recovered"] for item in summaries),
        "canonical": False,
    })


runner.startup_recovery_hook = _v31_startup_recovery

# Execution clock guard: no order may be sent unless the operator has pinned
# the current broker UTC offset and both tick freshness and MT5's strict offset
# helper independently agree. This is separate from the TTL cancellation guard.
_original_execute_candidate = runner.execute_candidate

def _validate_execution_clock(symbol: str) -> None:
    # This V3.1 candidate is intentionally hard-locked to Demo accounts.
    # A future live deployment requires a separate reviewed code change.
    account = mt5.account_info()
    demo_mode = getattr(mt5, "ACCOUNT_TRADE_MODE_DEMO", None)
    if account is None or demo_mode is None or int(getattr(account, "trade_mode", -1)) != int(demo_mode):
        raise RuntimeError("ORDER_BLOCKED: V3.1 forward runner is DEMO-ONLY")
    configured = os.getenv("SP2L_PENDING_SERVER_OFFSET_HOURS", "").strip()
    if not configured:
        raise RuntimeError("ORDER_BLOCKED: SP2L_PENDING_SERVER_OFFSET_HOURS must be explicitly set")
    try:
        hours = float(configured)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("ORDER_BLOCKED: invalid SP2L_PENDING_SERVER_OFFSET_HOURS") from exc
    if not hours.is_integer() or not -12 <= hours <= 14:
        raise RuntimeError("ORDER_BLOCKED: server offset must be an integer from -12 to +14")
    expected = timedelta(hours=int(hours))
    tick = mt5.symbol_info_tick(symbol)
    tick_time = int(getattr(tick, "time", 0) or 0) if tick else 0
    if tick_time <= 0:
        raise RuntimeError("ORDER_BLOCKED: broker tick timestamp unavailable")
    age = time.time() + expected.total_seconds() - tick_time
    if abs(age) > 120:
        raise RuntimeError(f"ORDER_BLOCKED: broker tick outside 120s freshness tolerance (age={age:.1f}s)")
    observed = runner.mt5_server_offset_strict()
    if observed != expected:
        raise RuntimeError(f"ORDER_BLOCKED: pinned broker offset {expected} != observed {observed}")

def _guarded_execute_candidate(candidate: dict, magic: int) -> dict:
    _validate_execution_clock(str(candidate.get("symbol", "")))
    return _original_execute_candidate(candidate, magic)

runner.execute_candidate = _guarded_execute_candidate


def _v3_main():
    global _TRAIL_FAVORABLE_EXTREMES, _TRAIL_STATE_LOADED
    # A corrupt/unreadable trailing recovery file must stop startup rather
    # than silently resetting a position's previously observed excursion.
    if not _TRAIL_STATE_LOADED:
        _TRAIL_FAVORABLE_EXTREMES = load_trailing_state(_TRAIL_STATE_FILE)
        _TRAIL_STATE_LOADED = True

    # V3 forward-session boundary: only newly formed triggers after startup
    # are eligible for execution. Recent M1 history is context, not backlog.
    original_load, original_reconcile = runner.load_state, runner.reconcile_state_from_events
    original_find = runner.find_latest_candidate
    # Candidate trigger_time is stamped in MT5 broker/server epoch, not host UTC epoch.
    # Convert the process-start boundary into the same clock before filtering,
    # otherwise a broker +3h offset makes pre-start candidates look future-dated.
    # MT5 is only initialized inside _original_main(), and the strict offset query
    # needs live ticks, so resolve the cutoff lazily on first use instead of here.
    cutoff_cache: dict = {}

    def _session_cutoff_epoch() -> int:
        if "epoch" not in cutoff_cache:
            server_offset = runner.mt5_server_offset_strict()
            cutoff_cache["epoch"] = int(_RUN_STARTED_UTC.timestamp() + server_offset.total_seconds())
        return int(cutoff_cache["epoch"])

    # A closed market can leave MT5 without a fresh tick, so the shared
    # server-clock helper may temporarily fail at startup. Do not crash the
    # forward runner or guess an offset: defer candidate detection until the
    # clock helper succeeds on a later poll. Other read-only/lifecycle polling
    # in the base loop continues; no new candidate can reach execution here.
    session_clock_error_log_at = -300.0  # Ensure the first unavailable-clock event is always logged.

    def _forward_session_find(data, symbol):
        nonlocal session_clock_error_log_at
        try:
            session_cutoff_epoch = _session_cutoff_epoch()
        except RuntimeError as exc:
            now_mono = time.monotonic()
            if now_mono - session_clock_error_log_at >= 300.0:
                runner.log_event({
                    "event": "SESSION_CUTOFF_DEFERRED",
                    "symbol": symbol,
                    "reason": "SERVER_OFFSET_UNAVAILABLE",
                    "detail": str(exc),
                    "retry_interval_seconds": 300,
                    "canonical": False,
                })
                session_clock_error_log_at = now_mono
            return None

        candidate = original_find(data, symbol)
        if candidate is None:
            return None
        trigger_time = int(candidate.get("trigger_time", 0) or 0)
        if trigger_time <= session_cutoff_epoch:
            return None
        return candidate

    runner.load_state = lambda: _fresh_v3_state()
    runner.reconcile_state_from_events = lambda state: None
    runner.find_latest_candidate = _forward_session_find
    try:
        _original_main()
    finally:
        runner.load_state, runner.reconcile_state_from_events = original_load, original_reconcile
        runner.find_latest_candidate = original_find


runner.main=_v3_main

if __name__=="__main__":
    runner.main()
