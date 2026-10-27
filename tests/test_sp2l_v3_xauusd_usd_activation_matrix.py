"""Tests for USD activation and configured pip-price conversion."""
import sys
import types
sys.modules.setdefault("MetaTrader5", types.ModuleType("MetaTrader5"))
from scripts.run_sp2l_v3_xauusd_usd_activation_matrix import price_move_for_profit_usd, pip_distance_to_price


def test_usd_threshold_conversion_uses_contract_and_volume():
    assert price_move_for_profit_usd(0.5, 100, 0.01) == 0.5
    assert price_move_for_profit_usd(1.0, 100, 0.01) == 1.0
    assert price_move_for_profit_usd(3.0, 100, 0.01) == 3.0


def test_pip_distance_uses_explicit_configured_price_convention():
    assert pip_distance_to_price(5, 0.1) == 0.5
    assert pip_distance_to_price(50, 0.1) == 5.0


def test_invalid_conversion_inputs_fail_closed():
    import pytest
    with pytest.raises(ValueError):
        price_move_for_profit_usd(1.0, 0, 0.01)
    with pytest.raises(ValueError):
        pip_distance_to_price(5, 0)
