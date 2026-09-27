import pytest

from scripts.sp2l_pip_contract import make_contract


@pytest.mark.parametrize(
    ("symbol", "point", "expected"),
    [
        ("EURUSD", 0.00001, 0.0001),
        ("GBPUSD", 0.00001, 0.0001),
        ("USDJPY", 0.001, 0.01),
        ("EURJPY", 0.001, 0.01),
        ("GBPJPY", 0.001, 0.01),
        ("XAUUSD.ecn", 0.01, 0.01),
    ],
)
def test_pip_size_is_symbol_specific(symbol, point, expected):
    contract = make_contract(symbol, point, 5, 0.01)
    assert contract.pip_size == expected


def test_price_to_pips_and_back():
    contract = make_contract("EURUSD", 0.00001, 5, 0.01)
    assert contract.price_to_pips(0.0012) == pytest.approx(12.0)
    assert contract.pips_to_price(12.0) == pytest.approx(0.0012)


def test_directional_gross_pips():
    contract = make_contract("USDJPY", 0.001, 3, 0.01)
    assert contract.gross_pips(150.00, 150.20, "BUY") == pytest.approx(20.0)
    assert contract.gross_pips(150.20, 150.00, "SELL") == pytest.approx(20.0)


def test_commission_scales_with_lot_size():
    contract = make_contract(
        "EURUSD", 0.00001, 5, 0.10,
        commission_per_lot_round_turn=7.0,
    )
    assert contract.commission_total() == pytest.approx(0.70)
