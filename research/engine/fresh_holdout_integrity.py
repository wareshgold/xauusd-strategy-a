from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FreshHoldoutDecision(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class FreshHoldoutIntegrityInput:
    dataset_fingerprint: str
    expected_fingerprint: str
    window_id: str
    result_fingerprint: str
    result_recorded: bool
    optimization_applied: bool = False


def decide_fresh_holdout_integrity(value: FreshHoldoutIntegrityInput) -> FreshHoldoutDecision:
    if value.optimization_applied:
        return FreshHoldoutDecision.BLOCK
    if not value.dataset_fingerprint or not value.expected_fingerprint or not value.window_id:
        return FreshHoldoutDecision.UNKNOWN
    if value.dataset_fingerprint != value.expected_fingerprint:
        return FreshHoldoutDecision.BLOCK
    if value.result_recorded and not value.result_fingerprint:
        return FreshHoldoutDecision.BLOCK
    if not value.result_recorded:
        return FreshHoldoutDecision.UNKNOWN
    return FreshHoldoutDecision.PASS
