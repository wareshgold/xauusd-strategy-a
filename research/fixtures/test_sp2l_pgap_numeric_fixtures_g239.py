"""G239 tests for numeric P-Gap hypothesis fixtures.

These tests validate deterministic candidate predicates only. Passing tests do
not freeze the canonical SP2L P-Gap definition.
"""
from research.fixtures.sp2l_pgap_numeric_fixtures_g239 import (
    Decision,
    body_only_bullish_gap,
    breakout_gap_hypothesis,
    fixtures,
    gap_plus_source_spike,
    inclusive_bullish_gap,
    strict_bullish_gap,
)


def test_f1_to_f8_expected_candidate_matrix() -> None:
    for fixture in fixtures():
        assert strict_bullish_gap(fixture.candles) is fixture.expected_strict_gap
        assert inclusive_bullish_gap(fixture.candles) is fixture.expected_inclusive_gap
        assert body_only_bullish_gap(fixture.candles) is fixture.expected_body_only_gap
        assert (
            gap_plus_source_spike(fixture.candles, fixture.source_spike_annotation)
            is fixture.expected_gap_plus_spike
        )
        assert (
            breakout_gap_hypothesis(fixture.candles, fixture.breakout_context)
            is fixture.expected_breakout_hypothesis
        )


def test_f2_separates_body_only_from_full_extrema() -> None:
    fixture = next(item for item in fixtures() if item.fixture_id == "F2")
    assert strict_bullish_gap(fixture.candles) is Decision.FAIL
    assert body_only_bullish_gap(fixture.candles) is Decision.PASS


def test_f3_exact_touch_is_boundary_dependent() -> None:
    fixture = next(item for item in fixtures() if item.fixture_id == "F3")
    assert strict_bullish_gap(fixture.candles) is Decision.FAIL
    assert inclusive_bullish_gap(fixture.candles) is Decision.PASS


def test_f4_and_f5_isolate_breakout_context() -> None:
    f4 = next(item for item in fixtures() if item.fixture_id == "F4")
    f5 = next(item for item in fixtures() if item.fixture_id == "F5")
    assert strict_bullish_gap(f4.candles) is Decision.PASS
    assert breakout_gap_hypothesis(f4.candles, f4.breakout_context) is Decision.FAIL
    assert strict_bullish_gap(f5.candles) is Decision.PASS
    assert breakout_gap_hypothesis(f5.candles, f5.breakout_context) is Decision.PASS


def test_f6_gap_is_required_even_when_spike_is_annotated() -> None:
    fixture = next(item for item in fixtures() if item.fixture_id == "F6")
    assert strict_bullish_gap(fixture.candles) is Decision.FAIL
    assert gap_plus_source_spike(fixture.candles, fixture.source_spike_annotation) is Decision.FAIL


def test_f7_spike_annotation_is_not_derived_from_an_invented_threshold() -> None:
    fixture = next(item for item in fixtures() if item.fixture_id == "F7")
    assert strict_bullish_gap(fixture.candles) is Decision.PASS
    assert gap_plus_source_spike(fixture.candles, fixture.source_spike_annotation) is Decision.FAIL


def test_f8_gap_plus_explicit_spike_and_breakout_annotations_pass() -> None:
    fixture = next(item for item in fixtures() if item.fixture_id == "F8")
    assert gap_plus_source_spike(fixture.candles, fixture.source_spike_annotation) is Decision.PASS
    assert breakout_gap_hypothesis(fixture.candles, fixture.breakout_context) is Decision.PASS


def test_unknown_when_history_or_required_annotation_is_missing() -> None:
    fixture = fixtures()[0]
    assert strict_bullish_gap(fixture.candles[:2]) is Decision.UNKNOWN
    assert inclusive_bullish_gap(fixture.candles[:2]) is Decision.UNKNOWN
    assert body_only_bullish_gap(fixture.candles[:2]) is Decision.UNKNOWN
    assert gap_plus_source_spike(fixture.candles, None) is Decision.UNKNOWN
    assert breakout_gap_hypothesis(fixture.candles, None) is Decision.UNKNOWN


def test_no_bearish_geometry_is_promoted_here() -> None:
    """G239 intentionally contains no bearish mirror predicate.

    The bearish P-Gap formula remains unresolved at this gate and therefore is
    not implemented, tested, or promoted by this fixture module.
    """
    assert not hasattr(__import__("research.fixtures.sp2l_pgap_numeric_fixtures_g239", fromlist=["*"]), "generic_bearish_gap")
