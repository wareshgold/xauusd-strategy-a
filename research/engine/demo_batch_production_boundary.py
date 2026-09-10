from __future__ import annotations

from enum import Enum


class BatchProductionDecision(str, Enum):
    BLOCK = "BLOCK"


def production_decision() -> BatchProductionDecision:
    """Recovery/integrity research evidence can never authorize production."""
    return BatchProductionDecision.BLOCK
