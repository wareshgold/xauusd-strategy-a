from dataclasses import dataclass
from enum import Enum


class Candidate(str, Enum):
    C1 = "C1_EQUAL_LADDER"
    C2 = "C2_ADJACENT_ANNOTATIONS"
    C3 = "C3_SHIFTED_ANCHORS"


@dataclass(frozen=True)
class TargetLevels:
    sl: float
    entry: float
    tp1: float
    tp2: float


def build_candidate(candidate: Candidate, entry: float = 100.0, point: float = 1.0) -> TargetLevels:
    if candidate is Candidate.C1:
        # Source-compatible hypothesis only: 250 to TP1, 500 to TP2,
        # 1000 total SL-to-TP2.
        return TargetLevels(sl=entry - 500 * point, entry=entry,
                            tp1=entry + 250 * point, tp2=entry + 500 * point)
    if candidate is Candidate.C2:
        # Alternative hypothesis: 250 and 500 are successive target intervals;
        # 1000 is treated as the total SL-to-TP2 distance.
        return TargetLevels(sl=entry - 250 * point, entry=entry,
                            tp1=entry + 250 * point, tp2=entry + 750 * point)
    if candidate is Candidate.C3:
        # Alternative anchor assignment: 250 risk-side, 500 first target,
        # 1000 second target.
        return TargetLevels(sl=entry - 250 * point, entry=entry,
                            tp1=entry + 500 * point, tp2=entry + 1000 * point)
    raise ValueError(candidate)


def assert_fixture_invariants() -> None:
    levels = {c: build_candidate(c) for c in Candidate}
    assert levels[Candidate.C1].sl < levels[Candidate.C1].entry < levels[Candidate.C1].tp1 < levels[Candidate.C1].tp2
    assert levels[Candidate.C2].sl < levels[Candidate.C2].entry < levels[Candidate.C2].tp1 < levels[Candidate.C2].tp2
    assert levels[Candidate.C3].sl < levels[Candidate.C3].entry < levels[Candidate.C3].tp1 < levels[Candidate.C3].tp2
    assert len({tuple(vars(v).values()) for v in levels.values()}) == 3
    assert levels[Candidate.C1].tp1 == 350.0
    assert levels[Candidate.C1].tp2 == 600.0
    assert levels[Candidate.C1].sl == -400.0


if __name__ == "__main__":
    assert_fixture_invariants()
    print("G319 target mapping candidate fixtures: PASS (hypotheses only)")
