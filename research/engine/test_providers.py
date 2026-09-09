from sp2l_engine.providers import parse_twelve_data_time_series


def payload():
    return {
        "meta": {
            "symbol": "XAU/USD",
            "interval": "1min",
            "timezone": "Australia/Sydney",
            "type": "Commodity",
        },
        "values": [
            {"datetime": "2026-09-09 12:01:00", "open": "3500.10", "high": "3500.80", "low": "3499.90", "close": "3500.50"},
            {"datetime": "2026-09-09 12:02:00", "open": "3500.50", "high": "3501.00", "low": "3500.20", "close": "3500.70"},
        ],
    }


def test_twelve_data_adapter_normalizes_to_utc_and_preserves_provenance():
    batch = parse_twelve_data_time_series(
        payload(), requested_symbol="XAU/USD", requested_interval="1min"
    )
    assert batch.provider == "Twelve Data"
    assert batch.source_timezone == "Australia/Sydney"
    assert batch.candles[0].timestamp.isoformat().endswith("+00:00")
    assert batch.candles[0].symbol == "XAU/USD"
    assert batch.candles[0].timeframe == "1min"
    assert batch.retrieval_metadata["meta"]["type"] == "Commodity"


def test_explicit_timezone_overrides_payload_timezone():
    batch = parse_twelve_data_time_series(
        payload(),
        requested_symbol="XAU/USD",
        requested_interval="1min",
        source_timezone="UTC",
    )
    assert batch.source_timezone == "UTC"
    assert batch.candles[0].timestamp.hour == 12


def test_naive_payload_without_timezone_is_blocked():
    broken = payload()
    broken["meta"].pop("timezone")
    try:
        parse_twelve_data_time_series(
            broken, requested_symbol="XAU/USD", requested_interval="1min"
        )
    except ValueError as exc:
        assert "timezone" in str(exc)
    else:
        raise AssertionError("missing provider timezone must not be guessed")


def test_provider_error_is_not_silently_converted_to_empty_data():
    try:
        parse_twelve_data_time_series(
            {"status": "error", "message": "bad request"},
            requested_symbol="XAU/USD", requested_interval="1min"
        )
    except ValueError as exc:
        assert str(exc) == "bad request"
    else:
        raise AssertionError("provider errors must remain explicit")
