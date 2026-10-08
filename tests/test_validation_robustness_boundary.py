from __future__ import annotations

import pytest

from strategy_factory.datasets import DatasetRegistry, DatasetRegistryError
from strategy_factory.handoff import (
    HANDOFF_ROUTES,
    ResearchHandoff,
    ResearchHandoffError,
    build_research_handoff,
)
from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.test_contract import DatasetRole, ExecutionSemantics, HistoricalTestSpec, TestDataset
from strategy_factory.usage import DatasetUsageError, DatasetUsageLedger


def _validation_dataset(dataset_id: str = "VALIDATION-001") -> TestDataset:
    return TestDataset(
        dataset_id=dataset_id,
        role=DatasetRole.UNTOUCHED_VALIDATION,
        data_revision="VALIDATION-R1",
        start="2026-10-01T00:00:00Z",
        end="2026-10-02T00:00:00Z",
        source="RESEARCH_FIXTURE",
        immutable=True,
    )


def _spec(dataset: TestDataset) -> HistoricalTestSpec:
    return HistoricalTestSpec(
        test_id="VALIDATION-TEST",
        strategy_id="SP2L-A",
        strategy_revision="REV-FROZEN",
        dataset=dataset,
        execution_semantics=ExecutionSemantics.TICK_FEASIBLE,
        parameters={"research_only": True},
    )


def test_validation_to_robustness_route_is_explicit():
    assert ("validation", "robustness") in HANDOFF_ROUTES


def test_validation_to_robustness_handoff_is_provenance_bound():
    events = FactoryJobEventLedger(path=None)
    event = events.append(
        event_type="COMPLETED",
        job_id="VALIDATION-001",
        job_fingerprint="a" * 64,
        worker_id="worker",
        station="validation",
        phase="VALIDATION",
        detail="validation complete",
        output_artifact="VALIDATION-EVIDENCE-001",
        research_run_fingerprint="b" * 64,
    )

    handoff = build_research_handoff(
        events=events,
        job_id="VALIDATION-001",
        source_station="validation",
        destination_station="robustness",
        dataset_content_sha256="c" * 64,
        dataset_artifact_id="VALIDATION-ARTIFACT-001",
    )

    assert handoff.source_station == "validation"
    assert handoff.destination_station == "robustness"
    assert handoff.dataset_content_sha256 == "c" * 64
    assert handoff.dataset_artifact_id == "VALIDATION-ARTIFACT-001"
    assert handoff.source_event_fingerprint == event.event_fingerprint


def test_validation_cannot_skip_to_holdout():
    with pytest.raises(ResearchHandoffError):
        ResearchHandoff(
            handoff_revision="RESEARCH-HANDOFF-1",
            handoff_id="H-INVALID",
            job_id="VALIDATION-001",
            job_fingerprint="a" * 64,
            source_station="validation",
            destination_station="holdout",
            output_artifact="VALIDATION-EVIDENCE-001",
            dataset_content_sha256="c" * 64,
            dataset_artifact_id="VALIDATION-ARTIFACT-001",
            source_event_fingerprint="b" * 64,
            detail="invalid route",
            fingerprint="0" * 64,
        ).validate()


def test_validation_identity_cannot_be_reused_under_new_robustness_dataset_id():
    registry = DatasetRegistry()
    validation = _validation_dataset()
    registry.register(validation, "d" * 64)

    robustness_dataset = TestDataset(
        dataset_id="ROBUSTNESS-001",
        role=DatasetRole.DEVELOPMENT,
        data_revision="ROBUSTNESS-R1",
        start=validation.start,
        end=validation.end,
        source=validation.source,
    )

    with pytest.raises(DatasetRegistryError, match="holdout identity cannot be reused"):
        registry.assert_no_holdout_reuse(robustness_dataset, "d" * 64)


def test_validation_role_cannot_drift_into_development():
    registry = DatasetRegistry()
    validation = _validation_dataset()
    registry.register(validation, "e" * 64, lock=True)

    drifted = TestDataset(
        dataset_id=validation.dataset_id,
        role=DatasetRole.DEVELOPMENT,
        data_revision=validation.data_revision,
        start=validation.start,
        end=validation.end,
        source=validation.source,
    )

    with pytest.raises(DatasetRegistryError):
        registry.register(drifted, "e" * 64)


def test_validation_cannot_be_parameter_fit_input():
    registry = DatasetRegistry()
    validation = _validation_dataset()
    registry.register(validation, "f" * 64)
    ledger = DatasetUsageLedger(registry)

    with pytest.raises(DatasetUsageError):
        ledger.record(_spec(validation), "f" * 64, purpose="PARAMETER_FIT")

    assert ledger.entries() == ()
