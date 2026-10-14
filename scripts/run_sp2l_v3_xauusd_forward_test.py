"""SP2L V3 XAUUSD Demo forward runner: frozen V2 geometry + research RR2/Trail 4.

Trailing is evaluated from the latest COMPLETED M1 bar, matching the V3
historical model. The initial TP remains fixed. Broker fills/exits are recorded
as observed facts; no canonical production decision is made here.
"""
from __future__ import annotations
import os
import time
from datetime import timedelta
import MetaTrader5 as mt5
import sp2l_v3_rr2_trail4_config as cfg

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
runner.EVENTS=runner.ARTIFACTS / "SP2L_V3_XAUUSD_RR2_TRAIL4_FORWARD_EVENTS.jsonl"
runner.STATE_FILE=runner.RUNTIME / "sp2l_v3_xauusd_rr2_trail4_forward_state.json"
runner.session_gate_status=lambda trigger_ts:(True,"V3_ALL_MARKET_HOURS")
_original_rates=runner.rates
runner.rates=lambda symbol,count=10:_original_rates(symbol,30)

_original_monitor=runner.monitor_position_lifecycle
def trail_positions(cfg_runtime,state):
    _original_monitor(cfg_runtime,state)
    symbol=cfg_runtime["symbol"]; magic=cfg_runtime["magic"]
    info=mt5.symbol_info(symbol)
    tick=mt5.symbol_info_tick(symbol)
    if info is None or tick is None: return
    # Bar 0 is forming; bar 1 is the latest completed M1 candle.
    bars=mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 1, 1)
    if bars is None or len(bars)!=1: return
    b=bars[0]
    completed_bar_time=int(b["time"])
    high=float(b["high"]); low=float(b["low"])
    positions=mt5.positions_get(symbol=symbol) or []
    attempts=state.setdefault("trail_attempts", set())
    point=float(getattr(info,"point",0.0) or 0.0)
    stops_level=int(getattr(info,"trade_stops_level",0) or 0)
    freeze_level=int(getattr(info,"trade_freeze_level",0) or 0)
    min_distance=max(stops_level,freeze_level)*point
    bid=float(getattr(tick,"bid",0.0) or 0.0)
    ask=float(getattr(tick,"ask",0.0) or 0.0)
    for p in positions:
        if int(getattr(p,"magic",0) or 0)!=magic: continue
        ticket=int(getattr(p,"ticket",0) or 0)
        entry=float(getattr(p,"price_open",0) or 0)
        old_sl=float(getattr(p,"sl",0) or 0)
        tp=float(getattr(p,"tp",0) or 0)
        if entry<=0 or ticket<=0: continue
        attempt_key=f"{ticket}:{completed_bar_time}"
        if attempt_key in attempts: continue
        if int(p.type)==mt5.POSITION_TYPE_BUY:
            favorable=high-entry
            if favorable < cfg.TRAIL_DISTANCE_PRICE: continue
            new_sl=cfg.trail_stop("BUY",high)
            if new_sl<=old_sl or new_sl>=high: continue
            # MT5 requires a BUY SL to remain below current Bid and outside
            # the broker's stops/freeze distance. The historical trail target
            # is retained; execution is deferred when the broker rejects the
            # target as currently unplaceable.
            if bid <= 0 or new_sl >= bid - min_distance: continue
            direction="BUY"
        else:
            favorable=entry-low
            if favorable < cfg.TRAIL_DISTANCE_PRICE: continue
            new_sl=cfg.trail_stop("SELL",low)
            if old_sl>0 and new_sl>=old_sl: continue
            if new_sl<=low: continue
            # MT5 requires a SELL SL to remain above current Ask and outside
            # the broker's stops/freeze distance.
            if ask <= 0 or new_sl <= ask + min_distance: continue
            direction="SELL"
        request={"action":mt5.TRADE_ACTION_SLTP,"symbol":symbol,
                 "position":ticket,"sl":float(new_sl),"tp":tp}
        send=mt5.order_send(request)
        ok=bool(send and send.retcode==mt5.TRADE_RETCODE_DONE)
        attempts.add(attempt_key)
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

def _fresh_v3_state():
    return {"seen": {}, "notified": set(), "deals": set(), "orders": set(),
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
    symbol, magic = cfg_runtime["symbol"], int(cfg_runtime["magic"])
    positions = mt5.positions_get(symbol=symbol)
    if positions is None:
        runner.log_event({
            "event": "POSITION_SNAPSHOT_QUERY_FAILED",
            "version": cfg.VERSION,
            "symbol": symbol,
            "reason": "MT5_POSITIONS_GET_RETURNED_NONE",
            "mt5_error": str(mt5.last_error()),
            "diagnostic_only": True,
            "canonical": False,
        })
        return
    for position in positions:
        position_id = int(
            getattr(position, "identifier", 0)
            or getattr(position, "ticket", 0)
            or 0
        )
        if (
            position_id not in state["positions"]
            or str(getattr(position, "symbol", "") or "") != symbol
            or int(getattr(position, "magic", 0) or 0) != magic
        ):
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
    symbol, magic, pip = cfg_runtime["symbol"], int(cfg_runtime["magic"]), cfg_runtime["pip_size"]

    # Adopt only currently open positions owned by this exact symbol + magic.
    # V3 intentionally starts with fresh in-memory state to avoid replaying old
    # signals; without this narrow reconciliation, a position opened before a
    # runner restart would be invisible to the CLOSED-result watcher.
    active_positions = mt5.positions_get(symbol=symbol)
    if active_positions is None:
        runner.log_event({
            "event": "POSITION_SNAPSHOT_QUERY_FAILED",
            "version": cfg.VERSION,
            "symbol": symbol,
            "reason": "MT5_POSITIONS_GET_RETURNED_NONE",
            "mt5_error": str(mt5.last_error()),
            "diagnostic_only": True,
            "canonical": False,
        })
        runner.save_state(state)
        return

    for active_position in active_positions:
        # Deal.position_id corresponds to the stable MT5 position identifier,
        # not necessarily the mutable/current position ticket.
        position_id = int(
            getattr(active_position, "identifier", 0)
            or getattr(active_position, "ticket", 0)
            or 0
        )
        if (
            position_id > 0
            and str(getattr(active_position, "symbol", "") or "") == symbol
            and int(getattr(active_position, "magic", 0) or 0) == magic
        ):
            state["positions"].add(position_id)

    tracked_orders, tracked_positions = set(state["orders"]), set(state["positions"])
    if not tracked_orders and not tracked_positions:
        return
    deals_result = mt5.history_deals_get(
        _RUN_STARTED_UTC, datetime.now(timezone.utc), group=symbol
    )
    if deals_result is None:
        runner.log_event({
            "event": "POSITION_HISTORY_QUERY_FAILED",
            "version": cfg.VERSION,
            "symbol": symbol,
            "reason": "MT5_HISTORY_DEALS_GET_RETURNED_NONE",
            "mt5_error": str(mt5.last_error()),
            "history_start_utc": _RUN_STARTED_UTC.isoformat(),
            "history_end_utc": datetime.now(timezone.utc).isoformat(),
            "diagnostic_only": True,
            "canonical": False,
        })
        runner.save_state(state)
        return
    deals = list(deals_result)
    # Enforce the forward-session boundary against each returned deal's Unix
    # epoch as well as the MT5 history query bounds. If MT5 returns records
    # outside the requested range, never send a new Telegram message for a
    # deal that predates this run. A genuinely new close of a pre-existing
    # position still passes because the close deal has its own current timestamp.
    run_started_epoch = int(_RUN_STARTED_UTC.timestamp())
    for deal in sorted(deals, key=lambda x:(int(x.time), int(x.ticket))):
        ticket=int(deal.ticket)
        deal_epoch = int(getattr(deal, "time", 0) or 0)
        if deal_epoch < run_started_epoch:
            continue
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
            # Do not send a close before its actual entry can be linked.
            # Keep polling history; the broker record may become available later.
            continue
        execution_meta={}
        for linked_order in state.get("position_orders",{}).get(str(position),set()):
            execution_meta=state.get("signal_orders",{}).get(str(linked_order),{})
            if execution_meta: break
        tg=runner.gateway.send_telegram_message(
            runner.lifecycle_message(deal,symbol,pip,magic), parse_mode="HTML")
        delivered=bool(getattr(tg,"success",False))
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
            "telegram":{"success":delivered,"detail":getattr(tg,"detail",None)},
            "canonical":False})
        if delivered:
            # Persist each acknowledged deal immediately. Otherwise a later
            # empty-rate poll or process crash could cause a successful post
            # to be sent again after restart.
            state["deals"].add(ticket)
            runner.save_state(state)
        else:
            # Preserve chronological OPENED -> CLOSED delivery. A failed
            # earlier deal remains eligible for retry; do not leapfrog it
            # with a later close message for the same history poll.
            runner.save_state(state)
            break

    # Reconcile disappearance separately from a close. A missing position
    # is not proof of an exit: only a broker history deal can establish P/L.
    # Emit one diagnostic per tracked position per process if it is absent
    # from the current position snapshot and no exit deal is present in history.
    active_position_ids = {
        int(
            getattr(position, "identifier", 0)
            or getattr(position, "ticket", 0)
            or 0
        )
        for position in active_positions
        if str(getattr(position, "symbol", "") or "") == symbol
        and int(getattr(position, "magic", 0) or 0) == magic
        and int(
            getattr(position, "identifier", 0)
            or getattr(position, "ticket", 0)
            or 0
        ) > 0
    }
    observed_exit_positions = {
        int(getattr(deal, "position_id", 0) or 0)
        for deal in deals
        if int(getattr(deal, "entry", -1)) != mt5.DEAL_ENTRY_IN
        and int(getattr(deal, "position_id", 0) or 0) > 0
    }
    for position_id in sorted(tracked_positions - active_position_ids - observed_exit_positions):
        marker = f"POSITION_RECONCILIATION_GAP:{position_id}"
        if marker in state["order_states"]:
            continue
        state["order_states"].add(marker)
        runner.log_event({
            "event": "POSITION_RECONCILIATION_GAP",
            "version": cfg.VERSION,
            "symbol": symbol,
            "position": position_id,
            "reason": "POSITION_ABSENT_WITHOUT_BROKER_EXIT_DEAL",
            "history_start_utc": _RUN_STARTED_UTC.isoformat(),
            "history_end_utc": datetime.now(timezone.utc).isoformat(),
            "diagnostic_only": True,
            "closed": False,
            "pnl": None,
            "canonical": False,
        })
        runner.save_state(state)

runner.enforce_pending_order_expiry=_run_scoped_pending
runner.monitor_pending_order_lifecycle=_run_scoped_pending_lifecycle
runner.monitor_position_lifecycle=trail_positions
runner.monitor_symbol_lifecycle=_run_scoped_symbol_lifecycle

def _v3_main():
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
