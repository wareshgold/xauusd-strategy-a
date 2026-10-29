from __future__ import annotations

"""Fail-closed Fresh Holdout -> Forward readiness gate.

Research/operations boundary only. This gate proves provenance and frozen
identity; it does not generate signals, place trades, or decide profitability.
"""

from dataclasses import dataclass
from pathlib import Path
import hashlib

from .handoff import ResearchHandoff, validate_evidence_bound_handoff
from .manifest import StrategyManifest
from .holdout_factory import HoldoutFactoryResult
from .dataset_provenance import DatasetProvenanceStatus
from .job_events import FactoryJobEvent
from .models import GateResult, GateStatus, StrategyPassport
from .research_record import ResearchRecord
from .snapshot import ReadinessSnapshot, validate_readiness_snapshot_against_sources
from .source_ledger import SourceResolutionLedger
from .test_contract import DatasetRole


class ForwardGateError(RuntimeError):
    """Raised when a Forward readiness gate cannot be proven."""

def _is_sha256_digest(value: str) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


@dataclass(frozen=True)
class ForwardGateContext:
    manifest_revision: str
    readiness_snapshot: ReadinessSnapshot
    handoff: ResearchHandoff
    source_record: ResearchRecord
    source_event: FactoryJobEvent
    forward_session_id: str
    forward_dataset_id: str
    forward_dataset_artifact_id: str
    forward_dataset_content_sha256: str
    readiness_manifest: StrategyManifest | None = None
    readiness_passport: StrategyPassport | None = None
    readiness_ledger: SourceResolutionLedger | None = None
    strategy_revision_frozen: bool = True
    post_holdout_tuning: bool = False
    holdout_result: HoldoutFactoryResult | None = None
    source_event_ledger_snapshot: tuple[FactoryJobEvent, ...] | None = None
    source_event_ledger_sha256: str | None = None
    source_event_ledger_byte_size: int | None = None
    source_event_ledger_source: str | None = None
    source_event_ledger_path: str | None = None
    source_event_ledger_prefix_sha256: str | None = None
    source_event_ledger_prefix_byte_size: int | None = None
    source_event_ledger_sequence_boundary: int | None = None
    source_event_ledger_prefix_source: str | None = None


@dataclass(frozen=True)
class ForwardGateResult:
    gate: GateResult
    holdout_result: HoldoutFactoryResult | None = None
    readiness_snapshot: ReadinessSnapshot | None = None
    readiness_manifest: StrategyManifest | None = None
    readiness_passport: StrategyPassport | None = None
    readiness_ledger: SourceResolutionLedger | None = None

    @property
    def passed(self) -> bool:
        return self.gate.status is GateStatus.PASS


class ForwardGateFactory:
    """Prove that a frozen Fresh Holdout result may enter forward validation."""

    def prepare(self, context: ForwardGateContext) -> ForwardGateResult:
        context.readiness_snapshot.validate()

        # Do not rely solely on a prior HoldoutFactory result: this is an
        # independent boundary and must fail closed on blocked readiness.
        readiness = context.readiness_snapshot.source_readiness
        if readiness.get("status") != "PASS":
            raise ForwardGateError(
                "Forward gate requires source readiness PASS; "
                f"status={readiness.get('status', 'MISSING')}"
            )
        if readiness.get("frozen_geometry_blocked") is not False:
            raise ForwardGateError(
                "Forward gate requires frozen geometry to be unblocked"
            )
        if readiness.get("canonical_strategy_eligible") is not True:
            raise ForwardGateError(
                "Forward gate requires canonical strategy eligibility"
            )

        eligibility = context.readiness_snapshot.passport_eligibility
        if eligibility.get("source_status") != "PASS":
            raise ForwardGateError(
                "Forward gate requires passport source_status PASS; "
                f"status={eligibility.get('source_status', 'MISSING')}"
            )
        if eligibility.get("frozen_geometry") != "READY":
            raise ForwardGateError(
                "Forward gate requires passport frozen_geometry READY"
            )
        if eligibility.get("canonical_strategy") != "ELIGIBLE":
            raise ForwardGateError(
                "Forward gate requires passport canonical_strategy ELIGIBLE"
            )

        context.handoff.validate()
        context.source_record.validate()
        context.source_event.validate()

        if context.handoff.source_station != "holdout":
            raise ForwardGateError("Forward gate requires a Holdout source handoff")
        if context.handoff.destination_station != "forward":
            raise ForwardGateError("Forward gate destination must be forward")

        if context.source_record.dataset_role != DatasetRole.FRESH_HOLDOUT.value:
            raise ForwardGateError(
                "Forward gate requires a source ResearchRecord from FRESH_HOLDOUT"
            )
        if not context.strategy_revision_frozen:
            raise ForwardGateError(
                "Forward gate requires the Strategy revision to remain frozen"
            )
        if context.post_holdout_tuning:
            raise ForwardGateError(
                "Forward gate rejects any post-holdout tuning"
            )


        if context.source_record.manifest_revision != context.manifest_revision:
            raise ForwardGateError(
                "Forward manifest_revision does not match the Holdout research record"
            )
        if context.readiness_snapshot.manifest_revision != context.manifest_revision:
            raise ForwardGateError(
                "Forward manifest_revision does not match the frozen readiness snapshot"
            )
        if context.source_record.strategy_id != context.readiness_snapshot.strategy_id:
            raise ForwardGateError(
                "Forward strategy_id does not match the frozen readiness snapshot"
            )
        if context.source_record.snapshot_fingerprint != context.readiness_snapshot.fingerprint:
            raise ForwardGateError(
                "readiness snapshot fingerprint does not match the Holdout research record"
            )

        # Require the completed Holdout result as independent evidence; the
        # handoff's own identity fields cannot be used as their own proof.
        holdout_result = context.holdout_result
        if holdout_result is None:
            raise ForwardGateError(
                "Forward gate requires the completed HoldoutFactoryResult binding"
            )
        holdout_run = holdout_result.result
        provenance = holdout_run.dataset_provenance
        if not holdout_run.accepted or provenance.status is not DatasetProvenanceStatus.PASS:
            raise ForwardGateError(
                "Forward gate requires an accepted Holdout result with PASS dataset provenance"
            )
        if holdout_run.record != context.source_record:
            raise ForwardGateError(
                "Holdout result record does not match the Forward source record"
            )
        if (
            holdout_result.job.job_id != holdout_run.job_id
            or holdout_result.job.job_id != holdout_run.run.run_id
            or holdout_result.job.dataset_fingerprint != holdout_run.run.dataset_fingerprint
            or holdout_run.run.dataset_id != holdout_run.record.dataset_id
            or holdout_run.run.dataset_role != DatasetRole.FRESH_HOLDOUT.value
            or holdout_run.run.artifact_id != provenance.observed_artifact_id
            or provenance.dataset_id != holdout_run.run.dataset_id
            or provenance.registered_fingerprint != holdout_run.run.dataset_fingerprint
            or provenance.observed_fingerprint != holdout_run.run.dataset_fingerprint
            or provenance.registered_artifact_id != holdout_run.run.artifact_id
            or provenance.observed_artifact_id != holdout_run.run.artifact_id
        ):
            raise ForwardGateError(
                "Holdout run, dataset provenance, artifact, and record identities do not agree"
            )

        holdout_sha = context.handoff.dataset_content_sha256
        holdout_artifact_id = context.handoff.dataset_artifact_id
        if not _is_sha256_digest(holdout_sha) or not holdout_artifact_id:
            raise ForwardGateError(
                "Holdout handoff must carry a valid SHA-256 and complete dataset identity"
            )
        if holdout_sha != holdout_result.holdout_dataset_content_sha256:
            raise ForwardGateError(
                "Holdout handoff SHA does not match the independently observed Holdout result SHA"
            )
        if holdout_artifact_id != holdout_run.run.artifact_id:
            raise ForwardGateError(
                "Holdout handoff artifact id does not match the independently observed Holdout result"
            )
        if (
            context.source_event.research_run_fingerprint != holdout_run.run.fingerprint
            or context.source_event.output_artifact != holdout_run.evidence.evidence_id
            or context.source_event.job_id != holdout_result.job.job_id
            or context.source_event.job_fingerprint != holdout_result.job.fingerprint
            or context.source_event.station != "holdout"
            or context.source_event.event_type != "COMPLETED"
        ):
            raise ForwardGateError(
                "Holdout source event does not bind to the completed Holdout run and evidence"
            )

        # A single event object cannot prove that no competing completion
        # exists elsewhere in the lifecycle ledger. Require the immutable
        # tuple snapshot and validate the entire sequence before trusting it.
        ledger_snapshot = context.source_event_ledger_snapshot
        if ledger_snapshot is None:
            raise ForwardGateError(
                "Forward gate requires a validated source event ledger snapshot"
            )
        ledger_sha256 = context.source_event_ledger_sha256
        ledger_byte_size = context.source_event_ledger_byte_size
        ledger_source = context.source_event_ledger_source
        if (
            not _is_sha256_digest(ledger_sha256)
            or not isinstance(ledger_byte_size, int)
            or isinstance(ledger_byte_size, bool)
            or ledger_byte_size < 0
            or ledger_source not in {"persisted_jsonl", "in_memory"}
            or (ledger_source == "persisted_jsonl" and not context.source_event_ledger_path)
        ):
            raise ForwardGateError(
                "Forward gate requires valid byte-level event-ledger snapshot evidence"
            )
        if ledger_source == "in_memory" and context.source_event_ledger_path is not None:
            raise ForwardGateError(
                "in-memory event-ledger snapshot must not claim a persisted journal path"
            )
        try:
            for expected_sequence, ledger_event in enumerate(ledger_snapshot, start=1):
                ledger_event.validate()
                if ledger_event.sequence != expected_sequence:
                    raise ValueError("event sequence is not contiguous")
        except (AttributeError, TypeError, ValueError) as exc:
            raise ForwardGateError(
                "source event ledger snapshot is invalid; manual reconciliation required"
            ) from exc
        matching_events = [
            item for item in ledger_snapshot
            if item.job_id == holdout_result.job.job_id
            and item.station == "holdout"
        ]
        completed_events = [
            item for item in matching_events if item.event_type == "COMPLETED"
        ]
        if len(completed_events) != 1 or completed_events[0] != context.source_event:
            raise ForwardGateError(
                "source event ledger snapshot does not prove exactly one matching Holdout completion"
            )
        if any(item.event_type == "FAILED" for item in matching_events):
            raise ForwardGateError(
                "source event ledger snapshot contains conflicting Holdout terminal events"
            )

        validate_evidence_bound_handoff(
            handoff=context.handoff,
            record=context.source_record,
            source_event=context.source_event,
            dataset_content_sha256=holdout_result.holdout_dataset_content_sha256,
            dataset_artifact_id=holdout_run.run.artifact_id,
        )

        if not context.forward_session_id:
            raise ForwardGateError("forward_session_id is required")
        if not context.forward_dataset_id:
            raise ForwardGateError("forward_dataset_id is required")
        if not context.forward_dataset_artifact_id:
            raise ForwardGateError("forward dataset artifact id is required")
        if not _is_sha256_digest(context.forward_dataset_content_sha256):
            raise ForwardGateError(
                "forward dataset content SHA must be a lowercase hexadecimal SHA-256"
            )
        if context.forward_dataset_content_sha256 == holdout_sha:
            raise ForwardGateError(
                "Forward dataset identity must differ from the Fresh Holdout dataset"
            )
        if context.forward_dataset_artifact_id == holdout_artifact_id:
            raise ForwardGateError(
                "Forward dataset artifact id must differ from the Fresh Holdout artifact"
            )
        if context.forward_dataset_id == context.source_record.dataset_id:
            raise ForwardGateError(
                "Forward dataset id must differ from the Fresh Holdout dataset id"
            )

        if (
            context.readiness_manifest is None
            or context.readiness_passport is None
            or context.readiness_ledger is None
        ):
            raise ForwardGateError(
                "Forward gate requires authoritative Manifest, Passport, and Source Ledger inputs"
            )
        try:
            validate_readiness_snapshot_against_sources(
                context.readiness_snapshot,
                context.readiness_manifest,
                context.readiness_passport,
                context.readiness_ledger,
            )
        except ValueError as exc:
            raise ForwardGateError(
                "Forward readiness snapshot does not match source inputs"
            ) from exc

        evidence = (
            f"holdout_record={context.source_record.run_id};"
            f"holdout_evidence={context.source_record.evidence_id};"
            f"strategy={context.source_record.strategy_id}@{context.source_record.strategy_revision};"
            f"manifest={context.manifest_revision};"
            f"forward_session={context.forward_session_id};"
            f"forward_dataset={context.forward_dataset_id};"
            f"forward_sha256={context.forward_dataset_content_sha256}"
        )
        gate = GateResult(
            name="FRESH_HOLDOUT_TO_FORWARD",
            status=GateStatus.PASS,
            evidence=evidence,
            details={
                "source_station": "holdout",
                "destination_station": "forward",
                "handoff_fingerprint": context.handoff.fingerprint,
                "strategy_revision": context.source_record.strategy_revision,
                "manifest_revision": context.manifest_revision,
                "holdout_dataset_id": context.source_record.dataset_id,
                "holdout_dataset_sha256": holdout_sha,
                "holdout_artifact_id": holdout_artifact_id,
                "forward_session_id": context.forward_session_id,
                "forward_dataset_id": context.forward_dataset_id,
                "forward_dataset_sha256": context.forward_dataset_content_sha256,
                "forward_artifact_id": context.forward_dataset_artifact_id,
                "source_event_ledger_sha256": ledger_sha256,
                "source_event_ledger_byte_size": ledger_byte_size,
                "source_event_ledger_event_count": len(ledger_snapshot),
                "source_event_ledger_source": ledger_source,
                "source_event_ledger_path": context.source_event_ledger_path,
                "source_event_ledger_prefix_sha256": context.source_event_ledger_prefix_sha256,
                "source_event_ledger_prefix_byte_size": context.source_event_ledger_prefix_byte_size,
                "source_event_ledger_sequence_boundary": context.source_event_ledger_sequence_boundary,
                "source_event_ledger_prefix_source": context.source_event_ledger_prefix_source,
                "production_decision": False,
            },
        )
        return ForwardGateResult(
            gate=gate,
            holdout_result=holdout_result,
            readiness_snapshot=context.readiness_snapshot,
            readiness_manifest=context.readiness_manifest,
            readiness_passport=context.readiness_passport,
            readiness_ledger=context.readiness_ledger,
        )
