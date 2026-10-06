import pytest

from strategy_factory.source_resolution import (
    SourceEvidence,
    SourceResolutionError,
    SourceVerdict,
    evaluate_source_resolution,
    resolve_fixture_set,
)
from strategy_factory.sp2l_discrimination import build_sp2l_discrimination_fixtures


def _fixture(question_id: str):
    return next(
        item
        for item in build_sp2l_discrimination_fixtures()
        if item.question_id == question_id
    )


def test_missing_source_evidence_is_blocked():
    result = evaluate_source_resolution(_fixture("SP2L.F10.Q1"))
    assert result.verdict is SourceVerdict.BLOCKED
    assert result.selected_alternative is None


def test_non_discriminating_source_stays_unresolved():
    fixture = _fixture("SP2L.F12.Q1")
    evidence = SourceEvidence(
        evidence_id="SRC-F12-001",
        question_id=fixture.question_id,
        selected_alternative=None,
        source_reference="F12",
        rationale="The source names the previous candle Low but does not define touch versus penetration.",
        directly_supported=False,
    )
    result = evaluate_source_resolution(fixture, evidence)
    assert result.verdict is SourceVerdict.UNRESOLVED


def test_direct_source_evidence_can_confirm_one_alternative():
    fixture = _fixture("SP2L.F12.Q1")
    evidence = SourceEvidence(
        evidence_id="SRC-F12-002",
        question_id=fixture.question_id,
        selected_alternative="TOUCH",
        source_reference="F12",
        rationale="Hypothetical direct source statement used only to test the evaluator.",
        directly_supported=True,
    )
    result = evaluate_source_resolution(fixture, evidence)
    assert result.verdict is SourceVerdict.CONFIRMED
    assert result.selected_alternative == "TOUCH"


def test_unsupported_alternative_is_rejected():
    fixture = _fixture("SP2L.F10.Q1")
    evidence = SourceEvidence(
        evidence_id="SRC-F10-001",
        question_id=fixture.question_id,
        selected_alternative="MADE_UP_RULE",
        source_reference="F10",
        rationale="invalid test evidence",
        directly_supported=True,
    )
    with pytest.raises(SourceResolutionError):
        evaluate_source_resolution(fixture, evidence)


def test_wrong_question_evidence_is_rejected():
    fixture = _fixture("SP2L.F10.Q1")
    evidence = SourceEvidence(
        evidence_id="SRC-F12-003",
        question_id="SP2L.F12.Q1",
        selected_alternative="TOUCH",
        source_reference="F12",
        rationale="wrong fixture",
        directly_supported=True,
    )
    with pytest.raises(SourceResolutionError):
        evaluate_source_resolution(fixture, evidence)


def test_fixture_set_without_evidence_remains_blocked():
    fixtures = build_sp2l_discrimination_fixtures()
    results = resolve_fixture_set(fixtures)
    assert results
    assert all(item.verdict is SourceVerdict.BLOCKED for item in results)


def test_partial_evidence_does_not_resolve_other_questions():
    fixtures = build_sp2l_discrimination_fixtures()
    evidence = (
        SourceEvidence(
            evidence_id="SRC-F13-001",
            question_id="SP2L.F12.Q1",
            selected_alternative="TOUCH",
            source_reference="F12",
            rationale="Hypothetical isolated evidence.",
            directly_supported=True,
        ),
    )
    results = resolve_fixture_set(fixtures, evidence)
    assert sum(item.verdict is SourceVerdict.CONFIRMED for item in results) == 1
    assert sum(item.verdict is SourceVerdict.BLOCKED for item in results) == len(fixtures) - 1


def test_direct_support_requires_selected_alternative():
    fixture = _fixture("SP2L.TP.Q1")
    evidence = SourceEvidence(
        evidence_id="SRC-TP-001",
        question_id=fixture.question_id,
        selected_alternative=None,
        source_reference="C04",
        rationale="direct support without a selected interpretation",
        directly_supported=True,
    )
    with pytest.raises(SourceResolutionError):
        evaluate_source_resolution(fixture, evidence)
