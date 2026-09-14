import pytest

from .sp2l_synthetic_fixture_contract import (
    BLOCKED_EXECUTABLE_GEOMETRY,
    EXAMPLE_BEARISH,
    EXAMPLE_BULLISH,
    Candle,
    Direction,
    EvidenceStatus,
    GeometryDimension,
    SyntheticFixture,
    make_fixture,
)


def test_examples_are_deterministic_and_fully_validated():
    EXAMPLE_BULLISH.validate()
    EXAMPLE_BEARISH.validate()
    assert EXAMPLE_BULLISH.direction is Direction.BULLISH
    assert EXAMPLE_BEARISH.direction is Direction.BEARISH
    assert len(EXAMPLE_BULLISH.candles) == 4
    assert len(EXAMPLE_BEARISH.candles) == 4


def test_every_executable_geometry_dimension_remains_blocked():
    assert BLOCKED_EXECUTABLE_GEOMETRY == frozenset(GeometryDimension)
    for fixture in (EXAMPLE_BULLISH, EXAMPLE_BEARISH):
        statuses = {label.dimension: label.status for label in fixture.labels}
        assert set(statuses) == set(GeometryDimension)
        assert all(status is EvidenceStatus.BLOCKED for status in statuses.values())


def test_fixture_requires_provenance():
    with pytest.raises(ValueError, match="source_refs"):
        make_fixture(
            "missing-provenance",
            Direction.BULLISH,
            (Candle(0, "2026-01-01T00:00:00Z", 1, 2, 0, 1.5),),
            (),
        )


def test_fixture_rejects_invalid_ohlc():
    with pytest.raises(ValueError, match="OHLC invariant"):
        make_fixture(
            "bad-ohlc",
            Direction.BULLISH,
            (Candle(0, "2026-01-01T00:00:00Z", 3, 2, 1, 1.5),),
            ("synthetic-only",),
        )


def test_fixture_rejects_duplicate_or_unsorted_indices():
    with pytest.raises(ValueError, match="ordered by index"):
        make_fixture(
            "unsorted",
            Direction.BULLISH,
            (
                Candle(1, "2026-01-01T00:01:00Z", 1, 2, 0, 1.5),
                Candle(0, "2026-01-01T00:00:00Z", 1, 2, 0, 1.5),
            ),
            ("synthetic-only",),
        )

    with pytest.raises(ValueError, match="unique"):
        make_fixture(
            "duplicate-index",
            Direction.BULLISH,
            (
                Candle(0, "2026-01-01T00:00:00Z", 1, 2, 0, 1.5),
                Candle(0, "2026-01-01T00:01:00Z", 1, 2, 0, 1.5),
            ),
            ("synthetic-only",),
        )


def test_contract_contains_no_signal_decision_field():
    # The fixture is data/provenance only. Production BUY/SELL generation is
    # intentionally outside this contract.
    assert not hasattr(EXAMPLE_BULLISH, "signal")
    assert not hasattr(EXAMPLE_BULLISH, "entry_price")
    assert not hasattr(EXAMPLE_BULLISH, "take_profit")
    assert not hasattr(EXAMPLE_BULLISH, "stop_loss")
