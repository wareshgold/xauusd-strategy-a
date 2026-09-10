from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ReproducibilityDecision(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ReproducibilityInput:
    dataset_fingerprint_match: bool
    specification_version_match: bool
    source_provenance_match: bool
    deterministic_execution: bool
    output_fingerprint_match: bool


def decide_reproducibility(value: ReproducibilityInput) -> ReproducibilityDecision:
    if not value.dataset_fingerprint_match or not value.source_provenance_match:
        return ReproducibilityDecision.BLOCK
    if not value.specification_version_match or not value.deterministic_execution:
        return ReproducibilityDecision.BLOCK
    if not value.output_fingerprint_match:
        return ReproducibilityDecision.BLOCK
    return ReproducibilityDecision.PASS
