from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ValidationDecision(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ValidationInput:
    specification_frozen: bool
    fixtures_passed: bool
    dev_complete: bool
    validation_isolated: bool
    holdout_touched: bool = False


def decide_validation(value: ValidationInput) -> ValidationDecision:
    if value.holdout_touched:
        return ValidationDecision.BLOCK
    if not value.specification_frozen:
        return ValidationDecision.UNKNOWN
    if not value.fixtures_passed or not value.dev_complete:
        return ValidationDecision.BLOCK
    if not value.validation_isolated:
        return ValidationDecision.BLOCK
    return ValidationDecision.PASS
