from types import SimpleNamespace

import discover_mt5_research_symbols as discovery


def test_unique_ecn_variant():
    discovery.mt5.symbols_get = lambda: [
        SimpleNamespace(name="XAUUSD.ecn"),
        SimpleNamespace(name="EURUSD.ecn"),
    ]
    result = discovery.discover_symbols(("XAUUSD",))
    assert result[0].broker_symbol == "XAUUSD.ecn"
    assert result[0].status == "UNIQUE_VARIANT"


def test_ambiguous_variants_are_rejected():
    discovery.mt5.symbols_get = lambda: [
        SimpleNamespace(name="EURUSD.ecn"),
        SimpleNamespace(name="EURUSD.raw"),
    ]
    result = discovery.discover_symbols(("EURUSD",))
    assert result[0].status == "AMBIGUOUS"
    assert result[0].broker_symbol is None


def test_exact_symbol_wins():
    discovery.mt5.symbols_get = lambda: [
        SimpleNamespace(name="GBPUSD"),
        SimpleNamespace(name="GBPUSD.ecn"),
    ]
    result = discovery.discover_symbols(("GBPUSD",))
    assert result[0].broker_symbol == "GBPUSD"
    assert result[0].status == "EXACT"


def test_missing_symbol_is_not_guessed():
    discovery.mt5.symbols_get = lambda: []
    result = discovery.discover_symbols(("USDCHF",))
    assert result[0].status == "NOT_FOUND"
    assert result[0].broker_symbol is None
