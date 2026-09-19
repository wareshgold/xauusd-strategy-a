"""Dry-run safety tests for the guarded MT5 live gateway.

These tests do not connect to MT5 or Telegram. They validate the
execution contract and safety gates only.
"""

import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace


def load_gateway(monkeypatch, tmp_path):
    fake_mt5 = SimpleNamespace(
        ORDER_TYPE_BUY=0,
        ORDER_TYPE_SELL=1,
        TRADE_ACTION_DEAL=1,
        ORDER_TIME_GTC=0,
        ORDER_FILLING_IOC=1,
        TRADE_RETCODE_DONE=10009,
    )
    monkeypatch.setitem(sys.modules, "MetaTrader5", fake_mt5)
    monkeypatch.setenv("TRADING_SYMBOL", "XAUUSD.ecn")
    monkeypatch.setenv("SIGNAL_FILE", str(tmp_path / "approved_signal.json"))
    monkeypatch.setenv("LIVE_TRADING_ENABLE", "false")
    monkeypatch.setenv("MAX_OPEN_POSITIONS", "1")
    sys.modules.pop("scripts.live_mt5_gateway", None)
    return importlib.import_module("scripts.live_mt5_gateway"), fake_mt5


def test_signal_requires_approved_status(monkeypatch, tmp_path):
    gateway, _ = load_gateway(monkeypatch, tmp_path)
    payload = {
        "direction": "BUY",
        "symbol": "XAUUSD.ecn",
        "entry": 100,
        "sl": 90,
        "tp": 110,
        "volume": 0.01,
        "signal_id": "TEST-STATUS",
        "source": "MANUAL_GATEWAY_TEST_ONLY",
        "status": "PENDING",
    }
    try:
        gateway.Signal.from_json(payload)
    except ValueError as exc:
        assert "APPROVED" in str(exc)
    else:
        raise AssertionError("non-approved signal must be rejected")


def test_sell_dry_run_builds_sell_order(monkeypatch, tmp_path):
    gateway, mt5 = load_gateway(monkeypatch, tmp_path)
    mt5.symbol_info_tick = lambda symbol: SimpleNamespace(bid=100.0, ask=100.2)
    mt5.positions_get = lambda symbol=None: []
    signal = gateway.Signal.from_json({
        "direction": "SELL",
        "symbol": "XAUUSD.ecn",
        "entry": 100.0,
        "sl": 110.0,
        "tp": 90.0,
        "volume": 0.01,
        "signal_id": "TEST-SELL-001",
        "source": "MANUAL_GATEWAY_TEST_ONLY",
        "status": "APPROVED",
    })
    result = gateway.execute_signal(signal)
    assert result["ok"] is True
    assert result["dry_run"] is True
    assert result["request"]["type"] == mt5.ORDER_TYPE_SELL
    assert result["request"]["price"] == 100.0
    assert result["request"]["sl"] == 110.0
    assert result["request"]["tp"] == 90.0


def test_max_open_positions_blocks_execution(monkeypatch, tmp_path):
    gateway, mt5 = load_gateway(monkeypatch, tmp_path)
    mt5.positions_get = lambda symbol=None: [object()]
    signal = gateway.Signal.from_json({
        "direction": "BUY",
        "symbol": "XAUUSD.ecn",
        "entry": 100.0,
        "sl": 90.0,
        "tp": 110.0,
        "volume": 0.01,
        "signal_id": "TEST-MAXPOS-001",
        "source": "MANUAL_GATEWAY_TEST_ONLY",
        "status": "APPROVED",
    })
    result = gateway.execute_signal(signal)
    assert result == {"ok": False, "reason": "MAX_OPEN_POSITIONS", "open_positions": 1}

def test_telegram_format_is_nexora_branded(monkeypatch, tmp_path):
    gateway, _ = load_gateway(monkeypatch, tmp_path)
    signal = gateway.Signal.from_json({
        "direction": "BUY",
        "symbol": "XAUUSD.ecn",
        "entry": 100.0,
        "sl": 90.0,
        "tp": 110.0,
        "volume": 0.01,
        "signal_id": "TEST-NEXORA-BRAND-001",
        "source": "NEXORA_TELEGRAM_TEST_ONLY",
        "status": "APPROVED",
    })

    signal_message = gateway.format_signal(signal, "DRY-RUN")
    execution_message = gateway.format_signal(
        signal,
        "DRY-RUN",
        {"retcode": None, "order": None, "deal": None, "comment": None},
    )

    assert "Nexora SIGNAL — BUY" in signal_message
    assert "Nexora EXECUTION — BUY" in execution_message
    assert "SP2L SIGNAL" not in signal_message
    assert "SP2L SIGNAL" not in execution_message
    assert "SP2L Live Gateway" not in signal_message
    assert "SP2L Live Gateway" not in execution_message

