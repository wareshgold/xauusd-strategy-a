import pytest

from strategy_factory.source_ledger import (
    ResolutionStatus,
    SourceLedgerError,
    SourceResolutionLedger,
)
from strategy_factory.source_resolution import (
    SourceEvidence,
    SourceVerdict,
    evaluate_source_resolution,
)
from strategy_factory.sp2l_discrimination import build_sp2l_discrimination_fixtures


def _fixture(question_id: str):
    return next(
        item
        for item in build_sp2l_discrimination_fixtures()
        if item.question_id == question_id
    )


def test_open_result_is_recorded_without_selecting_a_rule():
    fixture = _fixture("SP2L.F10.Q1")
    result = evaluate_source_resolution(fixture)
    ledger = SourceResolutionLedger()

    record = ledger.record(
        result,
        source_reference="F10/G4",
        rationale="Exact stop anchor remains unresolved in the source archive.",
    )

    assert record.status is ResolutionStatus.OPEN
    assert record.selected_alternative is None
    assert not ledger.all_confirmed


def test_non_discriminating_evidence_is_recorded_as_unresolved():
    fixture = _fixture("SP2L.F12.Q1")
    result = evaluate_source_resolution(
        fixture,
        SourceEvidence(
            evidence_id="SRC-F12-001",
            question_id=fixture.question_id,
            selected_alternative=None,
            source_reference="F12",
            rationale="The source names the level but does not define touch versus penetration.",
            directly_supported=False,
        ),
    )
    ledger = SourceResolutionLedger()
    record = ledger.record(
        result,
        source_reference="F12",
        rationale="Source wording is insufficient to choose an interaction semantics.",
    )

    assert record.status is ResolutionStatus.UNRESOLVED
    assert record.evidence_id == "SRC-F12-001"


def test_direct_source_evidence_can_be_recorded_as_confirmed():
    fixture = _fixture("SP2L.F12.Q1")
    result = evaluate_source_resolution(
        fixture,
        SourceEvidence(
            evidence_id="SRC-F12-HYPOTHETICAL",
            question_id=fixture.question_id,
            selected_alternative="TOUCH",
            source_reference="F12",
            rationale="Hypothetical direct statement used only to test the ledger.",
            directly_supported=True,
        ),
    )
    ledger = SourceResolutionLedger()
    record = ledger.record(
        result,
        source_reference="F12",
        rationale="Hypothetical direct source statement explicitly selects TOUCH.",
    )

    assert record.status is ResolutionStatus.CONFIRMED
    assert record.selected_alternative == "TOUCH"
    assert ledger.all_confirmed


def test_different_second_record_for_same_question_is_rejected():
    fixture = _fixture("SP2L.F12.Q1")
    result = evaluate_source_resolution(fixture)
    ledger = SourceResolutionLedger()

    ledger.record(
        result,
        source_reference="F12",
        rationale="Still unresolved.",
    )

    with pytest.raises(SourceLedgerError):
        ledger.record(
            result,
            source_reference="F12",
            rationale="Different audit statement.",
        )


def test_confirmed_record_requires_evidence_and_selection():
    ledger = SourceResolutionLedger()
    result = type(
        "Result",
        (),
        {
            "fixture_id": "X",
            "question_id": "Q",
            "verdict": SourceVerdict.CONFIRMED,
            "selected_alternative": None,
            "evidence_id": None,
        },
    )()

    with pytest.raises(SourceLedgerError):
        ledger.record(
            result,
            source_reference="SRC",
            rationale="invalid confirmed result",
        )


def test_records_are_deterministically_sorted():
    ledger = SourceResolutionLedger()

    for question_id in ("SP2L.F10.Q1", "SP2L.F12.Q1"):
        fixture = _fixture(question_id)
        ledger.record(
            evaluate_source_resolution(fixture),
            source_reference="SOURCE",
            rationale="unresolved",
        )

    assert [item.question_id for item in ledger.records] == [
        "SP2L.F10.Q1",
        "SP2L.F12.Q1",
    ]
