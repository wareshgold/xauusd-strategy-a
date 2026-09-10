from .validation_evidence_gate import EvidenceDecision, ValidationEvidence, decide_evidence


def valid():
    return ValidationEvidence(True, True, True, True, True, True, True)


def test_complete_evidence_passes():
    assert decide_evidence(valid()) is EvidenceDecision.PASS


def test_touched_holdout_blocks():
    v = valid(); v = ValidationEvidence(v.source_provenance_ok, v.dataset_fingerprint_ok, v.fixtures_ok, v.dev_results_recorded, v.validation_results_recorded, False, v.source_geometry_resolved)
    assert decide_evidence(v) is EvidenceDecision.BLOCK


def test_missing_provenance_blocks():
    v = valid(); v = ValidationEvidence(False, v.dataset_fingerprint_ok, v.fixtures_ok, v.dev_results_recorded, v.validation_results_recorded, v.holdout_untouched, v.source_geometry_resolved)
    assert decide_evidence(v) is EvidenceDecision.BLOCK


def test_fixture_failure_blocks():
    v = valid(); v = ValidationEvidence(v.source_provenance_ok, v.dataset_fingerprint_ok, False, v.dev_results_recorded, v.validation_results_recorded, v.holdout_untouched, v.source_geometry_resolved)
    assert decide_evidence(v) is EvidenceDecision.BLOCK


def test_missing_results_are_unknown():
    v = valid(); v = ValidationEvidence(True, True, True, False, True, True, True)
    assert decide_evidence(v) is EvidenceDecision.UNKNOWN


def test_unresolved_geometry_is_unknown():
    v = valid(); v = ValidationEvidence(True, True, True, True, True, True, False)
    assert decide_evidence(v) is EvidenceDecision.UNKNOWN
