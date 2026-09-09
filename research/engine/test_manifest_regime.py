from datetime import datetime, timedelta, timezone

from .dataset_manifest import build_manifest
from .models import Candle
from .regime import rolling_range_regimes


def test_manifest_is_stable_and_contains_provenance():
    t = datetime(2026, 1, 1, tzinfo=timezone.utc)
    bars = [Candle(t, 10, 11, 9, 10), Candle(t + timedelta(minutes=1), 10, 12, 9, 11)]
    m = build_manifest(bars, provider="fixture", symbol="XAUUSD", timeframe="1m", source_version="v1")
    assert m.row_count == 2
    assert m.timezone == "UTC"
    assert len(m.sha256) == 64
    assert m == build_manifest(list(reversed(bars)), provider="fixture", symbol="XAUUSD", timeframe="1m", source_version="v1")


def test_regime_report_is_descriptive_not_signal_logic():
    t = datetime(2026, 1, 1, tzinfo=timezone.utc)
    bars = [Candle(t + timedelta(minutes=i), 100, 100 + (1 if i % 2 == 0 else 2), 99, 100) for i in range(100)]
    slices = rolling_range_regimes(bars, window=50)
    assert len(slices) == 2
    assert all(s.bars == 50 for s in slices)
    assert all(s.mean_range > 0 for s in slices)
