"""F12: discriminate source-confirmed 1/2/3-candle trigger family.

Research-only. No trigger form is promoted to a universal production rule.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class TriggerForm(str, Enum):
    ONE_CANDLE = "1_CANDLE"
    TWO_CANDLE = "2_CANDLE"
    THREE_CANDLE = "3_CANDLE"
    KEY_BAR = "KEY_BAR"


class TriggerState(str, Enum):
    CANDIDATE = "CANDIDATE"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class TriggerFixture:
    form: TriggerForm
    candles: Tuple[int, ...]
    pending_limit_price: float


def trigger_candidates() -> Tuple[TriggerFixture, ...]:
    return (
        TriggerFixture(TriggerForm.ONE_CANDLE, (1,), 103.0),
        TriggerFixture(TriggerForm.TWO_CANDLE, (1, 2), 103.0),
        TriggerFixture(TriggerForm.THREE_CANDLE, (1, 2, 3), 103.0),
        TriggerFixture(TriggerForm.KEY_BAR, (3,), 103.0),
    )


def classify_source_neutral(fixture: TriggerFixture) -> TriggerState:
    """All source-confirmed forms remain candidates until acceptance rules exist."""
    return TriggerState.CANDIDATE


def is_market_reclaim_trigger(fixture: TriggerFixture) -> bool:
    """F12 invariant: trigger fixture does not redefine pending execution as market entry."""
    return False
