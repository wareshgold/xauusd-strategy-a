from dataclasses import replace
import pytest

from strategy_factory.multiple_comparison import adjust_p_values
from strategy_factory.research_comparison import ComparisonObservation, ResearchComparison
from strategy_factory.statistical_comparison_evidence import (
    StatisticalComparisonEvidenceError,
    bind_statistical_comparison_evidence,
    validate_statistical_comparison_evidence,
)


def _comparison():
    base = ComparisonObservation("base", "r"*64, "b"*64, 10, 0.5, 0.2, None, 0.1, 0.3)
    candidate = ComparisonObservation("candidate", "c"*64, "d"*64, 10, 0.6, 0.3, None, 0.2, 0.4)
    comparison = ResearchComparison(
        "REV", "SP2L", "R1", "DEVELOPMENT", base, (candidate,), 1,
        (0.1,), (0.1,), (None,), "",
    )
    import hashlib, json
    payload = comparison._fingerprint_payload()
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return replace(comparison, fingerprint=fingerprint)


def test_evidence_binds_comparison_and_adjustment():
    comparison = _comparison()
    adjustment = adjust_p_values((0.01,), method="HOLM")
    evidence = bind_statistical_comparison_evidence(comparison, adjustment)
    validate_statistical_comparison_evidence(evidence, comparison, adjustment)


def test_family_size_must_match_comparison():
    comparison = _comparison()
    adjustment = adjust_p_values((0.01, 0.02))
    with pytest.raises(StatisticalComparisonEvidenceError, match="family_size"):
        bind_statistical_comparison_evidence(comparison, adjustment)


def test_tampered_evidence_is_rejected():
    comparison = _comparison()
    adjustment = adjust_p_values((0.01,), method="HOLM")
    evidence = bind_statistical_comparison_evidence(comparison, adjustment)
    with pytest.raises(StatisticalComparisonEvidenceError, match="fingerprint"):
        replace(evidence, fingerprint="0" * 64).validate()


def test_adjustment_mismatch_is_rejected():
    comparison = _comparison()
    adjustment = adjust_p_values((0.01,), method="HOLM")
    other = adjust_p_values((0.02,), method="HOLM")
    evidence = bind_statistical_comparison_evidence(comparison, adjustment)
    with pytest.raises(StatisticalComparisonEvidenceError, match="adjustment fingerprint"):
        validate_statistical_comparison_evidence(evidence, comparison, other)
