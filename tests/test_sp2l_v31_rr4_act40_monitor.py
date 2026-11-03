from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path


def load_monitor(monkeypatch, tmp_path):
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    sys.modules.pop("sp2l_v31_rr4_act40_monitor", None)
    monitor = importlib.import_module("sp2l_v31_rr4_act40_monitor")
    monkeypatch.setattr(monitor, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(monitor, "EVENTS", tmp_path / "events.jsonl")
    monkeypatch.setattr(monitor, "RUNNER_LOCK", tmp_path / "runner.lock")
    monitor.STATE_FILE.write_text(
        json.dumps({"orders": [], "positions": [], "deal_events": [], "deals": []}),
        encoding="utf-8",
    )
    monitor.RUNNER_LOCK.write_text("0", encoding="utf-8")
    return monitor


def test_rr4_act40_monitor_renders_trailing_failure_diagnostics(monkeypatch, tmp_path):
    monitor = load_monitor(monkeypatch, tmp_path)
    event = {
        "ts_utc": "2026-11-03T08:00:00+00:00",
        "event": "TRAIL_UPDATE",
        "symbol": "XAUUSD.ecn",
        "position": 64991378,
        "old_sl": 3940.88,
        "new_sl": 3936.43,
        "success": False,
        "retcode": None,
        "comment": None,
        "last_error": "(-2, 'Terminal: Invalid params')",
        "attempt_number": 2,
        "retry_scheduled": True,
        "retry_max_attempts_per_bar": 3,
    }
    monitor.EVENTS.write_text(json.dumps(event) + "\n", encoding="utf-8")

    page = monitor._render()

    assert "last_error=(-2, &#x27;Terminal: Invalid params&#x27;)" in page
    assert "retry_scheduled=True" in page
    assert "retry_max_attempts_per_bar=3" in page
    assert "attempt_number=2" in page
    assert "success=False" in page
    assert "position=64991378" in page


def test_rr4_act40_monitor_keeps_legacy_trail_events_renderable(monkeypatch, tmp_path):
    monitor = load_monitor(monkeypatch, tmp_path)
    event = {
        "ts_utc": "2026-11-03T08:01:00+00:00",
        "event": "TRAIL_UPDATE",
        "symbol": "XAUUSD.ecn",
        "position": 123,
        "old_sl": 10.0,
        "new_sl": 9.9,
        "success": True,
    }
    monitor.EVENTS.write_text(json.dumps(event) + "\n", encoding="utf-8")

    page = monitor._render()

    assert "position=123" in page
    assert "success=True" in page
    assert "last_error=" not in page
    assert "retry_scheduled=" not in page



def test_rr4_act40_monitor_renders_full_tehran_timestamp(monkeypatch, tmp_path):
    monitor = load_monitor(monkeypatch, tmp_path)
    event = {
        "ts_utc": "2026-11-03T08:01:00+00:00",
        "event": "TELEGRAM_DEAL_LIFECYCLE",
        "symbol": "XAUUSD.ecn",
        "deal": 64128158,
        "position": 65001173,
        "entry": 1,
        "net": 2.5,
    }
    monitor.EVENTS.write_text(json.dumps(event) + "\n", encoding="utf-8")

    page = monitor._render()

    assert "2026-11-03 11:31:00 Tehran" in page
    assert "<th>Tehran time</th>" in page


def test_rr4_act40_monitor_uses_explicit_runner_root(monkeypatch, tmp_path):
    runner_root = tmp_path / "runner-worktree"
    runner_root.mkdir()
    monkeypatch.setenv("SP2L_RUNNER_ROOT", str(runner_root))

    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    sys.modules.pop("sp2l_v31_rr4_act40_monitor", None)
    monitor = importlib.import_module("sp2l_v31_rr4_act40_monitor")

    assert monitor.RUNNER_ROOT == runner_root.resolve()
    assert monitor.EVENTS == (
        runner_root / "artifacts" / "forward-test"
        / "SP2L_V3_1_XAUUSD_RR4_ACT40_FORWARD_EVENTS.jsonl"
    )
    assert monitor.STATE_FILE == (
        runner_root / "runtime"
        / "sp2l_v3_1_xauusd_rr4_act40_forward_state.json"
    )
    assert monitor.RUNNER_ROOT_SOURCE == "SP2L_RUNNER_ROOT"
