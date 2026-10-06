from dataclasses import replace
import pytest

from strategy_factory.research_certification import ResearchCertificationError, certify_research_result
from strategy_factory.unified_research_quality import evaluate_unified_research_quality
from tests.test_unified_research_quality import full_chain


def certified_chain():
    record, statistical, stability, bundle, ledger, acceptance, gate = full_chain()
    quality = evaluate_unified_research_quality(
        record, statistical, stability, bundle, ledger, acceptance, gate
    )
    certification = certify_research_result(
        record, statistical, stability, bundle, ledger, acceptance, gate, quality
    )
    return record, statistical, stability, bundle, ledger, acceptance, gate, quality, certification


def test_research_certification_passes_and_is_deterministic():
    *_, certification = certified_chain()
    certification.validate()
    assert certification.certified is True
    assert certification.production_eligible is False
    assert certification.fingerprint


def test_research_certification_rejects_quality_mismatch():
    record, statistical, stability, bundle, ledger, acceptance, gate, quality, _ = certified_chain()
    bad_quality = replace(
        quality,
        comparison_validated=False,
    )
    with pytest.raises(ResearchCertificationError):
        certify_research_result(
            record, statistical, stability, bundle, ledger, acceptance, gate, bad_quality
        )


def test_research_certification_rejects_gate_mismatch():
    record, statistical, stability, bundle, ledger, acceptance, gate, quality, _ = certified_chain()
    bad_gate = replace(gate, status="BLOCKED", blocking_reasons=("blocked",))
    with pytest.raises(ResearchCertificationError):
        certify_research_result(
            record, statistical, stability, bundle, ledger, acceptance, bad_gate, quality
        )


def test_research_certification_cannot_be_marked_production():
    record, statistical, stability, bundle, ledger, acceptance, gate, quality, certification = certified_chain()
    bad = replace(certification, production_eligible=True)
    with pytest.raises(ResearchCertificationError):
        bad.validate()
