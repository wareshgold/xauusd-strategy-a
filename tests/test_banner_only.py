"""Offline tests for the forward runner's --banner-only mode.

Research/infrastructure only: proves --banner-only sends exactly the same
startup text a real session sends (via the shared _build_banner_text
helper), exits non-zero when Telegram fails, and never touches the runner
lock or the scan loop.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = "run_sp2l_author_replica_multi_symbol_forward_test"


def load_runner(monkeypatch, tmp_path, fake_mt5):
    monkeypatch.setitem(sys.modules, "MetaTrader5", fake_mt5)
    sys.modules.pop(f"scripts.{RUNNER}", None)
    sys.modules.pop(RUNNER, None)
    sys.modules.pop("live_mt5_gateway", None)
    for p in (str(ROOT), str(ROOT / "scripts")):
        if p not in sys.path:
            sys.path.insert(0, p)
    before = dict(__import__("os").environ)
    mod = importlib.import_module(RUNNER)
    # runner import has module-level env side effects; undo them
    for key in set(__import__("os").environ) - set(before):
        __import__("os").environ.pop(key, None)
    monkeypatch.setattr(mod, "EVENTS", tmp_path / "events.jsonl")
    monkeypatch.setattr(mod, "STATE_FILE", tmp_path / "state.json")
    sent = []
    monkeypatch.setattr(
        mod.gateway, "send_telegram_message",
        lambda text, parse_mode=None: sent.append(text)
        or SimpleNamespace(success=True, detail="TEST"),
    )
    return mod, sent


def fake_mt5_env():
    mt5 = SimpleNamespace(
        TIMEFRAME_M1=1, ORDER_TYPE_BUY=0, ORDER_TYPE_SELL=1,
        ORDER_TYPE_BUY_LIMIT=2, ORDER_TYPE_SELL_LIMIT=3,
        TRADE_ACTION_PENDING=5, TRADE_ACTION_REMOVE=4,
        TRADE_RETCODE_DONE=10009,
    )
    mt5.initialize = lambda path=None: True
    mt5.shutdown = lambda: None
    mt5.symbol_info = lambda s: SimpleNamespace(
        digits=2, point=0.01, trade_mode=4, volume_min=0.01,
        volume_step=0.01, volume_max=100.0,
    )
    mt5.symbol_info_tick = lambda s: None
    mt5.symbol_select = lambda s, e: True
    mt5.orders_get = lambda symbol=None: []
    mt5.positions_get = lambda symbol=None: []
    mt5.history_deals_get = lambda *a, **k: []
    mt5.history_orders_get = lambda *a, **k: []
    mt5.account_info = lambda: SimpleNamespace(
        trade_mode=0, login=812930, server="OtetGroup-MT5",
    )
    mt5.symbols_get = lambda: [SimpleNamespace(name="XAUUSD.ecn")]
    mt5.last_error = lambda: (0, "")
    return mt5


def test_banner_only_sends_real_banner(monkeypatch, tmp_path, capsys):
    fake = fake_mt5_env()
    mod, sent = load_runner(monkeypatch, tmp_path, fake)
    monkeypatch.setattr(sys, "argv", [RUNNER, "--banner-only"])
    code = mod.run_banner_only()
    assert code == 0
    assert len(sent) == 1
    banner = sent[0]
    assert "SP2L Forward Test — started" in banner
    assert "XAUUSD.ecn" in banner
    assert "Execution:" in banner
    assert "RESEARCH / DEMO ONLY" in banner
    # identical to the helper a real start uses
    account = fake.account_info()
    assert banner == mod._build_banner_text(account, [
        {"symbol": "XAUUSD.ecn", "volume": mod.VOLUME}
    ])
    events = (tmp_path / "events.jsonl").read_text(encoding="utf-8")
    assert "BANNER_ONLY_TELEGRAM" in events


def test_banner_only_failing_telegram_exits_nonzero(monkeypatch, tmp_path):
    fake = fake_mt5_env()
    mod, sent = load_runner(monkeypatch, tmp_path, fake)
    monkeypatch.setattr(
        mod.gateway, "send_telegram_message",
        lambda text, parse_mode=None: SimpleNamespace(success=False, detail="HTTP_401"),
    )
    code = mod.run_banner_only()
    assert code == 1


def test_banner_only_never_acquires_lock_or_scans(monkeypatch, tmp_path):
    fake = fake_mt5_env()
    mod, sent = load_runner(monkeypatch, tmp_path, fake)

    def _boom():
        raise AssertionError("scan loop must not start in --banner-only")

    monkeypatch.setattr(mod, "acquire_runner_lock", _boom)
    monkeypatch.setattr(mod, "monitor_symbol_lifecycle", _boom)
    monkeypatch.setattr(mod, "enforce_pending_order_expiry", _boom)
    monkeypatch.setattr(sys, "argv", [RUNNER, "--banner-only"])
    code = mod.run_banner_only()
    assert code == 0 and len(sent) == 1


def test_main_routes_banner_only_without_loop(monkeypatch, tmp_path):
    fake = fake_mt5_env()
    mod, sent = load_runner(monkeypatch, tmp_path, fake)
    monkeypatch.setattr(sys, "argv", [RUNNER, "--banner-only"])
    called = []
    monkeypatch.setattr(mod, "run_banner_only", lambda: called.append(1) or 0)
    with pytest.raises(SystemExit) as exc:
        mod.main()
    assert exc.value.code == 0 and called == [1]
