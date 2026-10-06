from dataclasses import replace

import pytest

from strategy_factory.audit import bind_research_audit
from strategy_factory.dataset_provenance import (
    DatasetProvenanceStatus,
    evaluate_dataset_provenance,
)
from strategy_factory.datasets import DatasetRegistry
from strategy_factory.evidence import EvidenceBundle
from strategy_factory.execution import ExecutionReceipt
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.models import StrategyPassport
from strategy_factory.research_provenance import (
    ResearchProvenanceStatus,
    evaluate_research_provenance,
)
from strategy_factory.runs import ResearchRunIdentity
from strategy_factory.snapshot import build_readiness_snapshot
from strategy_factory.sp2l_manifest import build_sp2l_research_manifest
from strategy_factory.source_ledger import SourceResolutionLedger
from strategy_factory.test_contract import (
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
)


CONTENT_SHA = "a" * 64


def make_spec(role=DatasetRole.DEVELOPMENT, revision="DATA-001"):
    return HistoricalTestSpec(
        test_id="TEST-001",
        strategy_id="SP2L-A",
        strategy_revision="RESEARCH-001",
        dataset=TestDataset(
            dataset_id="DS-001",
            role=role,
            data_revision=revision,
            start="2026-01-01T00:00:00Z",
            end="2026-02-01T00:00:00Z",
            source="synthetic",
            immutable=role is not DatasetRole.DEVELOPMENT,
        ),
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
    )


def make_chain():
    manifest = build_sp2l_research_manifest()
    passport = StrategyPassport(
        strategy_id=manifest.strategy_id,
        source_revision=manifest.revision,
        geometry_revision="GEOMETRY-PENDING",
        code_revision="CODE-PENDING",
        data_revision="DATA-PENDING",
        execution_model="BAR_CLOSE_RESEARCH",
        parameter_set={"canonical": False},
    )
    snapshot = build_readiness_snapshot(manifest, passport, SourceResolutionLedger())

    spec = make_spec()
    registry = DatasetRegistry()
    identity = registry.register(spec.dataset, CONTENT_SHA)
    dataset_provenance = evaluate_dataset_provenance(spec, registry, CONTENT_SHA)
    assert dataset_provenance.status is DatasetProvenanceStatus.PASS

    job = ResearchJobSpec.from_test_spec(
        spec,
        manifest_revision=manifest.revision,
        dataset_fingerprint=identity.fingerprint,
        job_id="JOB-001",
    )
    run = ResearchRunIdentity(
        run_id=job.job_id,
        strategy_id=job.strategy_id,
        strategy_revision=job.strategy_revision,
        manifest_revision=job.manifest_revision,
        dataset_id=job.dataset_id,
        dataset_role=spec.dataset.role.value,
        data_revision=job.data_revision,
        dataset_fingerprint=job.dataset_fingerprint,
        artifact_id=None,
        execution_semantics=job.execution_semantics,
        parameters=dict(job.parameters),
    )
    metrics = ResearchMetrics(
        trades=2,
        decisive_trades=2,
        wins=1,
        losses=1,
        ambiguous=0,
        win_rate=0.5,
        net_r=0.0,
        profit_factor=1.0,
        max_drawdown_r=1.0,
        gross_profit_r=1.0,
        gross_loss_r=-1.0,
    )
    receipt = ExecutionReceipt(
        execution_id="EXEC-001",
        test_id=spec.test_id,
        strategy_revision=spec.strategy_revision,
        execution_semantics=spec.execution_semantics,
        engine_revision="ENGINE-001",
        input_fingerprint="b" * 64,
        completed=True,
        metrics=metrics,
    )
    evidence = EvidenceBundle(
        evidence_id="EVIDENCE-001",
        run_id=run.run_id,
        run_fingerprint=run.fingerprint,
        result_revision="RESULT-001",
        metrics=metrics,
        result={"execution_id": receipt.execution_id},
    )
    audit = bind_research_audit(run, snapshot, evidence)
    return {
        "spec": spec,
        "job": job,
        "run": run,
        "receipt": receipt,
        "evidence": evidence,
        "audit": audit,
        "snapshot": snapshot,
        "dataset_provenance": dataset_provenance,
    }


def test_exact_chain_passes():
    chain = make_chain()
    result = evaluate_research_provenance(**chain)

    assert result.status is ResearchProvenanceStatus.PASS
    assert result.reasons == ()


@pytest.mark.parametrize(
    "field",
    [
        "strategy_revision",
        "manifest_revision",
        "dataset_id",
        "data_revision",
        "dataset_fingerprint",
    ],
)
def test_run_identity_tampering_fails(field):
    chain = make_chain()
    original = chain["run"]
    replacement = "x" * 64 if field == "dataset_fingerprint" else "TAMPERED"
    chain["run"] = replace(original, **{field: replacement})

    result = evaluate_research_provenance(**chain)

    assert result.status is ResearchProvenanceStatus.FAIL
    assert result.reasons


def test_dataset_provenance_block_is_blocked():
    chain = make_chain()
    chain["dataset_provenance"] = replace(
        chain["dataset_provenance"],
        status=DatasetProvenanceStatus.BLOCKED,
        reasons=("dataset is not registered",),
    )

    result = evaluate_research_provenance(**chain)

    assert result.status is ResearchProvenanceStatus.BLOCKED
    assert "DATASET_PROVENANCE_BLOCKED" in result.reasons


def test_evidence_from_different_run_fails():
    chain = make_chain()
    chain["evidence"] = replace(chain["evidence"], run_id="OTHER-RUN")

    result = evaluate_research_provenance(**chain)

    assert result.status is ResearchProvenanceStatus.FAIL
    assert "EVIDENCE_RUN_ID" in result.reasons


def test_audit_from_different_snapshot_fails():
    chain = make_chain()
    chain["audit"] = replace(chain["audit"], snapshot_fingerprint="c" * 64)

    result = evaluate_research_provenance(**chain)

    assert result.status is ResearchProvenanceStatus.FAIL
    assert "AUDIT_SNAPSHOT_FINGERPRINT" in result.reasons


def test_snapshot_mismatch_fails():
    chain = make_chain()
    manifest = build_sp2l_research_manifest()
    passport = StrategyPassport(
        strategy_id=manifest.strategy_id,
        source_revision=manifest.revision,
        geometry_revision="OTHER",
        code_revision="CODE-PENDING",
        data_revision="DATA-PENDING",
        execution_model="BAR_CLOSE_RESEARCH",
        parameter_set={"canonical": False},
    )
    chain["snapshot"] = build_readiness_snapshot(
        manifest, passport, SourceResolutionLedger()
    )

    result = evaluate_research_provenance(**chain)

    assert result.status is ResearchProvenanceStatus.FAIL
    assert "AUDIT_SNAPSHOT_FINGERPRINT" in result.reasons


def test_receipt_semantics_mismatch_fails():
    chain = make_chain()
    chain["receipt"] = replace(
        chain["receipt"],
        execution_semantics=ExecutionSemantics.TICK_FEASIBLE,
    )

    result = evaluate_research_provenance(**chain)

    assert result.status is ResearchProvenanceStatus.FAIL
    assert any(reason.startswith("EXECUTION_BINDING:") for reason in result.reasons)
