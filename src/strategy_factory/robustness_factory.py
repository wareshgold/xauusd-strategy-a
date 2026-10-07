from __future__ import annotations

"""Dataset-bound Stability -> Robustness preparation and execution.

Research-only. Robustness consumes the exact dataset identity bound to the
upstream Stability handoff and delegates execution to a caller-supplied
adapter. This boundary does not define geometry, optimization, or production
eligibility.
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
from .test_contract import HistoricalTestSpec


class RobustnessFactoryError(RuntimeError):
    """Raised when Robustness cannot consume the declared Stability handoff."""


@dataclass(frozen=True)
class RobustnessFactoryContext:
    spec: HistoricalTestSpec
    manifest_revision: str
    job_id: str
    readiness_snapshot: ReadinessSnapshot
    handoff: ResearchHandoff
    source_record: ResearchRecord
    source_event: FactoryJobEvent
    dataset_artifact_path: Path
    dataset_artifact_id: str
    dataset_content_sha256: str
    adapter: ExecutionAdapter
    evidence_id: str | None = None
    purpose: str = "ROBUSTNESS"


@dataclass(frozen=True)
class RobustnessFactoryResult:
    job: ResearchJobSpec
    result: ResearchJobRunResult


class RobustnessFactory:
    """Consume one exact Stability dataset identity without re-querying MT5."""

    def __init__(self, runner: ResearchJobRunner) -> None:
        self.runner = runner

    def prepare_and_run(self, context: RobustnessFactoryContext) -> RobustnessFactoryResult:
        context.spec.validate()
        context.readiness_snapshot.validate()
        context.handoff.validate()
        context.source_record.validate()
        context.source_event.validate()

        if context.handoff.destination_station != "robustness":
            raise RobustnessFactoryError("handoff destination must be robustness")
        if context.handoff.source_station != "stability":
            raise RobustnessFactoryError("Robustness must consume a Stability handoff")
        if context.handoff.dataset_content_sha256 != context.dataset_content_sha256:
            raise RobustnessFactoryError("handoff dataset SHA does not match Robustness input")
        if context.handoff.dataset_artifact_id != context.dataset_artifact_id:
            raise RobustnessFactoryError("handoff artifact id does not match Robustness input")

        validate_evidence_bound_handoff(
            handoff=context.handoff,
            record=context.source_record,
            source_event=context.source_event,
            dataset_content_sha256=context.dataset_content_sha256,
            dataset_artifact_id=context.dataset_artifact_id,
        )

        artifact_path = Path(context.dataset_artifact_path)
        if not artifact_path.is_file():
            raise RobustnessFactoryError(f"dataset artifact not found: {artifact_path}")
        actual_sha = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        if actual_sha != context.dataset_content_sha256:
            raise RobustnessFactoryError("Robustness dataset bytes do not match handoff SHA")

        artifact = DatasetArtifact(
            artifact_id=context.dataset_artifact_id,
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
        return RobustnessFactoryResult(job=job, result=result)
