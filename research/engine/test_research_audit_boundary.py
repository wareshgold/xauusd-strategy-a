from .research_audit_boundary import AuditDecision, ResearchAuditInput, decide_audit


def base(**overrides):
    value = dict(
        provenance_complete=True,
        evidence_complete=True,
        fixture_results_recorded=True,
        dev_recorded=True,
        validation_recorded=True,
        holdout_untouched=True,
        source_geometry_resolved=True,
    )
    value.update(overrides)
    return ResearchAuditInput(**value)


def test_complete_audit_passes():
    assert decide_audit(base()) is AuditDecision.PASS


def test_missing_provenance_blocks():
    assert decide_audit(base(provenance_complete=False)) is AuditDecision.BLOCK


def test_missing_evidence_blocks():
    assert decide_audit(base(evidence_complete=False)) is AuditDecision.BLOCK


def test_missing_fixture_record_is_unknown():
    assert decide_audit(base(fixture_results_recorded=False)) is AuditDecision.UNKNOWN


def test_missing_dev_record_is_unknown():
    assert decide_audit(base(dev_recorded=False)) is AuditDecision.UNKNOWN


def test_missing_validation_record_is_unknown():
    assert decide_audit(base(validation_recorded=False)) is AuditDecision.UNKNOWN


def test_touched_holdout_blocks():
    assert decide_audit(base(holdout_untouched=False)) is AuditDecision.BLOCK


def test_unresolved_source_geometry_is_unknown():
    assert decide_audit(base(source_geometry_resolved=False)) is AuditDecision.UNKNOWN
