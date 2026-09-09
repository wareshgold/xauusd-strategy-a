"""F13: preserve the source's two 2X interpretations without inventing a formula."""
from dataclasses import dataclass
from enum import Enum


class TwoXInterpretation(str, Enum):
    HALF_TARGET = "HALF_TARGET"
    SECOND_POSITION_RISK_REWARD = "SECOND_POSITION_RISK_REWARD"


@dataclass(frozen=True)
class TwoXCase:
    interpretation: TwoXInterpretation
    entry: float
    target: float
    second_entry: float
    second_stop: float
    second_target: float


def f13_cases():
    return (
        TwoXCase(TwoXInterpretation.HALF_TARGET, 100.0, 110.0, 105.0, 100.0, 115.0),
        TwoXCase(TwoXInterpretation.SECOND_POSITION_RISK_REWARD, 100.0, 110.0, 104.0, 101.0, 113.0),
    )


def classify(case: TwoXCase):
    # Both interpretations are source-supported concepts; exact production
    # formula remains unresolved.
    return case.interpretation
