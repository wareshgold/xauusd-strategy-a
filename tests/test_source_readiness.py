from strategy_factory.readiness import evaluate_source_readiness
from strategy_factory.source_ledger import SourceResolutionLedger
from strategy_factory.sp2l_manifest import build_sp2l_research_manifest
from strategy_factory.source_gate import SourceGateStatus


def test_sp2l_source_readiness_is_blocked_without_resolution_evidence():
    manifest = build_sp2l_research_manifest()
    readiness = evaluate_source_readiness(manifest, SourceResolutionLedger())

    assert readiness.status is SourceGateStatus.BLOCKED
    assert readiness.total_questions == 18
    assert readiness.missing_questions == 18
    assert readiness.unresolved_questions == 0
    assert readiness.confirmed_questions == 0
    assert readiness.frozen_geometry_blocked is True
    assert readiness.canonical_strategy_eligible is False
    assert readiness.production_eligible is False
    assert readiness.gate.blocking_questions == tuple(
        sorted(question.question_id for question in manifest.unresolved)
    )


def test_readiness_does_not_promote_manifest_rules():
    manifest = build_sp2l_research_manifest()
    readiness = evaluate_source_readiness(manifest, SourceResolutionLedger())

    assert all(rule.authority.value == "NON_CANONICAL" for rule in manifest.rules)
    assert manifest.canonical_ready is False
    assert readiness.canonical_strategy_eligible is False
