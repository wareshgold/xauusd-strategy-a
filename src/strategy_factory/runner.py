from __future__ import annotations

from dataclasses import dataclass

from .acceptance import evidence_acceptance_gate
from .audit import AuditBindingError, ResearchAuditRecord, bind_research_audit
from .adapter import ExecutionAdapter, validate_adapter_output
from .dataset_provenance import DatasetProvenanceResult, DatasetProvenanceStatus, evaluate_dataset_provenance
from .datasets import fingerprint_dataset
from .evidence import EvidenceBundle, EvidenceLedger
from .execution import ExecutionReceipt, execution_gate
from .fresh_holdout_authority import (
    FreshHoldoutAuthorityError,
    FreshHoldoutAuthorityVerifier,
    require_verified_authority,
)
from .manifest import StrategyManifest
from .models import GateResult, GateStatus, StrategyPassport
from .jobs import ResearchJobError, ResearchJobSpec, validate_job_matches_test_spec
from .research_provenance import ResearchProvenanceResult, evaluate_research_provenance
from .research_record import ResearchRecord, ResearchRecordLedger
from .runs import ResearchRunError, ResearchRunIdentity, ResearchRunLedger
from .snapshot import ReadinessSnapshot, validate_readiness_snapshot_against_sources
from .source_ledger import SourceResolutionLedger
from .test_contract import DatasetRole, HistoricalTestSpec


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
        fresh_holdout_authority_verifier: FreshHoldoutAuthorityVerifier | None = None,
    ) -> None:
        self.runs = runs
        self.evidence = evidence
        self.records = records or ResearchRecordLedger()
        # Configured by the trusted application composition root, never per job.
        self.fresh_holdout_authority_verifier = fresh_holdout_authority_verifier
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
        readiness_manifest: StrategyManifest | None = None,
        readiness_passport: StrategyPassport | None = None,
        readiness_ledger: SourceResolutionLedger | None = None,
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

        if spec.dataset.role is DatasetRole.FRESH_HOLDOUT:
            try:
                if (
                    readiness_manifest is None
                    or readiness_passport is None
                    or readiness_ledger is None
                ):
                    raise FreshHoldoutAuthorityError(
                        "Fresh Holdout requires Manifest, Passport, and Source Ledger inputs"
                    )
                validate_readiness_snapshot_against_sources(
                    snapshot,
                    readiness_manifest,
                    readiness_passport,
                    readiness_ledger,
                )
                readiness = snapshot.source_readiness
                eligibility = snapshot.passport_eligibility
                if (
                    readiness.get("status") != "PASS"
                    or readiness.get("frozen_geometry_blocked") is not False
                    or readiness.get("canonical_strategy_eligible") is not True
                    or eligibility.get("source_status") != "PASS"
                    or eligibility.get("frozen_geometry") != "READY"
                    or eligibility.get("canonical_strategy") != "ELIGIBLE"
                ):
                    raise FreshHoldoutAuthorityError(
                        "Fresh Holdout requires recomputed source PASS, frozen geometry READY, and canonical eligibility"
                    )
                require_verified_authority(
                    verifier=self.fresh_holdout_authority_verifier,
                    manifest=readiness_manifest,
                    passport=readiness_passport,
                    ledger=readiness_ledger,
                    strategy_id=spec.strategy_id,
                    manifest_revision=job.manifest_revision,
                )
            except (FreshHoldoutAuthorityError, ValueError) as exc:
                raise ResearchJobRunnerError(
                    "Fresh Holdout authority gate rejected the job"
                ) from exc

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

        from .synthetic import SyntheticExecutionAdapter
        if type(adapter) is SyntheticExecutionAdapter and (
            purpose != "SYNTHETIC_INFRASTRUCTURE_TEST"
            or spec.dataset.role is not DatasetRole.DEVELOPMENT
        ):
            raise ResearchJobRunnerError(
                "synthetic adapter is restricted to SYNTHETIC_INFRASTRUCTURE_TEST on DEVELOPMENT datasets"
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
            receipt = adapter.execute(spec)
            validate_adapter_output(spec=spec, receipt=receipt)
            from .synthetic import SyntheticExecutionAdapter
            if receipt.receipt_schema_version != 2:
                raise ResearchJobRunnerError(
                    "LEGACY_UNVERIFIED: schema-v1 receipts cannot be promoted to dataset-verified evidence"
                )
            if type(adapter) is SyntheticExecutionAdapter:
                if receipt.dataset_content_sha256 is not None:
                    raise ResearchJobRunnerError(
                        "trusted synthetic adapter must declare dataset_content_sha256 as null"
                    )
            elif receipt.dataset_content_sha256 != observed_content_sha256:
                raise ResearchJobRunnerError(
                    "execution receipt dataset_content_sha256 does not match runner-observed dataset bytes"
                )
            expected_result_revision = "RECEIPT_METRICS_V2"
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
