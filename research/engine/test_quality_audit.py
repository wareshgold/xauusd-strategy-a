from datetime import datetime

from .models import Candle
from .quality_audit import audit_candles


def candle(minute, o=3500.0, h=3501.0, l=3499.0, c=3500.5):
    return Candle(
        datetime.fromisoformat(f"2026-09-09T00:{minute:02d}:00+00:00"),
        o, h, l, c, symbol="XAU/USD", timeframe="1min"
    )


def test_clean_one_minute_sample_passes():
    candles = tuple(candle(i) for i in range(3))
    audit = audit_candles(candles, 60)
    assert audit.passed
    assert audit.cadence_mode_seconds == 60
    assert audit.cadence_anomalies == 0


def test_duplicate_timestamp_is_explicit_failure():
    candles = (candle(0), candle(1), candle(1))
    audit = audit_candles(candles, 60)
    assert audit.duplicate_timestamps == 1
    assert not audit.passed


def test_gap_is_reported_without_fabrication():
    candles = (candle(0), candle(1), candle(3))
    audit = audit_candles(candles, 60)
    assert audit.cadence_anomalies == 1
    assert audit.passed


def test_invalid_ohlc_is_blocked():
    class InvalidCandle:
        timestamp = datetime.fromisoformat("2026-09-09T00:00:00+00:00")
        open = 3500.0
        high = 3499.0
        low = 3498.0
        close = 3498.5

    audit = audit_candles((InvalidCandle(),), 60)
    assert audit.invalid_ohlc_rows == 1
    assert not audit.passed
