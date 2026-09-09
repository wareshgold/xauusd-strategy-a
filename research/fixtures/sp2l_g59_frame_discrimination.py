from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Verdict(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONTRADICTED = "CONTRADICTED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class FrameObservation:
    timestamp: str
    claim: str
    candidate_ids: tuple[str, ...]
    verdict: Verdict


OBSERVATIONS = (
    FrameObservation("31:43", "SP2L / Spike-2Leg identity is visible.", ("B1-PGAP-V1", "B1-PGAP-V2"), Verdict.CONSISTENT),
    FrameObservation("32:21", "P-Gap is distinguished from E-Gap/Common-Gap.", ("B1-PGAP-V1", "B1-PGAP-V2"), Verdict.CONSISTENT),
    FrameObservation("36:50", "Valid BO = P-Gap is explicitly shown.", ("B1-PGAP-V1", "B1-PGAP-V2"), Verdict.CONSISTENT),
    FrameObservation("39:30", "Buy Limit is explicitly marked on the chart.", ("B2-ENTRY-STRUCTURAL", "B2-ENTRY-LATEST"), Verdict.CONSISTENT),
    FrameObservation("40:40", "Entry and SL are represented as distinct levels.", ("B3-SL-STRUCTURAL",), Verdict.CONSISTENT),
    FrameObservation("42:26", "TP1 and TP2 are separately shown.", ("B6-LEG2-MAGNITUDE",), Verdict.CONSISTENT),
    FrameObservation("53:16", "One/two/three candle trigger family is discussed.", ("B4-TRIGGER-1C", "B4-TRIGGER-2C", "B4-TRIGGER-3C", "B4-TRIGGER-KEYBAR"), Verdict.CONSISTENT),
    FrameObservation("54:29", "Buy Limit can provide a renewed opportunity.", ("B2-ENTRY-STRUCTURAL", "B2-ENTRY-LATEST"), Verdict.CONSISTENT),
    FrameObservation("55:22", "Bearish example shows SL above and Entry below.", ("B3-SL-STRUCTURAL",), Verdict.CONSISTENT),
)


def contradicted_candidates() -> tuple[str, ...]:
    # G59 intentionally records only source contradictions that are explicit.
    # Absence of contradiction is not evidence of canonical uniqueness.
    return ()


def source_unique() -> bool:
    return False
