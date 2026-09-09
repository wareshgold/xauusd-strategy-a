from datetime import datetime, timedelta, timezone

from .clustering import cluster_trades, summarize_clusters, summarize_excursions
from .models import Side, Trade
from .splits import assign_split, chronological_splits


def _t(minutes: int) -> datetime:
    return datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=minutes)


def test_splits_are_chronological_and_non_overlapping():
    candles = [type("C", (), {"timestamp": _t(i)})() for i in range(100)]
    splits = chronological_splits(candles)
    assert [s.name for s in splits] == ["DEV", "VAL", "FRESH_HOLDOUT"]
    assert splits[0].start < splits[0].end <= splits[1].start < splits[1].end <= splits[2].start < splits[2].end
    assert assign_split(_t(10), splits) == "DEV"
    assert assign_split(_t(99), splits) == "FRESH_HOLDOUT"


def _trade(minute: int, r: float, mae: float | None = None, mfe: float | None = None) -> Trade:
    metadata = {}
    if mae is not None:
        metadata["maeR"] = mae
    if mfe is not None:
        metadata["mfeR"] = mfe
    tr = Trade(f"o{minute}", Side.BUY, _t(minute), 1.0, 1.0, 0.5, 2.0, _t(minute + 1), 1.0 + r * 0.5, "TP", metadata=metadata)
    return tr


def test_cluster_boundary_is_deterministic():
    trades = [_trade(0, 1), _trade(20, -1), _trade(51, 1)]
    clusters = cluster_trades(trades, max_gap_minutes=30)
    assert [len(c) for c in clusters] == [2, 1]
    assert summarize_clusters(trades, max_gap_minutes=30)["maxClusterSize"] == 2


def test_excursion_summary_uses_only_present_fields():
    result = summarize_excursions([_trade(0, 1, -0.3, 1.2), _trade(1, -1, -0.8, 0.4)])
    assert result["maeCount"] == 2
    assert result["mfeCount"] == 2
    assert result["maxMaeR"] == -0.3
    assert result["maxMfeR"] == 1.2
