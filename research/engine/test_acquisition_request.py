import pytest

from research.engine.acquisition_request import AcquisitionRequest


def test_request_contains_explicit_market_parameters_without_strategy_logic():
    request = AcquisitionRequest(
        symbol="XAU/USD",
        interval="1min",
        outputsize=5000,
        source_timezone="Australia/Sydney",
    )
    params = request.query_params("secret")
    assert params["symbol"] == "XAU/USD"
    assert params["interval"] == "1min"
    assert params["outputsize"] == "5000"
    assert params["timezone"] == "Australia/Sydney"
    assert params["apikey"] == "secret"


def test_redacted_query_never_contains_real_key():
    request = AcquisitionRequest(symbol="XAU/USD", interval="1min")
    assert "REDACTED" in request.redacted_query()
    assert "apikey=REDACTED" in request.redacted_query()


def test_missing_api_key_fails_loudly():
    request = AcquisitionRequest(symbol="XAU/USD", interval="1min")
    with pytest.raises(ValueError, match="outside source control"):
        request.query_params("")
