from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EvidenceDecision(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ValidationEvidence:
    source_provenance_ok: bool
    dataset_fingerprint_ok: bool
    fixtures_ok: bool
    dev_results_recorded: bool
    validation_results_recorded: bool
    holdout_untouched: bool
    source_geometry_resolved: bool = False


def decide_evidence(value: ValidationEvidence) -> EvidenceDecision:
    if not value.holdout_untouched:
        return EvidenceDecision.BLOCK
    if not value.source_provenance_ok or not value.dataset_fingerprint_ok:
        return EvidenceDecision.BLOCK
    if not value.fixtures_ok:
        return EvidenceDecision.BLOCK
    if not value.dev_results_recorded or not value.validation_results_recorded:
        return EvidenceDecision.UNKNOWN
    if not value.source_geometry_resolved:
        return EvidenceDecision.UNKNOWN
    return EvidenceDecision.PASS
