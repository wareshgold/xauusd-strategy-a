from .demo_recovery_audit_boundary import AuditDecision, RecoveryAuditBoundary, decide_audit
from .demo_recovery_batch_audit import BatchDecision, audit_batch, guard_batch
from .demo_recovery_batch_v2 import BatchProductionBoundary, ProductionDecision, production_decision
from .demo_recovery_fingerprint import RecoveryFingerprint


def test_g110_to_g118_valid_batch_is_audit_only():
    audit = audit_batch([RecoveryFingerprint("o1", "FILLED", 1), RecoveryFingerprint("o2", "CANCELLED", 2)])
    assert all(d is BatchDecision.PASS for d in audit.decisions)
    assert audit.deterministic


def test_g110_to_g118_production_is_always_blocked():
    assert production_decision(BatchProductionBoundary(BatchDecision.PASS)) is ProductionDecision.BLOCK


def test_g110_to_g118_invalid_integrity_blocks():
    assert guard_batch(journal_valid=False, sequence_valid=True, recovered=True, reconciliation_match=True) is BatchDecision.BLOCK


def test_g110_to_g118_unknown_recovery_requires_review():
    assert guard_batch(journal_valid=True, sequence_valid=True, recovered=False, reconciliation_match=True) is BatchDecision.REQUIRE_REVIEW


def test_g110_to_g118_empty_audit_is_not_pass():
    assert decide_audit(RecoveryAuditBoundary(True, True, True, True, 0)) is not AuditDecision.PASS
