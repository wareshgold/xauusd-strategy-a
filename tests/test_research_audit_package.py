import pytest
from dataclasses import replace

from strategy_factory.research_audit_package import (
    ResearchAuditPackageError,
    build_research_audit_package,
)
from strategy_factory.research_certification_ledger import ResearchCertificationLedger
from test_research_certification import certified_chain


def package_chain():
    record, statistical, stability, bundle, research_ledger, acceptance, gate, quality, certification = certified_chain()
    from tests.test_research_record import chain
    _, _, snapshot, _, _ = chain("DEVELOPMENT")
    cert_ledger = ResearchCertificationLedger()
    cert_entry = cert_ledger.record(
        certification,
        strategy_id=record.strategy_id,
        strategy_revision=record.strategy_revision,
    )
    package = build_research_audit_package(
        snapshot, record, statistical, stability, bundle, research_ledger,
        acceptance, gate, quality, certification, cert_ledger,
    )
    return package, cert_ledger


def test_audit_package_passes_and_is_deterministic():
    package, ledger = package_chain()
    package.validate()
    ledger.assert_clean()
    assert package.certified is True
    assert package.production_eligible is False
    assert package.fingerprint


def test_audit_package_rejects_tampering():
    package, _ = package_chain()
    bad = replace(package, production_status="ELIGIBLE")
    with pytest.raises(ResearchAuditPackageError, match="fingerprint"):
        bad.validate()


def test_audit_package_rejects_unregistered_certification():
    record, statistical, stability, bundle, research_ledger, acceptance, gate, quality, certification = certified_chain()
    from tests.test_research_record import chain
    _, _, snapshot, _, _ = chain("DEVELOPMENT")
    with pytest.raises(ResearchAuditPackageError, match="certification is not registered"):
        build_research_audit_package(
            snapshot, record, statistical, stability, bundle, research_ledger,
            acceptance, gate, quality, certification, ResearchCertificationLedger(),
        )


def test_audit_package_cannot_be_marked_production():
    package, _ = package_chain()
    bad = replace(package, production_eligible=True)
    with pytest.raises(ResearchAuditPackageError):
        bad.validate()
