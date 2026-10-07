from __future__ import annotations

"""Dataset-bound preparation boundary for UNTOUCHED_VALIDATION.

This module intentionally does not implement validation strategy logic. It
only verifies that a Validation job consumes an immutable validation dataset
and an explicit Stability -> Validation handoff, then delegates execution to
the injected generic runner/adapter.
"""

from dataclasses import dataclass
from pathlib import Path
import hashlib

from .adapter import ExecutionAdapter
from .datasets import DatasetArtifact
from .handoff import ResearchHandoff, validate_evidence_bound_handoff
from .job_events import FactoryJobEvent
from .jobs import ResearchJobSpec
from .research_record import ResearchRecord
from .runner import ResearchJobRunner, ResearchJobRunResult
from .snapshot import ReadinessSnapshot
from .test_contract import DatasetRole, HistoricalTestSpec


class ValidationFactoryError(RuntimeError):
    """Raised when the Validation stage cannot consume its declared inputs."""


@dataclass(frozen=True)
class ValidationFactoryContext:
    spec: HistoricalTestSpec
    manifest_revision: str
    job_id: str
    readiness_snapshot: ReadinessSnapshot
    handoff: ResearchHandoff
    source_record: ResearchRecord
    source_event: FactoryJobEvent
    validation_dataset_artifact_path: Path
    validation_dataset_artifact_id: str
    validation_dataset_content_sha256: str
    adapter: ExecutionAdapter
    evidence_id: str | None = None
    purpose: str = "UNTOUCHED_VALIDATION"


@dataclass(frozen=True)
class ValidationFactoryResult:
    job: ResearchJobSpec
    result: ResearchJobRunResult


class ValidationFactory:
    """Prepare and execute one immutable, untouched validation dataset.

    The caller supplies the validation adapter. This factory never chooses
    Strategy A geometry, parameters, optimization criteria, or production
    decisions.
    """

    def __init__(self, runner: ResearchJobRunner) -> None:
        self.runner = runner

    def prepare_and_run(self, context: ValidationFactoryContext) -> ValidationFactoryResult:
        context.spec.validate()
        context.readiness_snapshot.validate()
        context.handoff.validate()
        context.source_record.validate()
        context.source_event.validate()

        if context.spec.dataset.role is not DatasetRole.UNTOUCHED_VALIDATION:
            raise ValidationFactoryError(
                "Validation requires an UNTOUCHED_VALIDATION dataset"
            )
        if not context.spec.dataset.immutable:
            raise ValidationFactoryError("Validation dataset must be immutable")
        if context.handoff.destination_station != "validation":
            raise ValidationFactoryError(
                "handoff destination must be validation"
            )
        if context.handoff.source_station != "stability":
            raise ValidationFactoryError(
                "Validation must consume a Stability handoff"
            )

        # A validation dataset must not be silently replaced by the upstream
        # Stability dataset. Identity is checked at the artifact level.
        source_sha = context.handoff.dataset_content_sha256
        source_artifact_id = context.handoff.dataset_artifact_id
        if not source_sha or not source_artifact_id:
            raise ValidationFactoryError(
                "Stability handoff must carry dataset identity"
            )
        if source_sha == context.validation_dataset_content_sha256:
            raise ValidationFactoryError(
                "validation dataset must differ from the upstream Stability dataset"
            )
        if source_artifact_id == context.validation_dataset_artifact_id:
            raise ValidationFactoryError(
                "validation artifact id must differ from the upstream Stability artifact"
            )

        validate_evidence_bound_handoff(
            handoff=context.handoff,
            record=context.source_record,
            source_event=context.source_event,
            dataset_content_sha256=source_sha,
            dataset_artifact_id=source_artifact_id,
        )

        artifact_path = Path(context.validation_dataset_artifact_path)
        if not artifact_path.is_file():
            raise ValidationFactoryError(
                f"validation dataset artifact not found: {artifact_path}"
            )
        actual_sha = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        if actual_sha != context.validation_dataset_content_sha256:
            raise ValidationFactoryError(
                "validation dataset bytes do not match declared validation SHA"
            )

        artifact = DatasetArtifact(
            artifact_id=context.validation_dataset_artifact_id,
            location=str(artifact_path),
            content_sha256=actual_sha,
            byte_size=artifact_path.stat().st_size,
            format="json",
        )
        artifact.validate()

        self.runner.runs.registry.register(
            context.spec.dataset,
            actual_sha,
            lock=True,
            artifact=artifact,
        )
        dataset_fingerprint = self.runner.runs.registry.get(
            context.spec.dataset.dataset_id
        ).fingerprint

        job = ResearchJobSpec.from_test_spec(
            context.spec,
            manifest_revision=context.manifest_revision,
            dataset_fingerprint=dataset_fingerprint,
            job_id=context.job_id,
        )

        result = self.runner.run(
            job=job,
            spec=context.spec,
            adapter=context.adapter,
            snapshot=context.readiness_snapshot,
            observed_content_sha256=actual_sha,
            observed_artifact=artifact,
            evidence_id=context.evidence_id,
            purpose=context.purpose,
        )
        return ValidationFactoryResult(job=job, result=result)
