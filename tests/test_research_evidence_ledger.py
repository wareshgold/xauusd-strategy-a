import pytest

from strategy_factory.research_evidence_bundle import bind_research_evidence_bundle
from strategy_factory.research_evidence_ledger import (
    ResearchEvidenceLedger,
    ResearchEvidenceLedgerError,
)
from test_research_evidence_bundle import evidence_chain


def test_ledger_records_and_is_idempotent():
    record, statistical, stability = evidence_chain()
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    ledger = ResearchEvidenceLedger()
    first = ledger.record(bundle)
    second = ledger.record(bundle)
    assert first == second
    assert len(ledger.entries()) == 1
    ledger.assert_clean()


def test_conflicting_bundle_for_same_run_is_rejected():
    record, statistical, stability = evidence_chain()
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    ledger = ResearchEvidenceLedger()
    ledger.record(bundle)

    changed = bind_research_evidence_bundle(
        record,
        statistical,
        stability,
        bundle_revision="OTHER",
    )
    assert changed.fingerprint != bundle.fingerprint
    with pytest.raises(ResearchEvidenceLedgerError, match="conflicting"):
        ledger.record(changed)


def test_tampered_bundle_is_rejected():
    from dataclasses import replace

    record, statistical, stability = evidence_chain()
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    ledger = ResearchEvidenceLedger()
    with pytest.raises(ResearchEvidenceLedgerError, match="fingerprint"):
        ledger.record(replace(bundle, fingerprint="bad"))


def test_ledger_entries_are_immutable():
    record, statistical, stability = evidence_chain()
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    entry = ResearchEvidenceLedger().record(bundle)
    with pytest.raises(Exception):
        entry.run_id = "OTHER"
