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



def test_rr4_act40_monitor_builds_actionable_diagnostics(monkeypatch, tmp_path):
    monitor = load_monitor(monkeypatch, tmp_path)
    events = [
        {
            "ts_utc": "2026-11-03T08:00:00+00:00",
            "event": "TRAIL_UPDATE", "symbol": "XAUUSD.ecn",
            "position": 65001173, "success": False, "retcode": 10030,
            "comment": "Invalid stops", "last_error": "broker rejected",
            "attempt_number": 3, "retry_scheduled": False,
        },
        {
            "ts_utc": "2026-11-03T08:01:00+00:00",
            "event": "TRAIL_DEFERRED", "symbol": "XAUUSD.ecn",
            "position": 65001173, "reason": "CURRENT_QUOTE_OR_BROKER_DISTANCE",
        },
        {
            "ts_utc": "2026-11-03T08:02:00+00:00",
            "event": "ORDER_RESULT", "symbol": "XAUUSD.ecn",
            "result": {"ok": False, "retcode": 10016, "comment": "Invalid stops"},
        },
        {
            "ts_utc": "2026-11-03T08:03:00+00:00",
            "event": "TELEGRAM_SIGNAL_RETRY", "symbol": "XAUUSD.ecn",
            "signal_id": "test-signal", "attempt": 2,
        },
    ]
    diagnostics = monitor._build_diagnostics(
        events, {"pid": 123, "alive": True},
        {"malformed_lines": 0, "read_error": None},
    )

    codes = {item["code"] for item in diagnostics}
    assert {"TRAIL_UPDATE_FAILED", "TRAIL_DEFERRED", "ORDER_SEND_FAILED", "TELEGRAM_SIGNAL_RETRY"} <= codes
    failed_trail = next(item for item in diagnostics if item["code"] == "TRAIL_UPDATE_FAILED")
    assert failed_trail["level"] == "ERROR"
    assert failed_trail["time_tehran"] == "2026-11-03 11:30:00"
    assert "retcode=10030" in failed_trail["detail"]
    assert "attempt_number=3" in failed_trail["detail"]
    assert failed_trail["position"] == 65001173


def test_rr4_act40_monitor_reports_malformed_event_json(monkeypatch, tmp_path):
    monitor = load_monitor(monkeypatch, tmp_path)
    monitor.EVENTS.write_text(
        '{"ts_utc":"2026-11-03T08:00:00+00:00","event":"HEARTBEAT"}\n'
        '{"event": broken json}\n',
        encoding="utf-8",
    )
    events, health = monitor._read_events_with_health()
    diagnostics = monitor._build_diagnostics(
        events, {"pid": 123, "alive": True}, health
    )

    assert len(events) == 1
    assert health["malformed_lines"] == 1
    assert health["last_malformed_line"] == 2
    assert any(item["code"] == "EVENT_JSON_INVALID" for item in diagnostics)


def test_rr4_act40_monitor_reports_mt5_disconnect_from_heartbeat(monkeypatch, tmp_path):
    monitor = load_monitor(monkeypatch, tmp_path)
    diagnostics = monitor._build_diagnostics(
        [{"ts_utc": "2026-11-03T08:00:00+00:00", "event": "HEARTBEAT",
          "mt5_connected": False, "trade_allowed": False}],
        {"pid": 123, "alive": True},
        {"malformed_lines": 0, "read_error": None},
    )
    assert any(item["code"] == "MT5_DISCONNECTED" and item["level"] == "ERROR"
               for item in diagnostics)
    assert any(item["code"] == "TRADING_NOT_ALLOWED" and item["level"] == "WARNING"
               for item in diagnostics)



def test_rr4_act40_monitor_marks_retried_events_recovered(monkeypatch, tmp_path):
    monitor = load_monitor(monkeypatch, tmp_path)
    events = [
        {"ts_utc": "2026-11-03T08:00:00+00:00", "event": "TRAIL_DEFERRED",
         "position": 7, "completed_bar_time": 1234},
        {"ts_utc": "2026-11-03T08:00:05+00:00", "event": "TRAIL_UPDATE",
         "position": 7, "completed_bar_time": 1234, "success": True},
        {"ts_utc": "2026-11-03T08:01:00+00:00", "event": "TELEGRAM_SIGNAL_RETRY",
         "signal_id": "sig-1"},
        {"ts_utc": "2026-11-03T08:01:05+00:00", "event": "TELEGRAM_SIGNAL",
         "signal_id": "sig-1", "success": True},
    ]
    diagnostics = monitor._build_diagnostics(
        events, {"pid": 123, "alive": True},
        {"malformed_lines": 0, "read_error": None},
    )
    codes = {item["code"] for item in diagnostics}
    assert "TRAIL_DEFERRED_RECOVERED" in codes
    assert "TELEGRAM_RETRY_RECOVERED" in codes
    assert "TRAIL_DEFERRED" not in codes
    assert "TELEGRAM_SIGNAL_RETRY" not in codes


def test_runner_process_detection_does_not_require_lock_file(monkeypatch, tmp_path):
    from types import SimpleNamespace

    monitor = load_monitor(monkeypatch, tmp_path)
    runner_root = tmp_path / "active-runner"
    scripts = runner_root / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "run_sp2l_v3_1_xauusd_forward_test.py").write_text("# fixture", encoding="utf-8")
    monkeypatch.setattr(monitor, "RUNNER_ROOT", runner_root)
    monkeypatch.setattr(monitor.os, "name", "nt")
    monitor.RUNNER_LOCK.unlink()

    payload = [
        {"pid": 11352, "parent_pid": 11216, "command_line": "python runner.py"},
        {"pid": 9088, "parent_pid": 11352, "command_line": "python runner.py"},
    ]
    monkeypatch.setattr(
        monitor.subprocess, "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0, stdout=json.dumps(payload), stderr=""
        ),
    )

    status = monitor._runner_status()

    assert status["alive"] is True
    assert status["pid"] == 11352
    assert status["pids"] == [11352, 9088]
    assert status["source"] == "windows_cim_process_probe"


def test_runner_process_missing_is_distinct_from_probe_unavailable(monkeypatch, tmp_path):
    from types import SimpleNamespace

    monitor = load_monitor(monkeypatch, tmp_path)
    runner_root = tmp_path / "active-runner"
    scripts = runner_root / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "run_sp2l_v3_1_xauusd_forward_test.py").write_text("# fixture", encoding="utf-8")
    monkeypatch.setattr(monitor, "RUNNER_ROOT", runner_root)
    monkeypatch.setattr(monitor.os, "name", "nt")
    monkeypatch.setattr(
        monitor.subprocess, "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="[]", stderr=""),
    )

    status = monitor._runner_status()
    diagnostics = monitor._build_diagnostics(
        [], status, {"malformed_lines": 0, "read_error": None}
    )

    assert status["alive"] is False
    assert any(item["code"] == "RUNNER_PROCESS_NOT_FOUND" and item["level"] == "ERROR"
               for item in diagnostics)
    assert all(item["code"] != "RUNNER_LOCK_UNAVAILABLE" for item in diagnostics)


def test_runner_process_probe_failure_is_unverified_not_stopped(monkeypatch, tmp_path):
    monitor = load_monitor(monkeypatch, tmp_path)
    runner_root = tmp_path / "active-runner"
    scripts = runner_root / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "run_sp2l_v3_1_xauusd_forward_test.py").write_text("# fixture", encoding="utf-8")
    monkeypatch.setattr(monitor, "RUNNER_ROOT", runner_root)
    monkeypatch.setattr(monitor.os, "name", "nt")

    def unavailable(*args, **kwargs):
        raise FileNotFoundError("powershell.exe unavailable")

    monkeypatch.setattr(monitor.subprocess, "run", unavailable)
    status = monitor._runner_status()
    diagnostics = monitor._build_diagnostics(
        [], status, {"malformed_lines": 0, "read_error": None}
    )

    assert status["alive"] is None
    assert any(item["code"] == "RUNNER_PROCESS_UNVERIFIED" and item["level"] == "WARNING"
               for item in diagnostics)
    assert all(item["code"] != "RUNNER_PROCESS_NOT_FOUND" for item in diagnostics)


def test_separate_monitor_and_runner_worktrees_are_not_a_warning(monkeypatch, tmp_path):
    monitor = load_monitor(monkeypatch, tmp_path)
    runner_root = tmp_path / "separate-runner-worktree"
    runner_root.mkdir()
    monitor.RUNNER_ROOT = runner_root
    monitor.RUNNER_ROOT_SOURCE = "SP2L_RUNNER_ROOT"
    monitor._RUNNER_ROOT_ENV = str(runner_root)
    monitor.STATE_FILE = tmp_path / "state.json"
    monitor.EVENTS = tmp_path / "events.jsonl"
    monitor.STATE_FILE.write_text(
        json.dumps({"orders": [], "positions": [], "deal_events": [], "deals": []}),
        encoding="utf-8",
    )
    monitor.EVENTS.write_text("", encoding="utf-8")
    monkeypatch.setattr(monitor, "_runner_status", lambda: {
        "pid": 11352, "pids": [11352, 9088], "alive": True, "detail": "fixture"
    })

    page = monitor._render()
    diagnostics = monitor._build_diagnostics(
        [], {"pid": 11352, "pids": [11352, 9088], "alive": True},
        {"malformed_lines": 0, "read_error": None},
    )

    assert "WARNING: monitor and runner data roots differ" not in page
    assert "RUNNER_ROOT_NOT_EXPLICIT" not in {item["code"] for item in diagnostics}
    assert "ACTIVE · PID 11352 · processes=11352,9088" in page
    assert "RUNNER_LOCK_UNAVAILABLE" not in {item["code"] for item in diagnostics}
