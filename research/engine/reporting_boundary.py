from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchReportContext:
    geometry_frozen: bool
    strategy_validation_unlocked: bool


def canonical_claim_allowed(context: ResearchReportContext) -> bool:
    return context.geometry_frozen and context.strategy_validation_unlocked
