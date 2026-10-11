"""Offline regression tests for the V3 RR2/TRAIL4 pending-order lifecycle.

Covers tick freshness and an operator-pinned broker offset; no MT5 connection
or order_send call is allowed in these tests.
"""
from __future__ import annotations

import importlib
import sys
import time
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
V3 = "run_sp2l_v3_xauusd_forward_test"
BASE = "run_sp2l_author_replica_multi_symbol_forward_test"
MAGIC = 26092201
SYMBOL = "XAUUSD.ecn"


def fake_mt5():
    m = SimpleNamespace(
        TIMEFRAME_M1=1,
        ORDER_TYPE_BUY=0, ORDER_TYPE_SELL=1,
        ORDER_TYPE_BUY_LIMIT=2, ORDER_TYPE_SELL_LIMIT=3,
        ORDER_TYPE_BUY_STOP=4, ORDER_TYPE_SELL_STOP=5,
        POSITION_TYPE_BUY=0, POSITION_TYPE_SELL=1,
        TRADE_ACTION_REMOVE=4, TRADE_ACTION_SLTP=6,
        TRADE_RETCODE_DONE=10009, ORDER_STATE_PLACED=1,
        DEAL_ENTRY_IN=0, DEAL_ENTRY_OUT=1,
        DEAL_TYPE_BUY=0, DEAL_TYPE_SELL=1,
        TRADE_ACTION_PENDING=5,
    )
    m.orders_get = lambda symbol=None: []
    m.history_orders_get = lambda *args, **kwargs: []
    m.history_deals_get = lambda *args, **kwargs: []
    m.positions_get = lambda symbol=None: []
    m.symbols_get = lambda: []
    m.symbol_info = lambda symbol: SimpleNamespace(digits=2, point=0.01)
    m.symbol_info_tick = lambda symbol: None
    m.account_info = lambda: SimpleNamespace(trade_mode=0)
    m.order_send = lambda request: (_ for _ in ()).throw(
        AssertionError("offline lifecycle test must never send an MT5 order")
    )
    return m


def load_v3(monkeypatch, tmp_path):
    m = fake_mt5()
    monkeypatch.setitem(sys.modules, "MetaTrader5", m)
    for name in (V3, BASE, "sp2l_v3_rr2_trail4_config", "live_mt5_gateway"):
        sys.modules.pop(name, None)
    for path in (str(ROOT), str(ROOT / "scripts")):
        if path not in sys.path:
            sys.path.insert(0, path)
    mod = importlib.import_module(V3)
    monkeypatch.setattr(mod.runner, "EVENTS", tmp_path / "events.jsonl")
    monkeypatch.setattr(mod.runner, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setenv("SP2L_PENDING_SERVER_OFFSET_HOURS", "3")
    # Normal-path tests start with a previously observed tick, then provide a
    # newer broker timestamp. Dedicated tests below cover cold/stale startup.
    broker_tick_time = int(time.time() + 3 * 3600)
    m.symbol_info_tick = lambda symbol: SimpleNamespace(time=broker_tick_time)
    monkeypatch.setattr(mod, "_PENDING_CLOCK_LAST_TICK_TIME", broker_tick_time - 1)
    return mod, m


def state():
    return {
        "seen": {}, "notified": set(), "deals": set(), "orders": set(),
        "positions": set(), "order_states": set(), "position_orders": {},
        "signal_orders": {}, "pending_signal_notifications": {},
    }


def order(ticket=123, *, magic=MAGIC, age_minutes=31, order_type=2):
    # Tests model a broker clock that is UTC+3; time_setup is on that clock.
    return SimpleNamespace(
        ticket=ticket, symbol=SYMBOL, magic=magic, type=order_type,
        time_setup=int(time.time() + 3 * 3600 - age_minutes * 60),
        time_done=0, state=1, position_id=0,
        volume_initial=0.01, volume_current=0.01,
        price_open=2300.0, price_current=2300.0, sl=2298.0, tp=2304.0,
    )


def test_expired_owned_order_is_cancelled_once(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    pending = order(ticket=123, age_minutes=31)
    m.orders_get = lambda symbol=None: [pending]
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: timedelta(hours=3))
    cancelled = []
    def cancel(o, s):
        cancelled.append(o.ticket)
        s["order_states"].add(f"{o.ticket}:EXPIRY_NOTIFIED:CANCELLED")
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", cancel)
    s = state()
    config = {"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}
    mod._run_scoped_pending(config, s)
    mod._run_scoped_pending(config, s)
    assert cancelled == [123]



def test_failed_expiry_attempt_is_retried(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    pending = order(ticket=131, age_minutes=90)
    m.orders_get = lambda symbol=None: [pending]
    broker_time = int(time.time() + 3 * 3600)
    tick_times = iter([broker_time, broker_time + 1])
    m.symbol_info_tick = lambda symbol: SimpleNamespace(time=next(tick_times))
    monkeypatch.setattr(mod, "_PENDING_CLOCK_LAST_TICK_TIME", broker_time - 1)
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: timedelta(hours=3))
    attempts = []

    def failed_cancel(o, s):
        attempts.append(o.ticket)
        s["order_states"].add(f"{o.ticket}:EXPIRY_NOTIFIED:CANCEL_FAILED(10006)")

    monkeypatch.setattr(mod.runner, "_cancel_pending_order", failed_cancel)
    s = state()
    config = {"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}
    mod._run_scoped_pending(config, s)
    mod._run_scoped_pending(config, s)

    assert attempts == [131, 131], "failed cancellation must remain retryable"


def test_recent_owned_order_is_not_cancelled(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    m.orders_get = lambda symbol=None: [order(ticket=124, age_minutes=5)]
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: timedelta(hours=3))
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []


def test_foreign_magic_order_is_never_cancelled(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    m.orders_get = lambda symbol=None: [order(ticket=125, magic=MAGIC + 1, age_minutes=90)]
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: timedelta(hours=3))
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []


def test_unknown_server_clock_fails_closed(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    m.orders_get = lambda symbol=None: [order(ticket=126, age_minutes=120)]
    def no_clock():
        raise RuntimeError("no fresh server tick")
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", no_clock)
    cancelled = []
    events = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    monkeypatch.setattr(mod.runner, "log_event", lambda event: events.append(event))
    s = state()
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, s)
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, s)
    assert cancelled == []
    assert len([e for e in events if e["event"] == "PENDING_ORDER_TTL_SKIPPED"]) == 1


def test_active_owned_order_is_reconciled_for_lifecycle_without_signal_replay(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    pending = order(ticket=127, age_minutes=5)
    m.orders_get = lambda symbol=None: [pending]
    m.history_orders_get = lambda *args, **kwargs: []
    events = []
    monkeypatch.setattr(mod.runner, "log_event", lambda event: events.append(event))
    s = state()
    assert not s["orders"]
    mod._run_scoped_pending_lifecycle({"symbol": SYMBOL, "magic": MAGIC}, s)
    assert 127 in s["orders"]
    lifecycle = [e for e in events if e["event"] == "PENDING_ORDER_LIFECYCLE"]
    assert len(lifecycle) == 1 and lifecycle[0]["order"] == 127
    assert lifecycle[0]["canonical"] is False


def test_foreign_active_order_is_not_adopted_by_lifecycle(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    m.orders_get = lambda symbol=None: [order(ticket=128, magic=MAGIC + 1, age_minutes=5)]
    m.history_orders_get = lambda *args, **kwargs: []
    events = []
    monkeypatch.setattr(mod.runner, "log_event", lambda event: events.append(event))
    s = state()
    mod._run_scoped_pending_lifecycle({"symbol": SYMBOL, "magic": MAGIC}, s)
    assert 128 not in s["orders"]
    assert not [e for e in events if e["event"] == "PENDING_ORDER_LIFECYCLE"]

def test_zero_setup_timestamp_is_never_cancelled(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    pending = order(ticket=129, age_minutes=120)
    pending.time_setup = 0
    m.orders_get = lambda symbol=None: [pending]
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: timedelta(hours=3))
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []


def test_future_setup_timestamp_is_never_cancelled(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    pending = order(ticket=130, age_minutes=0)
    pending.time_setup = int(time.time() + 3 * 3600 + 60)
    m.orders_get = lambda symbol=None: [pending]
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: timedelta(hours=3))
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []


def test_mt5_order_query_failure_fails_closed(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    m.orders_get = lambda symbol=None: None
    clock_calls = []
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: clock_calls.append(True))
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []
    assert clock_calls == []


def test_wrong_symbol_and_non_limit_orders_are_never_cancelled(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    wrong_symbol = order(ticket=131, age_minutes=120)
    wrong_symbol.symbol = "EURUSD"
    stop_order = order(ticket=132, age_minutes=120, order_type=m.ORDER_TYPE_BUY_STOP)
    m.orders_get = lambda symbol=None: [wrong_symbol, stop_order]
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: timedelta(hours=3))
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []


def test_lifecycle_does_not_adopt_active_stop_orders(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    stop_order = order(ticket=133, age_minutes=5, order_type=m.ORDER_TYPE_BUY_STOP)
    m.orders_get = lambda symbol=None: [stop_order]
    m.history_orders_get = lambda *args, **kwargs: []
    events = []
    monkeypatch.setattr(mod.runner, "log_event", lambda event: events.append(event))
    s = state()
    mod._run_scoped_pending_lifecycle({"symbol": SYMBOL, "magic": MAGIC}, s)
    assert 133 not in s["orders"]
    assert not [e for e in events if e["event"] == "PENDING_ORDER_LIFECYCLE"]


def test_cold_start_tick_is_not_enough_to_cancel_expired_order(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    broker_time = int(time.time() + 3 * 3600)
    m.symbol_info_tick = lambda symbol: SimpleNamespace(time=broker_time)
    monkeypatch.setattr(mod, "_PENDING_CLOCK_LAST_TICK_TIME", None)
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: timedelta(hours=3))
    m.orders_get = lambda symbol=None: [order(ticket=140, age_minutes=120)]
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []
    assert mod._PENDING_CLOCK_LAST_TICK_TIME == broker_time


def test_unchanged_stale_tick_fails_closed(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    stale_time = int(time.time() + 3 * 3600 - 3600)
    m.symbol_info_tick = lambda symbol: SimpleNamespace(time=stale_time)
    monkeypatch.setattr(mod, "_PENDING_CLOCK_LAST_TICK_TIME", stale_time)
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: timedelta(hours=3))
    m.orders_get = lambda symbol=None: [order(ticket=141, age_minutes=120)]
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []


def test_advancing_tick_allows_clock_revalidation_after_startup(monkeypatch, tmp_path):
    base_time = int(time.time() + 3 * 3600)
    tick_times = iter([base_time, base_time + 1])
    mod, m = load_v3(monkeypatch, tmp_path)
    m.symbol_info_tick = lambda symbol: SimpleNamespace(time=next(tick_times))
    monkeypatch.setattr(mod, "_PENDING_CLOCK_LAST_TICK_TIME", None)
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: timedelta(hours=3))
    m.orders_get = lambda symbol=None: [order(ticket=142, age_minutes=120)]
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    s = state()
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, s)
    assert cancelled == []
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, s)
    assert cancelled == [142]


def test_offset_mismatch_fails_closed_after_advancing_tick(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    broker_time = int(time.time() + 3 * 3600)
    m.symbol_info_tick = lambda symbol: SimpleNamespace(time=broker_time)
    monkeypatch.setattr(mod, "_PENDING_CLOCK_LAST_TICK_TIME", broker_time - 1)
    # Simulate a one-hour stale tick or unreviewed broker-clock shift.
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: timedelta(hours=2))
    m.orders_get = lambda symbol=None: [order(ticket=143, age_minutes=120)]
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []


def test_missing_pinned_offset_fails_closed(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    monkeypatch.delenv("SP2L_PENDING_SERVER_OFFSET_HOURS", raising=False)
    broker_time = int(time.time() + 3 * 3600)
    m.symbol_info_tick = lambda symbol: SimpleNamespace(time=broker_time)
    monkeypatch.setattr(mod, "_PENDING_CLOCK_LAST_TICK_TIME", broker_time - 1)
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: timedelta(hours=3))
    m.orders_get = lambda symbol=None: [order(ticket=144, age_minutes=120)]
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []



def test_advancing_but_stale_tick_fails_closed(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    # The timestamp advances between observations, but remains ten minutes
    # behind the operator-pinned server-time expectation.
    stale_time = int(time.time() + 3 * 3600 - 600)
    tick_times = iter([stale_time, stale_time + 1])
    m.symbol_info_tick = lambda symbol: SimpleNamespace(time=next(tick_times))
    monkeypatch.setattr(mod, "_PENDING_CLOCK_LAST_TICK_TIME", stale_time - 1)
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: timedelta(hours=3))
    m.orders_get = lambda symbol=None: [order(ticket=145, age_minutes=120)]
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    config = {"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}
    mod._run_scoped_pending(config, state())
    assert cancelled == []


def test_future_server_tick_timestamp_fails_closed(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    future_time = int(time.time() + 3 * 3600 + 600)
    m.symbol_info_tick = lambda symbol: SimpleNamespace(time=future_time)
    monkeypatch.setattr(mod, "_PENDING_CLOCK_LAST_TICK_TIME", future_time - 1)
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: timedelta(hours=3))
    m.orders_get = lambda symbol=None: [order(ticket=146, age_minutes=120)]
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending(
        {"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state()
    )
    assert cancelled == []


def test_invalid_pinned_offset_fails_closed(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    monkeypatch.setenv("SP2L_PENDING_SERVER_OFFSET_HOURS", "3.5")
    broker_time = int(time.time() + 3 * 3600)
    m.symbol_info_tick = lambda symbol: SimpleNamespace(time=broker_time)
    monkeypatch.setattr(mod, "_PENDING_CLOCK_LAST_TICK_TIME", broker_time - 1)
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: timedelta(hours=3))
    m.orders_get = lambda symbol=None: [order(ticket=147, age_minutes=120)]
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending(
        {"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state()
    )
    assert cancelled == []



def test_closed_market_session_clock_defers_candidate_and_retries(monkeypatch, tmp_path):
    mod, _ = load_v3(monkeypatch, tmp_path)
    candidate = {
        "trigger_time": int(mod._RUN_STARTED_UTC.timestamp() + 4 * 3600),
        "direction": "BUY",
    }
    monkeypatch.setattr(mod.runner, "find_latest_candidate", lambda data, symbol: candidate)
    clock_results = iter([
        RuntimeError("MT5 server offset unavailable: stale weekend tick"),
        timedelta(hours=3),
    ])

    def clock():
        result = next(clock_results)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", clock)
    events = []
    monkeypatch.setattr(mod.runner, "log_event", lambda event: events.append(event))
    observed = []

    def fake_original_main():
        observed.append(mod.runner.find_latest_candidate([], SYMBOL))
        observed.append(mod.runner.find_latest_candidate([], SYMBOL))

    monkeypatch.setattr(mod, "_original_main", fake_original_main)
    mod._v3_main()

    assert observed[0] is None, "stale clock must defer candidate execution"
    assert observed[1] == candidate, "runner must retry after clock becomes available"
    deferred = [event for event in events if event["event"] == "SESSION_CUTOFF_DEFERRED"]
    assert len(deferred) == 1
    assert deferred[0]["canonical"] is False
