"""Source-resolution fixtures for Entry, structural invalidation, Trigger and 2X.

These fixtures encode competing interpretations only. They are not a production
strategy implementation and intentionally leave unresolved source geometry
unfrozen.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Bar:
    i: int
    o: float
    h: float
    l: float
    c: float


def entry_variants() -> Dict[str, Dict[str, float]]:
    # Same correction sequence; candidate pending-limit anchors differ.
    return {
        "first_structural_low": {
            "base_low": 100.0,
            "first_low": 103.0,
            "relevant_higher_low": 106.0,
            "leg2_start": 108.0,
        },
        "relevant_higher_low": {
            "base_low": 100.0,
            "first_low": 103.0,
            "relevant_higher_low": 106.0,
            "leg2_start": 108.0,
        },
        "leg2_start": {
            "base_low": 100.0,
            "first_low": 103.0,
            "relevant_higher_low": 106.0,
            "leg2_start": 108.0,
        },
    }


def invalidation_variants() -> Dict[str, Dict[str, float]]:
    # Bullish example: the candidate entry moves with structure while the
    # structural/base invalidation remains below. The replacement threshold
    # is intentionally NOT encoded as a production percentage or price rule.
    return {
        "structural_base_low": {"entry": 106.0, "sl": 100.0, "new_entry": 107.0, "new_sl": 100.0},
        "entry_local_low": {"entry": 106.0, "sl": 103.0, "new_entry": 107.0, "new_sl": 104.0},
        "fixed_distance": {"entry": 106.0, "sl": 100.0, "new_entry": 107.0, "new_sl": 101.0},
    }


def trigger_variants() -> Dict[str, List[Bar]]:
    # The source demonstrates 1/2/3-candle trigger examples. These fixtures
    # distinguish candle-count interpretation from a universal close-reclaim
    # assumption, which is explicitly not canonical.
    return {
        "one_candle": [
            Bar(0, 106.0, 108.0, 105.5, 107.5),
        ],
        "two_candle": [
            Bar(0, 106.0, 107.0, 105.5, 106.5),
            Bar(1, 106.5, 108.0, 106.2, 107.8),
        ],
        "three_candle": [
            Bar(0, 106.0, 106.8, 105.5, 106.4),
            Bar(1, 106.4, 107.2, 105.9, 106.8),
            Bar(2, 106.8, 108.0, 106.6, 107.7),
        ],
    }


def two_x_variants() -> Dict[str, Dict[str, float]]:
    # The source describes 2X using a half-target-type trigger, but the exact
    # target/entry/SL construction is unresolved. Keep competing formulas
    # visible without selecting one.
    return {
        "half_target_from_entry": {"entry": 106.0, "target": 118.0, "sl": 100.0},
        "two_r_from_entry": {"entry": 106.0, "target": 118.0, "sl": 100.0},
        "half_range_reference": {"entry": 106.0, "target": 118.0, "sl": 100.0},
    }


def discrimination_report() -> Dict[str, object]:
    return {
        "entry": {
            name: {
                "candidate_anchor": values[name],
                "entry_not_leg2_start": values["relevant_higher_low"] != values["leg2_start"],
            }
            for name, values in entry_variants().items()
        },
        "invalidation": invalidation_variants(),
        "trigger": {name: len(bars) for name, bars in trigger_variants().items()},
        "2X": two_x_variants(),
        "unresolved": [
            "exact pending-limit price anchor",
            "exact structural invalidation anchor",
            "pending-order replacement threshold and timing",
            "trigger taxonomy and acceptance criteria",
            "2X exact formula and reference levels",
            "whether 2X is entry management, target management, or both",
        ],
    }
