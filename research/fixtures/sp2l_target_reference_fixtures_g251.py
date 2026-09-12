"""G251 source-schematic target-reference fixtures.

Research-only. Encodes the observed bullish target schematic as ordered
reference levels without promoting visual spacing to an executable R-multiple
rule. Bearish mirroring, terminal TP selection, point units, round-level
behavior, and execution semantics remain unresolved.
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
    expected_tp_order: Decision
    expected_terminal_is_reference: Decision


def ordered_bullish_targets(case: TargetCase) -> Decision:
    """Research-only schematic ordering check.

    The source visual shows TP1 and TP2 successively above Entry in the
    bullish schematic. This function deliberately does not encode a distance
    formula, R multiple, point unit, or target selector.
    """
    if case.direction != "bullish":
        return Decision.UNKNOWN
    if case.entry is None or case.tp1 is None or case.tp2 is None:
        return Decision.UNKNOWN
    return Decision.PASS if case.entry < case.tp1 < case.tp2 else Decision.FAIL


def terminal_tp_is_reference(case: TargetCase) -> Decision:
    """Do not infer terminal TP selection from schematic reference geometry."""
    if case.terminal_tp is None or case.tp1 is None or case.tp2 is None:
        return Decision.UNKNOWN
    return Decision.PASS if case.terminal_tp in (case.tp1, case.tp2) else Decision.FAIL


def fixtures() -> tuple[TargetCase, ...]:
    return (
        TargetCase("T1", "bullish", 100.0, 90.0, 110.0, 120.0, None,
                   Decision.PASS, Decision.UNKNOWN),
        TargetCase("T2", "bearish", 100.0, 110.0, 90.0, 80.0, None,
                   Decision.UNKNOWN, Decision.UNKNOWN),
        TargetCase("T3", "bullish", 3220.0, 3210.0, 3230.0, 3240.0, 3230.0,
                   Decision.PASS, Decision.PASS),
        TargetCase("T4", "bullish", 3220.0, 3210.0, 3230.0, 3240.0, 3240.0,
                   Decision.PASS, Decision.PASS),
        TargetCase("T5", "bullish", 3220.0, 3210.0, 3230.0, 3240.0, 3235.0,
                   Decision.PASS, Decision.FAIL),
        TargetCase("T6", "bullish", 3220.0, 3210.0, 3230.0, 3240.0, None,
                   Decision.PASS, Decision.UNKNOWN),
    )
