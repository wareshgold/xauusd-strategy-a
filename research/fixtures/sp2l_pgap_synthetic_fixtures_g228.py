"""Deterministic, source-neutral P-Gap discrimination fixtures.

These fixtures intentionally separate hypotheses. They do not encode a
canonical SP2L P-Gap rule and must not be imported by production code.
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
class Fixture:
    fixture_id: str
    candles: tuple[Candle, ...]
    expected_h1: Decision
    expected_body_only: Decision
    breakout_context: bool | None


def generic_bullish_gap(candles: tuple[Candle, ...]) -> Decision:
    """Research candidate only: High[t-2] < Low[t]."""
    if len(candles) < 3:
        return Decision.UNKNOWN
    return Decision.PASS if candles[-3].high < candles[-1].low else Decision.FAIL


def body_only_bullish_gap(candles: tuple[Candle, ...]) -> Decision:
    """Research candidate only: candle bodies are separated."""
    if len(candles) < 3:
        return Decision.UNKNOWN
    left = candles[-3]
    right = candles[-1]
    left_body_high = max(left.open, left.close)
    right_body_low = min(right.open, right.close)
    return Decision.PASS if left_body_high < right_body_low else Decision.FAIL


def h2_with_explicit_context(h1: Decision, breakout_context: bool | None) -> Decision:
    """Do not invent the source's unresolved breakout-context mapping."""
    if h1 is Decision.UNKNOWN or breakout_context is None:
        return Decision.UNKNOWN
    return Decision.PASS if h1 is Decision.PASS and breakout_context else Decision.FAIL


def fixtures() -> tuple[Fixture, ...]:
    return (
        Fixture(
            "PG-01",
            (
                Candle(100, 105, 99, 104),
                Candle(106, 108, 105.5, 107),
                Candle(109, 111, 106, 110),
            ),
            Decision.PASS,
            Decision.PASS,
            None,
        ),
        Fixture(
            "PG-02",
            (
                Candle(100, 106, 99, 105),
                Candle(105.5, 108, 104.5, 107),
                Candle(107, 110, 105.5, 109),
            ),
            Decision.FAIL,
            Decision.PASS,
            None,
        ),
        Fixture(
            "PG-03",
            (
                Candle(100, 104, 99, 103),
                Candle(103, 105, 102, 104),
                Candle(106, 108, 105.5, 108),
                Candle(108, 112, 106.5, 111),
            ),
            Decision.PASS,
            Decision.PASS,
            True,
        ),
        Fixture(
            "PG-04",
            (
                Candle(100, 105, 99, 104),
                Candle(106, 108, 105.5, 107),
                Candle(109, 111, 106, 110),
            ),
            Decision.PASS,
            Decision.PASS,
            False,
        ),
        Fixture(
            "PG-05",
            (
                Candle(100, 106, 99, 105),
                Candle(107, 109, 106.5, 108),
                Candle(106, 110, 105.5, 109),
            ),
            Decision.FAIL,
            Decision.PASS,
            None,
        ),
        Fixture(
            "PG-06",
            (
                Candle(100, 105, 99, 104),
                Candle(105, 107, 104, 106),
                Candle(106, 109, 105, 108),
            ),
            Decision.FAIL,
            Decision.PASS,
            None,
        ),
    )
