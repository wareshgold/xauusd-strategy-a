"""G279 research-only target geometry hypotheses.

These fixtures intentionally encode competing source interpretations. They are
not canonical Strategy A rules and must never be imported by production code.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TargetHypothesis:
    name: str
    description: str


HYPOTHESES = (
    TargetHypothesis("one_r", "TP1 at one entry-to-SL risk interval"),
    TargetHypothesis("two_r", "TP2 at two entry-to-SL risk intervals"),
    TargetHypothesis("point_250_500", "TP1/TP2 using source 250/500 point examples"),
    TargetHypothesis("round_level", "TP1/TP2 selected from source round-level references"),
    TargetHypothesis("abcd", "terminal target tied to an AB=CD endpoint"),
    TargetHypothesis("leg2_projection", "terminal target derived from source-confirmed second-leg projection"),
)


def simple_two_r_target(entry: float, stop: float, direction: str) -> float:
    """Research-only 2R candidate; intentionally not canonical."""
    risk = abs(entry - stop)
    if direction == "BUY":
        return entry + 2 * risk
    if direction == "SELL":
        return entry - 2 * risk
    raise ValueError("direction must be BUY or SELL")
