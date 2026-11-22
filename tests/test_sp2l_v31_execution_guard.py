from __future__ import annotations

from types import SimpleNamespace

import pytest

from scripts.sp2l_v31_execution_guard import validate_mt5_identity


def fake_mt5(*, login=853018, server="OtetGroup-MT5", trade_mode=0,
             terminal_path=r"C:\Program Files\Otet Group MT5 Terminal",
             symbol_mode=4):
    return SimpleNamespace(
        terminal_info=lambda: SimpleNamespace(path=terminal_path),
        account_info=lambda: SimpleNamespace(
            login=login, server=server, trade_mode=trade_mode
        ),
        symbol_info=lambda symbol: SimpleNamespace(trade_mode=symbol_mode),
    )


def test_expected_demo_identity_passes(monkeypatch):
    monkeypatch.setenv("LIVE_TRADING_ENABLE", "true")
    monkeypatch.setenv("ALLOW_REAL_EXECUTION", "true")
    validate_mt5_identity(fake_mt5(), symbol="XAUUSD.ecn", require_execution=True)


@pytest.mark.parametrize("kwargs", [
    {"login": 123456},
    {"server": "Other-Server"},
    {"trade_mode": 2},
    {"terminal_path": r"D:\Other MT5"},
])
def test_wrong_identity_fails_closed(kwargs):
    with pytest.raises(RuntimeError, match="EXECUTION_GUARD"):
        validate_mt5_identity(fake_mt5(**kwargs))


@pytest.mark.parametrize("name", ["LIVE_TRADING_ENABLE", "ALLOW_REAL_EXECUTION"])
def test_missing_execution_flag_fails_closed(monkeypatch, name):
    monkeypatch.setenv("LIVE_TRADING_ENABLE", "true")
    monkeypatch.setenv("ALLOW_REAL_EXECUTION", "true")
    monkeypatch.delenv(name)
    with pytest.raises(RuntimeError, match="EXECUTION_GUARD"):
        validate_mt5_identity(fake_mt5(), require_execution=True)


@pytest.mark.parametrize("mode", [0, 3, 5, -1])
def test_non_openable_symbol_fails_closed(mode):
    with pytest.raises(RuntimeError, match="symbol not openable"):
        validate_mt5_identity(fake_mt5(symbol_mode=mode), symbol="XAUUSD.ecn")


def test_unapproved_symbol_fails_closed():
    with pytest.raises(RuntimeError, match="unexpected symbol"):
        validate_mt5_identity(fake_mt5(), symbol="EURUSD")
