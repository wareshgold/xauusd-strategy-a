"""Source-resolution fixtures for P-Gap and AB=CD.

These fixtures deliberately encode competing interpretations, not a production
classifier. Values are synthetic and have no historical-market meaning.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Bar:
    i: int
    o: float
    h: float
    l: float
    c: float


def pgap_variants() -> Dict[str, List[Bar]]:
    # V1: breakout close above prior high, next bar follows without returning
    # into the prior candle's range. This mirrors the source-described BO + FT
    # construction while leaving the exact P-Gap formula unresolved.
    v1 = [
        Bar(0, 100, 101, 99, 100.5),
        Bar(1, 100.5, 102, 100.4, 101.8),
        Bar(2, 101.8, 105, 102.5, 104.5),
        Bar(3, 104.5, 107, 104.2, 106.5),
    ]
    # V2: same directional BO but follow-through overlaps prior range.
    v2 = [
        Bar(0, 100, 101, 99, 100.5),
        Bar(1, 100.5, 102, 100.4, 101.8),
        Bar(2, 101.8, 105, 102.5, 104.5),
        Bar(3, 104.5, 106, 101.5, 103.0),
    ]
    # V3: a conventional three-candle FVG-like geometry is present, but this
    # fixture intentionally has no claim that it is a P-Gap.
    v3 = [
        Bar(0, 100, 101, 99, 100.2),
        Bar(1, 100.2, 106, 100.5, 105.8),
        Bar(2, 105.8, 108, 106.2, 107.5),
    ]
    return {"V1_BO_FT_nonoverlap": v1, "V2_BO_FT_overlap": v2, "V3_generic_gap": v3}


def abcd_variants() -> Dict[str, Dict[str, float]]:
    # Same conceptual movement, with multiple plausible anchor definitions.
    # No tolerance is applied: exact equality is the fixture invariant.
    return {
        "pivot_wick": {"A": 100.0, "B": 110.0, "C": 105.0, "D": 115.0},
        "pivot_body": {"A": 101.0, "B": 109.0, "C": 105.0, "D": 113.0},
        "mixed_anchor": {"A": 100.0, "B": 109.0, "C": 105.0, "D": 114.0},
    }


def ab_length(points: Dict[str, float]) -> float:
    return abs(points["B"] - points["A"])


def cd_length(points: Dict[str, float]) -> float:
    return abs(points["D"] - points["C"])


def discrimination_report() -> Dict[str, object]:
    pg = pgap_variants()
    ab = abcd_variants()
    return {
        "pgap": {
            name: {
                "breakout": bars[2].c > bars[1].h,
                "follow_through_does_not_overlap_prior_range": bars[3].l > bars[2].h,
            }
            for name, bars in pg.items()
        },
        "abcd": {
            name: {
                "AB": ab_length(points),
                "CD": cd_length(points),
                "exact_equal": ab_length(points) == cd_length(points),
            }
            for name, points in ab.items()
        },
        "unresolved": [
            "exact P-Gap formula",
            "P-Gap anchor candles/price fields",
            "A/B/C/D source anchors",
            "AB=CD tolerance",
        ],
    }
