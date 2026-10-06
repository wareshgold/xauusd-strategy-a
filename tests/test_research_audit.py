from strategy_factory.audit import AuditBindingError, bind_research_audit
from strategy_factory.evidence import EvidenceBundle
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.models import StrategyPassport
from strategy_factory.runs import ResearchRunIdentity
from strategy_factory.snapshot import build_readiness_snapshot
from strategy_factory.sp2l_manifest import build_sp2l_research_manifest
from strategy_factory.source_ledger import SourceResolutionLedger
from strategy_factory.test_contract import ExecutionSemantics


def make_run(manifest):
    return ResearchRunIdentity(
        run_id="RUN-001",
        strategy_id=manifest.strategy_id,
        strategy_revision="RESEARCH-001",
        manifest_revision=manifest.revision,
        dataset_id="DEV-001",
        dataset_role="DEVELOPMENT",
        data_revision="DATA-001",
        dataset_fingerprint="a" * 64,
        artifact_id=None,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"sample": "synthetic"},
    )


def make_evidence(run):
    return EvidenceBundle(
        evidence_id="EVIDENCE-001",
        run_id=run.run_id,
        run_fingerprint=run.fingerprint,
        result_revision="RESULT-001",
        metrics=ResearchMetrics(
            trades=1,
            decisive_trades=1,
            wins=1,
            losses=0,
            ambiguous=0,
            win_rate=1.0,
            net_r=1.0,
            profit_factor=None,
            max_drawdown_r=0.0,
            gross_profit_r=1.0,
            gross_loss_r=0.0,
        ),
        result={"source": "synthetic"},
    )


def test_audit_record_binds_run_snapshot_and_evidence():
    manifest = build_sp2l_research_manifest()
    passport = StrategyPassport(
        strategy_id=manifest.strategy_id,
        source_revision=manifest.revision,
        geometry_revision="GEOMETRY-PENDING",
        code_revision="CODE-PENDING",
        data_revision="DATA-PENDING",
        execution_model="TICK_FEASIBLE_RESEARCH_ONLY",
        parameter_set={"canonical": False},
    )
    snapshot = build_readiness_snapshot(manifest, passport, SourceResolutionLedger())
    run = make_run(manifest)
    evidence = make_evidence(run)

    audit = bind_research_audit(run, snapshot, evidence)

    assert audit.run_fingerprint == run.fingerprint
    assert audit.snapshot_fingerprint == snapshot.fingerprint
    assert audit.evidence_fingerprint == evidence.fingerprint
    assert len(audit.fingerprint) == 64
    audit.validate()


def test_audit_rejects_mismatched_manifest_revision():
    manifest = build_sp2l_research_manifest()
    passport = StrategyPassport(
        strategy_id=manifest.strategy_id,
        source_revision=manifest.revision,
        geometry_revision="GEOMETRY-PENDING",
        code_revision="CODE-PENDING",
        data_revision="DATA-PENDING",
        execution_model="TICK_FEASIBLE_RESEARCH_ONLY",
        parameter_set={"canonical": False},
    )
    snapshot = build_readiness_snapshot(manifest, passport, SourceResolutionLedger())
    run = make_run(manifest)
    run = ResearchRunIdentity(**(run.as_dict() | {"manifest_revision": "OTHER"}))
    evidence = make_evidence(run)

    import pytest
    with pytest.raises(AuditBindingError, match="manifest_revision"):
        bind_research_audit(run, snapshot, evidence)
