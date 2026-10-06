from dataclasses import replace
import pytest

from strategy_factory.multiple_comparison import adjust_p_values
from strategy_factory.statistical_comparison_evidence import (
    StatisticalComparisonEvidenceError,
    bind_statistical_comparison_evidence,
    validate_statistical_comparison_evidence,
)


def test_evidence_binds_comparison_and_adjustment():
    from test_research_comparison import _chain
    record, statistical, stability = _chain()
    bundle = __import__("strategy_factory.research_evidence_bundle", fromlist=["bind_research_evidence_bundle"]).bind_research_evidence_bundle(record, statistical, stability)
    comparison = __import__("strategy_factory.research_comparison", fromlist=["build_research_comparison"]).build_research_comparison(
        (record, statistical, stability, bundle),
        [(replace(record, run_id="candidate"), statistical, stability, bundle)],
    )
    adjustment = adjust_p_values((0.01,), method="HOLM")
    evidence = bind_statistical_comparison_evidence(comparison, adjustment)
    validate_statistical_comparison_evidence(evidence, comparison, adjustment)


def test_family_size_must_match_comparison():
    from test_research_comparison import _chain
    from strategy_factory.research_evidence_bundle import bind_research_evidence_bundle
    from strategy_factory.research_comparison import build_research_comparison
    record, statistical, stability = _chain()
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    comparison = build_research_comparison((record, statistical, stability, bundle), [(replace(record, run_id="candidate"), statistical, stability, bundle)])
    adjustment = adjust_p_values((0.01, 0.02))
    with pytest.raises(StatisticalComparisonEvidenceError, match="family_size"):
        bind_statistical_comparison_evidence(comparison, adjustment)


def test_tampered_evidence_is_rejected():
    from test_research_comparison import _chain
    from strategy_factory.research_evidence_bundle import bind_research_evidence_bundle
    from strategy_factory.research_comparison import build_research_comparison
    record, statistical, stability = _chain()
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    comparison = build_research_comparison((record, statistical, stability, bundle), [(replace(record, run_id="candidate"), statistical, stability, bundle)])
    adjustment = adjust_p_values((0.01,), method="HOLM")
    evidence = bind_statistical_comparison_evidence(comparison, adjustment)
    with pytest.raises(StatisticalComparisonEvidenceError, match="fingerprint"):
        replace(evidence, fingerprint="0" * 64).validate()


def test_adjustment_mismatch_is_rejected():
    from test_research_comparison import _chain
    from strategy_factory.research_evidence_bundle import bind_research_evidence_bundle
    from strategy_factory.research_comparison import build_research_comparison
    record, statistical, stability = _chain()
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    comparison = build_research_comparison((record, statistical, stability, bundle), [(replace(record, run_id="candidate"), statistical, stability, bundle)])
    adjustment = adjust_p_values((0.01,), method="HOLM")
    other = adjust_p_values((0.02,), method="HOLM")
    evidence = bind_statistical_comparison_evidence(comparison, adjustment)
    with pytest.raises(StatisticalComparisonEvidenceError, match="adjustment fingerprint"):
        validate_statistical_comparison_evidence(evidence, comparison, other)
