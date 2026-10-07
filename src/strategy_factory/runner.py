from __future__ import annotations

from dataclasses import dataclass

from .acceptance import evidence_acceptance_gate
from .audit import AuditBindingError, ResearchAuditRecord, bind_research_audit
from .adapter import ExecutionAdapter, validate_adapter_output
from .dataset_provenance import DatasetProvenanceResult, DatasetProvenanceStatus, evaluate_dataset_provenance
from .evidence import EvidenceBundle, EvidenceLedger
from .execution import ExecutionReceipt, execution_gate
from .jobs import ResearchJobError, ResearchJobSpec, validate_job_matches_test_spec
from .models import GateResult, GateStatus
from .research_provenance import ResearchProvenanceResult, evaluate_research_provenance
from .research_record import ResearchRecord, ResearchRecordLedger
from .runs import ResearchRunError, ResearchRunIdentity, ResearchRunLedger
from .snapshot import ReadinessSnapshot
from .test_contract import HistoricalTestSpec


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
        evidence_id: str | None = None,
        result_revision: str = "RECEIPT_METRICS_V1",
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
            validate_job_matches_test_spec(
                job,
                spec,
                dataset_fingerprint=job.dataset_fingerprint,
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

        dataset_provenance = evaluate_dataset_provenance(
            spec,
            self.runs.registry,
            observed_content_sha256,
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
            )
        except Exception as exc:
            # DatasetRegistry / DatasetUsage / ResearchRun errors are deliberately
            # normalized at this orchestration boundary. Callers must not need to
            # know which lower-level registry rejected the job.
            raise ResearchJobRunnerError(
                "research job could not create a validated research run"
            ) from exc

        try:
            receipt = adapter.execute(spec)
            validate_adapter_output(spec=spec, receipt=receipt)
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
            result_revision=result_revision,
            metrics=receipt.metrics,
            result={
                "execution_id": receipt.execution_id,
                "engine_revision": receipt.engine_revision,
                "input_fingerprint": receipt.input_fingerprint,
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
            run, evidence, snapshot, audit, provenance
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
