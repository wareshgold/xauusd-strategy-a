from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Verdict(str, Enum):
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class TargetedCase:
    blocker: str
    case_id: str
    observation: str
    source_unique: bool
    verdict: Verdict


CASES = (
    TargetedCase("B1", "B1-RANGE-SEPARATION", "Source shows gap/separation constructions associated with valid BO/P-Gap.", False, Verdict.UNRESOLVED),
    TargetedCase("B1", "B1-GENERIC-FVG", "Generic three-candle imbalance is not sufficient as a canonical P-Gap definition.", True, Verdict.REJECTED),
    TargetedCase("B2", "B2-LATEST-STRUCTURAL", "Source examples support updating the pending level as structural Higher-Lows/Lower-Highs develop.", False, Verdict.UNRESOLVED),
    TargetedCase("B3", "B3-STRUCTURAL-INVALIDATION", "Source supports structural invalidation distinct from Entry, but exact OHLC boundary is not unique.", False, Verdict.UNRESOLVED),
    TargetedCase("B4", "B4-TRIGGER-FAMILY", "One-, two-, three-candle and Key-Bar forms are source-consistent; acceptance/precedence remains unspecified.", False, Verdict.UNRESOLVED),
    TargetedCase("B5", "B5-ABCD-MAGNITUDE", "AB=CD is explicit, while endpoint model and tolerance remain unspecified.", False, Verdict.UNRESOLVED),
    TargetedCase("B6", "B6-LEG2-PROJECTION", "Leg2 continuation and target concepts are source-supported, but executable projection is not unique.", False, Verdict.UNRESOLVED),
)


def canonical_cases() -> tuple[TargetedCase, ...]:
    return tuple(case for case in CASES if case.verdict is Verdict.RESOLVED)


def unresolved_critical_blockers() -> tuple[str, ...]:
    return tuple(sorted({case.blocker for case in CASES if case.verdict is Verdict.UNRESOLVED}))


def frozen_geometry_allowed() -> bool:
    return not unresolved_critical_blockers()
