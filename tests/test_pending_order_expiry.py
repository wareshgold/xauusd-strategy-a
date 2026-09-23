"""Offline tests for the pending-order expiry policy.

Research/infrastructure only: proves the expiry layer never touches foreign
orders or non-limit types, never sends a cancel request in DRY-RUN, requires
the DEMO account plus both operator flags for a real cancel, and is
idempotent (an already-expired ticket is never handled twice).
"""
from __future__ import annotations

import importlib
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
RUNNER = "run_sp2l_author_replica_multi_symbol_forward_test"

MAGIC = 26092201
SYMBOL = "XAUUSD.ecn"


def make_fake_mt5():
    mt5 = SimpleNamespace(
        TIMEFRAME_M1=1,
        ORDER_TYPE_BUY=0,
        ORDER_TYPE_SELL=1,
        ORDER_TYPE_BUY_LIMIT=2,
        ORDER_TYPE_SELL_LIMIT=3,
        TRADE_ACTION_PENDING=5,
        TRADE_ACTION_REMOVE=4,
        TRADE_RETCODE_DONE=10009,
        ORDER_STATE_PLACED=1,
    )
    mt5.orders_get = lambda symbol=None: []
    mt5.symbols_get = lambda: []
    mt5.symbol_info = lambda symbol: SimpleNamespace(digits=2, point=0.01)
    mt5.symbol_info_tick = lambda symbol: None
    mt5.account_info = lambda: SimpleNamespace(trade_mode=0)
    mt5.order_send = lambda request: (_ for _ in ()).throw(
        AssertionError("order_send must never be called in this scenario")
    )
    return mt5


def load_runner(monkeypatch, tmp_path, fake_mt5):
    monkeypatch.setitem(sys.modules, "MetaTrader5", fake_mt5)
    sys.modules.pop(f"scripts.{RUNNER}", None)
    sys.modules.pop(RUNNER, None)
    sys.modules.pop("live_mt5_gateway", None)
    for p in (str(ROOT), str(ROOT / "scripts")):
        if p not in sys.path:
            sys.path.insert(0, p)
    mod = importlib.import_module(RUNNER)
    monkeypatch.setattr(mod, "EVENTS", tmp_path / "events.jsonl")
    monkeypatch.setattr(mod, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(mod, "PENDING_TTL_MINUTES", 30.0)
    sent = []
    monkeypatch.setattr(
        mod.gateway, "send_telegram_message",
        lambda text, parse_mode=None: sent.append(text)
        or SimpleNamespace(success=True, detail="TEST"),
    )
    return mod, sent


def fresh_state():
    return {
        "seen": {}, "notified": set(), "deals": set(),
        "orders": set(), "positions": set(),
        "position_orders": {}, "order_states": set(),
    }


def pending_limit(ticket, age_minutes, magic=MAGIC, order_type=2):
    return SimpleNamespace(
        ticket=ticket, symbol=SYMBOL, magic=magic, type=order_type,
        time_setup=time.time() - age_minutes * 60,
        price_open=4318.60, sl=4320.23, tp=4316.97,
        state=1, volume_initial=0.01, volume_current=0.01,
    )


def scenario(monkeypatch, tmp_path, live="false", allow=None, account_mode=0):
    fake = make_fake_mt5()
    fake.account_info = lambda: SimpleNamespace(trade_mode=account_mode)
    monkeypatch.setenv("LIVE_TRADING_ENABLE", live)
    if allow is None:
        monkeypatch.delenv("ALLOW_REAL_EXECUTION", raising=False)
    else:
        monkeypatch.setenv("ALLOW_REAL_EXECUTION", allow)
    return fake


def test_dry_run_never_sends_cancel_but_notifies(monkeypatch, tmp_path):
    fake = scenario(monkeypatch, tmp_path, live="false")
    fake.orders_get = lambda symbol=None: [pending_limit(111, age_minutes=60)]
    mod, sent = load_runner(monkeypatch, tmp_path, fake)
    state = fresh_state()
    mod.enforce_pending_order_expiry({"symbol": SYMBOL, "magic": MAGIC}, state)
    assert sent, "expiry notice must be sent to Telegram"
    assert "EXPIRED" in sent[0]
    assert not state["order_states"] or any(
        s.startswith("111:EXPIRY_NOTIFIED:") for s in state["order_states"]
    )


def test_real_cancel_requires_demo_and_both_flags(monkeypatch, tmp_path):
    fake = scenario(monkeypatch, tmp_path, live="true", allow="true")
    calls = []
    fake.order_send = lambda request: calls.append(request)
    orjson = SimpleNamespace(retcode=10009, comment="")
    fake.order_send = lambda request: (calls.append(request), orjson)[1]
    fake.orders_get = lambda symbol=None: [pending_limit(112, age_minutes=60)]
    mod, sent = load_runner(monkeypatch, tmp_path, fake)
    state = fresh_state()
    mod.enforce_pending_order_expiry({"symbol": SYMBOL, "magic": MAGIC}, state)
    assert len(calls) == 1 and calls[0]["action"] == 4 and calls[0]["order"] == 112
    assert f"112:EXPIRY_NOTIFIED:CANCELLED" in state["order_states"]


def test_real_cancel_blocked_on_non_demo_account(monkeypatch, tmp_path):
    fake = scenario(monkeypatch, tmp_path, live="true", allow="true", account_mode=1)
    fake.orders_get = lambda symbol=None: [pending_limit(113, age_minutes=60)]
    mod, sent = load_runner(monkeypatch, tmp_path, fake)
    state = fresh_state()
    mod.enforce_pending_order_expiry({"symbol": SYMBOL, "magic": MAGIC}, state)
    assert any("113:EXPIRY_NOTIFIED:CANCEL_FAILED" in s for s in state["order_states"])
    assert sent and "CANCEL_FAILED" in sent[0]


def test_never_touches_foreign_orders_or_non_limit_types(monkeypatch, tmp_path):
    fake = scenario(monkeypatch, tmp_path, live="true", allow="true")
    fake.orders_get = lambda symbol=None: [
        pending_limit(114, age_minutes=60, magic=999),   # foreign magic
        pending_limit(115, age_minutes=60, order_type=0),  # market order
    ]
    mod, sent = load_runner(monkeypatch, tmp_path, fake)
    state = fresh_state()
    mod.enforce_pending_order_expiry({"symbol": SYMBOL, "magic": MAGIC}, state)
    assert not sent
    assert state["order_states"] == set()


def test_fresh_limit_order_is_untouched(monkeypatch, tmp_path):
    fake = scenario(monkeypatch, tmp_path, live="true", allow="true")
    fake.orders_get = lambda symbol=None: [pending_limit(116, age_minutes=5)]
    mod, sent = load_runner(monkeypatch, tmp_path, fake)
    state = fresh_state()
    mod.enforce_pending_order_expiry({"symbol": SYMBOL, "magic": MAGIC}, state)
    assert not sent and state["order_states"] == set()


def test_expiry_is_idempotent(monkeypatch, tmp_path):
    fake = scenario(monkeypatch, tmp_path, live="true", allow="true")
    fake.orders_get = lambda symbol=None: [pending_limit(117, age_minutes=60)]
    mod, sent = load_runner(monkeypatch, tmp_path, fake)
    state = fresh_state()
    state["order_states"].add("117:EXPIRY_NOTIFIED:CANCELLED")
    mod.enforce_pending_order_expiry({"symbol": SYMBOL, "magic": MAGIC}, state)
    assert not sent


def test_disabled_ttl_is_noop(monkeypatch, tmp_path):
    fake = scenario(monkeypatch, tmp_path, live="true", allow="true")
    fake.orders_get = lambda symbol=None: [pending_limit(118, age_minutes=999)]
    mod, sent = load_runner(monkeypatch, tmp_path, fake)
    monkeypatch.setattr(mod, "PENDING_TTL_MINUTES", 0.0)
    state = fresh_state()
    mod.enforce_pending_order_expiry({"symbol": SYMBOL, "magic": MAGIC}, state)
    assert not sent and state["order_states"] == set()


def test_expiry_event_logged(monkeypatch, tmp_path):
    fake = scenario(monkeypatch, tmp_path, live="false")
    fake.orders_get = lambda symbol=None: [pending_limit(119, age_minutes=45)]
    mod, sent = load_runner(monkeypatch, tmp_path, fake)
    state = fresh_state()
    mod.enforce_pending_order_expiry({"symbol": SYMBOL, "magic": MAGIC}, state)
    lines = (tmp_path / "events.jsonl").read_text(encoding="utf-8").strip().splitlines()
    events = [json.loads(l) for l in lines]
    expired = [e for e in events if e["event"] == "PENDING_ORDER_EXPIRED"]
    assert expired and expired[0]["order"] == 119 and expired[0]["canonical"] is False
    assert expired[0]["outcome"] == "CANCELLED" and expired[0]["cancel"]["dry_run"] is True
