from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FreshHoldoutResultDecision(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class FreshHoldoutResultInput:
    window_id: str
    dataset_fingerprint: str
    expected_dataset_fingerprint: str
    result_fingerprint: str
    expected_result_fingerprint: str
    optimization_applied: bool = False


def decide_fresh_holdout_result(value: FreshHoldoutResultInput) -> FreshHoldoutResultDecision:
    if value.optimization_applied:
        return FreshHoldoutResultDecision.BLOCK
    if not value.window_id:
        return FreshHoldoutResultDecision.UNKNOWN
    if not value.dataset_fingerprint or not value.expected_dataset_fingerprint:
        return FreshHoldoutResultDecision.UNKNOWN
    if value.dataset_fingerprint != value.expected_dataset_fingerprint:
        return FreshHoldoutResultDecision.BLOCK
    if not value.result_fingerprint or not value.expected_result_fingerprint:
        return FreshHoldoutResultDecision.UNKNOWN
    if value.result_fingerprint != value.expected_result_fingerprint:
        return FreshHoldoutResultDecision.BLOCK
    return FreshHoldoutResultDecision.PASS
