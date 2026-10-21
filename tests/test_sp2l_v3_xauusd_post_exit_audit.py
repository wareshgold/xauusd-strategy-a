"""Deterministic unit tests for the read-only RR2/TRAIL4 post-exit audit."""
import sys
import types
from pathlib import Path
from types import SimpleNamespace

sys.modules.setdefault("MetaTrader5", types.ModuleType("MetaTrader5"))
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_sp2l_v3_xauusd_post_exit_audit as audit


def setup_mt5_constants():
    mt5 = sys.modules["MetaTrader5"]
    mt5.DEAL_ENTRY_IN = 0
    mt5.DEAL_ENTRY_OUT = 1
    mt5.DEAL_ENTRY_OUT_BY = 3
    mt5.DEAL_TYPE_BUY = 0
    mt5.DEAL_TYPE_SELL = 1


def test_aggregate_deals_includes_commission_swap_and_fee_and_links_by_position():
    setup_mt5_constants()
    deals = [
        SimpleNamespace(symbol="XAUUSD.ecn", entry=0, magic=26092201, position_id=123,
                        time=100, ticket=1, type=0, price=2000.0, volume=0.01,
                        profit=0.0, commission=-0.05, swap=0.0, fee=0.0, reason=0),
        SimpleNamespace(symbol="XAUUSD.ecn", entry=1, magic=0, position_id=123,
                        time=200, ticket=2, type=1, price=2000.2, volume=0.01,
                        profit=0.20, commission=0.0, swap=-0.01, fee=-0.01, reason=4),
    ]
    result = audit.aggregate_position_deals(deals, "XAUUSD.ecn", 26092201)
    assert result["history_status"] == "CLOSED"
    assert result["position_id"] == 123
    assert abs(result["entry_price"] - 2000.0) < 1e-9
    assert abs(result["exit_price"] - 2000.2) < 1e-9
    assert abs(result["observed_gross_profit_usd"] - 0.20) < 1e-9
    assert abs(result["observed_net_usd"] - 0.13) < 1e-9


def test_post_exit_audit_excludes_exit_minute_and_measures_buy_and_sell_symmetrically():
    bars = [
        {"time": 120, "high": 100.50, "low": 99.80, "close": 100.10},  # exit minute; excluded
        {"time": 180, "high": 100.30, "low": 99.90, "close": 100.00},
        {"time": 240, "high": 100.60, "low": 99.70, "close": 100.20},
        {"time": 300, "high": 100.10, "low": 99.85, "close": 99.95},
    ]
    buy = audit.post_exit_excursions("BUY", 100.0, bars, exit_time=150, horizons=(2,))
    assert buy["post_exit_2m_bars"] == 2
    assert abs(buy["post_exit_2m_mfe_price"] - 0.60) < 1e-9
    assert abs(buy["post_exit_2m_mae_price"] - 0.30) < 1e-9

    sell = audit.post_exit_excursions("SELL", 100.0, bars, exit_time=150, horizons=(2,))
    assert sell["post_exit_2m_bars"] == 2
    assert abs(sell["post_exit_2m_mfe_price"] - 0.30) < 1e-9
    assert abs(sell["post_exit_2m_mae_price"] - 0.60) < 1e-9


def test_price_excursions_returns_null_for_missing_window():
    result = audit.price_excursions("BUY", 100.0, [], 60, 120)
    assert result == {"mfe_price": None, "mae_price": None, "bars": 0}
