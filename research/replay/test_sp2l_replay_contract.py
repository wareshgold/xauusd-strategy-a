"""Tests for source-safe SP2L observation replay."""

import pytest

from research.fixtures.sp2l_synthetic_fixture_contract import (
    Direction,
    EvidenceLabel,
    EvidenceStatus,
    EXAMPLE_BULLISH,
    GeometryDimension,
    SyntheticFixture,
)
from research.replay.sp2l_replay_contract import (
    ReplayEventKind,
    replay_examples,
    replay_fixture,
)


def test_examples_replay_deterministically_without_execution() -> None:
    results = replay_examples()
    assert len(results) == 2
    for result in results:
        result.validate()
        assert result.execution_authorized is False
        assert result.events[-1].kind is ReplayEventKind.GEOMETRY_BLOCKED
        assert len(result.events) == len(result.events[:-1]) + 1


def test_replay_preserves_candle_order_and_provenance() -> None:
    result = replay_fixture(EXAMPLE_BULLISH)
    observed = result.events[:-1]
    assert tuple(event.candle_index for event in observed) == (0, 1, 2, 3)
    assert all(event.source_refs == EXAMPLE_BULLISH.source_refs for event in result.events)
    assert all(event.direction == Direction.BULLISH.value for event in result.events)


def test_replay_preserves_all_blocked_geometry_dimensions() -> None:
    result = replay_fixture(EXAMPLE_BULLISH)
    expected = tuple(
        (dimension.value, EvidenceStatus.BLOCKED.value) for dimension in GeometryDimension
    )
    assert all(event.geometry_status == expected for event in result.events)


def test_missing_geometry_label_is_rejected() -> None:
    labels = tuple(
        EvidenceLabel(dimension, EvidenceStatus.BLOCKED, "blocked")
        for dimension in GeometryDimension
        if dimension is not GeometryDimension.P_GAP
    )
    fixture = SyntheticFixture(
        "missing-p-gap-label",
        Direction.BULLISH,
        EXAMPLE_BULLISH.candles,
        labels,
        ("synthetic-only",),
    )
    with pytest.raises(ValueError, match="missing executable-geometry blocker labels"):
        replay_fixture(fixture)


def test_replay_rejects_execution_authorization_contract() -> None:
    result = replay_fixture(EXAMPLE_BULLISH)
    assert result.execution_authorized is False
    assert all(
        event.kind in (ReplayEventKind.CANDLE_OBSERVED, ReplayEventKind.GEOMETRY_BLOCKED)
        for event in result.events
    )
