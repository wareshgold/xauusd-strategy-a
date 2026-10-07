from __future__ import annotations

"""Dataset-bound Fresh Holdout preparation and execution.

Research-only. The Fresh Holdout boundary consumes an explicit
Robustness -> Holdout handoff and an immutable, independently identified
dataset. It does not define Strategy A geometry, tune parameters, or make a
production decision.
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


class HoldoutFactoryError(RuntimeError):
    """Raised when Fresh Holdout cannot consume its declared inputs."""


@dataclass(frozen=True)
class HoldoutFactoryContext:
    spec: HistoricalTestSpec
    manifest_revision: str
    job_id: str
    readiness_snapshot: ReadinessSnapshot
    handoff: ResearchHandoff
    source_record: ResearchRecord
    source_event: FactoryJobEvent
    holdout_dataset_artifact_path: Path
    holdout_dataset_artifact_id: str
    holdout_dataset_content_sha256: str
    adapter: ExecutionAdapter
    # Explicit caller assertion that the Strategy revision is frozen before
    # this holdout run. The factory only verifies its identity against the
    # upstream immutable research record; it never chooses the revision.
    strategy_revision_frozen: bool = True
    evidence_id: str | None = None
    purpose: str = "FRESH_HOLDOUT"


@dataclass(frozen=True)
class HoldoutFactoryResult:
    job: ResearchJobSpec
    result: ResearchJobRunResult
    holdout_dataset_content_sha256: str


class HoldoutFactory:
    """Prepare and execute one immutable, independently bound holdout."""

    def __init__(self, runner: ResearchJobRunner) -> None:
        self.runner = runner

    def prepare_and_run(self, context: HoldoutFactoryContext) -> HoldoutFactoryResult:
        context.spec.validate()
        context.readiness_snapshot.validate()
        context.handoff.validate()
        context.source_record.validate()
        context.source_event.validate()

        if context.spec.dataset.role is not DatasetRole.FRESH_HOLDOUT:
            raise HoldoutFactoryError("Holdout requires a FRESH_HOLDOUT dataset")
        if not context.spec.dataset.immutable:
            raise HoldoutFactoryError("Fresh Holdout dataset must be immutable")
        if not context.strategy_revision_frozen:
            raise HoldoutFactoryError(
                "Fresh Holdout requires the Strategy revision to be frozen before entry"
            )

        if context.handoff.destination_station != "holdout":
            raise HoldoutFactoryError("handoff destination must be holdout")
        if context.handoff.source_station != "robustness":
            raise HoldoutFactoryError("Holdout must consume a Robustness handoff")

        if context.source_record.strategy_id != context.spec.strategy_id:
            raise HoldoutFactoryError(
                "holdout strategy_id does not match the upstream research record"
            )
        if context.source_record.strategy_revision != context.spec.strategy_revision:
            raise HoldoutFactoryError(
                "holdout strategy_revision does not match the frozen upstream revision"
            )
        if context.source_record.manifest_revision != context.manifest_revision:
            raise HoldoutFactoryError(
                "holdout manifest_revision does not match the upstream research record"
            )

        source_sha = context.handoff.dataset_content_sha256
        source_artifact_id = context.handoff.dataset_artifact_id
        if not source_sha or not source_artifact_id:
            raise HoldoutFactoryError(
                "Robustness handoff must carry dataset identity"
            )
        if source_sha == context.holdout_dataset_content_sha256:
            raise HoldoutFactoryError(
                "Fresh Holdout dataset must differ from the upstream Robustness dataset"
            )
        if source_artifact_id == context.holdout_dataset_artifact_id:
            raise HoldoutFactoryError(
                "Fresh Holdout artifact id must differ from the upstream Robustness artifact"
            )

        validate_evidence_bound_handoff(
            handoff=context.handoff,
            record=context.source_record,
            source_event=context.source_event,
            dataset_content_sha256=source_sha,
            dataset_artifact_id=source_artifact_id,
        )

        artifact_path = Path(context.holdout_dataset_artifact_path)
        if not artifact_path.is_file():
            raise HoldoutFactoryError(
                f"holdout dataset artifact not found: {artifact_path}"
            )

        actual_sha = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        if actual_sha != context.holdout_dataset_content_sha256:
            raise HoldoutFactoryError(
                "Fresh Holdout dataset bytes do not match declared holdout SHA"
            )

        artifact = DatasetArtifact(
            artifact_id=context.holdout_dataset_artifact_id,
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
        return HoldoutFactoryResult(
            job=job,
            result=result,
            holdout_dataset_content_sha256=context.holdout_dataset_content_sha256,
        )
