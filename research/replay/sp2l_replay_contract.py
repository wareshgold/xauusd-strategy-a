"""Deterministic, source-safe SP2L observation replay.

The replay layer emits observations only. It consumes the synthetic fixture
contract and preserves candle order, provenance, direction, and the current
geometry blocker state. No P-Gap, entry, invalidation, AB=CD, target, fill,
refresh, buffer, or BUY/SELL rule is implemented here.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final

from research.fixtures.sp2l_synthetic_fixture_contract import (
    BLOCKED_EXECUTABLE_GEOMETRY,
    EvidenceStatus,
    GeometryDimension,
    SyntheticFixture,
)


class ReplayEventKind(str, Enum):
    CANDLE_OBSERVED = "candle_observed"
    GEOMETRY_BLOCKED = "geometry_blocked"


@dataclass(frozen=True)
class ReplayEvent:
    fixture_id: str
    sequence: int
    candle_index: int
    timestamp: str
    direction: str
    kind: ReplayEventKind
    geometry_status: tuple[tuple[str, str], ...]
    source_refs: tuple[str, ...]


@dataclass(frozen=True)
class ReplayResult:
    fixture_id: str
    events: tuple[ReplayEvent, ...]
    execution_authorized: bool

    def validate(self) -> None:
        if not self.fixture_id:
            raise ValueError("fixture_id must be non-empty")
        if not self.events:
            raise ValueError("replay must contain at least one event")
        if self.execution_authorized:
            raise ValueError("source-safe replay can never authorize execution")
        sequences = tuple(event.sequence for event in self.events)
        if sequences != tuple(range(len(self.events))):
            raise ValueError("event sequence must be contiguous and deterministic")
        if any(not event.source_refs for event in self.events):
            raise ValueError("every replay event must preserve provenance")


BLOCKED_STATUS: Final[str] = EvidenceStatus.BLOCKED.value


def replay_fixture(fixture: SyntheticFixture) -> ReplayResult:
    """Replay a fixture as ordered observations while preserving blockers."""
    fixture.validate()

    labels_by_dimension = {label.dimension: label for label in fixture.labels}
    missing = set(BLOCKED_EXECUTABLE_GEOMETRY) - set(labels_by_dimension)
    if missing:
        raise ValueError("fixture is missing executable-geometry blocker labels")

    geometry_status = tuple(
        (dimension.value, labels_by_dimension[dimension].status.value)
        for dimension in GeometryDimension
    )

    events: list[ReplayEvent] = []
    for sequence, candle in enumerate(fixture.candles):
        events.append(
            ReplayEvent(
                fixture_id=fixture.fixture_id,
                sequence=sequence,
                candle_index=candle.index,
                timestamp=candle.timestamp,
                direction=fixture.direction.value,
                kind=ReplayEventKind.CANDLE_OBSERVED,
                geometry_status=geometry_status,
                source_refs=fixture.source_refs,
            )
        )

    events.append(
        ReplayEvent(
            fixture_id=fixture.fixture_id,
            sequence=len(events),
            candle_index=fixture.candles[-1].index,
            timestamp=fixture.candles[-1].timestamp,
            direction=fixture.direction.value,
            kind=ReplayEventKind.GEOMETRY_BLOCKED,
            geometry_status=geometry_status,
            source_refs=fixture.source_refs,
        )
    )

    result = ReplayResult(fixture.fixture_id, tuple(events), execution_authorized=False)
    result.validate()
    return result


def replay_examples() -> tuple[ReplayResult, ...]:
    """Return deterministic replay outputs for the two source-safe examples."""
    from research.fixtures.sp2l_synthetic_fixture_contract import EXAMPLE_BEARISH, EXAMPLE_BULLISH

    return (replay_fixture(EXAMPLE_BULLISH), replay_fixture(EXAMPLE_BEARISH))
