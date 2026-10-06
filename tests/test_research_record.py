from dataclasses import replace
import pytest
from strategy_factory.audit import bind_research_audit
from strategy_factory.evidence import EvidenceBundle
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.models import StrategyPassport
from strategy_factory.research_provenance import ResearchProvenanceResult, ResearchProvenanceStatus
from strategy_factory.research_record import ResearchRecord, ResearchRecordError, ResearchRecordLedger
from strategy_factory.runs import ResearchRunIdentity
from strategy_factory.snapshot import build_readiness_snapshot
from strategy_factory.sp2l_manifest import build_sp2l_research_manifest
from strategy_factory.source_ledger import SourceResolutionLedger
from strategy_factory.test_contract import ExecutionSemantics

def chain(dataset_role="DEVELOPMENT"):
    manifest = build_sp2l_research_manifest()
    passport = StrategyPassport(
        strategy_id=manifest.strategy_id, source_revision=manifest.revision,
        geometry_revision="GEOMETRY-PENDING", code_revision="CODE-PENDING",
        data_revision="DATA-PENDING", execution_model="BAR_CLOSE_RESEARCH",
        parameter_set={"canonical": False},
    )
    snapshot = build_readiness_snapshot(manifest, passport, SourceResolutionLedger())
    run = ResearchRunIdentity(
        run_id="RUN-001", strategy_id=manifest.strategy_id,
        strategy_revision="RESEARCH-001", manifest_revision=manifest.revision,
        dataset_id=f"{dataset_role}-001", dataset_role=dataset_role, data_revision="DATA-001",
        dataset_fingerprint="a" * 64, artifact_id=None,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"sample": "synthetic"},
    )
    evidence = EvidenceBundle(
        evidence_id="EVIDENCE-001", run_id=run.run_id, run_fingerprint=run.fingerprint,
        result_revision="RESULT-001",
        metrics=ResearchMetrics(1, 1, 1, 0, 0, 1.0, 1.0, None, 0.0, 1.0, 0.0),
        result={"source": "synthetic"},
    )
    audit = bind_research_audit(run, snapshot, evidence)
    provenance = ResearchProvenanceResult(ResearchProvenanceStatus.PASS, ())
    return run, evidence, snapshot, audit, provenance

def test_record_is_deterministic_and_validates():
    a = ResearchRecord.from_components(*chain())
    b = ResearchRecord.from_components(*chain())
    assert a == b
    assert len(a.fingerprint) == 64
    a.validate()

def test_record_binds_all_core_fingerprints():
    run, evidence, snapshot, audit, provenance = chain()
    record = ResearchRecord.from_components(run, evidence, snapshot, audit, provenance)
    assert record.run_fingerprint == run.fingerprint
    assert record.evidence_fingerprint == evidence.fingerprint
    assert record.snapshot_fingerprint == snapshot.fingerprint
    assert record.audit_fingerprint == audit.fingerprint
    assert record.provenance_status is ResearchProvenanceStatus.PASS

def test_record_rejects_tampering():
    record = ResearchRecord.from_components(*chain())
    with pytest.raises(ResearchRecordError, match="fingerprint mismatch"):
        replace(record, audit_fingerprint="c" * 64).validate()

def test_record_rejects_non_pass_provenance():
    run, evidence, snapshot, audit, _ = chain()
    blocked = ResearchProvenanceResult(ResearchProvenanceStatus.BLOCKED, ("DATASET_PROVENANCE_BLOCKED",))
    with pytest.raises(ResearchRecordError, match="PASS provenance"):
        ResearchRecord.from_components(run, evidence, snapshot, audit, blocked)

def test_ledger_is_append_only_for_run_id():
    record = ResearchRecord.from_components(*chain())
    ledger = ResearchRecordLedger()
    assert ledger.record(record) == record
    assert ledger.record(record) == record
    with pytest.raises(ResearchRecordError, match="different immutable"):
        ledger.record(replace(record, evidence_id="OTHER"))
