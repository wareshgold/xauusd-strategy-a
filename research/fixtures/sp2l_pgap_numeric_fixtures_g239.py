"""G239 numeric P-Gap fixture matrix.

Research-only. These fixtures encode competing hypotheses and source-derived
observations without selecting a canonical SP2L P-Gap geometry. They must not
be imported by production code.
"""
from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Candle:
    open: float
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class NumericFixture:
    fixture_id: str
    description: str
    candles: tuple[Candle, ...]
    breakout_context: bool | None
    source_spike_annotation: bool | None
    expected_strict_gap: Decision
    expected_inclusive_gap: Decision
    expected_body_only_gap: Decision
    expected_gap_plus_spike: Decision
    expected_breakout_hypothesis: Decision


def strict_bullish_gap(candles: tuple[Candle, ...]) -> Decision:
    """Candidate H1: High[t-2] < Low[t]."""
    if len(candles) < 3:
        return Decision.UNKNOWN
    return Decision.PASS if candles[-3].high < candles[-1].low else Decision.FAIL


def inclusive_bullish_gap(candles: tuple[Candle, ...]) -> Decision:
    """Boundary probe only: High[t-2] <= Low[t]."""
    if len(candles) < 3:
        return Decision.UNKNOWN
    return Decision.PASS if candles[-3].high <= candles[-1].low else Decision.FAIL


def body_only_bullish_gap(candles: tuple[Candle, ...]) -> Decision:
    """Candidate body-only interpretation; not source-frozen."""
    if len(candles) < 3:
        return Decision.UNKNOWN
    left = candles[-3]
    right = candles[-1]
    left_body_high = max(left.open, left.close)
    right_body_low = min(right.open, right.close)
    return Decision.PASS if left_body_high < right_body_low else Decision.FAIL


def gap_plus_source_spike(
    candles: tuple[Candle, ...], source_spike_annotation: bool | None
) -> Decision:
    """Candidate conjunction using an explicit source annotation.

    The fixture deliberately does not derive "spike" from a threshold. This
    preserves the unresolved source geometry while allowing the hypothesis to
    be tested deterministically.
    """
    gap = strict_bullish_gap(candles)
    if gap is Decision.UNKNOWN or source_spike_annotation is None:
        return Decision.UNKNOWN
    return Decision.PASS if gap is Decision.PASS and source_spike_annotation else Decision.FAIL


def breakout_gap_hypothesis(
    candles: tuple[Candle, ...], breakout_context: bool | None
) -> Decision:
    """Candidate H2: strict gap plus explicitly supplied breakout context."""
    gap = strict_bullish_gap(candles)
    if gap is Decision.UNKNOWN or breakout_context is None:
        return Decision.UNKNOWN
    return Decision.PASS if gap is Decision.PASS and breakout_context else Decision.FAIL


def fixtures() -> tuple[NumericFixture, ...]:
    return (
        NumericFixture(
            "F1",
            "Strict full-extrema separation",
            (
                Candle(100.0, 105.0, 99.0, 104.0),
                Candle(104.0, 120.0, 103.0, 118.0),
                Candle(108.0, 112.0, 106.0, 110.0),
            ),
            None,
            True,
            Decision.PASS,
            Decision.PASS,
            Decision.PASS,
            Decision.PASS,
            Decision.UNKNOWN,
        ),
        NumericFixture(
            "F2",
            "Body-only separation with overlapping wicks",
            (
                Candle(100.0, 108.0, 99.0, 104.0),
                Candle(104.0, 120.0, 103.0, 118.0),
                Candle(106.0, 112.0, 102.0, 109.0),
            ),
            None,
            True,
            Decision.FAIL,
            Decision.FAIL,
            Decision.PASS,
            Decision.FAIL,
            Decision.UNKNOWN,
        ),
        NumericFixture(
            "F3",
            "Exact-touch boundary",
            (
                Candle(100.0, 105.0, 99.0, 104.0),
                Candle(104.0, 120.0, 103.0, 118.0),
                Candle(105.0, 112.0, 105.0, 110.0),
            ),
            None,
            True,
            Decision.FAIL,
            Decision.PASS,
            Decision.PASS,
            Decision.FAIL,
            Decision.UNKNOWN,
        ),
        NumericFixture(
            "F4",
            "Generic gap without breakout context",
            (
                Candle(100.0, 105.0, 99.0, 104.0),
                Candle(104.0, 115.0, 103.0, 113.0),
                Candle(109.0, 112.0, 106.0, 110.0),
            ),
            False,
            True,
            Decision.PASS,
            Decision.PASS,
            Decision.PASS,
            Decision.PASS,
            Decision.FAIL,
        ),
        NumericFixture(
            "F5",
            "Gap with explicitly supplied breakout context",
            (
                Candle(100.0, 105.0, 99.0, 104.0),
                Candle(104.0, 120.0, 103.0, 118.0),
                Candle(109.0, 112.0, 106.0, 110.0),
            ),
            True,
            True,
            Decision.PASS,
            Decision.PASS,
            Decision.PASS,
            Decision.PASS,
            Decision.PASS,
        ),
        NumericFixture(
            "F6",
            "Directional move without qualifying gap",
            (
                Candle(100.0, 105.0, 99.0, 104.0),
                Candle(104.0, 115.0, 103.0, 113.0),
                Candle(103.0, 112.0, 101.0, 104.0),
            ),
            None,
            True,
            Decision.FAIL,
            Decision.FAIL,
            Decision.FAIL,
            Decision.FAIL,
            Decision.UNKNOWN,
        ),
        NumericFixture(
            "F7",
            "Gap with weak/non-spike intervening candle",
            (
                Candle(100.0, 105.0, 99.0, 104.0),
                Candle(104.0, 107.0, 103.0, 106.0),
                Candle(109.0, 112.0, 106.0, 110.0),
            ),
            None,
            False,
            Decision.PASS,
            Decision.PASS,
            Decision.PASS,
            Decision.FAIL,
            Decision.UNKNOWN,
        ),
        NumericFixture(
            "F8",
            "Gap with explicit clear-spike/breakout annotation",
            (
                Candle(100.0, 105.0, 99.0, 104.0),
                Candle(104.0, 125.0, 103.0, 122.0),
                Candle(109.0, 114.0, 106.0, 112.0),
            ),
            True,
            True,
            Decision.PASS,
            Decision.PASS,
            Decision.PASS,
            Decision.PASS,
            Decision.PASS,
        ),
    )
