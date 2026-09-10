from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AuditDecision(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ResearchAuditInput:
    provenance_complete: bool
    evidence_complete: bool
    fixture_results_recorded: bool
    dev_recorded: bool
    validation_recorded: bool
    holdout_untouched: bool
    source_geometry_resolved: bool


def decide_audit(value: ResearchAuditInput) -> AuditDecision:
    if not value.provenance_complete or not value.evidence_complete:
        return AuditDecision.BLOCK
    if not value.fixture_results_recorded or not value.dev_recorded or not value.validation_recorded:
        return AuditDecision.UNKNOWN
    if not value.holdout_untouched:
        return AuditDecision.BLOCK
    if not value.source_geometry_resolved:
        return AuditDecision.UNKNOWN
    return AuditDecision.PASS
