from __future__ import annotations

"""Dataset-bound Discovery -> Stability preparation and execution."""

from dataclasses import dataclass
from pathlib import Path
import hashlib

from .adapter import ExecutionAdapter
from .datasets import DatasetArtifact, fingerprint_dataset
from .handoff import ResearchHandoff
from .research_record import ResearchRecord
from .job_events import FactoryJobEvent
from .runner import ResearchJobRunner, ResearchJobRunResult
from .jobs import ResearchJobSpec
from .snapshot import ReadinessSnapshot
from .test_contract import HistoricalTestSpec
from .stability_adapter import StabilityMatrixAdapter


class StabilityFactoryError(RuntimeError):
    """Raised when the Stability stage cannot consume the declared handoff."""


@dataclass(frozen=True)
class StabilityFactoryContext:
    spec: HistoricalTestSpec
    manifest_revision: str
    job_id: str
    readiness_snapshot: ReadinessSnapshot
    handoff: ResearchHandoff
    source_record: ResearchRecord
    source_event: FactoryJobEvent
    discovery_json_path: Path
    dataset_artifact_path: Path
    dataset_artifact_id: str
    dataset_content_sha256: str
    stability_script: Path
    variant_name: str = "RR2_ACT10_D2"
    segments: int = 3
    python_executable: str = "python"
    engine_revision: str = "SP2L-V3-CONTROLLED-STABILITY-20261007"
    evidence_id: str | None = None
    purpose: str = "STABILITY"


@dataclass(frozen=True)
class StabilityFactoryResult:
    job: ResearchJobSpec
    result: ResearchJobRunResult


class StabilityFactory:
    """Consume one immutable Discovery handoff without re-querying MT5."""

    def __init__(self, runner: ResearchJobRunner) -> None:
        self.runner = runner

    def prepare_and_run(self, context: StabilityFactoryContext) -> StabilityFactoryResult:
        context.spec.validate()
        context.readiness_snapshot.validate()
        context.handoff.validate()
        context.source_record.validate()
        context.source_event.validate()

        if context.handoff.destination_station != "stability":
            raise StabilityFactoryError("handoff destination must be stability")
        if context.handoff.dataset_content_sha256 != context.dataset_content_sha256:
            raise StabilityFactoryError("handoff dataset SHA does not match Stability input")
        if context.handoff.dataset_artifact_id != context.dataset_artifact_id:
            raise StabilityFactoryError("handoff artifact id does not match Stability input")

        from .handoff import validate_evidence_bound_handoff
        validate_evidence_bound_handoff(
            handoff=context.handoff,
            record=context.source_record,
            source_event=context.source_event,
            dataset_content_sha256=context.dataset_content_sha256,
            dataset_artifact_id=context.dataset_artifact_id,
        )

        artifact_path = Path(context.dataset_artifact_path)
        if not artifact_path.is_file():
            raise StabilityFactoryError(f"dataset artifact not found: {artifact_path}")
        actual_sha = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        if actual_sha != context.dataset_content_sha256:
            raise StabilityFactoryError("Stability dataset bytes do not match handoff SHA")

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

        adapter = StabilityMatrixAdapter(
            script_path=context.stability_script,
            discovery_json_path=context.discovery_json_path,
            dataset_artifact_path=artifact_path,
            expected_dataset_content_sha256=context.dataset_content_sha256,
            expected_dataset_artifact_id=context.dataset_artifact_id,
            variant_name=context.variant_name,
            segments=context.segments,
            python_executable=context.python_executable,
            engine_revision=context.engine_revision,
        )
        result = self.runner.run(
            job=job,
            spec=context.spec,
            adapter=adapter,
            snapshot=context.readiness_snapshot,
            observed_content_sha256=actual_sha,
            observed_artifact=artifact,
            evidence_id=context.evidence_id,
            purpose=context.purpose,
        )
        return StabilityFactoryResult(job=job, result=result)
