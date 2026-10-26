"""Offline regression tests for the V3 RR2/TRAIL4 pending-order lifecycle.

Pending TTL uses order setup and advancing MT5 tick timestamps in the same
broker clock domain. No host/server offset or live MT5 order mutation is used.
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
    # Tests model a broker clock offset from host time; both MT5 timestamps share it.
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


def test_ttl_uses_broker_timestamp_domain_without_host_offset(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    # Deliberately use a timestamp unrelated to host UTC; only order/tick
    # timestamps in the same broker domain determine the elapsed duration.
    broker_now = 2_000_000_000
    m.symbol_info_tick = lambda symbol: SimpleNamespace(time=broker_now)
    monkeypatch.setattr(mod, "_PENDING_CLOCK_LAST_TICK_TIME", broker_now - 1)
    pending = order(ticket=148, age_minutes=31)
    pending.time_setup = broker_now - 31 * 60
    m.orders_get = lambda symbol=None: [pending]
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == [148]


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


def test_missing_tick_timestamp_fails_closed_and_logs_once(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    m.orders_get = lambda symbol=None: [order(ticket=126, age_minutes=120)]
    m.symbol_info_tick = lambda symbol: None
    cancelled = []
    events = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    monkeypatch.setattr(mod.runner, "log_event", lambda event: events.append(event))
    s = state()
    config = {"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}
    mod._run_scoped_pending(config, s)
    mod._run_scoped_pending(config, s)
    assert cancelled == []
    skipped = [e for e in events if e["event"] == "PENDING_ORDER_TTL_SKIPPED"]
    assert len(skipped) == 1
    assert skipped[0]["reason"] == "ORDER_CLOCK_UNAVAILABLE"


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
    broker_now = int(time.time() + 3 * 3600)
    m.symbol_info_tick = lambda symbol: SimpleNamespace(time=broker_now)
    monkeypatch.setattr(mod, "_PENDING_CLOCK_LAST_TICK_TIME", broker_now - 1)
    pending = order(ticket=130, age_minutes=0)
    pending.time_setup = broker_now + 60
    m.orders_get = lambda symbol=None: [pending]
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []


def test_mt5_order_query_failure_fails_closed(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    m.orders_get = lambda symbol=None: None
    tick_calls = []
    m.symbol_info_tick = lambda symbol: tick_calls.append(symbol)
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []
    assert tick_calls == []


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


def test_deal_lifecycle_timestamp_uses_utc_then_iran_time(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    from datetime import datetime, timezone

    deal_time = int(datetime(2026, 10, 13, 4, 2, 8, tzinfo=timezone.utc).timestamp())
    deal = SimpleNamespace(
        ticket=62474707, position_id=63282226, entry=m.DEAL_ENTRY_IN,
        type=m.DEAL_TYPE_BUY, time=deal_time, price=4159.75, volume=0.01,
        profit=0.0, commission=0.0, swap=0.0, reason=0,
    )
    # A broker offset must not be subtracted from an already-UTC deal epoch.
    monkeypatch.setattr(mod.runner, "mt5_server_offset", lambda: timedelta(hours=3))
    message = mod.runner.lifecycle_message(deal, SYMBOL, 0.01, MAGIC)
    assert "07:32:08 (UTC+3:30) · 2026-10-13" in message


def test_lifecycle_retries_failed_open_before_sending_close(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    run_epoch = int(time.time()) + 10
    entry = SimpleNamespace(
        ticket=100, order=500, position_id=900, entry=m.DEAL_ENTRY_IN,
        reason=0, time=run_epoch, price=2300.0, volume=0.01, profit=0.0,
        commission=0.0, swap=0.0, magic=MAGIC, type=m.DEAL_TYPE_BUY,
    )
    close = SimpleNamespace(
        ticket=101, order=501, position_id=900, entry=m.DEAL_ENTRY_OUT,
        reason=1, time=run_epoch + 1, price=2301.0, volume=0.01, profit=1.0,
        commission=-0.05, swap=0.0, magic=MAGIC, type=m.DEAL_TYPE_SELL,
    )
    m.history_deals_get = lambda *args, **kwargs: [close, entry]
    monkeypatch.setattr(mod.runner, "_remember_position_links", lambda s, d: None)
    monkeypatch.setattr(mod.runner, "position_entry_price", lambda d, magic=None: 2300.0)
    monkeypatch.setattr(
        mod.runner, "lifecycle_message",
        lambda d, symbol, pip, magic=None: f"{'OPENED' if d.entry == m.DEAL_ENTRY_IN else 'CLOSED'}:{d.ticket}",
    )
    attempts = iter([
        SimpleNamespace(success=False, detail="HTTP timeout"),
        SimpleNamespace(success=True, detail="HTTP_200"),
        SimpleNamespace(success=True, detail="HTTP_200"),
    ])
    sent = []

    def send(message, **kwargs):
        sent.append(message)
        return next(attempts)

    monkeypatch.setattr(mod.runner.gateway, "send_telegram_message", send)
    monkeypatch.setattr(mod.runner, "log_event", lambda event: None)
    saved = []
    monkeypatch.setattr(mod.runner, "save_state", lambda s: saved.append(set(s["deals"])))
    s = state()
    s["orders"].add(500)
    s["positions"].add(900)
    config = {"symbol": SYMBOL, "magic": MAGIC, "pip_size": 0.01}

    mod._run_scoped_symbol_lifecycle(config, s)
    assert sent == ["OPENED:100"], "failed OPENED must prevent CLOSED overtaking it"
    assert s["deals"] == set()

    mod._run_scoped_symbol_lifecycle(config, s)
    assert sent == ["OPENED:100", "OPENED:100", "CLOSED:101"]
    assert s["deals"] == {100, 101}
    assert saved[-2:] == [{100}, {100, 101}], "persist each acknowledged lifecycle post"

def test_pending_signal_message_explicitly_says_not_filled(monkeypatch, tmp_path):
    mod, _ = load_v3(monkeypatch, tmp_path)
    sent = []
    monkeypatch.setattr(
        mod.runner.gateway, "send_telegram_message",
        lambda message, **kwargs: sent.append(message) or SimpleNamespace(success=True, detail="ok"),
    )
    candidate = {
        "symbol": SYMBOL, "direction": "BUY", "trigger_time": int(time.time()),
        "risk": 2.0, "theoretical_entry": 2300.0, "sl": 2298.0,
        "tp": 2304.0, "secondary_entry_2x": 2299.0, "volume": 0.01,
        "signal_id": "test-signal",
    }
    result = mod.runner.send_signal(candidate, 0.01, order_ticket=456)
    assert result.success is True
    assert "PENDING ORDER ACCEPTED (NOT FILLED)" in sent[0]
    assert "Pending Limit ACCEPTED" in sent[0]


def test_execution_blocked_message_reports_no_order(monkeypatch, tmp_path):
    mod, _ = load_v3(monkeypatch, tmp_path)
    sent = []
    monkeypatch.setattr(
        mod.runner.gateway, "send_telegram_message",
        lambda message, **kwargs: sent.append(message) or SimpleNamespace(success=True, detail="ok"),
    )
    candidate = {"symbol": SYMBOL, "direction": "SELL", "signal_id": "blocked-signal"}
    result = mod.runner.send_execution_blocked(
        candidate, {"reason": "LIMIT_ENTRY_NOT_PLACEABLE_AT_CURRENT_MARKET"}
    )
    assert result.success is True
    assert "ORDER NOT PLACED" in sent[0]
    assert "LIMIT_ENTRY_NOT_PLACEABLE_AT_CURRENT_MARKET" in sent[0]
    assert "No pending order accepted" in sent[0]
    assert "\\n" not in sent[0], "message must not contain literal backslash-n sequences"
    assert sent[0].count("\n") >= 4, "message fields should be separated by actual newlines"




def test_lifecycle_history_query_failure_defers_telegram(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    m.history_orders_get = lambda **kwargs: []
    m.history_deals_get = lambda **kwargs: None
    events = []
    monkeypatch.setattr(mod.runner, "log_event", events.append)
    monkeypatch.setattr(mod.runner, "save_state", lambda current: None)
    s = state()
    s["orders"].add(123)

    mod._run_scoped_symbol_lifecycle(
        {"symbol": SYMBOL, "magic": MAGIC, "pip_size": 0.01}, s
    )

    assert any(e.get("event") == "MT5_DEAL_HISTORY_QUERY_FAILED" for e in events)
    assert not any(e.get("event") == "TELEGRAM_DEAL_LIFECYCLE" for e in events)
    assert not s["deals"]


def test_lifecycle_suppresses_stale_deal_returned_outside_query_window(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    stale = SimpleNamespace(
        ticket=987, order=123, position_id=0,
        time=int(time.time()) - 120,
        symbol=SYMBOL, entry=0, price=2300.0,
    )
    m.history_orders_get = lambda **kwargs: []
    m.history_deals_get = lambda **kwargs: [stale] if kwargs == {"ticket": 123} else []
    events = []
    monkeypatch.setattr(mod.runner, "log_event", events.append)
    monkeypatch.setattr(mod.runner, "save_state", lambda current: None)
    s = state()
    s["orders"].add(123)

    mod._run_scoped_symbol_lifecycle(
        {"symbol": SYMBOL, "magic": MAGIC, "pip_size": 0.01}, s
    )

    assert 987 in s["deals"]
    assert any(e.get("event") == "TELEGRAM_STALE_DEAL_SUPPRESSED" for e in events)
    assert not any(e.get("event") == "TELEGRAM_DEAL_LIFECYCLE" for e in events)
