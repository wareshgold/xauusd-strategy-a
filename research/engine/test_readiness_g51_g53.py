from datetime import datetime, timedelta, timezone

import pytest

from .baselines import flat_baseline, price_baseline
from .dataset_package import SplitSummary, _splits_are_contiguous
from .models import Candle
from .timeframes import aggregate_m1_to_m5


def make_candles(start: datetime, count: int) -> list[Candle]:
    return [Candle(start + timedelta(minutes=i), 100 + i, 101 + i, 99 + i, 100.5 + i, "XAU/USD", "1m") for i in range(count)]


def test_m1_to_m5_is_deterministic_and_uses_utc_buckets():
    candles = make_candles(datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc), 10)
    out = aggregate_m1_to_m5(candles)
    assert len(out) == 2
    assert out[0].timestamp.isoformat() == "2026-01-01T00:00:00+00:00"
    assert out[0].open == 100
    assert out[0].high == 105
    assert out[0].low == 99
    assert out[0].close == 104.5
    assert [c.timestamp for c in aggregate_m1_to_m5(candles)] == [c.timestamp for c in out]


def test_incomplete_or_gapped_bucket_is_not_synthesized():
    candles = make_candles(datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc), 5)
    candles.append(Candle(datetime(2026, 1, 1, 0, 7, tzinfo=timezone.utc), 107, 108, 106, 107.5, "XAU/USD", "1m"))
    assert len(aggregate_m1_to_m5(candles)) == 1


def test_split_readiness_requires_contiguous_windows():
    good = (
        SplitSummary("DEV", "2026-06-01T00:00:00+00:00", "2026-06-30T23:59:00+00:00", 1, 1, True),
        SplitSummary("VAL", "2026-07-01T00:00:00+00:00", "2026-07-31T23:59:00+00:00", 1, 1, True),
    )
    bad = (
        good[0],
        SplitSummary("VAL", "2026-07-01T00:01:00+00:00", "2026-07-31T23:59:00+00:00", 1, 1, True),
    )
    assert _splits_are_contiguous(good)
    assert not _splits_are_contiguous(bad)


def test_baselines_are_strategy_neutral():
    candles = make_candles(datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc), 3)
    result = price_baseline(candles)
    assert result.candle_count == 3
    assert result.first_open == 100
    assert result.last_close == 102.5
    assert result.buy_hold_return == pytest.approx(0.025)
    assert flat_baseline() == {"tradeCount": 0, "return": 0.0, "maxDrawdown": 0.0}
