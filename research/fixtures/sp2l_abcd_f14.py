"""F14: discriminate AB=CD anchor candidates without selecting a source rule.

Research-only. Synthetic values expose wick/body/pivot/mixed constructions.
No tolerance or production anchor rule is encoded.
"""
from dataclasses import dataclass
from enum import Enum


class AnchorModel(str, Enum):
    WICK = "WICK"
    BODY = "BODY"
    STRUCTURAL_PIVOT = "STRUCTURAL_PIVOT"
    MIXED = "MIXED"


@dataclass(frozen=True)
class AB CDCase:
    model: AnchorModel
    A: float
    B: float
    C: float
    D: float

    def ab(self) -> float:
        return abs(self.B - self.A)

    def cd(self) -> float:
        return abs(self.D - self.C)


def f14_cases():
    return (
        AB_CDCase(AnchorModel.WICK, 100.0, 110.0, 105.0, 115.0),
        AB_CDCase(AnchorModel.BODY, 101.0, 109.0, 105.0, 113.0),
        AB_CDCase(AnchorModel.STRUCTURAL_PIVOT, 99.5, 110.5, 104.5, 115.5),
        AB_CDCase(AnchorModel.MIXED, 100.0, 109.0, 105.0, 114.0),
    )


def exact_equal(case: AB_CDCase) -> bool:
    return case.ab() == case.cd()


def classify(case: AB_CDCase):
    # Equality is observable for the supplied candidate anchors, but this
    # fixture intentionally does not infer which anchor model the source uses.
    return case.model, exact_equal(case)
