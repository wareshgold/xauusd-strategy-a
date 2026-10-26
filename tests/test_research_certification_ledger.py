import pytest
from dataclasses import replace

from strategy_factory.research_certification import certify_research_result
from strategy_factory.research_certification_ledger import (
    ResearchCertificationLedger,
    ResearchCertificationLedgerError,
)
from test_research_certification import certified_chain


def test_certification_ledger_records_and_is_idempotent():
    *_, certification = certified_chain()
    ledger = ResearchCertificationLedger()
    first = ledger.record(certification, strategy_id="SP2L", strategy_revision="R1")
    second = ledger.record(certification, strategy_id="SP2L", strategy_revision="R1")
    assert first == second
    assert len(ledger.entries()) == 1
    assert first.verification_scope == "SELF_CONSISTENT_FINGERPRINT_ONLY_NOT_AUTHENTICATED"
    assert first.as_dict()["verification_scope"] == "SELF_CONSISTENT_FINGERPRINT_ONLY_NOT_AUTHENTICATED"
    ledger.assert_clean()


def test_conflicting_certification_for_same_run_is_rejected():
    *chain, certification = certified_chain()
    ledger = ResearchCertificationLedger()
    ledger.record(certification, strategy_id="SP2L", strategy_revision="R1")
    changed = certify_research_result(*chain, certification_revision="OTHER")
    assert changed.fingerprint != certification.fingerprint
    with pytest.raises(ResearchCertificationLedgerError, match="conflicting"):
        ledger.record(changed, strategy_id="SP2L", strategy_revision="R1")


def test_tampered_certification_is_rejected():
    *_, certification = certified_chain()
    ledger = ResearchCertificationLedger()
    with pytest.raises(ResearchCertificationLedgerError, match="fingerprint"):
        ledger.record(replace(certification, fingerprint="bad"), strategy_id="SP2L", strategy_revision="R1")


def test_ledger_entries_are_immutable():
    *_, certification = certified_chain()
    entry = ResearchCertificationLedger().record(certification, strategy_id="SP2L", strategy_revision="R1")
    with pytest.raises(Exception):
        entry.run_id = "OTHER"


def test_ledger_rejects_authenticated_scope_claim():
    *_, certification = certified_chain()
    ledger = ResearchCertificationLedger()
    entry = ledger.record(certification, strategy_id="SP2L", strategy_revision="R1")
    forged = replace(entry, verification_scope="AUTHENTICATED")
    with pytest.raises(ResearchCertificationLedgerError, match="cannot claim authenticated"):
        forged.validate()
