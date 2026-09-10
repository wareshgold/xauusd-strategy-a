"""Tests for G228 P-Gap discrimination fixtures.

The tests validate fixture determinism and candidate predicates only. They do
not establish the canonical SP2L P-Gap definition.
"""
from research.fixtures.sp2l_pgap_synthetic_fixtures_g228 import (
    Decision,
    body_only_bullish_gap,
    fixtures,
    generic_bullish_gap,
    h2_with_explicit_context,
)


def test_fixture_h1_and_body_only_expectations_are_deterministic() -> None:
    for fixture in fixtures():
        assert generic_bullish_gap(fixture.candles) is fixture.expected_h1
        assert body_only_bullish_gap(fixture.candles) is fixture.expected_body_only


def test_h2_requires_explicit_context_and_does_not_invent_mapping() -> None:
    for fixture in fixtures():
        h1 = generic_bullish_gap(fixture.candles)
        result = h2_with_explicit_context(h1, fixture.breakout_context)
        if fixture.breakout_context is None:
            assert result is Decision.UNKNOWN
        elif fixture.breakout_context:
            assert result is Decision.PASS
        else:
            assert result is Decision.FAIL


def test_strict_boundary_rejects_exact_touch() -> None:
    fixture = next(item for item in fixtures() if item.fixture_id == "PG-06")
    assert fixture.candles[-3].high == fixture.candles[-1].low
    assert generic_bullish_gap(fixture.candles) is Decision.FAIL


def test_wick_overlap_can_discriminate_body_only_candidate() -> None:
    fixture = next(item for item in fixtures() if item.fixture_id == "PG-02")
    assert generic_bullish_gap(fixture.candles) is Decision.FAIL
    assert body_only_bullish_gap(fixture.candles) is Decision.PASS


def test_adjacent_only_fixture_does_not_satisfy_t_minus_2_relation() -> None:
    fixture = next(item for item in fixtures() if item.fixture_id == "PG-05")
    assert generic_bullish_gap(fixture.candles) is Decision.FAIL
    assert body_only_bullish_gap(fixture.candles) is Decision.PASS


def test_insufficient_history_is_unknown() -> None:
    fixture = fixtures()[0]
    assert generic_bullish_gap(fixture.candles[:2]) is Decision.UNKNOWN
    assert body_only_bullish_gap(fixture.candles[:2]) is Decision.UNKNOWN
