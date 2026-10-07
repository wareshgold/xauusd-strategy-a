from __future__ import annotations

"""Renderer-neutral bridge from Factory telemetry to the SP2L station world.

This module is deliberately small. It translates already-declared Factory
worker telemetry into a deterministic presentation state. It does not execute
research, define strategy geometry, create signals, or authorize production.
"""

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .job_events import FactoryJobEvent


VALID_STATIONS = {
    "discovery",
    "stability",
    "robustness",
    "holdout",
    "forward",
    "idle",
}

VALID_STATES = {
    "QUEUED",
    "RUNNING",
    "HEARTBEAT",
    "COMPLETED",
    "FAILED",
    "IDLE",
}


@dataclass(frozen=True)
class WorldWorker:
    worker_id: str
    station: str
    state: str
    progress: float
    job_id: str | None
    job_type: str | None
    phase: str | None
    detail: str | None
    output_artifact: str | None
    error: str | None


@dataclass(frozen=True)
class WorldHandoff:
    sequence: int
    job_id: str
    source_station: str
    destination_station: str
    output_artifact: str
    event_fingerprint: str


@dataclass(frozen=True)
class FactoryWorldState:
    workers: tuple[WorldWorker, ...]
    handoffs: tuple[WorldHandoff, ...] = ()
    production_locked: bool = True
    buy_sell_generation: int = 0


def _station(value: Any) -> str:
    station = str(value or "idle").strip().lower()
    if station not in VALID_STATIONS:
        raise ValueError(f"invalid Factory world station: {station!r}")
    return station


def _state(value: Any) -> str:
    state = str(value or "IDLE").strip().upper()
    if state not in VALID_STATES:
        raise ValueError(f"invalid Factory worker state: {state!r}")
    return state


def _progress(value: Any) -> float:
    try:
        progress = float(value or 0.0)
    except (TypeError, ValueError) as exc:
        raise ValueError("worker progress must be numeric") from exc
    if progress < 0.0 or progress > 100.0:
        raise ValueError("worker progress must be between 0 and 100")
    return progress


def _worker(item: Mapping[str, Any]) -> WorldWorker:
    worker_id = str(item.get("worker_id") or "").strip()
    if not worker_id:
        raise ValueError("worker_id is required")

    return WorldWorker(
        worker_id=worker_id,
        station=_station(item.get("station")),
        state=_state(item.get("state")),
        progress=_progress(item.get("progress")),
        job_id=item.get("job_id"),
        job_type=item.get("job_type"),
        phase=item.get("phase"),
        detail=item.get("detail"),
        output_artifact=item.get("output_artifact"),
        error=item.get("error"),
    )


def build_world_state(workers: Iterable[Mapping[str, Any]], events: Iterable[FactoryJobEvent] = ()) -> FactoryWorldState:
    """Translate normalized Factory telemetry into deterministic world state.

    Ordering is stable by worker_id so the renderer cannot introduce
    nondeterministic presentation ordering from dictionary/list insertion.
    """
    state = tuple(sorted((_worker(item) for item in workers), key=lambda w: w.worker_id))
    handoffs = build_world_handoffs(events)
    return FactoryWorldState(workers=state, handoffs=handoffs)



def build_world_handoffs(events: Iterable[FactoryJobEvent]) -> tuple[WorldHandoff, ...]:
    """Expose accepted handoffs with source reconstructed from the same journal."""
    ordered = tuple(sorted(events, key=lambda event: event.sequence))
    result = []
    for event in ordered:
        if event.event_type != "HANDOFF_ACCEPTED":
            continue
        event.validate()
        if not event.station or not event.output_artifact:
            continue
        source = ""
        for prior in reversed(ordered):
            if prior.sequence >= event.sequence or prior.job_id != event.job_id:
                continue
            if prior.event_type == "COMPLETED" and prior.station and prior.output_artifact == event.output_artifact:
                source = prior.station
                break
        result.append(WorldHandoff(sequence=event.sequence, job_id=event.job_id, source_station=source, destination_station=event.station, output_artifact=event.output_artifact, event_fingerprint=event.event_fingerprint))
    return tuple(sorted(result, key=lambda item: item.sequence))
