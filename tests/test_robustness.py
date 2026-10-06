from dataclasses import replace

import pytest

from strategy_factory.audit import bind_research_audit
from strategy_factory.evidence import EvidenceBundle
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.models import StrategyPassport
from strategy_factory.research_evidence_bundle import bind_research_evidence_bundle
from strategy_factory.research_provenance import ResearchProvenanceResult, ResearchProvenanceStatus
from strategy_factory.research_record import ResearchRecord
from strategy_factory.research_evidence_bundle import validate_research_evidence_bundle
from strategy_factory.research_record import ResearchRecord
from strategy_factory.robustness import RobustnessMatrixError, build_robustness_matrix
from strategy_factory.snapshot import build_readiness_snapshot
from strategy_factory.sp2l_manifest import build_sp2l_research_manifest
from strategy_factory.source_ledger import SourceResolutionLedger
from strategy_factory.stability import StabilitySegment, evaluate_stability
from strategy_factory.stability_evidence import bind_stability_evidence
from strategy_factory.statistics import evaluate_statistical_validation
from strategy_factory.statistical_evidence import bind_statistical_evidence
from strategy_factory.test_contract import DatasetRole, ExecutionSemantics
from strategy_factory.runs import ResearchRunIdentity


def _chain(run_id: str = "RUN-001", role: str = "DEVELOPMENT",
           execution: ExecutionSemantics = ExecutionSemantics.BAR_CLOSE_RESEARCH,
           strategy_revision: str = "RESEARCH-001"):
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
    run = ResearchRunIdentity(
        run_id=run_id,
        strategy_id=manifest.strategy_id,
        strategy_revision=strategy_revision,
        manifest_revision=manifest.revision,
        dataset_id=f"{role}-001",
        dataset_role=role,
        data_revision="DATA-001",
        dataset_fingerprint="a" * 64,
        artifact_id=None,
        execution_semantics=execution,
        parameters={"sample": run_id},
    )
    evidence = EvidenceBundle(
        evidence_id=f"EVIDENCE-{run_id}",
        run_id=run.run_id,
        run_fingerprint=run.fingerprint,
        result_revision="RESULT-001",
        metrics=ResearchMetrics(4, 4, 3, 1, 0, 0.75, 2.0, 3.0, 1.0, 3.0, -1.0),
        result={"source": "synthetic"},
    )
    audit = bind_research_audit(run, snapshot, evidence)
    provenance = ResearchProvenanceResult(ResearchProvenanceStatus.PASS, ())
    record = ResearchRecord.from_components(run, evidence, snapshot, audit, provenance)
    statistical = bind_statistical_evidence(
        record,
        evaluate_statistical_validation(
            evidence.metrics,
            role=DatasetRole.DEVELOPMENT,
            trade_returns_r=(1.0, 1.0, 1.0, -1.0),
        ),
    )
    stability = bind_stability_evidence(
        record,
        evaluate_stability((
            StabilitySegment("S1", "A", 2, 0.5, 1.0),
            StabilitySegment("S2", "B", 2, -0.5, 0.5),
        )),
    )
    bundle = bind_research_evidence_bundle(record, statistical, stability)
    return record, statistical, stability, bundle


def _member(run_id: str, **kwargs):
    record, statistical, stability, bundle = _chain(run_id, **kwargs)
    return (record, statistical, stability, bundle, run_id, {"variant": run_id})


def test_robustness_matrix_is_deterministic_and_preserves_provenance():
    members = [_member("RUN-001"), _member("RUN-002")]
    first = build_robustness_matrix(members)
    second = build_robustness_matrix(members)
    assert first == second
    assert first.member_count == 2
    assert first.members[0].run_fingerprint == members[0][0].run_fingerprint
    assert first.members[0].research_record_fingerprint == members[0][0].fingerprint
    assert first.members[0].bundle_fingerprint == members[0][3].fingerprint
    first.validate()


def test_matrix_requires_two_members():
    with pytest.raises(RobustnessMatrixError, match="at least two"):
        build_robustness_matrix([_member("RUN-001")])


def test_matrix_rejects_duplicate_run_ids():
    record, statistical, stability, bundle = _chain("RUN-001")
    member = (record, statistical, stability, bundle, "A", {"variant": "A"})
    duplicate = (record, statistical, stability, bundle, "B", {"variant": "B"})
    with pytest.raises(RobustnessMatrixError, match="run_id"):
        build_robustness_matrix([member, duplicate])


def test_matrix_rejects_strategy_revision_mismatch():
    with pytest.raises(RobustnessMatrixError, match="strategy identity"):
        build_robustness_matrix([
            _member("RUN-001"),
            _member("RUN-002", strategy_revision="OTHER"),
        ])


def test_matrix_rejects_dataset_role_mismatch():
    with pytest.raises(RobustnessMatrixError, match="dataset roles"):
        build_robustness_matrix([
            _member("RUN-001", role="DEVELOPMENT"),
            _member("RUN-002", role="UNTOUCHED_VALIDATION"),
        ])


def test_matrix_rejects_execution_semantics_mismatch():
    with pytest.raises(RobustnessMatrixError, match="execution semantics"):
        build_robustness_matrix([
            _member("RUN-001", execution=ExecutionSemantics.BAR_CLOSE_RESEARCH),
            _member("RUN-002", execution=ExecutionSemantics.TICK_FEASIBLE),
        ])


def test_matrix_rejects_tampered_bundle():
    record, statistical, stability, bundle = _chain("RUN-001")
    tampered = replace(bundle, fingerprint="0" * 64)
    with pytest.raises(Exception, match="fingerprint"):
        build_robustness_matrix([
            (record, statistical, stability, bundle, "A", {"variant": "A"}),
            (record, statistical, stability, tampered, "B", {"variant": "B"}),
        ])


def test_matrix_fingerprint_tampering_is_detected():
    matrix = build_robustness_matrix([_member("RUN-001"), _member("RUN-002")])
    with pytest.raises(RobustnessMatrixError, match="fingerprint"):
        replace(matrix, fingerprint="0" * 64).validate()
