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
    result_fingerprint: str
    source_result_fingerprint: str
    optimization_applied: bool = False


def decide_fresh_holdout_result(value: FreshHoldoutResultInput) -> FreshHoldoutResultDecision:
    if value.optimization_applied:
        return FreshHoldoutResultDecision.BLOCK
    if not value.window_id or not value.result_fingerprint or not value.source_result_fingerprint:
        return FreshHoldoutResultDecision.UNKNOWN
    if value.result_fingerprint != value.source_result_fingerprint:
        return FreshHoldoutResultDecision.BLOCK
    return FreshHoldoutResultDecision.PASS
