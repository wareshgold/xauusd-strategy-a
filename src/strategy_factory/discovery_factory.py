from __future__ import annotations

"""End-to-end research-only Discovery preparation and execution.

This layer binds the real MT5 M1 snapshot to the generic Factory runner.
It does not define Strategy A geometry, optimization, ranking, or production
decisions.
"""

from dataclasses import dataclass
from pathlib import Path

from .discovery_adapter import DiscoveryMatrixAdapter
from .jobs import ResearchJobSpec
from .mt5_dataset import MT5M1ArtifactExporter, MT5M1Snapshot
from .runner import ResearchJobRunner, ResearchJobRunResult
from .snapshot import ReadinessSnapshot
from .test_contract import HistoricalTestSpec


class DiscoveryFactoryError(RuntimeError):
    """Raised when the real Discovery Factory path cannot be assembled safely."""


@dataclass(frozen=True)
class DiscoveryFactoryContext:
    """Already-declared inputs for one real Discovery research job."""

    spec: HistoricalTestSpec
    manifest_revision: str
    job_id: str
    readiness_snapshot: ReadinessSnapshot
    mt5_path: str
    exporter_script: Path
    artifact_path: Path
    discovery_script: Path
    variant_name: str = "RR2_ACT10_D2"
    python_executable: str = "python"
    engine_revision: str = "SP2L-V3-CONTROLLED-DISCOVERY-20261007"
    evidence_id: str | None = None
    purpose: str = "HISTORICAL_TEST"


@dataclass(frozen=True)
class DiscoveryFactoryResult:
    job: ResearchJobSpec
    snapshot: MT5M1Snapshot
    result: ResearchJobRunResult


class DiscoveryFactory:
    """Prepare one immutable MT5 dataset and execute exactly one declared variant."""

    def __init__(self, runner: ResearchJobRunner) -> None:
        self.runner = runner

    def prepare_and_run(self, context: DiscoveryFactoryContext) -> DiscoveryFactoryResult:
        context.spec.validate()
        context.readiness_snapshot.validate()
        if context.spec.dataset.source != "MT5:XAUUSD.ecn:M1":
            raise DiscoveryFactoryError(
                "Discovery Factory requires the declared dataset source MT5:XAUUSD.ecn:M1"
            )

        exporter = MT5M1ArtifactExporter(
            script_path=context.exporter_script,
            mt5_path=context.mt5_path,
            output_path=context.artifact_path,
            symbol="XAUUSD.ecn",
            start=context.spec.dataset.start,
            end=context.spec.dataset.end,
            python_executable=context.python_executable,
        )
        snapshot = exporter.export()
        snapshot.register(self.runner.runs.registry, context.spec, lock=True)

        dataset_fingerprint = self.runner.runs.registry.get(
            context.spec.dataset.dataset_id
        ).fingerprint
        job = ResearchJobSpec.from_test_spec(
            context.spec,
            manifest_revision=context.manifest_revision,
            dataset_fingerprint=dataset_fingerprint,
            job_id=context.job_id,
        )

        adapter = DiscoveryMatrixAdapter(
            script_path=context.discovery_script,
            mt5_path=context.mt5_path,
            symbol="XAUUSD.ecn",
            start=context.spec.dataset.start,
            end=context.spec.dataset.end,
            variant_name=context.variant_name,
            bars_artifact_path=Path(snapshot.artifact.location),
            python_executable=context.python_executable,
            engine_revision=context.engine_revision,
        )

        result = self.runner.run(
            job=job,
            spec=context.spec,
            adapter=adapter,
            snapshot=context.readiness_snapshot,
            observed_content_sha256=snapshot.dataset_content_sha256,
            observed_artifact=snapshot.artifact,
            evidence_id=context.evidence_id,
            purpose=context.purpose,
        )
        return DiscoveryFactoryResult(job=job, snapshot=snapshot, result=result)
