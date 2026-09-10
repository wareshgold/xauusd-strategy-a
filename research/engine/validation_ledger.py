from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LedgerDecision(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ValidationLedgerInput:
    source_version: str
    dataset_fingerprint: str
    specification_version: str
    fixture_fingerprint: str
    dev_result_fingerprint: str
    validation_result_fingerprint: str
    holdout_untouched: bool


def decide_ledger(value: ValidationLedgerInput) -> LedgerDecision:
    required = (
        value.source_version,
        value.dataset_fingerprint,
        value.specification_version,
        value.fixture_fingerprint,
        value.dev_result_fingerprint,
        value.validation_result_fingerprint,
    )
    if not all(required):
        return LedgerDecision.UNKNOWN
    if not value.holdout_untouched:
        return LedgerDecision.BLOCK
    return LedgerDecision.PASS
