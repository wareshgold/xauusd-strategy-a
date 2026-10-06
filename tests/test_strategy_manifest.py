from strategy_factory.sp2l_manifest import build_sp2l_research_manifest
from strategy_factory.manifest import EvidenceStatus, RuleAuthority


def test_sp2l_manifest_is_not_canonical_ready():
    manifest = build_sp2l_research_manifest()
    assert manifest.canonical_ready is False
    assert manifest.unresolved


def test_sp2l_manifest_records_source_confirmed_evidence():
    manifest = build_sp2l_research_manifest()
    assert manifest.evidence_for("SP2L.F13")[0].status is EvidenceStatus.SOURCE_CONFIRMED
    assert manifest.evidence_for("SP2L.PGAP")[0].source_reference == "C01"


def test_sp2l_manifest_does_not_promote_rules_to_canonical():
    manifest = build_sp2l_research_manifest()
    assert all(rule.authority is RuleAuthority.NON_CANONICAL for rule in manifest.rules)


def test_blocking_questions_are_explicit():
    manifest = build_sp2l_research_manifest()
    ids = {question.question_id for question in manifest.unresolved}
    assert "SP2L.F12.Q1" in ids
    assert "SP2L.F10.Q1" in ids
    assert all(question.blocking for question in manifest.unresolved)
