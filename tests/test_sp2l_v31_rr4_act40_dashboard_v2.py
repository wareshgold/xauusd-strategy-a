from __future__ import annotations

import importlib
import sys
from datetime import datetime

import pytest


def load_v2(monkeypatch):
    scripts = __import__("pathlib").Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    sys.modules.pop("sp2l_v31_rr4_act40_dashboard_v2", None)
    sys.modules.pop("sp2l_v31_rr4_act40_monitor", None)
    return importlib.import_module("sp2l_v31_rr4_act40_dashboard_v2")


def test_dashboard_v2_counts_only_unique_deals_for_tehran_today(monkeypatch):
    dashboard = load_v2(monkeypatch)
    now = datetime.now(dashboard.source.TEHRAN_TZ)
    ts = now.astimezone(__import__("datetime").timezone.utc).isoformat()
    events = [
        {"ts_utc": ts, "event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 101, "net": 2.5},
        {"ts_utc": ts, "event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 101, "net": 2.5},
        {"ts_utc": ts, "event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 102, "net": -1.0},
        {"ts_utc": ts, "event": "TELEGRAM_SIGNAL"},
        {"ts_utc": ts, "event": "ORDER_RESULT", "result": {"ok": True}},
        {"ts_utc": ts, "event": "TRAIL_UPDATE", "success": True},
        {"ts_utc": ts, "event": "TRAIL_UPDATE", "success": False},
    ]

    metrics = dashboard._metrics(events)

    assert metrics["closed_deals"] == 2
    assert metrics["wins"] == 1
    assert metrics["losses"] == 1
    assert metrics["net"] == pytest.approx(1.5)
    assert metrics["signals"] == 1
    assert metrics["orders_ok"] == 1
    assert metrics["trail_ok"] == 1
    assert metrics["trail_failed"] == 1


def test_dashboard_v2_hides_session_from_primary_view_and_keeps_it_collapsed(monkeypatch):
    dashboard = load_v2(monkeypatch)
    monkeypatch.setattr(dashboard, "_snapshot", lambda: {
        "runner": {"alive": True, "pid": 11352, "pids": [11352, 9088], "detail": "matched"},
        "events": [], "health": {"malformed_lines": 0},
        "diagnostics": [], "state": {"orders": [], "positions": []},
        "metrics": {"signals": 0, "orders_ok": 0, "closed_deals": 0, "wins": 0,
                    "losses": 0, "net": 0.0, "trail_ok": 0, "trail_failed": 0},
        "latest": None, "state_age_seconds": 3.0,
        "diagnostic_counts": {"ERROR": 0, "WARNING": 0, "INFO": 0},
    })

    page = dashboard._render()

    assert "Right now" in page
    assert "System attention" in page
    assert "Today's recorded trading results" in page
    assert "<details>" in page
    assert "<h2>Session</h2>" not in page
    assert "MT5 is deliberately not queried" in page


def test_dashboard_v2_labels_runner_unverified_without_calling_it_stopped(monkeypatch):
    dashboard = load_v2(monkeypatch)
    label, css = dashboard._status_label({"alive": None})
    assert label == "RUNNER STATUS UNVERIFIED"
    assert css == "warn"
