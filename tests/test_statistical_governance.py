from dataclasses import replace
import pytest

from strategy_factory.statistical_governance import (
    StatisticalUsageError,
    StatisticalUsageLedger,
    StatisticalUsageDisposition,
)
from strategy_factory.statistical_evidence import bind_statistical_evidence
from strategy_factory.statistics import evaluate_statistical_validation
from strategy_factory.test_contract import DatasetRole
from tests.test_research_record import chain
from strategy_factory.research_record import ResearchRecord


def evidence_for(role):
    run, evidence, snapshot, audit, provenance = chain()
    record = ResearchRecord.from_components(run, evidence, snapshot, audit, provenance)
    result = evaluate_statistical_validation(evidence.metrics, role=role, trade_returns_r=(1.0,))
    return bind_statistical_evidence(record, result)


def test_development_statistics_are_allowed_for_research():
    evidence = evidence_for(DatasetRole.DEVELOPMENT)
    ledger = StatisticalUsageLedger()
    entry = ledger.record(evidence, purpose="DEVELOPMENT")
    assert entry.disposition is StatisticalUsageDisposition.ALLOWED
    assert entry.dataset_role is DatasetRole.DEVELOPMENT
    ledger.assert_clean()


@pytest.mark.parametrize("role", [DatasetRole.UNTOUCHED_VALIDATION, DatasetRole.FRESH_HOLDOUT])
@pytest.mark.parametrize("purpose", ["DEVELOPMENT", "OPTIMIZATION", "PARAMETER_FIT"])
def test_validation_and_holdout_statistics_cannot_be_used_for_fitting(role, purpose):
    evidence = evidence_for(role)
    ledger = StatisticalUsageLedger()
    with pytest.raises(StatisticalUsageError):
        ledger.record(evidence, purpose=purpose)
    assert ledger.entries() == ()


def test_holdout_statistics_are_allowed_for_final_evidence():
    evidence = evidence_for(DatasetRole.FRESH_HOLDOUT)
    ledger = StatisticalUsageLedger()
    entry = ledger.record(evidence, purpose="FRESH_HOLDOUT_EVIDENCE")
    assert entry.disposition is StatisticalUsageDisposition.ALLOWED


def test_usage_fingerprint_is_deterministic_and_tamper_evident():
    evidence = evidence_for(DatasetRole.DEVELOPMENT)
    a = StatisticalUsageLedger().record(evidence, purpose="DEVELOPMENT")
    b = StatisticalUsageLedger().record(evidence, purpose="DEVELOPMENT")
    assert a == b
    with pytest.raises(StatisticalUsageError, match="fingerprint mismatch"):
        replace(a, purpose="OPTIMIZATION").validate()
