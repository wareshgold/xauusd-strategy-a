import hashlib

import pytest

from strategy_factory.datasets import DatasetRegistry, fingerprint_dataset
from strategy_factory.evidence import EvidenceLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.runs import ResearchRunLedger
from strategy_factory.runner import ResearchJobRunner, ResearchJobRunnerError
from strategy_factory.snapshot import ReadinessSnapshot
from strategy_factory.synthetic import (
    SyntheticExecutionAdapter,
    SyntheticExecutionError,
    SyntheticExecutionFixture,
)
from strategy_factory.test_contract import (
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
)
from strategy_factory.usage import DatasetUsageLedger


BAR_METRICS = ResearchMetrics(4, 4, 3, 1, 0, 0.75, 2.0, 3.0, 0.75, 3.0, -1.0)
TICK_METRICS = ResearchMetrics(5, 4, 2, 2, 1, 0.5, 1.25, 2.0, 1.0, 3.0, -1.75)


def make_spec_and_job(semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH):
    dataset = TestDataset(
        "SYNTH-DATA-1", DatasetRole.DEVELOPMENT, "SYNTH-R1",
        "2026-01-01", "2026-02-01", "SYNTHETIC",
    )
    spec = HistoricalTestSpec(
        "SYNTH-TEST-1", "SYNTH-STRATEGY", "SYNTH-STRATEGY-R1",
        dataset, semantics, parameters={"scenario": "controlled"},
    )
    job = ResearchJobSpec.from_test_spec(
        spec, manifest_revision="SYNTH-M1",
        dataset_fingerprint=fingerprint_dataset(dataset, "a" * 64),
        job_id=f"JOB-{semantics.value}",
    )
    return spec, job


def make_snapshot(spec):
    payload = ReadinessSnapshot._fingerprint_payload(
        snapshot_revision="READINESS-SNAPSHOT-SYNTHETIC",
        strategy_id=spec.strategy_id,
        manifest_revision="SYNTH-M1",
        manifest_fingerprint="m" * 64,
        passport_fingerprint="p" * 64,
        source_ledger={},
        source_readiness={},
        passport_eligibility={},
    )
    fingerprint = hashlib.sha256(payload).hexdigest()
    return ReadinessSnapshot(
        snapshot_revision="READINESS-SNAPSHOT-SYNTHETIC",
        strategy_id=spec.strategy_id,
        manifest_revision="SYNTH-M1",
        manifest_fingerprint="m" * 64,
        passport_fingerprint="p" * 64,
        source_ledger={},
        source_readiness={},
        passport_eligibility={},
        fingerprint=fingerprint,
    )


def make_runner(spec):
    registry = DatasetRegistry()
    registry.register(spec.dataset, content_fingerprint="a" * 64)
    usage = DatasetUsageLedger(registry)
    runs = ResearchRunLedger(registry, usage)
    evidence = EvidenceLedger(runs)
    return ResearchJobRunner(runs=runs, evidence=evidence)


@pytest.mark.parametrize(
    ("semantics", "metrics"),
    [
        (ExecutionSemantics.BAR_CLOSE_RESEARCH, BAR_METRICS),
        (ExecutionSemantics.TICK_FEASIBLE, TICK_METRICS),
    ],
)
def test_synthetic_adapter_produces_controlled_receipt(semantics, metrics):
    spec, _ = make_spec_and_job(semantics)
    adapter = SyntheticExecutionAdapter(
        SyntheticExecutionFixture("FIXTURE-1", semantics, metrics)
    )
    receipt = adapter.execute(spec)
    assert receipt.execution_semantics is semantics
    assert receipt.metrics == metrics
    assert receipt.completed is True


def test_synthetic_adapter_is_deterministic():
    spec, _ = make_spec_and_job()
    fixture = SyntheticExecutionFixture("FIXTURE-1", ExecutionSemantics.BAR_CLOSE_RESEARCH, BAR_METRICS)
    first = SyntheticExecutionAdapter(fixture).execute(spec)
    second = SyntheticExecutionAdapter(fixture).execute(spec)
    assert first.execution_id == second.execution_id
    assert first.input_fingerprint == second.input_fingerprint
    assert first.as_dict() == second.as_dict()


def test_synthetic_adapter_changes_identity_when_input_changes():
    spec, _ = make_spec_and_job()
    changed = HistoricalTestSpec(
        spec.test_id, spec.strategy_id, spec.strategy_revision, spec.dataset,
        spec.execution_semantics, parameters={"scenario": "changed"},
        objective=spec.objective,
    )
    adapter = SyntheticExecutionAdapter(
        SyntheticExecutionFixture("FIXTURE-1", ExecutionSemantics.BAR_CLOSE_RESEARCH, BAR_METRICS)
    )
    first = adapter.execute(spec)
    second = adapter.execute(changed)
    assert first.input_fingerprint != second.input_fingerprint
    assert first.execution_id != second.execution_id


def test_synthetic_adapter_keeps_bar_and_tick_semantics_distinct():
    bar_spec, _ = make_spec_and_job(ExecutionSemantics.BAR_CLOSE_RESEARCH)
    tick_spec, _ = make_spec_and_job(ExecutionSemantics.TICK_FEASIBLE)
    bar = SyntheticExecutionAdapter(
        SyntheticExecutionFixture("FIXTURE-BAR", ExecutionSemantics.BAR_CLOSE_RESEARCH, BAR_METRICS)
    )
    tick = SyntheticExecutionAdapter(
        SyntheticExecutionFixture("FIXTURE-TICK", ExecutionSemantics.TICK_FEASIBLE, TICK_METRICS)
    )
    bar_receipt = bar.execute(bar_spec)
    tick_receipt = tick.execute(tick_spec)
    assert bar_receipt.execution_semantics is ExecutionSemantics.BAR_CLOSE_RESEARCH
    assert tick_receipt.execution_semantics is ExecutionSemantics.TICK_FEASIBLE
    assert bar_receipt.input_fingerprint != tick_receipt.input_fingerprint


def test_synthetic_adapter_rejects_semantics_mismatch():
    spec, _ = make_spec_and_job(ExecutionSemantics.TICK_FEASIBLE)
    adapter = SyntheticExecutionAdapter(
        SyntheticExecutionFixture("FIXTURE-BAR", ExecutionSemantics.BAR_CLOSE_RESEARCH, BAR_METRICS)
    )
    with pytest.raises(SyntheticExecutionError):
        adapter.execute(spec)


def test_synthetic_fixture_rejects_invalid_metrics():
    bad_metrics = ResearchMetrics(2, 2, 2, 0, 0, 0.25, 1.0, 2.0, 0.0, 2.0, -1.0)
    with pytest.raises(ValueError):
        SyntheticExecutionFixture("BAD", ExecutionSemantics.BAR_CLOSE_RESEARCH, bad_metrics).validate()


def test_synthetic_runner_completes_end_to_end_for_bar_close():
    spec, job = make_spec_and_job(ExecutionSemantics.BAR_CLOSE_RESEARCH)
    result = make_runner(spec).run(
        job=job, spec=spec,
        snapshot=make_snapshot(spec),
        observed_content_sha256="a" * 64,
        adapter=SyntheticExecutionAdapter(
            SyntheticExecutionFixture("FIXTURE-BAR", ExecutionSemantics.BAR_CLOSE_RESEARCH, BAR_METRICS)
        ),
    )
    assert result.accepted
    assert result.receipt.metrics == BAR_METRICS
    assert result.evidence.metrics == BAR_METRICS
    assert result.receipt.execution_semantics is ExecutionSemantics.BAR_CLOSE_RESEARCH


def test_synthetic_runner_completes_end_to_end_for_tick_feasible():
    spec, job = make_spec_and_job(ExecutionSemantics.TICK_FEASIBLE)
    result = make_runner(spec).run(
        job=job, spec=spec,
        adapter=SyntheticExecutionAdapter(
            SyntheticExecutionFixture("FIXTURE-TICK", ExecutionSemantics.TICK_FEASIBLE, TICK_METRICS)
        ),
        snapshot=make_snapshot(spec),
        observed_content_sha256="a" * 64,
    )
    assert result.accepted
    assert result.receipt.execution_semantics is ExecutionSemantics.TICK_FEASIBLE
    assert result.evidence.result["execution_semantics"] == "TICK_FEASIBLE"


def test_synthetic_runner_failure_is_isolated_at_adapter_boundary():
    spec, job = make_spec_and_job()
    adapter = SyntheticExecutionAdapter(
        SyntheticExecutionFixture("FIXTURE-TICK", ExecutionSemantics.TICK_FEASIBLE, TICK_METRICS)
    )
    with pytest.raises(ResearchJobRunnerError):
        make_runner(spec).run(
            job=job,
            spec=spec,
            adapter=adapter,
            snapshot=make_snapshot(spec),
            observed_content_sha256="a" * 64,
        )


def test_synthetic_runner_repeat_is_reproducible():
    spec, job = make_spec_and_job()
    fixture = SyntheticExecutionFixture("FIXTURE-BAR", ExecutionSemantics.BAR_CLOSE_RESEARCH, BAR_METRICS)
    first = make_runner(spec).run(
        job=job,
        spec=spec,
        adapter=SyntheticExecutionAdapter(fixture),
        snapshot=make_snapshot(spec),
        observed_content_sha256="a" * 64,
    )
    second = make_runner(spec).run(
        job=job,
        spec=spec,
        adapter=SyntheticExecutionAdapter(fixture),
        snapshot=make_snapshot(spec),
        observed_content_sha256="a" * 64,
    )
    assert first.run.fingerprint == second.run.fingerprint
    assert first.receipt.input_fingerprint == second.receipt.input_fingerprint
    assert first.evidence.fingerprint == second.evidence.fingerprint
