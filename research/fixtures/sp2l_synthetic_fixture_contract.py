"""Source-safe synthetic fixtures for SP2L research.

This module defines a deterministic *fixture contract*, not Strategy A
execution logic. It deliberately separates source-confirmed semantics from
geometry that remains unresolved. No P-Gap formula, entry anchor, fill rule,
AB=CD tolerance, target formula, refresh threshold, or BUY/SELL decision is
encoded here.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final


class EvidenceStatus(str, Enum):
    CONFIRMED = "confirmed"
    UNRESOLVED = "unresolved"
    BLOCKED = "blocked"


class Direction(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"


class GeometryDimension(str, Enum):
    P_GAP = "p_gap"
    ENTRY_ANCHOR = "entry_anchor"
    LEG2_START = "leg2_start"
    STRUCTURAL_INVALIDATION = "structural_invalidation"
    PENDING_REFRESH = "pending_refresh"
    TRIGGER_CLASSIFIER = "trigger_classifier"
    ABCD_ANCHORS = "abcd_anchors"
    ABCD_TOLERANCE = "abcd_tolerance"
    TARGETS_2X = "targets_2x"
    BEARISH_MIRROR = "bearish_mirror"


@dataclass(frozen=True)
class Candle:
    index: int
    timestamp: str
    open: float
    high: float
    low: float
    close: float

    def validate(self) -> None:
        if self.index < 0:
            raise ValueError("candle index must be non-negative")
        if not self.timestamp:
            raise ValueError("candle timestamp must be non-empty")
        if not all(isinstance(value, (int, float)) for value in (self.open, self.high, self.low, self.close)):
            raise ValueError("OHLC values must be numeric")
        if not (self.low <= self.open <= self.high):
            raise ValueError("OHLC invariant violated: open outside low/high")
        if not (self.low <= self.close <= self.high):
            raise ValueError("OHLC invariant violated: close outside low/high")


@dataclass(frozen=True)
class EvidenceLabel:
    dimension: GeometryDimension
    status: EvidenceStatus
    note: str


@dataclass(frozen=True)
class SyntheticFixture:
    fixture_id: str
    direction: Direction
    candles: tuple[Candle, ...]
    labels: tuple[EvidenceLabel, ...]
    source_refs: tuple[str, ...]

    def validate(self) -> None:
        if not self.fixture_id:
            raise ValueError("fixture_id must be non-empty")
        if not self.candles:
            raise ValueError("fixture must contain at least one candle")
        if tuple(sorted(self.candles, key=lambda c: c.index)) != self.candles:
            raise ValueError("candles must be ordered by index")
        if len({c.index for c in self.candles}) != len(self.candles):
            raise ValueError("candle indices must be unique")
        for candle in self.candles:
            candle.validate()
        dimensions = [label.dimension for label in self.labels]
        if len(set(dimensions)) != len(dimensions):
            raise ValueError("each geometry dimension may have one label per fixture")
        if not self.source_refs:
            raise ValueError("source_refs must identify provenance")
        if any(not ref.strip() for ref in self.source_refs):
            raise ValueError("source_refs may not contain empty references")


CONFIRMED_SEMANTICS: Final[frozenset[GeometryDimension]] = frozenset()
BLOCKED_EXECUTABLE_GEOMETRY: Final[frozenset[GeometryDimension]] = frozenset(GeometryDimension)


def make_fixture(fixture_id: str, direction: Direction, candles: tuple[Candle, ...], source_refs: tuple[str, ...]) -> SyntheticFixture:
    labels = tuple(EvidenceLabel(dimension=dimension, status=EvidenceStatus.BLOCKED, note="Synthetic fixture only; source does not uniquely discriminate executable geometry.") for dimension in GeometryDimension)
    fixture = SyntheticFixture(fixture_id, direction, candles, labels, source_refs)
    fixture.validate()
    return fixture


EXAMPLE_BULLISH: Final[SyntheticFixture] = make_fixture(
    "synthetic-bullish-confirmed-semantics-only-v1", Direction.BULLISH,
    (Candle(0, "2026-01-01T00:00:00Z", 100.0, 101.0, 99.5, 100.5), Candle(1, "2026-01-01T00:01:00Z", 100.5, 103.0, 100.4, 102.7), Candle(2, "2026-01-01T00:02:00Z", 102.7, 104.0, 102.0, 103.5), Candle(3, "2026-01-01T00:03:00Z", 103.5, 103.8, 101.8, 102.4)),
    ("synthetic-only; no source frame asserted",),
)

EXAMPLE_BEARISH: Final[SyntheticFixture] = make_fixture(
    "synthetic-bearish-confirmed-semantics-only-v1", Direction.BEARISH,
    (Candle(0, "2026-01-01T00:00:00Z", 200.0, 200.5, 199.0, 199.5), Candle(1, "2026-01-01T00:01:00Z", 199.5, 199.7, 197.0, 197.3), Candle(2, "2026-01-01T00:02:00Z", 197.3, 198.0, 196.0, 196.5), Candle(3, "2026-01-01T00:03:00Z", 196.5, 198.2, 196.3, 197.8)),
    ("synthetic-only; no source frame asserted",),
)
