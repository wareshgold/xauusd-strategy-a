from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .acceptance import evidence_acceptance_gate, validate_evidence_acceptance
from .adapter import ExecutionAdapter, ExecutionAdapterError, validate_adapter_output
from .evidence import EvidenceBundle, EvidenceLedger
from .execution import ExecutionReceipt, execution_gate
from .jobs import ResearchJobError, ResearchJobSpec, validate_job_matches_test_spec
from .models import GateResult, GateStatus
from .runs import ResearchRunError, ResearchRunIdentity, ResearchRunLedger
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
    ) -> None:
        self.runs = runs
        self.evidence = evidence
        self._completed_jobs: set[str] = set()

    def run(
        self,
        *,
        job: ResearchJobSpec,
        spec: HistoricalTestSpec,
        adapter: ExecutionAdapter,
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

        run = self.runs.create(
            spec,
            manifest_revision=job.manifest_revision,
            run_id=job.job_id,
            observed_fingerprint=job.dataset_fingerprint,
            purpose=purpose,
        )

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

        self._completed_jobs.add(job.job_id)

        return ResearchJobRunResult(
            job_id=job.job_id,
            run=run,
            receipt=receipt,
            evidence=evidence,
            gates=(execution_result, acceptance),
        )
