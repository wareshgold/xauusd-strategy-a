"""Source-safe synthetic fixtures for SP2L research.

This module defines a deterministic fixture contract, not Strategy A execution logic.
No unresolved geometry or execution behavior is encoded here.
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
        if self.index < 0 or not self.timestamp:
            raise ValueError("candle index/timestamp invalid")
        if not all(isinstance(v, (int, float)) for v in (self.open, self.high, self.low, self.close)):
            raise ValueError("OHLC values must be numeric")
        if not (self.low <= self.open <= self.high and self.low <= self.close <= self.high):
            raise ValueError("OHLC invariant violated")

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
        if not self.fixture_id or not self.candles or not self.source_refs:
            raise ValueError("fixture identity/candles/provenance required")
        if tuple(sorted(self.candles, key=lambda c: c.index)) != self.candles:
            raise ValueError("candles must be ordered by index")
        if len({c.index for c in self.candles}) != len(self.candles):
            raise ValueError("candle indices must be unique")
        for candle in self.candles: candle.validate()
        dimensions = [label.dimension for label in self.labels]
        if len(set(dimensions)) != len(dimensions):
            raise ValueError("geometry dimensions must be unique")

CONFIRMED_SEMANTICS: Final[frozenset[GeometryDimension]] = frozenset()
BLOCKED_EXECUTABLE_GEOMETRY: Final[frozenset[GeometryDimension]] = frozenset(GeometryDimension)

def make_fixture(fixture_id: str, direction: Direction, candles: tuple[Candle, ...], source_refs: tuple[str, ...]) -> SyntheticFixture:
    fixture = SyntheticFixture(fixture_id, direction, candles, tuple(EvidenceLabel(d, EvidenceStatus.BLOCKED, "Source-safe synthetic fixture only; executable geometry remains blocked.") for d in GeometryDimension), source_refs)
    fixture.validate()
    return fixture
