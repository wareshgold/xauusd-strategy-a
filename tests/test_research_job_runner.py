import hashlib
from pathlib import Path

import pytest

from strategy_factory.adapter import build_execution_receipt
from strategy_factory.datasets import DatasetArtifact, DatasetRegistry, fingerprint_dataset
from strategy_factory.evidence import EvidenceLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.runs import ResearchRunLedger
from strategy_factory.runner import ResearchJobRunner, ResearchJobRunnerError
from strategy_factory.research_record import ResearchRecordError
from strategy_factory.snapshot import ReadinessSnapshot
from strategy_factory.synthetic import SyntheticExecutionAdapter, SyntheticExecutionFixture
from strategy_factory.test_contract import (
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
)
from strategy_factory.usage import DatasetUsageLedger


DATASET_BYTES = b"controlled dataset bytes for receipt contract tests"
DATASET_SHA256 = hashlib.sha256(DATASET_BYTES).hexdigest()


@pytest.fixture
def dataset_fixture(tmp_path):
    dataset_path = tmp_path / "dataset.bin"
    dataset_path.write_bytes(DATASET_BYTES)
    artifact = DatasetArtifact(
        artifact_id="TEST-DATASET-ARTIFACT-1",
        location=str(dataset_path.resolve()),
        content_sha256=DATASET_SHA256,
        byte_size=len(DATASET_BYTES),
        format="binary",
    )
    return dataset_path, artifact


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
        dataset_fingerprint=fingerprint_dataset(dataset, DATASET_SHA256),
        job_id="JOB-1",
    )
    return spec, job


def make_runner(artifact):
    registry = DatasetRegistry()
    spec, _ = make_spec_and_job()
    registry.register(spec.dataset, content_fingerprint=DATASET_SHA256, artifact=artifact)
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


def run_job(runner, job, spec, adapter, artifact):
    return runner.run(
        job=job,
        spec=spec,
        adapter=adapter,
        snapshot=make_snapshot(spec),
        observed_content_sha256=DATASET_SHA256,
        observed_artifact=artifact,
    )


class FakeAdapter:
    engine_revision = "ENGINE-1"

    def __init__(self, dataset_path, *, metrics=METRICS, execution_id="EX-1"):
        self.dataset_path = dataset_path
        self.metrics = metrics
        self.execution_id = execution_id
        self.calls = 0

    @property
    def dataset_artifact_path(self):
        return self.dataset_path

    def execute(self, spec):
        self.calls += 1
        return build_execution_receipt(
            execution_id=self.execution_id,
            spec=spec,
            engine_revision=self.engine_revision,
            input_fingerprint=hashlib.sha256(f"FAKE-ENGINE:{spec.test_id}:{DATASET_SHA256}".encode()).hexdigest(),
            metrics=self.metrics,
            receipt_schema_version=2,
            dataset_content_sha256=hashlib.sha256(DATASET_BYTES).hexdigest(),
        )


def test_runner_completes_end_to_end(dataset_fixture):
    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    runner = make_runner(artifact)
    adapter = FakeAdapter(dataset_path)

    result = run_job(runner, job, spec, adapter, artifact)

    assert result.accepted
    assert result.run.run_id == "JOB-1"
    assert result.receipt.execution_id == "EX-1"
    assert result.evidence.run_id == result.run.run_id
    assert result.dataset_provenance.status.value == "PASS"
    assert result.audit.run_fingerprint == result.run.fingerprint
    assert result.provenance.status.value == "PASS"
    assert result.record.run_fingerprint == result.run.fingerprint
    assert result.record.record_revision == "RESEARCH-RECORD-2"
    assert result.record.dataset_content_sha256 == DATASET_SHA256
    assert result.record.dataset_artifact_id == artifact.artifact_id
    assert result.record.dataset_byte_size == len(DATASET_BYTES)
    assert len(result.record.execution_receipt_fingerprint) == 64
    assert len(result.record.dataset_binding_fingerprint) == 64
    assert result.record.fingerprint == result.record.fingerprint
    assert [gate.name for gate in result.gates] == [
        "EXECUTION_CONTRACT",
        "EVIDENCE_ACCEPTANCE",
        "RESEARCH_PROVENANCE",
    ]
    assert adapter.calls == 1


def test_runner_does_not_execute_completed_job_twice(dataset_fixture):
    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    runner = make_runner(artifact)
    adapter = FakeAdapter(dataset_path)
    run_job(runner, job, spec, adapter, artifact)

    with pytest.raises(ResearchJobRunnerError):
        run_job(runner, job, spec, adapter, artifact)

    assert adapter.calls == 1


def test_runner_rejects_job_test_mismatch(dataset_fixture):
    dataset_path, artifact = dataset_fixture
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
    runner = make_runner(artifact)

    with pytest.raises(ResearchJobRunnerError):
        run_job(runner, job, changed, FakeAdapter(dataset_path), artifact)


def test_runner_rejects_dataset_fingerprint_mismatch(dataset_fixture):
    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    bad_job = ResearchJobSpec(
        **{
            **job.as_dict(),
            "dataset_fingerprint": "b" * 64,
            "execution_semantics": ExecutionSemantics(job.execution_semantics),
        }
    )
    runner = make_runner(artifact)

    with pytest.raises(ResearchJobRunnerError):
        run_job(runner, bad_job, spec, FakeAdapter(dataset_path), artifact)


def test_runner_rejects_adapter_identity_mismatch(dataset_fixture):
    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    runner = make_runner(artifact)

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
        run_job(runner, job, spec, BadAdapter(dataset_path), artifact)


def test_runner_rejects_incomplete_adapter_execution(dataset_fixture):
    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    runner = make_runner(artifact)

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
        run_job(runner, job, spec, IncompleteAdapter(dataset_path), artifact)


def test_runner_evidence_is_derived_from_receipt(dataset_fixture):
    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    runner = make_runner(artifact)
    result = run_job(runner, job, spec, FakeAdapter(dataset_path), artifact)

    assert result.evidence.metrics == result.receipt.metrics
    assert result.evidence.result["execution_id"] == result.receipt.execution_id
    assert result.evidence.result["engine_revision"] == result.receipt.engine_revision


def test_runner_preserves_declared_execution_semantics(dataset_fixture):
    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    runner = make_runner(artifact)
    result = run_job(runner, job, spec, FakeAdapter(dataset_path), artifact)

    assert result.run.execution_semantics is ExecutionSemantics.TICK_FEASIBLE
    assert result.receipt.execution_semantics is ExecutionSemantics.TICK_FEASIBLE
    assert result.evidence.result["execution_semantics"] == "TICK_FEASIBLE"


def test_runner_creates_reproducible_run_identity(dataset_fixture):
    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    first = run_job(make_runner(artifact), job, spec, FakeAdapter(dataset_path), artifact)
    second = run_job(make_runner(artifact), job, spec, FakeAdapter(dataset_path), artifact)

    assert first.run.fingerprint == second.run.fingerprint
    assert first.evidence.fingerprint == second.evidence.fingerprint
    assert first.audit.fingerprint == second.audit.fingerprint
    assert first.provenance == second.provenance
    assert first.record == second.record


def test_runner_never_requires_strategy_geometry(dataset_fixture):
    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    runner = make_runner(artifact)
    result = run_job(runner, job, spec, FakeAdapter(dataset_path), artifact)

    assert result.accepted
    assert result.run.strategy_id == "SP2L-A"
    assert result.run.parameters == {"tp_r": 2}


def test_runner_rejects_legacy_v1_receipt_as_unverified(dataset_fixture):
    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    runner = make_runner(artifact)
    class LegacyAdapter(FakeAdapter):
        def execute(self, source_spec):
            return build_execution_receipt(
                execution_id=self.execution_id,
                spec=source_spec,
                engine_revision=self.engine_revision,
                input_fingerprint="b" * 64,
                metrics=self.metrics,
            )
    with pytest.raises(ResearchJobRunnerError, match="LEGACY_UNVERIFIED"):
        run_job(runner, job, spec, LegacyAdapter(dataset_path), artifact)


def test_runner_rejects_dataset_digest_mismatch(dataset_fixture):
    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    runner = make_runner(artifact)
    class MismatchedAdapter(FakeAdapter):
        def execute(self, source_spec):
            receipt = super().execute(source_spec)
            return receipt.__class__(
                receipt.execution_id,
                receipt.test_id,
                receipt.strategy_revision,
                receipt.execution_semantics,
                receipt.engine_revision,
                receipt.input_fingerprint,
                receipt.completed,
                receipt.metrics,
                receipt_schema_version=2,
                dataset_content_sha256="b" * 64,
            )
    with pytest.raises(ResearchJobRunnerError, match="dataset_content_sha256"):
        run_job(runner, job, spec, MismatchedAdapter(dataset_path), artifact)


def test_runner_rejects_adapter_without_local_dataset_path(dataset_fixture):
    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    runner = make_runner(artifact)
    delegate = FakeAdapter(dataset_path)

    class AdapterWithoutPath:
        engine_revision = delegate.engine_revision

        def execute(self, source_spec):
            return delegate.execute(source_spec)

    with pytest.raises(ResearchJobRunnerError, match="must expose dataset_artifact_path"):
        run_job(runner, job, spec, AdapterWithoutPath(), artifact)


def test_runner_rejects_dataset_mutated_during_adapter_execution(dataset_fixture):
    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    runner = make_runner(artifact)

    class MutatingAdapter(FakeAdapter):
        def execute(self, source_spec):
            receipt = super().execute(source_spec)
            dataset_path.write_bytes(b"mutated during execution")
            return receipt

    try:
        with pytest.raises(ResearchJobRunnerError, match="local dataset artifact changed during adapter execution"):
            run_job(runner, job, spec, MutatingAdapter(dataset_path), artifact)
    finally:
        dataset_path.write_bytes(DATASET_BYTES)



def test_runner_rejects_dataset_mutated_before_adapter_exception(dataset_fixture):
    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    runner = make_runner(artifact)

    class MutatingFailingAdapter(FakeAdapter):
        def execute(self, source_spec):
            dataset_path.write_bytes(b"mutated before adapter failure")
            raise RuntimeError("adapter failed after mutation")

    try:
        with pytest.raises(
            ResearchJobRunnerError,
            match="local dataset artifact changed during adapter execution",
        ):
            run_job(runner, job, spec, MutatingFailingAdapter(dataset_path), artifact)
    finally:
        dataset_path.write_bytes(DATASET_BYTES)


def test_runner_rejects_artifact_path_mismatch(dataset_fixture):
    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    runner = make_runner(artifact)

    class WrongPathAdapter(FakeAdapter):
        @property
        def dataset_artifact_path(self):
            return dataset_path.parent / "not-the-registered-dataset.bin"

    with pytest.raises(ResearchJobRunnerError, match="must resolve to existing local files"):
        run_job(runner, job, spec, WrongPathAdapter(dataset_path), artifact)


def test_runner_rejects_synthetic_adapter_subclass_before_ledger_writes(dataset_fixture):
    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    runner = make_runner(artifact)

    class UntrustedSyntheticAdapter(SyntheticExecutionAdapter):
        def __init__(self):
            fixture = SyntheticExecutionFixture(
                "UNTRUSTED-SUBCLASS-FIXTURE",
                ExecutionSemantics.TICK_FEASIBLE,
                METRICS,
            )
            super().__init__(fixture)
            self.calls = 0

        def execute(self, source_spec):
            self.calls += 1
            return super().execute(source_spec)

    adapter = UntrustedSyntheticAdapter()

    with pytest.raises(ResearchJobRunnerError, match="synthetic adapter subclasses are not trusted"):
        run_job(runner, job, spec, adapter, artifact)

    assert adapter.calls == 0
    assert runner.runs.entries() == ()
    assert runner.runs.usage_ledger.entries() == ()



def test_runner_research_record_v2_rejects_dataset_binding_tampering(dataset_fixture):
    from dataclasses import replace

    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    result = run_job(
        make_runner(artifact), job, spec, FakeAdapter(dataset_path), artifact
    )

    with pytest.raises(ResearchRecordError, match="dataset binding fingerprint mismatch"):
        replace(result.record, dataset_content_sha256="b" * 64).validate()


def test_runner_research_record_v2_round_trips_serialized_binding(dataset_fixture):
    from strategy_factory.research_record import ResearchRecord

    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    result = run_job(
        make_runner(artifact), job, spec, FakeAdapter(dataset_path), artifact
    )

    restored = ResearchRecord.from_dict(result.record.as_dict())
    assert restored == result.record
    assert restored.dataset_content_sha256 == DATASET_SHA256
    assert restored.dataset_artifact_id == artifact.artifact_id
    assert restored.dataset_byte_size == len(DATASET_BYTES)


def _completed_event_for_record(result, job):
    from strategy_factory.job_events import FactoryJobEventLedger

    events = FactoryJobEventLedger(path=None)
    events.append(
        event_type="COMPLETED",
        job_id=result.record.run_id,
        job_fingerprint=job.fingerprint,
        station="discovery",
        phase="DISCOVERY",
        output_artifact=result.record.evidence_id,
        research_run_fingerprint=result.record.run_fingerprint,
    )
    return events


def test_handoff_v2_inherits_dataset_binding_from_research_record(dataset_fixture):
    from strategy_factory.handoff import build_research_handoff

    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    result = run_job(
        make_runner(artifact), job, spec, FakeAdapter(dataset_path), artifact
    )
    events = _completed_event_for_record(result, job)

    handoff = build_research_handoff(
        events=events,
        job_id=result.record.run_id,
        source_station="discovery",
        destination_station="stability",
        record=result.record,
    )

    assert handoff.dataset_content_sha256 == result.record.dataset_content_sha256
    assert handoff.dataset_artifact_id == result.record.dataset_artifact_id
    handoff.validate()


def test_handoff_v2_rejects_dataset_binding_substitution(dataset_fixture):
    from strategy_factory.handoff import ResearchHandoffError, build_research_handoff

    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    result = run_job(
        make_runner(artifact), job, spec, FakeAdapter(dataset_path), artifact
    )
    events = _completed_event_for_record(result, job)

    with pytest.raises(ResearchHandoffError, match="conflicts with research record binding"):
        build_research_handoff(
            events=events,
            job_id=result.record.run_id,
            source_station="discovery",
            destination_station="stability",
            record=result.record,
            dataset_content_sha256="b" * 64,
        )


def test_research_record_v2_rejects_malformed_binding_field_types(dataset_fixture):
    from dataclasses import replace

    dataset_path, artifact = dataset_fixture
    spec, job = make_spec_and_job()
    result = run_job(
        make_runner(artifact), job, spec, FakeAdapter(dataset_path), artifact
    )

    with pytest.raises(ResearchRecordError, match="byte size is invalid"):
        replace(result.record, dataset_byte_size=True).validate()

    with pytest.raises(ResearchRecordError, match="SHA-256 is invalid"):
        replace(result.record, dataset_content_sha256=123).validate()
