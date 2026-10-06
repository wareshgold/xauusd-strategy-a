from dataclasses import dataclass

from strategy_factory.source_gate import SourceGateStatus, evaluate_source_gate
from strategy_factory.source_ledger import SourceResolutionLedger
from strategy_factory.source_resolution import evaluate_source_resolution
from strategy_factory.sp2l_discrimination import build_sp2l_discrimination_fixtures


@dataclass(frozen=True)
class Question:
    question_id: str
    blocking: bool = True


def _fixture(question_id: str):
    return next(
        item
        for item in build_sp2l_discrimination_fixtures()
        if item.question_id == question_id
    )


def test_missing_blocking_question_is_blocked():
    ledger = SourceResolutionLedger()
    result = evaluate_source_gate(
        (Question("SP2L.F10.Q1"),),
        ledger,
    )
    assert result.status is SourceGateStatus.BLOCKED
    assert result.missing_questions == ("SP2L.F10.Q1",)


def test_open_blocking_question_is_blocked():
    ledger = SourceResolutionLedger()
    fixture = _fixture("SP2L.F10.Q1")
    ledger.record(
        evaluate_source_resolution(fixture),
        source_reference="F10/G4",
        rationale="Exact anchor unresolved.",
    )
    result = evaluate_source_gate(
        (Question("SP2L.F10.Q1"),),
        ledger,
    )
    assert result.status is SourceGateStatus.BLOCKED
    assert result.blocking_questions == ("SP2L.F10.Q1",)


def test_nonblocking_unresolved_question_does_not_block_gate():
    ledger = SourceResolutionLedger()
    fixture = _fixture("SP2L.F10.Q1")
    ledger.record(
        evaluate_source_resolution(fixture),
        source_reference="F10/G4",
        rationale="Research-only unresolved question.",
    )
    result = evaluate_source_gate(
        (Question("SP2L.F10.Q1", blocking=False),),
        ledger,
    )
    assert result.status is SourceGateStatus.PASS
    assert result.unresolved_questions == ("SP2L.F10.Q1",)


def test_confirmed_blocking_question_passes():
    ledger = SourceResolutionLedger()
    fixture = _fixture("SP2L.F12.Q1")
    from strategy_factory.source_resolution import SourceEvidence

    result = evaluate_source_resolution(
        fixture,
        SourceEvidence(
            evidence_id="SRC-HYPOTHETICAL",
            question_id=fixture.question_id,
            selected_alternative="TOUCH",
            source_reference="F12",
            rationale="Hypothetical direct source statement for gate testing.",
            directly_supported=True,
        ),
    )
    ledger.record(
        result,
        source_reference="F12",
        rationale="Hypothetical direct source statement.",
    )

    gate = evaluate_source_gate(
        (Question("SP2L.F12.Q1"),),
        ledger,
    )
    assert gate.status is SourceGateStatus.PASS
