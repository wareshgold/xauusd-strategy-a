import pytest

from strategy_factory.jobs import (
    ResearchJobError,
    ResearchJobSpec,
    validate_job_matches_test_spec,
)
from strategy_factory.test_contract import (
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
)


def make_spec():
    dataset = TestDataset(
        "D1",
        DatasetRole.DEVELOPMENT,
        "DATA-R1",
        "2026-01-01",
        "2026-02-01",
        "FIXTURE",
    )
    return HistoricalTestSpec(
        "TEST-1",
        "SP2L-A",
        "STRAT-R1",
        dataset,
        ExecutionSemantics.TICK_FEASIBLE,
        parameters={"tp_r": 2, "trail": 2},
    )


def make_job():
    return ResearchJobSpec.from_test_spec(
        make_spec(),
        manifest_revision="MANIFEST-R1",
        dataset_fingerprint="a" * 64,
        job_id="JOB-1",
    )


def test_job_is_created_from_test_spec():
    job = make_job()
    assert job.job_id == "JOB-1"
    assert job.test_id == "TEST-1"
    assert job.strategy_revision == "STRAT-R1"
    assert job.execution_semantics is ExecutionSemantics.TICK_FEASIBLE


def test_job_fingerprint_is_deterministic():
    first = make_job()
    second = make_job()
    assert first.fingerprint == second.fingerprint


def test_job_fingerprint_changes_when_inputs_change():
    first = make_job()
    fields = first.as_dict()
    fields["execution_semantics"] = ExecutionSemantics(fields["execution_semantics"])
    fields["parameters"] = {"tp_r": 3, "trail": 2}
    second = ResearchJobSpec(**fields)
    assert first.fingerprint != second.fingerprint


def test_job_requires_sha256_dataset_fingerprint():
    with pytest.raises(ResearchJobError):
        ResearchJobSpec(
            "J", "S", "R", "M", "T", "D", "DR", "bad",
            ExecutionSemantics.TICK_FEASIBLE,
        ).validate()


def test_job_rejects_missing_identity():
    with pytest.raises(ResearchJobError):
        ResearchJobSpec(
            "", "S", "R", "M", "T", "D", "DR", "a" * 64,
            ExecutionSemantics.TICK_FEASIBLE,
        ).validate()


def test_job_matches_test_spec_exactly():
    job = make_job()
    validate_job_matches_test_spec(
        job, make_spec(), dataset_fingerprint="a" * 64
    )


def test_job_mismatch_is_rejected():
    job = make_job()
    spec = make_spec()
    changed = HistoricalTestSpec(
        spec.test_id,
        spec.strategy_id,
        "STRAT-R2",
        spec.dataset,
        spec.execution_semantics,
        spec.parameters,
        spec.objective,
    )
    with pytest.raises(ResearchJobError):
        validate_job_matches_test_spec(
            job, changed, dataset_fingerprint="a" * 64
        )


def test_dataset_fingerprint_mismatch_is_rejected():
    with pytest.raises(ResearchJobError):
        validate_job_matches_test_spec(
            make_job(), make_spec(), dataset_fingerprint="b" * 64
        )


def test_job_is_immutable():
    job = make_job()
    with pytest.raises((AttributeError, TypeError)):
        job.job_id = "OTHER"


def test_parameters_are_part_of_job_identity():
    job = make_job()
    assert job.as_dict()["parameters"] == {"tp_r": 2, "trail": 2}
    assert len(job.fingerprint) == 64
