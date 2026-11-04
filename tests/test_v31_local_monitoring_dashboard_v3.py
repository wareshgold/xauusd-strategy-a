from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import sp2l_v31_rr4_act40_monitor as monitor

spec = importlib.util.spec_from_file_location(
    "sp2l_v31_local_monitoring_dashboard_v3",
    SCRIPTS / "sp2l_v31_local_monitoring_dashboard_v3.py",
)
dashboard = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(dashboard)


def test_module_compiles_and_has_no_mt5_or_trade_api_calls():
    source = (SCRIPTS / "sp2l_v31_local_monitoring_dashboard_v3.py").read_text(encoding="utf-8")
    ast.parse(source)
    forbidden = (
        "import MetaTrader5",
        "from MetaTrader5",
        ".initialize(",
        ".shutdown(",
        ".order_send(",
        ".positions_get(",
        ".orders_get(",
        ".history_deals_get(",
    )
    assert not [token for token in forbidden if token in source]


def test_order_result_false_is_not_classified_as_broker_send_failure(monkeypatch):
    monkeypatch.setattr(monitor, "_RUNNER_ROOT_ENV", "configured")
    monkeypatch.setattr(monitor, "RUNNER_ROOT", ROOT)
    events = [
        {"event": "ORDER_RESULT", "ts_utc": "2026-11-04T09:00:00Z",
         "result": {"ok": False, "retcode": 10016}},
        {"event": "EXECUTION_BLOCKED", "ts_utc": "2026-11-04T09:00:00Z",
         "reason": "LIMIT_ENTRY_NOT_PLACEABLE_AT_CURRENT_MARKET"},
    ]
    diagnostics = dashboard._diagnostics(events, {}, {"malformed_lines": 0}, 1)
    codes = [item["code"] for item in diagnostics]
    assert "ORDER_RESULT_NOT_ACCEPTED" in codes
    assert "EXECUTION_BLOCKED" in codes
    assert "ORDER_SEND_FAILED" not in codes


def test_trailing_retry_and_recovery_are_distinguished():
    events = [
        {"event": "TRAIL_UPDATE", "position": 71, "completed_bar_time": "bar-1",
         "success": False, "retry_scheduled": True},
        {"event": "TRAIL_DEFERRED", "position": 72, "completed_bar_time": "bar-2"},
        {"event": "TRAIL_UPDATE", "position": 72, "completed_bar_time": "bar-2",
         "success": True},
    ]
    diagnostics = dashboard._diagnostics(events, {}, {"malformed_lines": 0}, 1)
    by_code = {item["code"]: item for item in diagnostics}
    assert by_code["TRAIL_UPDATE_RETRY_PENDING"]["level"] == "WARNING"
    assert by_code["TRAIL_DEFERRED_RECOVERED"]["level"] == "INFO"


def test_metrics_deduplicate_deals_and_do_not_call_pending_events_active_orders():
    events = [
        {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 101, "net": 12.5},
        {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 101, "net": 12.5},
        {"event": "PENDING_ORDER_LIFECYCLE", "order": 55, "state": "placed"},
        {"event": "PENDING_ORDER_LIFECYCLE", "order": 55, "state": "filled"},
    ]
    metrics = dashboard._metrics(events)["all_time_read_window"]
    assert metrics["closed_deals"] == 1
    assert metrics["net"] == 12.5
    assert metrics["pending_lifecycle_events"] == 2
    assert "active_pending_orders" not in metrics


def test_malformed_event_lines_are_data_quality_error():
    diagnostics = dashboard._diagnostics(
        [], {"read_error": None, "malformed_lines": 2, "last_malformed_line": 9,
             "last_parse_error": "invalid JSON"},
        {"alive": None, "detail": "probe unavailable"}, 1,
    )
    codes = {item["code"] for item in diagnostics}
    assert "EVENT_JSON_INVALID" in codes
    assert "RUNNER_PROCESS_UNVERIFIED" in codes


def test_state_staleness_is_explicit():
    diagnostics = dashboard._diagnostics(
        [], {"malformed_lines": 0}, {"alive": True}, 120,
    )
    assert any(item["code"] == "STATE_FILE_STALE" for item in diagnostics)
