from __future__ import annotations

from dataclasses import replace

import pytest

from strategy_factory.research_acceptance import (
    ResearchAcceptanceError,
    evaluate_research_acceptance,
)
from strategy_factory.research_evidence_bundle import bind_research_evidence_bundle
from strategy_factory.research_evidence_ledger import ResearchEvidenceLedger
from strategy_factory.statistical_evidence import bind_statistical_evidence
from strategy_factory.stability_evidence import bind_stability_evidence


def evidence_chain():
    from test_research_job_runner import build_chain

    record, _ = build_chain()
    statistical = bind_statistical_evidence(record, record.run.metrics)
    stability = bind_stability_evidence(record, record.run.metrics)
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    return record, statistical, stability, bundle


def registered_chain():
    record, statistical, stability, bundle = evidence_chain()
    ledger = ResearchEvidenceLedger()
    ledger.record(bundle)
    return record, statistical, stability, bundle, ledger


def test_acceptance_requires_ledger_registration():
    record, statistical, stability, bundle = evidence_chain()
    with pytest.raises(ResearchAcceptanceError, match="not registered"):
        evaluate_research_acceptance(
            record, statistical, stability, bundle, ResearchEvidenceLedger()
        )


def test_acceptance_validates_full_chain():
    record, statistical, stability, bundle, ledger = registered_chain()
    result = evaluate_research_acceptance(
        record, statistical, stability, bundle, ledger
    )
    assert result.accepted is True
    assert result.ledger_registered is True
    result.validate()


def test_tampered_bundle_is_rejected():
    from strategy_factory.research_evidence_bundle import ResearchEvidenceBundleError

    record, statistical, stability, bundle, ledger = registered_chain()
    tampered = replace(bundle, fingerprint="bad")
    with pytest.raises(ResearchAcceptanceError, match="fingerprint"):
        evaluate_research_acceptance(
            record, statistical, stability, tampered, ledger
        )


def test_acceptance_fingerprint_is_deterministic():
    chain = registered_chain()
    first = evaluate_research_acceptance(*chain)
    second = evaluate_research_acceptance(*chain)
    assert first.fingerprint == second.fingerprint
