"""Deterministic synthetic SP2L geometry fixtures.

Research-only. These fixtures do not encode a production strategy and do not
select between unresolved source interpretations. They expose coordinates and
invariants needed for discrimination before historical testing.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass(frozen=True)
class Candle:
    t: int
    o: float
    h: float
    l: float
    c: float


@dataclass(frozen=True)
class Fixture:
    fixture_id: str
    concept: str
    candles: List[Candle]
    candidates: Dict[str, Any]
    invariants: List[str]

    def record(self) -> Dict[str, Any]:
        return {
            "fixture_id": self.fixture_id,
            "concept": self.concept,
            "candles": [asdict(c) for c in self.candles],
            "candidates": self.candidates,
            "invariants": self.invariants,
        }


def bullish_structure() -> Fixture:
    candles = [
        Candle(0, 100.0, 101.0, 99.0, 100.5),
        Candle(1, 100.5, 103.0, 100.4, 102.8),
        Candle(2, 102.8, 104.0, 102.2, 103.7),
        Candle(3, 103.7, 105.0, 103.0, 104.8),
        Candle(4, 104.8, 106.5, 104.6, 106.2),
        Candle(5, 106.2, 107.0, 105.4, 106.0),
        Candle(6, 106.0, 107.5, 105.8, 107.2),
    ]
    return Fixture(
        "F02",
        "fixed_first_low_vs_relevant_higher_low",
        candles,
        {"first_low": 99.0, "candidate_relevant_low": 105.4, "midpoint": 102.2},
        [
            "candidate entry anchors remain distinct",
            "no canonical entry anchor is selected by fixture generation",
        ],
    )


def entry_vs_leg2() -> Fixture:
    candles = [
        Candle(0, 100.0, 101.0, 99.0, 100.5),
        Candle(1, 100.5, 104.0, 100.4, 103.8),
        Candle(2, 103.8, 105.0, 103.0, 104.5),
        Candle(3, 104.5, 105.2, 103.8, 104.0),
        Candle(4, 104.0, 106.0, 103.9, 105.8),
        Candle(5, 105.8, 108.0, 105.5, 107.7),
    ]
    return Fixture(
        "F03",
        "entry_vs_leg2_start",
        candles,
        {"entry_candidate": 103.8, "leg2_start_candidate": 105.8},
        ["entry_price and leg2_start are independently representable", "do not alias coordinates"],
    )


def wick_vs_body() -> Fixture:
    candles = [
        Candle(0, 100.0, 101.0, 99.0, 100.5),
        Candle(1, 100.5, 105.0, 100.0, 104.5),
        Candle(2, 104.5, 106.0, 102.0, 105.0),
    ]
    return Fixture(
        "F05",
        "wick_extreme_vs_body_edge",
        candles,
        {"wick_low": 100.0, "body_low": 104.5, "wick_high": 106.0, "body_high": 105.0},
        ["wick and body anchors remain distinct", "no implicit anchor selection"],
    )


def invalidation_change() -> Fixture:
    candles = [
        Candle(0, 100.0, 101.0, 99.0, 100.5),
        Candle(1, 100.5, 104.0, 100.4, 103.8),
        Candle(2, 103.8, 105.0, 102.5, 104.5),
        Candle(3, 104.5, 106.0, 101.0, 105.5),
    ]
    return Fixture(
        "F06",
        "structural_invalidation_and_order_replacement",
        candles,
        {"initial_entry": 102.5, "initial_sl": 99.0, "later_relevant_low": 101.0},
        ["order state supports KEEP/DELETE/REPLACE", "replacement threshold remains unresolved"],
    )


def build_suite() -> List[Fixture]:
    return [bullish_structure(), entry_vs_leg2(), wick_vs_body(), invalidation_change()]


if __name__ == "__main__":
    import json
    print(json.dumps([f.record() for f in build_suite()], indent=2))
