from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchReportContext:
    geometry_frozen: bool
    strategy_validation_unlocked: bool


def assert_report_is_research_only(context: ResearchReportContext) -> None:
    if context.geometry_frozen or context.strategy_validation_unlocked:
        raise RuntimeError("G68 research-only report context cannot be used after production-gate transition")


def canonical_claim_allowed(context: ResearchReportContext) -> bool:
    return context.geometry_frozen and context.strategy_validation_unlocked
