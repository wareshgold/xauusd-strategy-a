from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
from pathlib import Path

from .acceptance import evidence_acceptance_gate
from .audit import AuditBindingError, ResearchAuditRecord, bind_research_audit
from .adapter import ExecutionAdapter, validate_adapter_output
from .dataset_provenance import DatasetProvenanceResult, DatasetProvenanceStatus, evaluate_dataset_provenance
from .datasets import fingerprint_dataset
from .evidence import EvidenceBundle, EvidenceLedger
from .execution import ExecutionReceipt, execution_gate
from .jobs import ResearchJobError, ResearchJobSpec, validate_job_matches_test_spec
from .models import GateResult, GateStatus
from .research_provenance import ResearchProvenanceResult, evaluate_research_provenance
from .research_record import ResearchRecord, ResearchRecordLedger
from .runs import ResearchRunError, ResearchRunIdentity, ResearchRunLedger
from .snapshot import ReadinessSnapshot
from .test_contract import DatasetRole, HistoricalTestSpec


def _observe_local_dataset(
    adapter, artifact, expected_sha256: str, *, verify_identity: bool = True
) -> tuple[str, int]:
    """Independently hash the exact local file bound to a dataset-backed job."""
    if artifact is None:
        raise ResearchJobRunnerError(
            "dataset-backed jobs require a registered local DatasetArtifact"
        )
    adapter_path = getattr(adapter, "dataset_artifact_path", None)
    if adapter_path is None:
        raise ResearchJobRunnerError(
            "dataset-backed adapter must expose dataset_artifact_path"
        )
    try:
        path = Path(adapter_path).expanduser().resolve(strict=True)
        artifact_path = Path(artifact.location).expanduser().resolve(strict=True)
    except (OSError, TypeError, ValueError) as exc:
        raise ResearchJobRunnerError(
            "dataset artifact and adapter path must resolve to existing local files"
        ) from exc
    if path != artifact_path or not path.is_file():
        raise ResearchJobRunnerError(
            "adapter dataset_artifact_path must identify the registered local artifact"
        )
    digest = hashlib.sha256()
    observed_size = 0
    with path.open("rb") as dataset_file:
        for chunk in iter(lambda: dataset_file.read(1024 * 1024), b""):
            digest.update(chunk)
            observed_size += len(chunk)
    observed_sha256 = digest.hexdigest()
    if verify_identity:
        if observed_sha256 != expected_sha256:
            raise ResearchJobRunnerError(
                "local dataset bytes do not match the runner-declared SHA-256"
            )
        if observed_sha256 != artifact.content_sha256:
            raise ResearchJobRunnerError(
                "local dataset bytes do not match the registered artifact SHA-256"
            )
        if observed_size != artifact.byte_size:
            raise ResearchJobRunnerError(
                "local dataset byte size does not match the registered artifact"
            )
    return observed_sha256, observed_size


def _observe_execution_output_artifact(receipt):
    """Verify and normalize an adapter-declared local output artifact."""
    output = getattr(receipt, "output_artifact", None)
    if output is None:
        return receipt
    from .execution import ExecutionArtifact
    if not isinstance(output, ExecutionArtifact):
        raise ResearchJobRunnerError("execution output artifact contract is invalid")
    try:
        path = Path(output.local_path).expanduser().resolve(strict=True)
        if not path.is_file():
            raise OSError("output artifact is not a regular file")
        digest = hashlib.sha256()
        byte_size = 0
        with path.open("rb") as artifact_file:
            for chunk in iter(lambda: artifact_file.read(1024 * 1024), b""):
                digest.update(chunk)
                byte_size += len(chunk)
    except (OSError, TypeError, ValueError) as exc:
        raise ResearchJobRunnerError("execution output artifact must be an existing local file") from exc
    if digest.hexdigest() != output.content_sha256:
        raise ResearchJobRunnerError("execution output artifact SHA-256 does not match Runner observation")
    if byte_size != output.byte_size:
        raise ResearchJobRunnerError("execution output artifact byte size does not match Runner observation")
    return replace(receipt, output_artifact=replace(output, local_path=str(path)))


class ResearchJobRunnerError(ValueError):
    """Raised when a research job cannot be orchestrated safely."""


@dataclass(frozen=True)
class ResearchJobRunResult:
    """Immutable output of one accepted research-job orchestration."""

    job_id: str
    run: ResearchRunIdentity
    receipt: ExecutionReceipt
    evidence: EvidenceBundle
    dataset_provenance: DatasetProvenanceResult
    snapshot: ReadinessSnapshot
    audit: ResearchAuditRecord
    provenance: ResearchProvenanceResult
    record: ResearchRecord
    gates: tuple[GateResult, ...]

    @property
    def accepted(self) -> bool:
        return all(gate.status is GateStatus.PASS for gate in self.gates)


class ResearchJobRunner:
    """Orchestrate one portable research job without implementing strategy logic.

    The runner validates identity/provenance, delegates execution to an
    adapter, creates evidence from the adapter receipt, and evaluates the
    existing Factory gates. It never defines strategy geometry, optimization
    policy, or production decisions.
    """

    def __init__(
        self,
        *,
        runs: ResearchRunLedger,
        evidence: EvidenceLedger,
        records: ResearchRecordLedger | None = None,
    ) -> None:
        self.runs = runs
        self.evidence = evidence
        self.records = records or ResearchRecordLedger()
        self._completed_jobs: set[str] = set()

    def run(
        self,
        *,
        job: ResearchJobSpec,
        spec: HistoricalTestSpec,
        adapter: ExecutionAdapter,
        snapshot: ReadinessSnapshot,
        observed_content_sha256: str,
        observed_artifact=None,
        evidence_id: str | None = None,
        result_revision: str | None = None,
        purpose: str = "HISTORICAL_TEST",
    ) -> ResearchJobRunResult:
        """Execute and accept one job under its already-declared semantics.

        A completed job is not executed a second time by this runner instance.
        A fresh runner may safely replay the same immutable job; determinism is
        then established by the adapter/input contracts rather than hidden
        runner state.
        """
        try:
            job.validate()
            expected_dataset_fingerprint = fingerprint_dataset(
                spec.dataset, observed_content_sha256
            )
            if job.dataset_fingerprint != expected_dataset_fingerprint:
                raise ResearchJobRunnerError(
                    "research job dataset fingerprint does not match observed dataset identity"
                )
            validate_job_matches_test_spec(
                job,
                spec,
                dataset_fingerprint=expected_dataset_fingerprint,
            )
        except (ResearchJobError, ValueError) as exc:
            raise ResearchJobRunnerError(
                "research job does not match its test specification"
            ) from exc

        if job.job_id in self._completed_jobs:
            raise ResearchJobRunnerError(
                f"research job {job.job_id!r} has already completed in this runner"
            )

        try:
            snapshot.validate()
        except Exception as exc:
            raise ResearchJobRunnerError("readiness snapshot is invalid") from exc

        from .synthetic import SyntheticExecutionAdapter
        is_synthetic = isinstance(adapter, SyntheticExecutionAdapter)
        if is_synthetic and type(adapter) is not SyntheticExecutionAdapter:
            raise ResearchJobRunnerError(
                "synthetic adapter subclasses are not trusted"
            )
        if is_synthetic and (
            purpose != "SYNTHETIC_INFRASTRUCTURE_TEST"
            or spec.dataset.role is not DatasetRole.DEVELOPMENT
        ):
            raise ResearchJobRunnerError(
                "synthetic adapter is restricted to SYNTHETIC_INFRASTRUCTURE_TEST on DEVELOPMENT datasets"
            )

        pre_execution_observation = None
        if not is_synthetic:
            pre_execution_observation = _observe_local_dataset(
                adapter, observed_artifact, observed_content_sha256
            )

        dataset_provenance = evaluate_dataset_provenance(
            spec,
            self.runs.registry,
            observed_content_sha256,
            observed_artifact=observed_artifact,
        )
        if dataset_provenance.status is not DatasetProvenanceStatus.PASS:
            raise ResearchJobRunnerError(
                "dataset provenance gate rejected the research job"
            )

        try:
            run = self.runs.create(
                spec,
                manifest_revision=job.manifest_revision,
                run_id=job.job_id,
                observed_fingerprint=observed_content_sha256,
                purpose=purpose,
                artifact=observed_artifact,
            )
        except Exception as exc:
            # DatasetRegistry / DatasetUsage / ResearchRun errors are deliberately
            # normalized at this orchestration boundary. Callers must not need to
            # know which lower-level registry rejected the job.
            raise ResearchJobRunnerError(
                "research job could not create a validated research run"
            ) from exc

        try:
            try:
                receipt = adapter.execute(spec)
            finally:
                if not is_synthetic:
                    post_execution_observation = _observe_local_dataset(
                        adapter,
                        observed_artifact,
                        observed_content_sha256,
                        verify_identity=False,
                    )
                    if post_execution_observation != pre_execution_observation:
                        raise ResearchJobRunnerError(
                            "local dataset artifact changed during adapter execution"
                        )
            receipt = _observe_execution_output_artifact(receipt)
            validate_adapter_output(spec=spec, receipt=receipt)
            from .synthetic import SyntheticExecutionAdapter
            if receipt.receipt_schema_version not in {2, 3}:
                raise ResearchJobRunnerError(
                    "LEGACY_UNVERIFIED: schema-v1 receipts cannot be promoted to dataset-verified evidence"
                )
            if receipt.receipt_schema_version == 3 and receipt.output_artifact is None:
                raise ResearchJobRunnerError("schema-v3 receipt requires a produced output artifact")
            if is_synthetic:
                if receipt.dataset_content_sha256 is not None:
                    raise ResearchJobRunnerError(
                        "trusted synthetic adapter must declare dataset_content_sha256 as null"
                    )
            if not is_synthetic and receipt.dataset_content_sha256 != observed_content_sha256:
                raise ResearchJobRunnerError(
                    "execution receipt dataset_content_sha256 does not match runner-observed dataset bytes"
                )
            expected_result_revision = f"RECEIPT_METRICS_V{receipt.receipt_schema_version}"
            if result_revision is not None and result_revision != expected_result_revision:
                raise ResearchJobRunnerError(
                    "result_revision does not match the execution receipt schema"
                )
        except ResearchJobRunnerError:
            raise
        except Exception as exc:
            raise ResearchJobRunnerError("execution adapter failed") from exc

        execution_result = execution_gate(spec=spec, run=run, receipt=receipt)
        if execution_result.status is not GateStatus.PASS:
            raise ResearchJobRunnerError(
                "execution contract rejected adapter output"
            )

        evidence = EvidenceBundle(
            evidence_id=evidence_id or f"EVIDENCE-{job.job_id}",
            run_id=run.run_id,
            run_fingerprint=run.fingerprint,
            result_revision=expected_result_revision,
            metrics=receipt.metrics,
            result={
                "execution_id": receipt.execution_id,
                "engine_revision": receipt.engine_revision,
                "input_fingerprint": receipt.input_fingerprint,
                "receipt_schema_version": receipt.receipt_schema_version,
                "dataset_content_sha256": receipt.dataset_content_sha256,
                "output_artifact": receipt.output_artifact.as_dict() if receipt.output_artifact is not None else None,
                "execution_semantics": receipt.execution_semantics.value,
                "metrics": receipt.metrics.as_dict(),
            },
        )

        try:
            evidence = self.evidence.record(evidence)
        except ResearchRunError as exc:
            raise ResearchJobRunnerError(
                "evidence could not be registered against the research run"
            ) from exc

        acceptance = evidence_acceptance_gate(
            spec=spec,
            run=run,
            receipt=receipt,
            evidence=evidence,
            dataset_provenance=dataset_provenance,
            adapter=adapter,
            purpose=purpose,
        )
        if acceptance.status is not GateStatus.PASS:
            raise ResearchJobRunnerError(
                "evidence acceptance gate rejected the research result"
            )

        try:
            audit = bind_research_audit(run, snapshot, evidence)
        except AuditBindingError as exc:
            raise ResearchJobRunnerError(
                "research audit binding rejected the result"
            ) from exc

        provenance = evaluate_research_provenance(
            spec=spec,
            job=job,
            run=run,
            receipt=receipt,
            evidence=evidence,
            audit=audit,
            snapshot=snapshot,
            dataset_provenance=dataset_provenance,
            adapter=adapter,
            purpose=purpose,
        )
        provenance_gate = GateResult(
            name="RESEARCH_PROVENANCE",
            status=GateStatus(provenance.status.value),
            evidence="END_TO_END_PROVENANCE",
            details=provenance.as_dict(),
        )
        if provenance_gate.status is not GateStatus.PASS:
            raise ResearchJobRunnerError(
                "end-to-end research provenance gate rejected the result"
            )

        record = ResearchRecord.from_components(
            run,
            evidence,
            snapshot,
            audit,
            provenance,
            receipt=receipt if observed_artifact is not None else None,
            observed_artifact=observed_artifact if observed_artifact is not None else None,
            observed_content_sha256=(
                observed_content_sha256 if observed_artifact is not None else None
            ),
        )
        record = self.records.record(record)

        self._completed_jobs.add(job.job_id)

        return ResearchJobRunResult(
            job_id=job.job_id,
            run=run,
            receipt=receipt,
            evidence=evidence,
            dataset_provenance=dataset_provenance,
            snapshot=snapshot,
            audit=audit,
            provenance=provenance,
            record=record,
            gates=(execution_result, acceptance, provenance_gate),
        )
