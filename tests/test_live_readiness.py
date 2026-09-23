"""Offline tests for the live-readiness checker and the session runner gates.

No MT5 connection and no network: the Telegram status function is
monkeypatched, and MT5 probing is either skipped or replaced with fixtures.
"""

from __future__ import annotations

import importlib
import sys
from types import SimpleNamespace

import scripts.live_readiness as live_readiness
from scripts.live_readiness import (
    check_live_readiness,
    double_gate_state,
    format_readiness,
)

TG_UNCONFIGURED = {
    "bot_configuration_detected": "no",
    "chat_destination_configured": "no",
}
TG_CONFIGURED = {
    "bot_configuration_detected": "yes",
    "chat_destination_configured": "yes",
}

MT5_PROBE_OK = {
    "initialize": True,
    "terminal_connected": True,
    "terminal_algo_trading": True,
    "account_login": 812930,
    "account_server": "TEST-SERVER",
    "account_trade_allowed": True,
    "account_trade_expert": True,
    "margin_mode": 2,
    "symbol_visible": True,
    "symbol_trade_mode": 4,
    "trade_mode": 0,  # account_trade_mode: DEMO(0); required by _mt5_items
    "stops_level_points": 0,
    "volume_min": 0.01,
    "volume_step": 0.01,
    "volume_max": 100.0,
    "tick_value": 1.0,
    "tick_size": 0.01,
}


def test_double_gate_matrix(monkeypatch):
    monkeypatch.delenv("LIVE_TRADING_ENABLE", raising=False)
    monkeypatch.delenv("ALLOW_REAL_EXECUTION", raising=False)
    assert double_gate_state()["real_execution_possible"] is False

    monkeypatch.setenv("LIVE_TRADING_ENABLE", "true")
    assert double_gate_state()["real_execution_possible"] is False

    monkeypatch.setenv("ALLOW_REAL_EXECUTION", "false")
    assert double_gate_state()["real_execution_possible"] is False

    monkeypatch.setenv("ALLOW_REAL_EXECUTION", "true")
    assert double_gate_state()["real_execution_possible"] is True


def test_offline_check_partial_without_mt5(monkeypatch):
    monkeypatch.delenv("LIVE_TRADING_ENABLE", raising=False)
    monkeypatch.delenv("ALLOW_REAL_EXECUTION", raising=False)
    monkeypatch.setattr(
        live_readiness, "telegram_delivery_status", lambda: TG_UNCONFIGURED
    )
    report = check_live_readiness(probe_mt5=False)
    assert report["verdict"] == "PARTIAL"  # MT5 unknown -> cannot claim READY
    statuses = {i["item"]: i["status"] for i in report["items"]}
    assert statuses["mt5_terminal"] == "SKIPPED"
    assert statuses["telegram_alerts"] == "DEGRADED"
    assert statuses["real_execution_double_gate"] == "SKIPPED"


def test_check_ready_when_all_probes_pass(monkeypatch):
    monkeypatch.delenv("LIVE_TRADING_ENABLE", raising=False)
    monkeypatch.delenv("ALLOW_REAL_EXECUTION", raising=False)
    monkeypatch.setattr(live_readiness, "telegram_delivery_status", lambda: TG_CONFIGURED)
    monkeypatch.setattr(live_readiness, "_probe_mt5", lambda symbol: dict(MT5_PROBE_OK))
    report = check_live_readiness(probe_mt5=True)
    assert report["verdict"] == "READY"
    assert report["real_execution_possible"] is False  # env keys unset
    assert report["blocking_items"] == []


def test_disabled_symbol_trade_mode_blocks(monkeypatch):
    monkeypatch.delenv("LIVE_TRADING_ENABLE", raising=False)
    monkeypatch.delenv("ALLOW_REAL_EXECUTION", raising=False)
    monkeypatch.setattr(live_readiness, "telegram_delivery_status", lambda: TG_CONFIGURED)
    probe = dict(MT5_PROBE_OK)
    probe["symbol_trade_mode"] = 0  # SYMBOL_TRADE_MODE_DISABLED
    monkeypatch.setattr(live_readiness, "_probe_mt5", lambda symbol: probe)
    report = check_live_readiness(probe_mt5=True)
    assert report["verdict"] == "NOT_READY"
    assert "mt5_symbol_spec" in report["blocking_items"]


def test_closeonly_symbol_is_hard_real_execution_blocker(monkeypatch):
    """REGRESSION: CLOSEONLY (mode 3, the observed OtetGroup state for
    XAUUSD.ecn/XAUEUR.ecn/XAGUSD.ecn) must make the whole verdict NOT_READY
    even when both real-execution env keys are set — it can never be a
    merely-degraded warning."""
    monkeypatch.setenv("LIVE_TRADING_ENABLE", "true")
    monkeypatch.setenv("ALLOW_REAL_EXECUTION", "true")
    monkeypatch.setattr(live_readiness, "telegram_delivery_status", lambda: TG_CONFIGURED)
    probe = dict(MT5_PROBE_OK)
    probe["symbol_trade_mode"] = 3  # CLOSEONLY
    monkeypatch.setattr(live_readiness, "_probe_mt5", lambda symbol: probe)
    report = check_live_readiness(probe_mt5=True)
    assert report["verdict"] == "NOT_READY"
    assert "mt5_symbol_spec" in report["blocking_items"]
    assert report["real_execution_possible"] is True  # flags set...
    # ...but the blocker still refuses the symbol.
    spec = next(i for i in report["items"] if i["item"] == "mt5_symbol_spec")
    assert spec["status"] == "FAILED"
    assert "openable=False" in spec["detail"]


def test_unknown_trade_mode_fails_closed(monkeypatch):
    monkeypatch.setenv("LIVE_TRADING_ENABLE", "true")
    monkeypatch.setenv("ALLOW_REAL_EXECUTION", "true")
    monkeypatch.setattr(live_readiness, "telegram_delivery_status", lambda: TG_CONFIGURED)
    probe = dict(MT5_PROBE_OK)
    probe["symbol_trade_mode"] = None  # unavailable -> fail closed
    monkeypatch.setattr(live_readiness, "_probe_mt5", lambda symbol: probe)
    report = check_live_readiness(probe_mt5=True)
    assert report["verdict"] == "NOT_READY"
    assert "mt5_symbol_spec" in report["blocking_items"]


def test_mt5_initialize_failure_blocks(monkeypatch):
    monkeypatch.delenv("LIVE_TRADING_ENABLE", raising=False)
    monkeypatch.delenv("ALLOW_REAL_EXECUTION", raising=False)
    monkeypatch.setattr(live_readiness, "telegram_delivery_status", lambda: TG_CONFIGURED)
    monkeypatch.setattr(
        live_readiness, "_probe_mt5", lambda symbol: {"initialize": False, "error": "boom"}
    )
    report = check_live_readiness(probe_mt5=True)
    assert report["verdict"] == "NOT_READY"
    assert "mt5_terminal" in report["blocking_items"]


def test_format_readiness_lists_blocking_items(monkeypatch):
    monkeypatch.delenv("LIVE_TRADING_ENABLE", raising=False)
    monkeypatch.delenv("ALLOW_REAL_EXECUTION", raising=False)
    monkeypatch.setattr(
        live_readiness, "telegram_delivery_status", lambda: TG_UNCONFIGURED
    )
    monkeypatch.setattr(
        live_readiness, "_probe_mt5", lambda symbol: {"initialize": False, "error": "no terminal"}
    )
    text = format_readiness(check_live_readiness(probe_mt5=True))
    assert "Verdict: NOT_READY" in text
    assert "[FAIL]" in text
    assert "Blocking:" in text


def test_session_runner_refuses_real_mode_without_env_keys(monkeypatch, capsys):
    monkeypatch.delenv("LIVE_TRADING_ENABLE", raising=False)
    monkeypatch.delenv("ALLOW_REAL_EXECUTION", raising=False)
    import scripts.run_live_session as runner

    monkeypatch.setattr(
        sys, "argv", ["run_live_session.py", "--mode", "real", "--check-only"]
    )
    code = runner.main()
    assert code == 2
    assert "REFUSED" in capsys.readouterr().err


def test_probe_never_crashes_on_exception(monkeypatch):
    """The MT5 probe must degrade gracefully, never raise."""

    class ExplodingMt5:
        def __getattr__(self, name):
            raise RuntimeError("terminal exploded")

    original_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "MetaTrader5":
            return ExplodingMt5()
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)
    out = live_readiness._probe_mt5("XAUUSD.ecn")
    assert out["initialize"] is False
    assert "error" in out
