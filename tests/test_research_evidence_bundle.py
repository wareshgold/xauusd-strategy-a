from dataclasses import replace

import pytest

from strategy_factory.research_evidence_bundle import (
    ResearchEvidenceBundleError,
    bind_research_evidence_bundle,
    validate_research_evidence_bundle,
)
from strategy_factory.stability import StabilitySegment, evaluate_stability
from strategy_factory.stability_evidence import bind_stability_evidence
from strategy_factory.statistics import evaluate_statistical_validation
from strategy_factory.statistical_evidence import bind_statistical_evidence
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.test_contract import DatasetRole
from test_research_record import chain


def evidence_chain():
    run, evidence, snapshot, audit, provenance = chain(DatasetRole.DEVELOPMENT.value)
    from strategy_factory.research_record import ResearchRecord

    record = ResearchRecord.from_components(run, evidence, snapshot, audit, provenance)
    metrics = ResearchMetrics(
        trades=4,
        decisive_trades=4,
        wins=3,
        losses=1,
        ambiguous=0,
        win_rate=0.75,
        net_r=2.0,
        profit_factor=3.0,
        max_drawdown_r=1.0,
        gross_profit_r=3.0,
        gross_loss_r=-1.0,
    )
    statistical = bind_statistical_evidence(
        record,
        evaluate_statistical_validation(metrics, role=DatasetRole.DEVELOPMENT, trade_returns_r=(1.0, 1.0, 1.0, -1.0)),
    )
    stability = bind_stability_evidence(
        record,
        evaluate_stability(
            (
                StabilitySegment("S1", "A", 2, 0.5, 1.0),
                StabilitySegment("S2", "B", 2, -0.5, 0.5),
            )
        ),
    )
    return record, statistical, stability


def test_bundle_binds_exact_statistical_and_stability_evidence():
    record, statistical, stability = evidence_chain()
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    bundle.validate()
    validate_research_evidence_bundle(bundle, record, statistical, stability)
    assert bundle.run_id == record.run_id
    assert bundle.statistical_evidence_fingerprint == statistical.fingerprint
    assert bundle.stability_evidence_fingerprint == stability.fingerprint


def test_bundle_tampering_is_detected():
    record, statistical, stability = evidence_chain()
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    with pytest.raises(ResearchEvidenceBundleError, match="fingerprint"):
        replace(bundle, fingerprint="bad").validate()


def test_wrong_statistical_evidence_is_rejected():
    record, statistical, stability = evidence_chain()
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    other = replace(statistical, evidence_revision="OTHER")
    with pytest.raises(Exception, match="fingerprint"):
        validate_research_evidence_bundle(bundle, record, other, stability)


def test_wrong_record_is_rejected():
    record, statistical, stability = evidence_chain()
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    other = replace(record, run_id="OTHER", fingerprint=record.fingerprint)
    with pytest.raises(Exception, match="run_id"):
        validate_research_evidence_bundle(bundle, other, statistical, stability)


def test_bundle_fingerprint_changes_when_bound_evidence_changes():
    record, statistical, stability = evidence_chain()
    first = bind_research_evidence_bundle(record, statistical, stability)
    changed_statistical = replace(statistical, evidence_revision="OTHER")
    with pytest.raises(Exception):
        bind_research_evidence_bundle(record, changed_statistical, stability)
    changed_stability = bind_stability_evidence(
        record,
        evaluate_stability(
            (
                StabilitySegment("S1", "A", 2, 0.7, 1.0),
                StabilitySegment("S2", "B", 2, -0.5, 0.5),
            )
        ),
    )
    second = bind_research_evidence_bundle(record, statistical, changed_stability)
    assert first.fingerprint != second.fingerprint
