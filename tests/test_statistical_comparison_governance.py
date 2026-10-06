import pytest
from dataclasses import replace

from strategy_factory.multiple_comparison import adjust_p_values
from strategy_factory.research_comparison import ComparisonObservation, ResearchComparison
from strategy_factory.statistical_comparison_evidence import bind_statistical_comparison_evidence
from strategy_factory.statistical_comparison_evidence_ledger import StatisticalComparisonEvidenceLedger
from strategy_factory.statistical_comparison_governance import (
    StatisticalComparisonUsageError,
    StatisticalComparisonUsageLedger,
    StatisticalComparisonUsageDisposition,
)
from strategy_factory.test_contract import DatasetRole
import hashlib, json


def comparison_for(role):
    base = ComparisonObservation("base", "r"*64, "b"*64, 10, 0.5, 0.2, None, 0.1, 0.3)
    candidate = ComparisonObservation("candidate", "c"*64, "d"*64, 10, 0.6, 0.3, None, 0.2, 0.4)
    comparison = ResearchComparison("REV", "SP2L", "R1", role.value, base, (candidate,), 1, (0.1,), (0.1,), (None,), "")
    fp = hashlib.sha256(json.dumps(comparison._fingerprint_payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return replace(comparison, fingerprint=fp)


def evidence_for(role):
    comparison = comparison_for(role)
    return bind_statistical_comparison_evidence(comparison, adjust_p_values((0.01,), method="HOLM"))


@pytest.mark.parametrize("role", [DatasetRole.DEVELOPMENT, DatasetRole.UNTOUCHED_VALIDATION, DatasetRole.FRESH_HOLDOUT])
def test_registered_comparison_evidence_can_be_governed(role):
    evidence = evidence_for(role)
    registry = StatisticalComparisonEvidenceLedger()
    registry.record(evidence)
    usage = StatisticalComparisonUsageLedger().record(evidence, ledger=registry, purpose="FINAL_EVIDENCE")
    assert usage.disposition is StatisticalComparisonUsageDisposition.ALLOWED


def test_unregistered_evidence_is_rejected():
    evidence = evidence_for(DatasetRole.DEVELOPMENT)
    with pytest.raises(StatisticalComparisonUsageError, match="not registered"):
        StatisticalComparisonUsageLedger().record(
            evidence, ledger=StatisticalComparisonEvidenceLedger(), purpose="DEVELOPMENT"
        )


@pytest.mark.parametrize("role", [DatasetRole.UNTOUCHED_VALIDATION, DatasetRole.FRESH_HOLDOUT])
@pytest.mark.parametrize("purpose", ["DEVELOPMENT", "OPTIMIZATION", "PARAMETER_FIT"])
def test_validation_and_holdout_comparison_evidence_cannot_enter_fitting(role, purpose):
    evidence = evidence_for(role)
    registry = StatisticalComparisonEvidenceLedger()
    registry.record(evidence)
    usage = StatisticalComparisonUsageLedger()
    with pytest.raises(StatisticalComparisonUsageError):
        usage.record(evidence, ledger=registry, purpose=purpose)
    assert usage.entries() == ()


def test_usage_is_idempotent_and_tamper_evident():
    evidence = evidence_for(DatasetRole.DEVELOPMENT)
    registry = StatisticalComparisonEvidenceLedger()
    registry.record(evidence)
    ledger = StatisticalComparisonUsageLedger()
    a = ledger.record(evidence, ledger=registry, purpose="DEVELOPMENT")
    b = ledger.record(evidence, ledger=registry, purpose="DEVELOPMENT")
    assert a == b
    assert len(ledger.entries()) == 1
    with pytest.raises(StatisticalComparisonUsageError, match="fingerprint"):
        replace(a, purpose="OPTIMIZATION").validate()
