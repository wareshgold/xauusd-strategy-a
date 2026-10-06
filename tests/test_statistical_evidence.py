from dataclasses import replace
import pytest

from strategy_factory.research_record import ResearchRecord
from strategy_factory.statistical_evidence import (
    StatisticalEvidenceError,
    bind_statistical_evidence,
    validate_statistical_evidence_binding,
)
from strategy_factory.statistics import evaluate_statistical_validation
from strategy_factory.test_contract import DatasetRole
from tests.test_research_record import chain


def statistical():
    run, evidence, snapshot, audit, provenance = chain()
    record = ResearchRecord.from_components(run, evidence, snapshot, audit, provenance)
    result = evaluate_statistical_validation(
        evidence.metrics,
        role=DatasetRole.DEVELOPMENT,
        trade_returns_r=(1.0,),
    )
    return record, result


def test_statistical_evidence_is_deterministic_and_bound():
    record, result = statistical()
    a = bind_statistical_evidence(record, result)
    b = bind_statistical_evidence(record, result)
    assert a == b
    assert len(a.fingerprint) == 64
    validate_statistical_evidence_binding(a, record)


def test_statistical_evidence_rejects_role_mismatch():
    record, result = statistical()
    mismatched = replace(result, role=DatasetRole.FRESH_HOLDOUT)
    with pytest.raises(StatisticalEvidenceError, match="role"):
        bind_statistical_evidence(record, mismatched)


def test_statistical_evidence_rejects_tampering():
    record, result = statistical()
    evidence = bind_statistical_evidence(record, result)
    with pytest.raises(StatisticalEvidenceError, match="fingerprint mismatch"):
        replace(evidence, dataset_id="OTHER").validate()


def test_statistical_evidence_rejects_wrong_record():
    record, result = statistical()
    evidence = bind_statistical_evidence(record, result)
    other = replace(record, run_id="OTHER")
    with pytest.raises(StatisticalEvidenceError, match="run_id"):
        validate_statistical_evidence_binding(evidence, other)
