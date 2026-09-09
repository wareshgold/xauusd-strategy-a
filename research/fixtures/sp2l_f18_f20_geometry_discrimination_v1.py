"""SP2L F18-F20 source-resolution discrimination fixtures.

These fixtures test interpretation boundaries only. They intentionally do not
choose a production trigger, AB=CD anchor model, or Leg-2/TP formula.
"""
from dataclasses import dataclass
from enum import Enum


class TriggerForm(str, Enum):
    ONE_CANDLE = "one_candle"
    TWO_CANDLE = "two_candle"
    THREE_CANDLE = "three_candle"
    KEY_BAR = "key_bar"
    MARKET_RECLAIM = "market_reclaim"  # negative candidate


class AnchorModel(str, Enum):
    WICK = "wick"
    BODY = "body"
    STRUCTURAL_PIVOT = "structural_pivot"
    MIXED = "mixed"


@dataclass(frozen=True)
class TriggerCandidate:
    form: TriggerForm
    confirms_pending_limit: bool


@dataclass(frozen=True)
class LegMeasurement:
    entry: float
    leg2_start: float
    leg1_magnitude: float
    leg2_magnitude: float


def trigger_candidate(form: TriggerForm) -> TriggerCandidate:
    # Source confirms candle-count/key-bar families; acceptance is unresolved.
    return TriggerCandidate(form=form, confirms_pending_limit=form != TriggerForm.MARKET_RECLAIM)


def abcd_equal(leg1_magnitude: float, leg2_magnitude: float) -> bool:
    # Exact equality is a discrimination fixture only. Source tolerance is unresolved.
    return leg1_magnitude == leg2_magnitude


def candidate_anchor_points(values: dict[str, float], model: AnchorModel) -> tuple[float, float, float, float]:
    """Return candidate A/B/C/D values without selecting a canonical model."""
    if model == AnchorModel.WICK:
        return values["A_wick"], values["B_wick"], values["C_wick"], values["D_wick"]
    if model == AnchorModel.BODY:
        return values["A_body"], values["B_body"], values["C_body"], values["D_body"]
    if model == AnchorModel.STRUCTURAL_PIVOT:
        return values["A_pivot"], values["B_pivot"], values["C_pivot"], values["D_pivot"]
    return values["A_wick"], values["B_body"], values["C_pivot"], values["D_wick"]


def entry_leg2_separated(m: LegMeasurement) -> bool:
    return m.entry != m.leg2_start


def leg2_projection_candidate(entry: float, leg1_magnitude: float, direction: int) -> float:
    """Source-shaped magnitude projection candidate, not a frozen TP rule."""
    return entry + direction * leg1_magnitude
