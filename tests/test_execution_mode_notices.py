"""Offline tests: execution-mode line in watchdog and daily-summary notices.

Research/infrastructure only. Proves that the watchdog DOWN/UP/restart/give-up
messages and the runner's daily summary all self-declare the execution mode
(LIVE-DEMO vs DRY-RUN) together with the raw LIVE_TRADING_ENABLE /
ALLOW_REAL_EXECUTION flag values, without any network or MT5 access.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------- watchdog --
def load_watchdog(monkeypatch, sent):
    sys.modules.pop("forward_watchdog", None)
    for p in (str(ROOT), str(ROOT / "scripts")):
        if p not in sys.path:
            sys.path.insert(0, p)
    mod = importlib.import_module("forward_watchdog")
    monkeypatch.setattr(
        mod, "send_telegram_message",
        lambda text: sent.append(text) or __import__("types").SimpleNamespace(
            success=True, detail="TEST"),
    )
    # never spawn a real runner
    monkeypatch.setattr(mod, "spawn_runner",
                        lambda: __import__("types").SimpleNamespace(wait=lambda: 0))
    return mod


def test_watchdog_down_message_declares_mode(monkeypatch, tmp_path):
    sent = []
    monkeypatch.setenv("LIVE_TRADING_ENABLE", "true")
    monkeypatch.setenv("ALLOW_REAL_EXECUTION", "true")
    monkeypatch.setenv("FORWARD_WATCHDOG_MAX_RESTARTS", "1")
    monkeypatch.setenv("FORWARD_WATCHDOG_STOP_ON_CLEAN_EXIT", "0")
    mod = load_watchdog(monkeypatch, sent)
    monkeypatch.setattr(mod, "WATCHDOG_PID", tmp_path / "wd.pid")
    monkeypatch.setattr(mod.time, "sleep", lambda s: None)
    monkeypatch.setattr(mod, "notify", lambda text: sent.append(text))
    mod.main()
    down = [t for t in sent if "runner DOWN" in t]
    assert down and "🟩 Execution: LIVE-DEMO" in down[0]
    assert "LIVE_TRADING_ENABLE=true" in down[0] and "ALLOW_REAL_EXECUTION=true" in down[0]


def test_watchdog_dry_run_mode_when_flags_missing(monkeypatch, tmp_path):
    sent = []
    monkeypatch.delenv("LIVE_TRADING_ENABLE", raising=False)
    monkeypatch.delenv("ALLOW_REAL_EXECUTION", raising=False)
    monkeypatch.setenv("FORWARD_WATCHDOG_MAX_RESTARTS", "1")
    monkeypatch.setenv("FORWARD_WATCHDOG_STOP_ON_CLEAN_EXIT", "0")
    mod = load_watchdog(monkeypatch, sent)
    monkeypatch.setattr(mod, "WATCHDOG_PID", tmp_path / "wd.pid")
    monkeypatch.setattr(mod.time, "sleep", lambda s: None)
    monkeypatch.setattr(mod, "notify", lambda text: sent.append(text))
    mod.main()
    down = [t for t in sent if "runner DOWN" in t]
    assert down and "🟨 Execution: DRY-RUN" in down[0]
    assert "LIVE_TRADING_ENABLE=false" in down[0]


def test_watchdog_started_message_declares_mode(monkeypatch, tmp_path):
    sent = []
    monkeypatch.setenv("LIVE_TRADING_ENABLE", "true")
    monkeypatch.setenv("ALLOW_REAL_EXECUTION", "true")
    monkeypatch.setenv("FORWARD_WATCHDOG_MAX_RESTARTS", "1")
    monkeypatch.setenv("FORWARD_WATCHDOG_STOP_ON_CLEAN_EXIT", "0")
    mod = load_watchdog(monkeypatch, sent)
    monkeypatch.setattr(mod, "WATCHDOG_PID", tmp_path / "wd.pid")
    monkeypatch.setattr(mod.time, "sleep", lambda s: None)
    monkeypatch.setattr(mod, "notify", lambda text: sent.append(text))
    mod.main()
    started = [t for t in sent if "watchdog started" in t]
    assert started and "Execution:" in started[0]


# ----------------------------------------------------- runner daily summary --
def load_runner_module():
    for p in (str(ROOT), str(ROOT / "scripts")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import os

    # Importing the runner has module-level side effects: it does
    # os.environ.setdefault("MT5_FORWARD_ORDER_MODE", ...), which would leak
    # into the gateway tests running after this module. Snapshot and restore.
    before = dict(os.environ)
    import MetaTrader5  # noqa: F401  (must already be importable in tests env)
    mod = importlib.import_module("run_sp2l_author_replica_multi_symbol_forward_test")
    leaked = set(os.environ) - set(before) | {
        k for k, v in os.environ.items() if before.get(k) != v
    }
    for key in leaked:
        if before.get(key) is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = before[key]
    return mod


def test_daily_summary_declares_mode(monkeypatch, tmp_path):
    monkeypatch.setenv("LIVE_TRADING_ENABLE", "true")
    monkeypatch.setenv("ALLOW_REAL_EXECUTION", "true")
    mod = load_runner_module()
    events = tmp_path / "events.jsonl"
    events.write_text(
        '{"ts_utc":"2099-01-01T10:00:00+00:00","event":"TELEGRAM_SIGNAL",'
        '"symbol":"XAUUSD.ecn","success":true}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "EVENTS", events)
    monkeypatch.setattr(mod, "datetime", __import__("datetime").datetime)
    # freeze "today" to the date used in the fixture event
    real_dt = __import__("datetime")
    class FrozenDateTime(real_dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return real_dt.datetime(2099, 1, 1, 22, 0, 0, tzinfo=real_dt.timezone.utc)
    monkeypatch.setattr(mod, "datetime", FrozenDateTime)
    summary = mod.build_daily_summary({"last_daily_summary_utc_day": None})
    assert summary is not None
    assert "Execution:" in summary and "🟩 Execution: LIVE-DEMO" in summary
    assert "LIVE_TRADING_ENABLE=true" in summary and "ALLOW_REAL_EXECUTION=true" in summary


def test_daily_summary_dry_run_mode(monkeypatch, tmp_path):
    monkeypatch.delenv("LIVE_TRADING_ENABLE", raising=False)
    monkeypatch.delenv("ALLOW_REAL_EXECUTION", raising=False)
    mod = load_runner_module()
    events = tmp_path / "events.jsonl"
    events.write_text(
        '{"ts_utc":"2099-01-01T10:00:00+00:00","event":"TELEGRAM_SIGNAL",'
        '"symbol":"XAUUSD.ecn","success":true}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "EVENTS", events)
    real_dt = __import__("datetime")
    class FrozenDateTime(real_dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return real_dt.datetime(2099, 1, 1, 22, 0, 0, tzinfo=real_dt.timezone.utc)
    monkeypatch.setattr(mod, "datetime", FrozenDateTime)
    summary = mod.build_daily_summary({"last_daily_summary_utc_day": None})
    assert summary is not None
    assert "🟨 Execution: DRY-RUN" in summary
    assert "LIVE_TRADING_ENABLE=false" in summary
