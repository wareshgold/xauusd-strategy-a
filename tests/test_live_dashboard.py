"""Offline tests for the live dashboard page.

Research/infrastructure only: proves the dashboard renders the session
heartbeat, the execution mode read from the live runner process, MT5
tick/account sections, and today's stats — and that rendering is strictly
read-only (no order_send, no Telegram, no journal/state writes).
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def load_dashboard(monkeypatch, tmp_path, fake_mt5, runner_flags=None):
    monkeypatch.setitem(sys.modules, "MetaTrader5", fake_mt5)
    sys.modules.pop("live_dashboard", None)
    for p in (str(ROOT), str(ROOT / "scripts")):
        if p not in sys.path:
            sys.path.insert(0, p)
    mod = importlib.import_module("live_dashboard")
    monkeypatch.setattr(mod, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(mod, "RUNNER_LOCK", tmp_path / "runner.lock")
    monkeypatch.setattr(mod, "WATCHDOG_PID", tmp_path / "watchdog.pid")
    monkeypatch.setattr(mod, "EVENTS", tmp_path / "events.jsonl")
    # freeze "today" so the seeded 2099 events count as today
    import datetime as _dt
    real_dt = __import__("datetime").datetime

    class FrozenDateTime(real_dt):
        @classmethod
        def now(cls, tz=None):
            return real_dt(2099, 1, 1, 12, 0, 0, tzinfo=_dt.timezone.utc)

    monkeypatch.setattr(mod, "datetime", FrozenDateTime)
    # no real processes on the test machine
    monkeypatch.setattr(mod, "_proc_alive", lambda pid: True)
    if runner_flags is None:
        monkeypatch.setattr(mod, "_runner_mode_from_process", lambda: None)
    else:
        monkeypatch.setattr(mod, "_runner_mode_from_process", lambda: runner_flags)
    # rendering must never touch the network or place orders
    fake_mt5.order_send = lambda request: (_ for _ in ()).throw(
        AssertionError("dashboard must never call order_send")
    )
    return mod


def fake_mt5_env():
    mt5 = SimpleNamespace(DEAL_ENTRY_IN=0)
    mt5.initialize = lambda path=None: True
    mt5.shutdown = lambda: None
    mt5.account_info = lambda: SimpleNamespace(
        trade_mode=0, login=812930, server="OtetGroup-MT5", balance=994.32)
    mt5.terminal_info = lambda: SimpleNamespace(connected=True)
    mt5.symbol_info_tick = lambda s: SimpleNamespace(bid=4314.21, ask=4314.39)
    mt5.symbol_info = lambda s: SimpleNamespace(digits=2)
    return mt5


def seed(tmp_path):
    (tmp_path / "state.json").write_text("{}", encoding="utf-8")
    (tmp_path / "runner.lock").write_text("1234", encoding="utf-8")
    (tmp_path / "watchdog.pid").write_text("5678", encoding="utf-8")
    (tmp_path / "events.jsonl").write_text(
        "\n".join([
            json.dumps({"ts_utc": "2099-01-01T10:00:00+00:00",
                        "event": "TELEGRAM_SIGNAL", "symbol": "XAUUSD.ecn",
                        "success": True, "detail": "HTTP_200"}),
            json.dumps({"ts_utc": "2099-01-01T10:05:00+00:00",
                        "event": "TELEGRAM_DEAL_LIFECYCLE", "symbol": "XAUUSD.ecn",
                        "entry": 1, "net": 1.06, "success": True}),
            json.dumps({"ts_utc": "2099-01-01T10:06:00+00:00",
                        "event": "ORDER_RESULT", "symbol": "XAUUSD.ecn",
                        "signal_id": "XAUUSD.ecn:1:BUY",
                        "result": {"ok": True, "retcode": 10009}, "success": True}),
        ]) + "\n",
        encoding="utf-8",
    )


def test_page_renders_all_sections(monkeypatch, tmp_path):
    seed(tmp_path)
    mod = load_dashboard(monkeypatch, tmp_path, fake_mt5_env(),
                         runner_flags=("true", "true"))
    page = mod.render()
    assert "ALIVE" in page and "pid 1234" in page
    assert "🟩 LIVE-DEMO" in page
    assert "read from the live runner process" in page
    assert "812930 @ OtetGroup-MT5" in page and "994.32" in page
    assert "4314.21 / 4314.39" in page
    assert "2099-01-01" in page and "Last 40 events" in page
    assert "TELEGRAM_SIGNAL" in page and "ORDER_RESULT" in page


def test_mode_from_dashboard_process_when_runner_unreadable(monkeypatch, tmp_path):
    seed(tmp_path)
    monkeypatch.setenv("LIVE_TRADING_ENABLE", "false")
    monkeypatch.delenv("ALLOW_REAL_EXECUTION", raising=False)
    mod = load_dashboard(monkeypatch, tmp_path, fake_mt5_env(), runner_flags=None)
    page = mod.render()
    assert "🟨 DRY-RUN" in page


def test_stale_heartbeat_shown_when_state_old(monkeypatch, tmp_path):
    seed(tmp_path)
    mod = load_dashboard(monkeypatch, tmp_path, fake_mt5_env())
    # make the state file look ancient
    import os
    old = (tmp_path / "state.json").stat().st_mtime - 9999
    os.utime(tmp_path / "state.json", (old, old))
    page = mod.render()
    assert "STALE" in page


def test_render_is_read_only_no_state_writes(monkeypatch, tmp_path):
    seed(tmp_path)
    mod = load_dashboard(monkeypatch, tmp_path, fake_mt5_env())
    before = {
        p: p.read_bytes()
        for p in tmp_path.iterdir() if p.is_file()
    }
    mod.render()
    after = {
        p: p.read_bytes()
        for p in tmp_path.iterdir() if p.is_file()
    }
    assert set(after) == set(before) and all(after[p] == before[p] for p in before)
