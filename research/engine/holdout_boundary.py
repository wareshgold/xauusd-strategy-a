from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HoldoutDecision(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class HoldoutInput:
    dataset_fingerprint: str
    window_id: str
    touched: bool
    results_recorded: bool
    specification_version: str


def decide_holdout(value: HoldoutInput) -> HoldoutDecision:
    if value.touched:
        return HoldoutDecision.BLOCK
    if not value.dataset_fingerprint or not value.window_id or not value.specification_version:
        return HoldoutDecision.UNKNOWN
    if value.results_recorded:
        return HoldoutDecision.UNKNOWN
    return HoldoutDecision.PASS
