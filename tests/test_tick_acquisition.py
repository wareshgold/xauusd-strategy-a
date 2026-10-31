from datetime import datetime, timezone

import pytest

from scripts.acquire_xauusd_tick_bidask import _tick_row, parse_utc


def test_parse_utc_requires_timezone_and_normalizes_to_utc():
    assert parse_utc("2026-08-21T03:00:00+03:00") == datetime(
        2026, 8, 21, 0, 0, tzinfo=timezone.utc
    )
    assert parse_utc("2026-08-21T00:00:00Z") == datetime(
        2026, 8, 21, 0, 0, tzinfo=timezone.utc
    )
    with pytest.raises(ValueError):
        parse_utc("2026-08-21T00:00:00")


def test_tick_row_preserves_quote_fields_and_millisecond_time():
    tick = {
        "time_msc": 1787270400123,
        "bid": 3330.12,
        "ask": 3330.34,
        "last": 0.0,
        "volume": 0.0,
        "flags": 6,
    }
    row = _tick_row(tick)
    assert row[0] == 1787270400123
    assert row[1].endswith("Z")
    assert row[2:4] == (3330.12, 3330.34)
    assert row[-1] == 6


def test_tick_row_preserves_zero_bidask_rows_instead_of_filtering():
    row = _tick_row({
        "time_msc": 1787270400123,
        "bid": 0.0,
        "ask": 0.0,
        "last": 3330.0,
        "volume": 1.0,
        "flags": 8,
    })
    assert row[2:4] == (0.0, 0.0)
    assert row[-1] == 8
