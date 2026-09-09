from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GateState(str, Enum):
    PASS = "PASS"
    PARTIAL_PASS = "PARTIAL_PASS"
    BLOCKED = "BLOCKED"
    LOCKED = "LOCKED"


@dataclass(frozen=True)
class ResearchGateStatus:
    source_resolution: GateState
    synthetic_fixtures: GateState
    frozen_geometry: GateState
    dev_validation: GateState
    val_validation: GateState
    fresh_holdout: GateState
    production: GateState


def production_ready(status: ResearchGateStatus) -> bool:
    return all(
        state is GateState.PASS
        for state in (
            status.source_resolution,
            status.synthetic_fixtures,
            status.frozen_geometry,
            status.dev_validation,
            status.val_validation,
            status.fresh_holdout,
            status.production,
        )
    )
