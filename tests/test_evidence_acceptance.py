import pytest

from strategy_factory.acceptance import evidence_acceptance_gate, validate_evidence_acceptance
from strategy_factory.datasets import DatasetRegistry
from strategy_factory.evidence import EvidenceBundle
from strategy_factory.execution import ExecutionReceipt
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.models import GateStatus
from strategy_factory.runs import ResearchRunLedger, ResearchRunError
from strategy_factory.test_contract import DatasetRole, ExecutionSemantics, HistoricalTestSpec, TestDataset
from strategy_factory.usage import DatasetUsageLedger


METRICS = ResearchMetrics(10, 10, 6, 4, 0, 0.6, 2.5, 1.4, 1.2, 6.0, -3.5)


def setup():
    dataset = TestDataset(
        "D1", DatasetRole.DEVELOPMENT, "R1",
        "2026-01-01", "2026-02-01", "FIXTURE"
    )
    spec = HistoricalTestSpec(
        "T1", "SP2L-A", "S1", dataset,
        ExecutionSemantics.TICK_FEASIBLE,
    )
    registry = DatasetRegistry()
    registry.register(dataset, "a" * 64)
    usage = DatasetUsageLedger(registry)
    runs = ResearchRunLedger(registry, usage)
    run = runs.create(
        spec,
        manifest_revision="M1",
        run_id="RUN1",
        observed_fingerprint="a" * 64,
        purpose="DEVELOPMENT",
    )
    receipt = ExecutionReceipt(
        "EX1", "T1", "S1", ExecutionSemantics.TICK_FEASIBLE,
        "ENGINE1", "a" * 64, True, METRICS
    )
    evidence = EvidenceBundle(
        "E1", run.run_id, run.fingerprint, "RESULT1", METRICS,
        {"trades": 10},
    )
    return spec, run, receipt, evidence


def test_exact_evidence_acceptance_passes():
    spec, run, receipt, evidence = setup()
    validate_evidence_acceptance(
        spec=spec, run=run, receipt=receipt, evidence=evidence
    )
    assert evidence_acceptance_gate(
        spec=spec, run=run, receipt=receipt, evidence=evidence
    ).status is GateStatus.PASS


def test_missing_inputs_are_blocked():
    assert evidence_acceptance_gate(
        spec=None, run=None, receipt=None, evidence=None
    ).status is GateStatus.BLOCKED


def test_wrong_provenance_is_rejected():
    spec, run, receipt, evidence = setup()
    bad = EvidenceBundle(
        "E1", run.run_id, "0" * 64, "RESULT1", METRICS, {"trades": 10}
    )
    result = evidence_acceptance_gate(
        spec=spec, run=run, receipt=receipt, evidence=bad
    )
    assert result.status is GateStatus.FAIL


def test_metric_mismatch_is_rejected():
    spec, run, receipt, evidence = setup()
    other = ResearchMetrics(10, 10, 5, 5, 0, 0.5, 0.0, 1.0, 2.0, 5.0, -5.0)
    bad = EvidenceBundle(
        "E1", run.run_id, run.fingerprint, "RESULT1", other, {"trades": 10}
    )
    result = evidence_acceptance_gate(
        spec=spec, run=run, receipt=receipt, evidence=bad
    )
    assert result.status is GateStatus.FAIL


def test_execution_semantics_mismatch_is_rejected():
    spec, run, receipt, evidence = setup()
    bad_receipt = ExecutionReceipt(
        "EX1", "T1", "S1", ExecutionSemantics.BAR_CLOSE_RESEARCH,
        "ENGINE1", "a" * 64, True, METRICS
    )
    result = evidence_acceptance_gate(
        spec=spec, run=run, receipt=bad_receipt, evidence=evidence
    )
    assert result.status is GateStatus.FAIL


def test_incomplete_receipt_is_blocked_by_execution_validation():
    spec, run, receipt, evidence = setup()
    bad_receipt = ExecutionReceipt(
        "EX1", "T1", "S1", ExecutionSemantics.TICK_FEASIBLE,
        "ENGINE1", "a" * 64, False, METRICS
    )
    result = evidence_acceptance_gate(
        spec=spec, run=run, receipt=bad_receipt, evidence=evidence
    )
    assert result.status is GateStatus.FAIL


def test_acceptance_does_not_compare_performance_values():
    spec, run, receipt, evidence = setup()
    different_metrics = ResearchMetrics(
        10, 10, 1, 9, 0, 0.1, -8.0, 0.2, 9.0, 1.0, -9.0
    )
    different = EvidenceBundle(
        "E2", run.run_id, run.fingerprint, "RESULT2",
        different_metrics, {"trades": 10}
    )
    different_receipt = ExecutionReceipt(
        "EX2", "T1", "S1", ExecutionSemantics.TICK_FEASIBLE,
        "ENGINE2", "a" * 64, True, different_metrics
    )
    result = evidence_acceptance_gate(
        spec=spec, run=run, receipt=different_receipt, evidence=different
    )
    assert result.status is GateStatus.PASS
