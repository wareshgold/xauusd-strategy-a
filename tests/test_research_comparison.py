from dataclasses import replace

import pytest

from strategy_factory.research_comparison import (
    ResearchComparisonError,
    build_research_comparison,
)
from strategy_factory.research_evidence_bundle import bind_research_evidence_bundle
from strategy_factory.research_evidence_bundle import validate_research_evidence_bundle
from strategy_factory.statistical_evidence import bind_statistical_evidence
from strategy_factory.stability_evidence import bind_stability_evidence


def _chain():
    from test_research_evidence_bundle import evidence_chain
    return evidence_chain()


def test_comparison_is_deterministic_and_descriptive():
    record, statistical, stability = _chain()
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    baseline = (record, statistical, stability, bundle)

    candidate = (record, statistical, stability,
                 bind_research_evidence_bundle(record, statistical, stability,
                                               bundle_revision="ALT"))

    # Same run is intentionally rejected even though the evidence is valid.
    with pytest.raises(ResearchComparisonError, match="run_id"):
        build_research_comparison(baseline, [candidate])


def test_comparison_requires_same_strategy_revision():
    record, statistical, stability = _chain()
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    altered = replace(record, strategy_revision="OTHER")
    with pytest.raises(Exception):
        build_research_comparison(
            (record, statistical, stability, bundle),
            [(altered, statistical, stability, bundle)],
        )


def test_comparison_rejects_empty_candidates():
    record, statistical, stability = _chain()
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    with pytest.raises(ResearchComparisonError, match="candidate"):
        build_research_comparison((record, statistical, stability, bundle), [])


def test_comparison_requires_provenance_valid_bundle():
    record, statistical, stability = _chain()
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    tampered = replace(bundle, fingerprint="0" * 64)
    with pytest.raises(Exception, match="fingerprint"):
        build_research_comparison(
            (record, statistical, stability, bundle),
            [(record, statistical, stability, tampered)],
        )
