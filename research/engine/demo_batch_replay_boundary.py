from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ReplayBoundaryDecision(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    REQUIRE_REVIEW = "REQUIRE_REVIEW"


@dataclass(frozen=True)
class ReplayBoundaryInput:
    sequence_contiguous: bool
    replay_deterministic: bool
    state_recovered: bool
    reconciliation_match: bool


def decide_replay_boundary(value: ReplayBoundaryInput) -> ReplayBoundaryDecision:
    if not value.sequence_contiguous:
        return ReplayBoundaryDecision.BLOCK
    if not value.replay_deterministic or not value.state_recovered or not value.reconciliation_match:
        return ReplayBoundaryDecision.REQUIRE_REVIEW
    return ReplayBoundaryDecision.PASS
