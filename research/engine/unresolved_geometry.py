from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GeometryState(str, Enum):
    RESOLVED_SOURCE_GEOMETRY = "RESOLVED_SOURCE_GEOMETRY"
    CANDIDATE_RESEARCH_GEOMETRY = "CANDIDATE_RESEARCH_GEOMETRY"
    UNRESOLVED_SOURCE_GEOMETRY = "UNRESOLVED_SOURCE_GEOMETRY"
    BLOCKED_PRODUCTION = "BLOCKED_PRODUCTION"


@dataclass(frozen=True)
class GeometryDecision:
    component: str
    state: GeometryState
    reason: str


def production_allowed(decision: GeometryDecision) -> bool:
    return decision.state is GeometryState.RESOLVED_SOURCE_GEOMETRY


def require_resolved_for_production(decision: GeometryDecision) -> None:
    if not production_allowed(decision):
        raise RuntimeError(
            f"Production blocked for {decision.component}: {decision.state.value}. {decision.reason}"
        )
