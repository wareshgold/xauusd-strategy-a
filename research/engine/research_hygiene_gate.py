from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HygieneDecision(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class HygieneInput:
    source_versioned: bool
    dataset_versioned: bool
    specification_frozen: bool
    validation_isolation_preserved: bool
    live_authorization: bool = False


def decide_hygiene(value: HygieneInput) -> HygieneDecision:
    if not value.source_versioned or not value.dataset_versioned:
        return HygieneDecision.BLOCK
    if not value.validation_isolation_preserved:
        return HygieneDecision.BLOCK
    if value.live_authorization:
        return HygieneDecision.BLOCK
    if not value.specification_frozen:
        return HygieneDecision.UNKNOWN
    return HygieneDecision.PASS
