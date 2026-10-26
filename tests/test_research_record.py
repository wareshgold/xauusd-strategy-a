from dataclasses import replace

import pytest

from strategy_factory.audit import bind_research_audit
from strategy_factory.dataset_provenance import evaluate_dataset_provenance
from strategy_factory.datasets import DatasetRegistry
from strategy_factory.evidence import EvidenceBundle
from strategy_factory.execution import ExecutionReceipt
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.models import StrategyPassport
from strategy_factory.research_provenance import (
    ResearchProvenanceResult,
    ResearchProvenanceStatus,
    evaluate_research_provenance,
)
from strategy_factory.research_record import ResearchRecord, ResearchRecordError, ResearchRecordLedger
from strategy_factory.runs import ResearchRunIdentity
from strategy_factory.snapshot import build_readiness_snapshot
from strategy_factory.sp2l_manifest import build_sp2l_research_manifest
from strategy_factory.source_ledger import SourceResolutionLedger
from strategy_factory.test_contract import DatasetRole, ExecutionSemantics, HistoricalTestSpec, TestDataset


CONTENT_SHA = "a" * 64


def chain(dataset_role="DEVELOPMENT"):
    manifest = build_sp2l_research_manifest()
    passport = StrategyPassport(
        strategy_id=manifest.strategy_id, source_revision=manifest.revision,
        geometry_revision="GEOMETRY-PENDING", code_revision="CODE-PENDING",
        data_revision="DATA-PENDING", execution_model="BAR_CLOSE_RESEARCH",
        parameter_set={"canonical": False},
    )
    snapshot = build_readiness_snapshot(manifest, passport, SourceResolutionLedger())
    role = DatasetRole(dataset_role)
    spec = HistoricalTestSpec(
        test_id="TEST-001", strategy_id=manifest.strategy_id,
        strategy_revision="RESEARCH-001",
        dataset=TestDataset(
            dataset_id=f"{dataset_role}-001", role=role, data_revision="DATA-001",
            start="2026-01-01T00:00:00Z", end="2026-02-01T00:00:00Z",
            source="synthetic", immutable=role is not DatasetRole.DEVELOPMENT,
        ),
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"sample": "synthetic"},
    )
    registry = DatasetRegistry()
    identity = registry.register(spec.dataset, CONTENT_SHA)
    dataset_provenance = evaluate_dataset_provenance(spec, registry, CONTENT_SHA)
    job = ResearchJobSpec.from_test_spec(
        spec, manifest_revision=manifest.revision,
        dataset_fingerprint=identity.fingerprint, job_id="RUN-001",
    )
    run = ResearchRunIdentity(
        run_id=job.job_id, strategy_id=job.strategy_id,
        strategy_revision=job.strategy_revision, manifest_revision=job.manifest_revision,
        dataset_id=job.dataset_id, dataset_role=dataset_role, data_revision=job.data_revision,
        dataset_fingerprint=job.dataset_fingerprint, artifact_id=None,
        execution_semantics=job.execution_semantics, parameters=dict(job.parameters),
    )
    metrics = ResearchMetrics(1, 1, 1, 0, 0, 1.0, 1.0, None, 0.0, 1.0, 0.0)
    receipt = ExecutionReceipt(
        execution_id="EXEC-001", test_id=spec.test_id,
        strategy_revision=spec.strategy_revision,
        execution_semantics=spec.execution_semantics, engine_revision="ENGINE-001",
        input_fingerprint="b" * 64, completed=True, metrics=metrics,
    )
    evidence = EvidenceBundle(
        evidence_id="EVIDENCE-001", run_id=run.run_id, run_fingerprint=run.fingerprint,
        result_revision="RESULT-001", metrics=metrics,
        result={"execution_id": receipt.execution_id},
    )
    audit = bind_research_audit(run, snapshot, evidence)
    provenance = evaluate_research_provenance(
        spec=spec, job=job, run=run, receipt=receipt, evidence=evidence,
        audit=audit, snapshot=snapshot, dataset_provenance=dataset_provenance,
    )
    return run, evidence, snapshot, audit, provenance


def test_record_is_deterministic_and_validates():
    a = ResearchRecord.from_components(*chain())
    b = ResearchRecord.from_components(*chain())
    assert a == b
    assert len(a.fingerprint) == 64
    a.validate()


def test_record_binds_all_core_fingerprints_and_provenance_decision():
    run, evidence, snapshot, audit, provenance = chain()
    record = ResearchRecord.from_components(run, evidence, snapshot, audit, provenance)
    assert record.run_fingerprint == run.fingerprint
    assert record.evidence_fingerprint == evidence.fingerprint
    assert record.snapshot_fingerprint == snapshot.fingerprint
    assert record.audit_fingerprint == audit.fingerprint
    assert record.provenance_status is ResearchProvenanceStatus.PASS
    assert record.provenance_decision_fingerprint == provenance.decision_fingerprint


def test_record_rejects_tampering():
    record = ResearchRecord.from_components(*chain())
    with pytest.raises(ResearchRecordError, match="fingerprint mismatch"):
        replace(record, audit_fingerprint="c" * 64).validate()


def test_record_rejects_non_pass_provenance():
    run, evidence, snapshot, audit, _ = chain()
    blocked = ResearchProvenanceResult(ResearchProvenanceStatus.BLOCKED, ("DATASET_PROVENANCE_BLOCKED",))
    with pytest.raises(ResearchRecordError, match="PASS provenance"):
        ResearchRecord.from_components(run, evidence, snapshot, audit, blocked)


def test_record_rejects_unbound_manually_constructed_pass():
    run, evidence, snapshot, audit, _ = chain()
    forged = ResearchProvenanceResult(ResearchProvenanceStatus.PASS, ())
    with pytest.raises(ResearchRecordError, match="invalid provenance decision"):
        ResearchRecord.from_components(run, evidence, snapshot, audit, forged)


def test_record_rejects_decision_reused_for_different_run():
    run, evidence, snapshot, audit, provenance = chain()
    other = replace(run, run_id="OTHER-RUN")
    other_evidence = replace(evidence, run_id=other.run_id, run_fingerprint=other.fingerprint)
    other_audit = bind_research_audit(other, snapshot, other_evidence)
    with pytest.raises(ResearchRecordError, match="not bound to supplied research_run"):
        ResearchRecord.from_components(other, other_evidence, snapshot, other_audit, provenance)


def test_ledger_is_append_only_for_run_id():
    record = ResearchRecord.from_components(*chain())
    ledger = ResearchRecordLedger()
    assert ledger.record(record) == record
    assert ledger.record(record) == record
    with pytest.raises(ResearchRecordError, match="different immutable"):
        ledger.record(replace(record, evidence_id="OTHER"))
