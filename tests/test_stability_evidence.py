from dataclasses import replace
import pytest

from strategy_factory.stability import StabilitySegment, evaluate_stability
from strategy_factory.stability_evidence import (
    StabilityEvidenceError,
    bind_stability_evidence,
    validate_stability_evidence_binding,
)
from strategy_factory.test_contract import DatasetRole
from test_research_record import chain


def profile():
    return evaluate_stability(
        (
            StabilitySegment("S1", "A", 10, 0.2, 0.6),
            StabilitySegment("S2", "B", 12, -0.1, 0.5),
        )
    )


def test_stability_evidence_is_bound_to_exact_research_record():
    run, evidence, snapshot, audit, provenance = chain(DatasetRole.DEVELOPMENT.value)
    record = __import__("strategy_factory.research_record", fromlist=["ResearchRecord"]).ResearchRecord.from_components(
        run, evidence, snapshot, audit, provenance
    )
    bound = bind_stability_evidence(record, profile())
    bound.validate()
    validate_stability_evidence_binding(bound, record)
    assert bound.run_id == record.run_id
    assert bound.research_record_fingerprint == record.fingerprint


def test_tampering_is_detected():
    run, evidence, snapshot, audit, provenance = chain(DatasetRole.DEVELOPMENT.value)
    from strategy_factory.research_record import ResearchRecord
    record = ResearchRecord.from_components(run, evidence, snapshot, audit, provenance)
    bound = bind_stability_evidence(record, profile())
    with pytest.raises(StabilityEvidenceError, match="fingerprint"):
        replace(bound, fingerprint="bad").validate()


def test_wrong_record_is_rejected():
    run, evidence, snapshot, audit, provenance = chain(DatasetRole.DEVELOPMENT.value)
    from strategy_factory.research_record import ResearchRecord
    record = ResearchRecord.from_components(run=run, audit=audit, provenance=provenance)
    bound = bind_stability_evidence(record, profile())
    other = replace(record, run_id="OTHER", fingerprint=record.fingerprint)
    with pytest.raises(StabilityEvidenceError, match="run_id"):
        validate_stability_evidence_binding(bound, other)


def test_profile_change_changes_evidence_fingerprint():
    run, evidence, snapshot, audit, provenance = chain(DatasetRole.DEVELOPMENT.value)
    from strategy_factory.research_record import ResearchRecord
    record = ResearchRecord.from_components(run=run, audit=audit, provenance=provenance)
    first = bind_stability_evidence(record, profile())
    changed = evaluate_stability((StabilitySegment("S1", "A", 10, 0.3, 0.6), StabilitySegment("S2", "B", 12, -0.1, 0.5)))
    second = bind_stability_evidence(record, changed)
    assert first.fingerprint != second.fingerprint
