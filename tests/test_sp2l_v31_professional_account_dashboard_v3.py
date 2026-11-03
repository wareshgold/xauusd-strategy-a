from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sp2l_v31_professional_account_dashboard_v3.py"
SPEC = importlib.util.spec_from_file_location("sp2l_v31_professional_account_dashboard_v3", SCRIPT)
dashboard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dashboard)


def test_curve_is_hidden_until_more_than_five_closed_trades():
    five = [{"net": 1.0, "close_time": i} for i in range(5)]
    six = [{"net": 1.0, "close_time": i} for i in range(6)]
    assert dashboard.performance(five)["curve_ready"] is False
    assert "unlocks after 6" in dashboard._curve_svg(dashboard.performance(five))
    assert dashboard.performance(six)["curve_ready"] is True
    assert "<polyline" in dashboard._curve_svg(dashboard.performance(six))


def test_performance_counts_wins_losses_breakeven_and_drawdown():
    result = dashboard.performance([
        {"net": 5.0}, {"net": -2.0}, {"net": 0.0}, {"net": -4.0}, {"net": 3.0},
    ])
    assert (result["wins"], result["losses"], result["breakeven"]) == (2, 2, 1)
    assert result["net"] == 2.0
    assert result["max_drawdown_currency"] == 6.0
    assert result["win_rate"] == 40.0
    assert result["profit_factor"] == pytest.approx(8 / 6, abs=1e-4)


def test_closed_trade_aggregation_groups_partial_fills_by_position():
    deals = [
        SimpleNamespace(symbol="XAUUSD.ecn", position_id=7, entry=0, time=10, ticket=1,
                        profit=0.0, commission=-0.2, swap=0.0, fee=0.0),
        SimpleNamespace(symbol="XAUUSD.ecn", position_id=7, entry=1, time=20, ticket=2,
                        profit=3.0, commission=-0.2, swap=-0.1, fee=0.0),
        SimpleNamespace(symbol="XAUUSD.ecn", position_id=8, entry=0, time=11, ticket=3,
                        profit=0.0, commission=0.0, swap=0.0, fee=0.0),
    ]
    rows = dashboard.build_closed_trades(deals, "XAUUSD.ecn")
    assert len(rows) == 1
    assert rows[0]["position_id"] == 7
    assert rows[0]["net"] == pytest.approx(2.5)


def test_observer_allows_existing_runner_terminal_path(tmp_path):
    terminal = tmp_path / "terminal64.exe"
    terminal.write_bytes(b"test")
    assert dashboard.validate_terminal_paths(str(terminal), str(terminal)) == str(terminal.resolve())


def test_observer_requires_explicit_terminal_path():
    with pytest.raises(RuntimeError, match="SP2L_OBSERVER_TERMINAL_PATH is required"):
        dashboard.validate_terminal_paths(None, r"C:\runner\terminal64.exe")


def test_dashboard_is_localhost_only_and_never_exposes_trade_api():
    source = SCRIPT.read_text(encoding="utf-8")
    assert 'host="127.0.0.1"' in source
    assert "portable=False" in source
    assert "portable=True" not in source
    assert "self.mt5.shutdown()" not in source
    assert ".order_send(" not in source
    assert ".order_modify(" not in source
    assert ".positions_get(" not in source
    assert "positions_get," in source
    assert "history_deals_get," in source
