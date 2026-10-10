import hashlib

import pytest

from strategy_factory.adapter import build_execution_receipt
from strategy_factory.datasets import DatasetRegistry, fingerprint_dataset
from strategy_factory.evidence import EvidenceLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.runs import ResearchRunLedger
from strategy_factory.runner import ResearchJobRunner, ResearchJobRunnerError
from strategy_factory.snapshot import ReadinessSnapshot
from strategy_factory.test_contract import (
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
)
from strategy_factory.usage import DatasetUsageLedger


METRICS = ResearchMetrics(
    10, 10, 6, 4, 0, 0.6, 2.5, 1.4, 1.2, 6.0, -3.5
)


def make_spec_and_job():
    dataset = TestDataset(
        "D1",
        DatasetRole.DEVELOPMENT,
        "R1",
        "2026-01-01",
        "2026-02-01",
        "FIXTURE",
    )
    spec = HistoricalTestSpec(
        "T1",
        "SP2L-A",
        "S1",
        dataset,
        ExecutionSemantics.TICK_FEASIBLE,
        parameters={"tp_r": 2},
    )
    job = ResearchJobSpec.from_test_spec(
        spec,
        manifest_revision="M1",
        dataset_fingerprint=fingerprint_dataset(dataset, "a" * 64),
        job_id="JOB-1",
    )
    return spec, job


def make_runner():
    registry = DatasetRegistry()
    spec, _ = make_spec_and_job()
    registry.register(spec.dataset, content_fingerprint="a" * 64)
    usage = DatasetUsageLedger(registry)
    runs = ResearchRunLedger(registry, usage)
    evidence = EvidenceLedger(runs)
    return ResearchJobRunner(runs=runs, evidence=evidence)


def make_snapshot(spec):
    payload = ReadinessSnapshot._fingerprint_payload(
        snapshot_revision="READINESS-SNAPSHOT-TEST",
        strategy_id=spec.strategy_id,
        manifest_revision="M1",
        manifest_fingerprint="c" * 64,
        passport_fingerprint="d" * 64,
        source_ledger={},
        source_readiness={},
        passport_eligibility={},
    )
    fingerprint = hashlib.sha256(payload).hexdigest()
    return ReadinessSnapshot(
        snapshot_revision="READINESS-SNAPSHOT-TEST",
        strategy_id=spec.strategy_id,
        manifest_revision="M1",
        manifest_fingerprint="c" * 64,
        passport_fingerprint="d" * 64,
        source_ledger={},
        source_readiness={},
        passport_eligibility={},
        fingerprint=fingerprint,
    )


def run_job(runner, job, spec, adapter):
    return runner.run(
        job=job,
        spec=spec,
        adapter=adapter,
        snapshot=make_snapshot(spec),
        observed_content_sha256="a" * 64,
    )


class FakeAdapter:
    engine_revision = "ENGINE-1"

    def __init__(self, *, metrics=METRICS, execution_id="EX-1"):
        self.metrics = metrics
        self.execution_id = execution_id
        self.calls = 0

    def execute(self, spec):
        self.calls += 1
        return build_execution_receipt(
            execution_id=self.execution_id,
            spec=spec,
            engine_revision=self.engine_revision,
            input_fingerprint="b" * 64,
            metrics=self.metrics,
        )


def test_runner_completes_end_to_end():
    spec, job = make_spec_and_job()
    runner = make_runner()
    adapter = FakeAdapter()

    result = run_job(runner, job, spec, adapter)

    assert result.accepted
    assert result.run.run_id == "JOB-1"
    assert result.receipt.execution_id == "EX-1"
    assert result.evidence.run_id == result.run.run_id
    assert result.dataset_provenance.status.value == "PASS"
    assert result.audit.run_fingerprint == result.run.fingerprint
    assert result.provenance.status.value == "PASS"
    assert result.record.run_fingerprint == result.run.fingerprint
    assert result.record.fingerprint == result.record.fingerprint
    assert [gate.name for gate in result.gates] == [
        "EXECUTION_CONTRACT",
        "EVIDENCE_ACCEPTANCE",
        "RESEARCH_PROVENANCE",
    ]
    assert adapter.calls == 1


def test_runner_does_not_execute_completed_job_twice():
    spec, job = make_spec_and_job()
    runner = make_runner()
    adapter = FakeAdapter()
    run_job(runner, job, spec, adapter)

    with pytest.raises(ResearchJobRunnerError):
        run_job(runner, job, spec, adapter)

    assert adapter.calls == 1


def test_runner_rejects_job_test_mismatch():
    spec, job = make_spec_and_job()
    changed = HistoricalTestSpec(
        spec.test_id,
        spec.strategy_id,
        "S2",
        spec.dataset,
        spec.execution_semantics,
        spec.parameters,
        spec.objective,
    )
    runner = make_runner()

    with pytest.raises(ResearchJobRunnerError):
        run_job(runner, job, changed, FakeAdapter())


def test_runner_rejects_dataset_fingerprint_mismatch():
    spec, job = make_spec_and_job()
    bad_job = ResearchJobSpec(
        **{
            **job.as_dict(),
            "dataset_fingerprint": "b" * 64,
            "execution_semantics": ExecutionSemantics(job.execution_semantics),
        }
    )
    runner = make_runner()

    with pytest.raises(ResearchJobRunnerError):
        run_job(runner, bad_job, spec, FakeAdapter())


def test_runner_rejects_adapter_identity_mismatch():
    spec, job = make_spec_and_job()
    runner = make_runner()

    class BadAdapter(FakeAdapter):
        def execute(self, source_spec):
            receipt = super().execute(source_spec)
            return receipt.__class__(
                receipt.execution_id,
                "OTHER",
                receipt.strategy_revision,
                receipt.execution_semantics,
                receipt.engine_revision,
                receipt.input_fingerprint,
                receipt.completed,
                receipt.metrics,
            )

    with pytest.raises(ResearchJobRunnerError):
        run_job(runner, job, spec, BadAdapter())


def test_runner_rejects_incomplete_adapter_execution():
    spec, job = make_spec_and_job()
    runner = make_runner()

    class IncompleteAdapter(FakeAdapter):
        def execute(self, source_spec):
            return build_execution_receipt(
                execution_id="EX-1",
                spec=source_spec,
                engine_revision=self.engine_revision,
                input_fingerprint="b" * 64,
                metrics=self.metrics,
                completed=False,
            )

    with pytest.raises(ResearchJobRunnerError):
        run_job(runner, job, spec, IncompleteAdapter())


def test_runner_evidence_is_derived_from_receipt():
    spec, job = make_spec_and_job()
    runner = make_runner()
    result = run_job(runner, job, spec, FakeAdapter())

    assert result.evidence.metrics == result.receipt.metrics
    assert result.evidence.result["execution_id"] == result.receipt.execution_id
    assert result.evidence.result["engine_revision"] == result.receipt.engine_revision


def test_runner_preserves_declared_execution_semantics():
    spec, job = make_spec_and_job()
    runner = make_runner()
    result = run_job(runner, job, spec, FakeAdapter())

    assert result.run.execution_semantics is ExecutionSemantics.TICK_FEASIBLE
    assert result.receipt.execution_semantics is ExecutionSemantics.TICK_FEASIBLE
    assert result.evidence.result["execution_semantics"] == "TICK_FEASIBLE"


def test_runner_creates_reproducible_run_identity():
    spec, job = make_spec_and_job()
    first = run_job(make_runner(), job, spec, FakeAdapter())
    second = run_job(make_runner(), job, spec, FakeAdapter())

    assert first.run.fingerprint == second.run.fingerprint
    assert first.evidence.fingerprint == second.evidence.fingerprint
    assert first.audit.fingerprint == second.audit.fingerprint
    assert first.provenance == second.provenance
    assert first.record == second.record


def test_runner_never_requires_strategy_geometry():
    spec, job = make_spec_and_job()
    runner = make_runner()
    result = run_job(runner, job, spec, FakeAdapter())

    assert result.accepted
    assert result.run.strategy_id == "SP2L-A"
    assert result.run.parameters == {"tp_r": 2}
