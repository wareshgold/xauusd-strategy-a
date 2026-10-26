from hashlib import sha256

import pytest

from strategy_factory.ledger_report import build_ledger_report
from strategy_factory.research_ledger import (
    ZERO_HASH,
    EvidenceStatus,
    ExperimentStatus,
    create_record,
)


def digest(value):
    return sha256(value.encode()).hexdigest()


def make_record(record_id, sequence, previous, status=ExperimentStatus.PLANNED,
                evidence_status=EvidenceStatus.SYNTHETIC_ONLY, evidence_refs=("fixture://evidence",),
                counterexamples=()):
    return create_record(
        record_id=record_id,
        sequence=sequence,
        experiment_key="H-TICK-ORDER-001",
        hypothesis_id="H-TICK-ORDER-001",
        hypothesis_version="v1",
        input_sha256=digest("inputs"),
        code_sha256=digest("code"),
        status=status,
        evidence_status=evidence_status,
        result_summary=f"Record {record_id} summary.",
        evidence_refs=evidence_refs,
        counterexample_refs=counterexamples,
        previous_record_sha256=previous,
    )


def ledger():
    first = make_record("planned-1", 1, ZERO_HASH)
    second = make_record(
        "failed-2", 2, first.record_sha256, ExperimentStatus.FAIL,
        EvidenceStatus.CONTRADICTED, counterexamples=("fixture://counterexample-1",),
    )
    third = make_record(
        "review-3", 3, second.record_sha256, ExperimentStatus.INCONCLUSIVE,
        EvidenceStatus.SOURCE_REVIEW_REQUIRED,
    )
    return (first, second, third)


def test_report_verifies_pinned_tip_and_count_and_summarizes_without_authority():
    records = ledger()
    report = build_ledger_report(
        records, expected_tip_sha256=records[-1].record_sha256, expected_record_count=3
    )
    assert report.verified is True
    assert report.record_count == 3
    assert report.tip_sha256 == records[-1].record_sha256
    assert dict(report.status_counts) == {"FAIL": 1, "INCONCLUSIVE": 1, "PLANNED": 1}
    assert report.planned_record_ids == ("planned-1",)
    assert report.failure_record_ids == ("failed-2",)
    assert report.inconclusive_record_ids == ("review-3",)
    assert report.counterexample_refs == ("fixture://counterexample-1",)
    assert report.source_review_required_record_ids == ("review-3",)
    assert report.contradicted_record_ids == ("failed-2",)
    assert report.canonical_authorized is False
    assert report.production_decision_authorized is False


def test_report_detects_truncated_valid_prefix_with_pinned_tip():
    records = ledger()
    with pytest.raises(ValueError, match="pinned tip"):
        build_ledger_report(
            records[:-1], expected_tip_sha256=records[-1].record_sha256, expected_record_count=2
        )


def test_report_detects_truncation_with_pinned_count():
    records = ledger()
    with pytest.raises(ValueError, match="pinned count"):
        build_ledger_report(
            records[:-1], expected_tip_sha256=records[1].record_sha256, expected_record_count=3
        )


def test_report_rejects_missing_external_tip():
    records = ledger()
    with pytest.raises(ValueError, match="externally pinned"):
        build_ledger_report(records, expected_tip_sha256="", expected_record_count=3)


def test_report_rejects_missing_external_count():
    records = ledger()
    with pytest.raises(ValueError, match="externally pinned"):
        build_ledger_report(records, expected_tip_sha256=records[-1].record_sha256, expected_record_count=None)


def test_report_flags_incomplete_or_missing_evidence():
    first = make_record(
        "incomplete-1", 1, ZERO_HASH, evidence_status=EvidenceStatus.EVIDENCE_INCOMPLETE,
        evidence_refs=(),
    )
    report = build_ledger_report(
        (first,), expected_tip_sha256=first.record_sha256, expected_record_count=1
    )
    assert report.missing_evidence_record_ids == ("incomplete-1",)


def test_report_is_read_only_and_deterministic():
    records = ledger()
    args = dict(expected_tip_sha256=records[-1].record_sha256, expected_record_count=len(records))
    assert build_ledger_report(records, **args) == build_ledger_report(records, **args)


def test_report_does_not_suppress_multiple_counterexamples():
    first = make_record(
        "failure-1", 1, ZERO_HASH, ExperimentStatus.FAIL,
        counterexamples=("fixture://c1", "fixture://c2"),
    )
    report = build_ledger_report(
        (first,), expected_tip_sha256=first.record_sha256, expected_record_count=1
    )
    assert report.counterexample_refs == ("fixture://c1", "fixture://c2")
