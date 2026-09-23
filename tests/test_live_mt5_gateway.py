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
        ORDER_TYPE_BUY_LIMIT=2,
        ORDER_TYPE_SELL_LIMIT=3,
        TRADE_ACTION_DEAL=1,
        TRADE_ACTION_PENDING=5,
        ORDER_TIME_GTC=0,
        ORDER_FILLING_IOC=1,
        ORDER_FILLING_RETURN=2,
        TRADE_RETCODE_DONE=10009,
        TRADE_RETCODE_PLACED=10008,
        ACCOUNT_TRADE_MODE_DEMO=0,
    )
    # exposure guard + limit-mode plumbing added after these fixtures were
    # written; every execute_signal test must provide them.
    fake_mt5.orders_get = lambda symbol=None: []
    fake_mt5.positions_get = lambda symbol=None: []
    fake_mt5.symbol_info = lambda symbol: SimpleNamespace(
        trade_stops_level=0, point=0.01, trade_mode=4,
        volume_min=0.01, volume_step=0.01,
    )
    fake_mt5.account_info = lambda: SimpleNamespace(trade_mode=0)
    monkeypatch.setitem(sys.modules, "MetaTrader5", fake_mt5)
    monkeypatch.setenv("TRADING_SYMBOL", "XAUUSD.ecn")
    monkeypatch.setenv("SIGNAL_FILE", str(tmp_path / "approved_signal.json"))
    monkeypatch.setenv("LIVE_TRADING_ENABLE", "false")
    monkeypatch.delenv("ALLOW_REAL_EXECUTION", raising=False)
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
    assert result == {"ok": False, "reason": "MAX_OPEN_POSITIONS", "active_exposure": 1}

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


def _approved_buy(gateway):
    return gateway.Signal.from_json({
        "direction": "BUY",
        "symbol": "XAUUSD.ecn",
        "entry": 100.0,
        "sl": 90.0,
        "tp": 110.0,
        "volume": 0.01,
        "signal_id": "TEST-DOUBLE-GATE-001",
        "source": "MANUAL_GATEWAY_TEST_ONLY",
        "status": "APPROVED",
    })


def test_live_flag_without_allow_stays_dry_run(monkeypatch, tmp_path):
    """One forgotten key must never reach order_send."""
    gateway, mt5 = load_gateway(monkeypatch, tmp_path)
    monkeypatch.setenv("LIVE_TRADING_ENABLE", "true")
    monkeypatch.delenv("ALLOW_REAL_EXECUTION", raising=False)
    monkeypatch.setattr(
        gateway, "LIVE_TRADING_ENABLE", True, raising=False
    )
    mt5.positions_get = lambda symbol=None: []
    mt5.symbol_info_tick = lambda symbol: SimpleNamespace(bid=100.0, ask=100.2)
    result = gateway.execute_signal(_approved_buy(gateway))
    assert result["dry_run"] is True
    assert result["reason"] == "ALLOW_REAL_EXECUTION!=true"


def test_both_keys_enable_real_path_only_with_fake_order_send(monkeypatch, tmp_path):
    """With BOTH keys set the real path is taken — verified against a fake
    MT5 module (no broker connection in tests)."""
    gateway, mt5 = load_gateway(monkeypatch, tmp_path)
    monkeypatch.setenv("LIVE_TRADING_ENABLE", "true")
    monkeypatch.setenv("ALLOW_REAL_EXECUTION", "true")
    monkeypatch.setattr(gateway, "LIVE_TRADING_ENABLE", True, raising=False)
    monkeypatch.setattr(gateway, "ALLOW_REAL_EXECUTION", True, raising=False)
    mt5.symbol_info_tick = lambda symbol: SimpleNamespace(bid=100.0, ask=100.2)
    mt5.account_info = lambda: SimpleNamespace(trade_mode=0)
    mt5.symbol_info = lambda symbol: SimpleNamespace(trade_mode=4)  # FULL
    mt5.positions_get = lambda symbol=None: []
    sent = {}

    def fake_order_send(request):
        sent.update(request)
        return SimpleNamespace(retcode=mt5.TRADE_RETCODE_DONE, order=111, deal=222, comment="ok")

    mt5.order_send = fake_order_send
    result = gateway.execute_signal(_approved_buy(gateway))
    assert result["dry_run"] is False
    assert result["ok"] is True
    assert result["retcode"] == mt5.TRADE_RETCODE_DONE
    assert sent["symbol"] == "XAUUSD.ecn"


def test_effective_mode_is_truthful(monkeypatch, tmp_path):
    gateway, _ = load_gateway(monkeypatch, tmp_path)
    assert gateway.effective_mode() == "DRY-RUN"
    monkeypatch.setattr(gateway, "LIVE_TRADING_ENABLE", True, raising=False)
    assert gateway.effective_mode() == "DRY-RUN"  # still dry: ALLOW key missing
    monkeypatch.setattr(gateway, "ALLOW_REAL_EXECUTION", True, raising=False)
    assert gateway.effective_mode() == "LIVE"


def test_closeonly_symbol_blocks_real_order_send(monkeypatch, tmp_path):
    """REGRESSION (hard blocker): even with BOTH real-execution keys set, a
    CLOSEONLY symbol must NEVER reach an MT5 open-order request. The block
    happens at the last line before order_send, verified against the live
    terminal state, and fails closed when symbol info is missing."""
    gateway, mt5 = load_gateway(monkeypatch, tmp_path)
    monkeypatch.setenv("LIVE_TRADING_ENABLE", "true")
    monkeypatch.setenv("ALLOW_REAL_EXECUTION", "true")
    monkeypatch.setattr(gateway, "LIVE_TRADING_ENABLE", True, raising=False)
    monkeypatch.setattr(gateway, "ALLOW_REAL_EXECUTION", True, raising=False)
    mt5.positions_get = lambda symbol=None: []
    mt5.symbol_info_tick = lambda symbol: SimpleNamespace(bid=100.0, ask=100.2)

    calls = {"order_send": 0}

    def forbidden_order_send(request):
        calls["order_send"] += 1
        raise AssertionError("order_send must never be called for a CLOSEONLY symbol")

    mt5.order_send = forbidden_order_send

    # Case 1: live terminal reports CLOSEONLY (mode 3).
    mt5.account_info = lambda: SimpleNamespace(trade_mode=0)
    mt5.symbol_info = lambda symbol: SimpleNamespace(trade_mode=3)
    result = gateway.execute_signal(_approved_buy(gateway))
    assert result["ok"] is False
    assert result["reason"] == "SYMBOL_NOT_OPENABLE"
    assert result["symbol_trade_mode"] == 3
    assert result["trade_mode_name"] == "CLOSEONLY"
    assert calls["order_send"] == 0

    # Case 2: symbol info unavailable — must fail closed too. The early
    # SYMBOL_INFO_UNAVAILABLE guard fires before the openable check; what
    # matters is that no order_send ever happens.
    mt5.symbol_info = lambda symbol: None
    result = gateway.execute_signal(_approved_buy(gateway))
    assert result["ok"] is False
    assert result["reason"] == "SYMBOL_INFO_UNAVAILABLE"
    assert calls["order_send"] == 0


def test_disabled_symbol_also_blocks_real_order_send(monkeypatch, tmp_path):
    """DISABLED (mode 0) is equally a hard blocker — only LONGONLY/SHORTONLY/
    FULL may pass to order_send."""
    gateway, mt5 = load_gateway(monkeypatch, tmp_path)
    monkeypatch.setenv("LIVE_TRADING_ENABLE", "true")
    monkeypatch.setenv("ALLOW_REAL_EXECUTION", "true")
    monkeypatch.setattr(gateway, "LIVE_TRADING_ENABLE", True, raising=False)
    monkeypatch.setattr(gateway, "ALLOW_REAL_EXECUTION", True, raising=False)
    mt5.positions_get = lambda symbol=None: []
    mt5.symbol_info_tick = lambda symbol: SimpleNamespace(bid=100.0, ask=100.2)
    mt5.order_send = lambda request: (_ for _ in ()).throw(
        AssertionError("order_send must never be called for a DISABLED symbol")
    )
    mt5.account_info = lambda: SimpleNamespace(trade_mode=0)
    mt5.symbol_info = lambda symbol: SimpleNamespace(trade_mode=0)
    result = gateway.execute_signal(_approved_buy(gateway))
    assert result["reason"] == "SYMBOL_NOT_OPENABLE"
    assert result["trade_mode_name"] == "DISABLED"


def test_full_trade_mode_allows_real_order_send(monkeypatch, tmp_path):
    """Control case: with FULL (4) and both keys set, order_send IS reached
    (against the fake MT5 module) — proving the blocker targets the mode,
    not the flags."""
    gateway, mt5 = load_gateway(monkeypatch, tmp_path)
    monkeypatch.setenv("LIVE_TRADING_ENABLE", "true")
    monkeypatch.setenv("ALLOW_REAL_EXECUTION", "true")
    monkeypatch.setattr(gateway, "LIVE_TRADING_ENABLE", True, raising=False)
    monkeypatch.setattr(gateway, "ALLOW_REAL_EXECUTION", True, raising=False)
    mt5.positions_get = lambda symbol=None: []
    mt5.symbol_info_tick = lambda symbol: SimpleNamespace(bid=100.0, ask=100.2)
    mt5.account_info = lambda: SimpleNamespace(trade_mode=0)
    mt5.symbol_info = lambda symbol: SimpleNamespace(trade_mode=4)
    mt5.order_send = lambda request: SimpleNamespace(
        retcode=mt5.TRADE_RETCODE_DONE, order=1, deal=2, comment="ok"
    )
    result = gateway.execute_signal(_approved_buy(gateway))
    assert result["ok"] is True
    assert result["dry_run"] is False

