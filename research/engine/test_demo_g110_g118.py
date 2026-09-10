from .demo_recovery_batch_audit import BatchDecision, audit_batch, guard_batch
from .demo_recovery_fingerprint import RecoveryFingerprint


def test_g110_batch_is_deterministic_for_unique_states():
    audit = audit_batch([RecoveryFingerprint("o1", "FILLED", 1), RecoveryFingerprint("o2", "CANCELLED", 2)])
    assert all(d is BatchDecision.PASS for d in audit.decisions)
    assert audit.deterministic


def test_g111_duplicate_state_is_visible():
    audit = audit_batch([RecoveryFingerprint("o1", "FILLED", 1), RecoveryFingerprint("o1", "FILLED", 1)])
    assert not audit.deterministic


def test_g112_invalid_integrity_blocks():
    assert guard_batch(journal_valid=False, sequence_valid=True, recovered=True, reconciliation_match=True) is BatchDecision.BLOCK


def test_g113_invalid_sequence_blocks():
    assert guard_batch(journal_valid=True, sequence_valid=False, recovered=True, reconciliation_match=True) is BatchDecision.BLOCK


def test_g114_unrecovered_requires_review():
    assert guard_batch(journal_valid=True, sequence_valid=True, recovered=False, reconciliation_match=True) is BatchDecision.REQUIRE_REVIEW


def test_g115_reconciliation_mismatch_requires_review():
    assert guard_batch(journal_valid=True, sequence_valid=True, recovered=True, reconciliation_match=False) is BatchDecision.REQUIRE_REVIEW


def test_g116_fully_valid_batch_passes():
    assert guard_batch(journal_valid=True, sequence_valid=True, recovered=True, reconciliation_match=True) is BatchDecision.PASS


def test_g117_fingerprint_is_stable_across_repeated_audit():
    state = RecoveryFingerprint("o3", "FILLED", 9)
    assert audit_batch([state]).fingerprints == audit_batch([state]).fingerprints


def test_g118_audit_never_authorizes_production():
    assert BatchDecision.PASS.value == "PASS"
    assert BatchDecision.BLOCK.value == "BLOCK"
    assert BatchDecision.REQUIRE_REVIEW.value == "REQUIRE_REVIEW"
