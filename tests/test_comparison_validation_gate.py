from dataclasses import replace
import hashlib, json
import pytest

from strategy_factory.comparison_validation_gate import (
    ComparisonValidationGateStatus,
    evaluate_comparison_validation_gate,
)
from strategy_factory.multiple_comparison import adjust_p_values
from strategy_factory.research_comparison import ComparisonObservation, ResearchComparison
from strategy_factory.statistical_comparison_evidence import bind_statistical_comparison_evidence
from strategy_factory.statistical_comparison_evidence_ledger import StatisticalComparisonEvidenceLedger
from strategy_factory.statistical_comparison_governance import StatisticalComparisonUsageLedger


def comparison():
    base = ComparisonObservation("base", "r"*64, "b"*64, 10, .5, .2, None, .1, .3)
    cand = ComparisonObservation("candidate", "c"*64, "d"*64, 10, .6, .3, None, .2, .4)
    x = ResearchComparison("REV", "SP2L", "R1", "DEVELOPMENT", base, (cand,), 1, (.1,), (.1,), (None,), "")
    fp = hashlib.sha256(json.dumps(x._fingerprint_payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return replace(x, fingerprint=fp)


def chain():
    c = comparison()
    a = adjust_p_values((.01,), method="HOLM")
    e = bind_statistical_comparison_evidence(c, a)
    registry = StatisticalComparisonEvidenceLedger()
    registry.record(e)
    return c, a, e, registry


def test_unified_gate_passes_registered_governed_evidence():
    c, a, e, registry = chain()
    result = evaluate_comparison_validation_gate(c, a, e, registry, StatisticalComparisonUsageLedger())
    assert result.status is ComparisonValidationGateStatus.PASS
    assert result.registered is True
    assert result.governed is True
    assert result.blocking_reasons == ()
    result.validate()


def test_unregistered_evidence_is_blocked():
    c = comparison()
    a = adjust_p_values((.01,), method="HOLM")
    e = bind_statistical_comparison_evidence(c, a)
    result = evaluate_comparison_validation_gate(c, a, e, StatisticalComparisonEvidenceLedger(), StatisticalComparisonUsageLedger())
    assert result.status is ComparisonValidationGateStatus.BLOCKED
    assert "STATISTICAL_COMPARISON_EVIDENCE_NOT_REGISTERED" in result.blocking_reasons


def test_tampered_evidence_fails_closed():
    c, a, e, registry = chain()
    bad = replace(e, fingerprint="0"*64)
    result = evaluate_comparison_validation_gate(c, a, bad, registry, StatisticalComparisonUsageLedger())
    assert result.status is ComparisonValidationGateStatus.FAIL
    assert result.governed is False


def test_validation_role_cannot_be_used_for_optimization():
    c, a, e, registry = chain()
    c2 = replace(c, dataset_role="UNTOUCHED_VALIDATION")
    fp = hashlib.sha256(json.dumps(c2._fingerprint_payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    c2 = replace(c2, fingerprint=fp)
    e2 = bind_statistical_comparison_evidence(c2, a)
    registry = StatisticalComparisonEvidenceLedger()
    registry.record(e2)
    result = evaluate_comparison_validation_gate(
        c2, a, e2, registry, StatisticalComparisonUsageLedger(), purpose="OPTIMIZATION"
    )
    assert result.status is ComparisonValidationGateStatus.BLOCKED
