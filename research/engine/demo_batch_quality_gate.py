from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BatchQualityDecision(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class BatchQualityInput:
    journal_valid: bool
    sequence_valid: bool
    fingerprints_stable: bool
    recovery_reconciled: bool
    event_count: int


def decide_batch_quality(value: BatchQualityInput) -> BatchQualityDecision:
    if value.event_count < 1:
        return BatchQualityDecision.UNKNOWN
    if not value.journal_valid or not value.sequence_valid:
        return BatchQualityDecision.BLOCK
    if not value.fingerprints_stable or not value.recovery_reconciled:
        return BatchQualityDecision.BLOCK
    return BatchQualityDecision.PASS
