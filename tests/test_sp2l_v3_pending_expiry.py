"""Offline regression tests for the V3 RR2/TRAIL4 pending-order lifecycle.

Pending TTL tests use MT5 Unix-epoch timestamps directly; no MT5 connection
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
    # Shared session-clock tests may use this mocked broker-time tick; TTL tests do not.
    broker_tick_time = int(time.time() + 3 * 3600)
    m.symbol_info_tick = lambda symbol: SimpleNamespace(time=broker_tick_time)
    return mod, m


def state():
    return {
        "seen": {}, "notified": set(), "deals": set(), "orders": set(),
        "positions": set(), "order_states": set(), "position_orders": {},
        "signal_orders": {}, "pending_signal_notifications": {},
    }


def order(ticket=123, *, magic=MAGIC, age_minutes=31, order_type=2):
    # MT5 time_setup is a Unix-epoch timestamp; broker display offset is irrelevant.
    return SimpleNamespace(
        ticket=ticket, symbol=SYMBOL, magic=magic, type=order_type,
        time_setup=int(time.time() - age_minutes * 60),
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
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []


def test_foreign_magic_order_is_never_cancelled(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    m.orders_get = lambda symbol=None: [order(ticket=125, magic=MAGIC + 1, age_minutes=90)]
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []


def test_expiry_does_not_depend_on_tick_or_server_offset(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    pending = order(ticket=126, age_minutes=120)
    m.orders_get = lambda symbol=None: [pending]
    m.symbol_info_tick = lambda symbol: None
    monkeypatch.setattr(mod.runner, "mt5_server_offset_strict", lambda: (_ for _ in ()).throw(RuntimeError("offset unavailable")))
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == [126]


def test_ttl_boundary_does_not_cancel_before_expiry(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    pending = order(ticket=135, age_minutes=29)
    m.orders_get = lambda symbol=None: [pending]
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []


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
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []


def test_future_setup_timestamp_is_never_cancelled(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    pending = order(ticket=130, age_minutes=0)
    pending.time_setup = int(time.time() + 60)
    m.orders_get = lambda symbol=None: [pending]
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []


def test_mt5_order_query_failure_fails_closed(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    m.orders_get = lambda symbol=None: None
    cancelled = []
    monkeypatch.setattr(mod.runner, "_cancel_pending_order", lambda o, s: cancelled.append(o.ticket))
    mod._run_scoped_pending({"symbol": SYMBOL, "magic": MAGIC, "pending_ttl_minutes": 30}, state())
    assert cancelled == []


def test_wrong_symbol_and_non_limit_orders_are_never_cancelled(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    wrong_symbol = order(ticket=131, age_minutes=120)
    wrong_symbol.symbol = "EURUSD"
    wrong_magic = order(ticket=132, magic=MAGIC + 1, age_minutes=120)
    stop_order = order(ticket=133, age_minutes=120, order_type=m.ORDER_TYPE_BUY_STOP)
    m.orders_get = lambda symbol=None: [wrong_symbol, wrong_magic, stop_order]
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
    entry = SimpleNamespace(
        ticket=100, order=500, position_id=900, entry=m.DEAL_ENTRY_IN,
        reason=0, time=100, price=2300.0, volume=0.01, profit=0.0,
        commission=0.0, swap=0.0, magic=MAGIC, type=m.DEAL_TYPE_BUY,
    )
    close = SimpleNamespace(
        ticket=101, order=501, position_id=900, entry=m.DEAL_ENTRY_OUT,
        reason=1, time=101, price=2301.0, volume=0.01, profit=1.0,
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

def test_blocked_execution_notification_is_queued_when_telegram_fails(monkeypatch, tmp_path):
    mod, _ = load_v3(monkeypatch, tmp_path)
    candidate = {"symbol": SYMBOL, "direction": "BUY", "signal_id": "blocked-1"}
    result = {"reason": "VOLUME_BELOW_MIN", "comment": "requested_volume=0.01"}
    sent = []
    events = []
    monkeypatch.setattr(mod.runner, "send_execution_blocked", lambda c, r: sent.append((c, r)) or SimpleNamespace(success=False, detail="HTTP timeout"))
    monkeypatch.setattr(mod.runner, "log_event", lambda event: events.append(event))
    s = state()

    assert mod.runner.notify_execution_blocked(candidate, result, "blocked-1", s) is False
    assert len(sent) == 1
    assert s["pending_execution_notifications"]["blocked-1"] == {"candidate": candidate, "result": result}
    assert events[-1]["event"] == "TELEGRAM_EXECUTION_BLOCKED"
    assert events[-1]["success"] is False

def test_blocked_execution_notification_success_clears_retry_queue(monkeypatch, tmp_path):
    mod, _ = load_v3(monkeypatch, tmp_path)
    candidate = {"symbol": SYMBOL, "direction": "SELL", "signal_id": "blocked-2"}
    result = {"reason": "ORDER_REJECTED"}
    events = []
    monkeypatch.setattr(mod.runner, "send_execution_blocked", lambda c, r: SimpleNamespace(success=True, detail="HTTP_200"))
    monkeypatch.setattr(mod.runner, "log_event", lambda event: events.append(event))
    s = state()
    s["pending_execution_notifications"] = {"blocked-2": {"candidate": candidate, "result": result}}

    assert mod.runner.notify_execution_blocked(candidate, result, "blocked-2", s) is True
    assert "blocked-2" not in s["pending_execution_notifications"]
    assert events[-1]["event"] == "TELEGRAM_EXECUTION_BLOCKED"
    assert events[-1]["success"] is True

def test_existing_owned_position_is_adopted_and_close_result_is_not_lost_after_restart(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    # MT5 position ticket may differ from the stable identifier referenced by deals.
    active = SimpleNamespace(ticket=9991, identifier=9001, symbol=SYMBOL, magic=MAGIC)
    close_deal = SimpleNamespace(
        ticket=9101, time=int(time.time()), order=9201, position_id=9001,
        entry=1, reason=0, price=2297.0, profit=-3.0, commission=0.0, swap=0.0,
        volume=0.01,
    )
    m.positions_get = lambda symbol=None: [active]
    m.history_deals_get = lambda *args, **kwargs: []
    s = state()
    cfg = {"symbol": SYMBOL, "magic": MAGIC, "pip_size": 0.01}

    # First poll after restart: adopt the exact owned open position.
    mod._run_scoped_symbol_lifecycle(cfg, s)
    assert 9001 in s["positions"]

    # Later the position has closed. Its exit deal must still be eligible.
    m.positions_get = lambda symbol=None: []
    m.history_deals_get = lambda *args, **kwargs: [close_deal]
    monkeypatch.setattr(mod.runner, "position_entry_price", lambda deal, magic: 2300.0)
    monkeypatch.setattr(mod.runner, "lifecycle_message", lambda *args, **kwargs: "CLOSED result")
    sent = []
    monkeypatch.setattr(
        mod.runner.gateway, "send_telegram_message",
        lambda message, **kwargs: sent.append(message) or SimpleNamespace(success=True, detail="HTTP_200"),
    )
    monkeypatch.setattr(mod.runner, "log_event", lambda event: None)
    monkeypatch.setattr(mod.runner, "save_state", lambda state: None)

    mod._run_scoped_symbol_lifecycle(cfg, s)
    assert sent == ["CLOSED result"]
    assert 9101 in s["deals"]

def test_missing_tracked_position_emits_one_diagnostic_without_fabricating_close(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    cfg = {"symbol": SYMBOL, "magic": MAGIC, "pip_size": 0.01}
    s = state()
    s["orders"].add(9301)
    s["positions"].add(9401)
    m.positions_get = lambda symbol=None: []
    m.history_deals_get = lambda *args, **kwargs: []
    events = []
    monkeypatch.setattr(mod.runner, "log_event", lambda event: events.append(event))
    monkeypatch.setattr(mod.runner, "save_state", lambda state: None)
    sent = []
    monkeypatch.setattr(
        mod.runner.gateway, "send_telegram_message",
        lambda *args, **kwargs: sent.append(args) or SimpleNamespace(success=True, detail="HTTP_200"),
    )

    mod._run_scoped_symbol_lifecycle(cfg, s)
    mod._run_scoped_symbol_lifecycle(cfg, s)

    gaps = [event for event in events if event.get("event") == "POSITION_RECONCILIATION_GAP"]
    assert len(gaps) == 1
    assert gaps[0]["position"] == 9401
    assert gaps[0]["reason"] == "POSITION_ABSENT_WITHOUT_BROKER_EXIT_DEAL"
    assert gaps[0]["diagnostic_only"] is True
    assert gaps[0]["closed"] is False
    assert gaps[0]["pnl"] is None
    assert sent == []
    assert "POSITION_RECONCILIATION_GAP:9401" in s["order_states"]

def test_broker_exit_deal_prevents_missing_position_gap(monkeypatch, tmp_path):
    mod, m = load_v3(monkeypatch, tmp_path)
    cfg = {"symbol": SYMBOL, "magic": MAGIC, "pip_size": 0.01}
    s = state()
    s["orders"].add(9501)
    s["positions"].add(9402)
    exit_deal = SimpleNamespace(
        ticket=9601, time=int(time.time()), order=9501, position_id=9402,
        entry=1, reason=0, price=2297.0, profit=-3.0, commission=0.0, swap=0.0,
        volume=0.01,
    )
    m.positions_get = lambda symbol=None: []
    m.history_deals_get = lambda *args, **kwargs: [exit_deal]
    monkeypatch.setattr(mod.runner, "position_entry_price", lambda deal, magic: 2300.0)
    monkeypatch.setattr(mod.runner, "lifecycle_message", lambda *args, **kwargs: "CLOSED result")
    monkeypatch.setattr(
        mod.runner.gateway, "send_telegram_message",
        lambda *args, **kwargs: SimpleNamespace(success=True, detail="HTTP_200"),
    )
    events = []
    monkeypatch.setattr(mod.runner, "log_event", lambda event: events.append(event))
    monkeypatch.setattr(mod.runner, "save_state", lambda state: None)

    mod._run_scoped_symbol_lifecycle(cfg, s)

    assert any(event.get("event") == "TELEGRAM_DEAL_LIFECYCLE" for event in events)
    assert not any(event.get("event") == "POSITION_RECONCILIATION_GAP" for event in events)

