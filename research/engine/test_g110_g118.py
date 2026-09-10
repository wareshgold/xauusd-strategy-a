from .demo_recovery_batch_audit import BatchDecision, audit_batch, guard_batch
from .demo_recovery_fingerprint import RecoveryFingerprint


def test_g110_batch_unique_states_pass():
    audit = audit_batch([RecoveryFingerprint("o1", "FILLED", 1), RecoveryFingerprint("o2", "CANCELLED", 2)])
    assert all(d is BatchDecision.PASS for d in audit.decisions)
    assert audit.deterministic


def test_g111_duplicate_state_detected():
    audit = audit_batch([RecoveryFingerprint("o1", "FILLED", 1), RecoveryFingerprint("o1", "FILLED", 1)])
    assert not audit.deterministic


def test_g112_g113_integrity_fail_closed():
    assert guard_batch(journal_valid=False, sequence_valid=True, recovered=True, reconciliation_match=True) is BatchDecision.BLOCK
    assert guard_batch(journal_valid=True, sequence_valid=False, recovered=True, reconciliation_match=True) is BatchDecision.BLOCK


def test_g114_g115_uncertainty_requires_review():
    assert guard_batch(journal_valid=True, sequence_valid=True, recovered=False, reconciliation_match=True) is BatchDecision.REQUIRE_REVIEW
    assert guard_batch(journal_valid=True, sequence_valid=True, recovered=True, reconciliation_match=False) is BatchDecision.REQUIRE_REVIEW


def test_g116_valid_recovery_passes():
    assert guard_batch(journal_valid=True, sequence_valid=True, recovered=True, reconciliation_match=True) is BatchDecision.PASS


def test_g117_repeat_audit_stable():
    state = RecoveryFingerprint("o3", "FILLED", 9)
    assert audit_batch([state]).fingerprints == audit_batch([state]).fingerprints


def test_g118_outcomes_are_not_production_authorization():
    assert set(d.value for d in BatchDecision) == {"PASS", "BLOCK", "REQUIRE_REVIEW"}
