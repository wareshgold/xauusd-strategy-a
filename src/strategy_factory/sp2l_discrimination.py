from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class FixtureDisposition(str, Enum):
    SOURCE_DISCRIMINATES = "SOURCE_DISCRIMINATES"
    SOURCE_DOES_NOT_DISCRIMINATE = "SOURCE_DOES_NOT_DISCRIMINATE"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class DiscriminationFixture:
    fixture_id: str
    question_id: str
    description: str
    alternatives: tuple[str, ...]
    expected_disposition: FixtureDisposition = FixtureDisposition.BLOCKED
    source_reference: str = ""

    def validate(self) -> None:
        if not self.fixture_id or not self.question_id:
            raise ValueError("fixture identity is required")
        if not self.description:
            raise ValueError("fixture description is required")
        if len(self.alternatives) < 2:
            raise ValueError("at least two competing alternatives are required")
        if any(not item for item in self.alternatives):
            raise ValueError("fixture alternatives must be non-empty")

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "fixture_id": self.fixture_id,
            "question_id": self.question_id,
            "description": self.description,
            "alternatives": list(self.alternatives),
            "expected_disposition": self.expected_disposition.value,
            "source_reference": self.source_reference,
        }


def build_sp2l_discrimination_fixtures() -> tuple[DiscriminationFixture, ...]:
    fixtures = (
        DiscriminationFixture(
            "SP2L.PGAP.D01",
            "SP2L.PGAP.Q1",
            "Construct a minimal candle sequence where competing P-Gap OHLC formulas disagree.",
            ("FORMULA_A", "FORMULA_B"),
            source_reference="C01/G4",
        ),
        DiscriminationFixture(
            "SP2L.F12.D01",
            "SP2L.F12.Q1",
            "Place price exactly on, then through, the previous candle retrace level.",
            ("TOUCH", "PENETRATION"),
            source_reference="F12",
        ),
        DiscriminationFixture(
            "SP2L.F12.D02",
            "SP2L.F12.Q2",
            "Create an intrabar retrace that does not close beyond the trigger.",
            ("INTRABAR", "CLOSE"),
            source_reference="F12",
        ),
        DiscriminationFixture(
            "SP2L.F12.D03",
            "SP2L.F12.Q3",
            "Separate the source trigger level from the eventual executable entry price.",
            ("TRIGGER_PRICE", "OTHER_EXECUTABLE_PRICE"),
            source_reference="F12",
        ),
        DiscriminationFixture(
            "SP2L.F10.D01",
            "SP2L.F10.Q1",
            "Create a spike-start candle whose wick extreme and body extreme differ.",
            ("WICK_EXTREME", "BODY_EXTREME"),
            source_reference="F10/G4",
        ),
        DiscriminationFixture(
            "SP2L.C06.D01",
            "SP2L.C06.Q1",
            "Create candidate candles that distinguish one-candle, two-candle, and context-dependent expiry.",
            ("ONE_CANDLE", "TWO_CANDLES", "CONTEXT_DEPENDENT"),
            source_reference="C06",
        ),
        DiscriminationFixture(
            "SP2L.F14.D01",
            "SP2L.F14.Q1",
            "Create a four-point sequence where alternative AB=CD anchor choices produce different targets.",
            ("ANCHORS_A", "ANCHORS_B"),
            source_reference="F14/G4",
        ),
        DiscriminationFixture(
            "SP2L.F14.D02",
            "SP2L.F14.Q2",
            "Create an AB=CD comparison whose equality depends on tolerance.",
            ("EXACT_EQUALITY", "TOLERANCE_ALLOWED"),
            source_reference="F14/G4",
        ),
        DiscriminationFixture(
            "SP2L.TP.D01",
            "SP2L.TP.Q1",
            "Create a trade template where competing TP1 formulas produce different prices.",
            ("FORMULA_A", "FORMULA_B"),
            source_reference="C04",
        ),
        DiscriminationFixture(
            "SP2L.TP.D02",
            "SP2L.TP.Q2",
            "Create a trade template where competing TP2 rules produce different prices.",
            ("FORMULA_A", "FORMULA_B"),
            source_reference="C04",
        ),
    )
    for fixture in fixtures:
        fixture.validate()
    return fixtures
