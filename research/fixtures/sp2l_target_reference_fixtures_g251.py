"""G251 source-confirmed target-reference fixtures.

Research-only. Encodes the G250 schematic target geometry without deciding
terminal TP selection, round-level behavior, or execution semantics.
"""
from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class TargetCase:
    case_id: str
    direction: str
    entry: float | None
    stop: float | None
    tp1: float | None
    tp2: float | None
    terminal_tp: float | None
    expected_tp1: Decision
    expected_tp2: Decision
    expected_terminal_is_reference: Decision


def risk(entry: float | None, stop: float | None) -> float | None:
    if entry is None or stop is None:
        return None
    return abs(entry - stop)


def tp1_reference(case: TargetCase) -> Decision:
    """G250 reference: one risk distance from Entry in trade direction."""
    r = risk(case.entry, case.stop)
    if r is None or case.tp1 is None or case.entry is None:
        return Decision.UNKNOWN
    expected = case.entry + r if case.direction == "bullish" else case.entry - r
    return Decision.PASS if case.tp1 == expected else Decision.FAIL


def tp2_reference(case: TargetCase) -> Decision:
    """G250 reference: two risk distances from Entry in trade direction."""
    r = risk(case.entry, case.stop)
    if r is None or case.tp2 is None or case.entry is None:
        return Decision.UNKNOWN
    expected = case.entry + 2 * r if case.direction == "bullish" else case.entry - 2 * r
    return Decision.PASS if case.tp2 == expected else Decision.FAIL


def terminal_tp_is_reference(case: TargetCase) -> Decision:
    """Do not infer terminal TP selection from reference geometry."""
    if case.terminal_tp is None or case.tp1 is None or case.tp2 is None:
        return Decision.UNKNOWN
    return Decision.PASS if case.terminal_tp in (case.tp1, case.tp2) else Decision.FAIL


def fixtures() -> tuple[TargetCase, ...]:
    return (
        TargetCase("T1", "bullish", 100.0, 90.0, 110.0, 120.0, None,
                   Decision.PASS, Decision.PASS, Decision.UNKNOWN),
        TargetCase("T2", "bearish", 100.0, 110.0, 90.0, 80.0, None,
                   Decision.PASS, Decision.PASS, Decision.UNKNOWN),
        TargetCase("T3", "bullish", 3220.0, 3210.0, 3230.0, 3240.0, 3230.0,
                   Decision.PASS, Decision.PASS, Decision.PASS),
        TargetCase("T4", "bullish", 3220.0, 3210.0, 3230.0, 3240.0, 3240.0,
                   Decision.PASS, Decision.PASS, Decision.PASS),
        TargetCase("T5", "bullish", 3220.0, 3210.0, 3230.0, 3240.0, 3235.0,
                   Decision.PASS, Decision.PASS, Decision.FAIL),
        TargetCase("T6", "bullish", 3220.0, 3210.0, 3230.0, 3240.0, None,
                   Decision.PASS, Decision.PASS, Decision.UNKNOWN),
    )
