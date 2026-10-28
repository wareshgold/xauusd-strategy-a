from __future__ import annotations

"""Compose the immutable Holdout -> Forward Factory boundary.

Research-only orchestration. This module binds a completed Fresh Holdout result
to an evidence-bound Holdout -> Forward handoff, then to the existing Forward
Gate and frozen Demo Forward Session. It does not execute trades, define
strategy geometry, tune parameters, or authorize production decisions.
"""

from dataclasses import dataclass
import hashlib
import json

from .forward_gate_factory import ForwardGateContext, ForwardGateFactory, ForwardGateResult
from .forward_session_factory import DemoForwardSession, DemoForwardSessionFactory
from .handoff import ResearchHandoff, build_research_handoff
from .holdout_factory import HoldoutFactoryResult
from .job_events import FactoryJobEvent, FactoryJobEventLedger, inspect_job_journal_snapshot
from .forward_session_factory import DemoForwardSessionResult


class ForwardPreparationError(RuntimeError):
    """Raised when a completed Holdout cannot be prepared for Forward."""


@dataclass(frozen=True)
class ForwardPreparationResult:
    holdout_event: FactoryJobEvent
    handoff: ResearchHandoff
    gate: ForwardGateResult
    session: DemoForwardSession

    @property
    def ready(self) -> bool:
        return self.gate.passed and self.session.production_decision is False


def prepare_holdout_to_forward(
    *,
    holdout_result: HoldoutFactoryResult,
    events: FactoryJobEventLedger,
    manifest_revision: str,
    forward_session_id: str,
    forward_dataset_id: str,
    forward_dataset_artifact_id: str,
    forward_dataset_content_sha256: str,
    holdout_dataset_content_sha256: str,
    holdout_dataset_artifact_id: str,
    strategy_revision_frozen: bool = True,
    post_holdout_tuning: bool = False,
    handoff_id: str | None = None,
    worker_id: str = "factory-forward-preparation",
) -> ForwardPreparationResult:
    """Bind one completed Fresh Holdout to a frozen demo Forward session."""

    if not strategy_revision_frozen:
        raise ForwardPreparationError(
            "Forward preparation requires the Strategy revision to remain frozen"
        )
    if post_holdout_tuning:
        raise ForwardPreparationError(
            "Forward preparation rejects post-holdout tuning"
        )
    if not manifest_revision:
        raise ForwardPreparationError("manifest_revision is required")
    if not forward_session_id:
        raise ForwardPreparationError("forward_session_id is required")
    if not forward_dataset_id or not forward_dataset_artifact_id:
        raise ForwardPreparationError("forward dataset identity is required")
    if len(forward_dataset_content_sha256) != 64:
        raise ForwardPreparationError(
            "forward dataset content SHA must be a 64-character SHA-256"
        )
    if len(holdout_dataset_content_sha256) != 64 or not holdout_dataset_artifact_id:
        raise ForwardPreparationError("Holdout dataset identity is required")

    result = holdout_result.result
    record = result.record
    job = holdout_result.job
    record.validate()
    job.validate()

    if not result.accepted:
        raise ForwardPreparationError("Forward preparation requires an accepted Holdout result")
    if record.dataset_role != "FRESH_HOLDOUT":
        raise ForwardPreparationError("Forward preparation requires a FRESH_HOLDOUT record")
    if record.manifest_revision != manifest_revision:
        raise ForwardPreparationError(
            "manifest_revision does not match the completed Holdout record"
        )
    if record.strategy_revision != job.strategy_revision:
        raise ForwardPreparationError(
            "completed Holdout strategy revision does not match its job"
        )
    if holdout_dataset_artifact_id != result.run.artifact_id:
        raise ForwardPreparationError(
            "Holdout artifact id does not match the completed Holdout run"
        )
    if holdout_dataset_content_sha256 != holdout_result.holdout_dataset_content_sha256:
        raise ForwardPreparationError(
            "Holdout dataset SHA does not match the completed Holdout run"
        )

    holdout_event = events.append(
        event_type="COMPLETED",
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
        worker_id=worker_id,
        station="holdout",
        phase="HOLDOUT",
        detail="Fresh Holdout completed; eligible for Holdout-to-Forward preparation",
        output_artifact=record.evidence_id,
        research_run_fingerprint=record.run_fingerprint,
    )

    handoff = build_research_handoff(
        events=events,
        job_id=job.job_id,
        source_station="holdout",
        destination_station="forward",
        handoff_id=handoff_id,
        detail="Evidence-bound Fresh Holdout -> Forward handoff",
        record=record,
        dataset_content_sha256=holdout_dataset_content_sha256,
        dataset_artifact_id=holdout_dataset_artifact_id,
    )

    # Bind the exact event tuple used by the gate to byte-level snapshot
    # evidence. Persisted journals are read once by the audit helper; no
    # repair, normalization, or write is performed here.
    ledger_snapshot = events.entries()
    if events.path is not None:
        journal_report, journal_events = inspect_job_journal_snapshot(events.path)
        if journal_report.get("status") != "VALID" or journal_events is None:
            raise ForwardPreparationError(
                "persisted event journal is not valid; manual reconciliation required"
            )
        if journal_events != ledger_snapshot:
            raise ForwardPreparationError(
                "persisted event journal differs from the in-memory ledger snapshot; manual reconciliation required"
            )
        ledger_sha256 = journal_report.get("sha256")
        ledger_byte_size = journal_report.get("byte_size")
        ledger_source = "persisted_jsonl"
        ledger_path = str(events.path)
    else:
        serialized_snapshot = "".join(
            json.dumps(event.as_dict(), ensure_ascii=False, separators=(",", ":")) + "\n"
            for event in ledger_snapshot
        ).encode("utf-8")
        ledger_sha256 = hashlib.sha256(serialized_snapshot).hexdigest()
        ledger_byte_size = len(serialized_snapshot)
        ledger_source = "in_memory"
        ledger_path = None

    gate = ForwardGateFactory().prepare(
        ForwardGateContext(
            manifest_revision=manifest_revision,
            readiness_snapshot=result.snapshot,
            handoff=handoff,
            source_record=record,
            source_event=holdout_event,
            forward_session_id=forward_session_id,
            forward_dataset_id=forward_dataset_id,
            forward_dataset_artifact_id=forward_dataset_artifact_id,
            forward_dataset_content_sha256=forward_dataset_content_sha256,
            strategy_revision_frozen=strategy_revision_frozen,
            holdout_result=holdout_result,
            source_event_ledger_snapshot=ledger_snapshot,
            source_event_ledger_sha256=ledger_sha256,
            source_event_ledger_byte_size=ledger_byte_size,
            source_event_ledger_source=ledger_source,
            source_event_ledger_path=ledger_path,
            post_holdout_tuning=post_holdout_tuning,
        )
    )

    session_result: DemoForwardSessionResult = DemoForwardSessionFactory().prepare(
        gate=gate,
        source_record=record,
        session_id=forward_session_id,
        forward_dataset_id=forward_dataset_id,
        forward_dataset_artifact_id=forward_dataset_artifact_id,
        forward_dataset_content_sha256=forward_dataset_content_sha256,
        post_holdout_tuning=post_holdout_tuning,
    )

    forward_event = events.append(
        event_type="HANDOFF_ACCEPTED",
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
        worker_id=worker_id,
        station="forward",
        phase="FORWARD",
        detail=f"Holdout-to-Forward handoff accepted; session={session_result.session.session_id}; session_fingerprint={session_result.session.fingerprint}",
        output_artifact=session_result.session.fingerprint,
        research_run_fingerprint=record.run_fingerprint,
    )

    return ForwardPreparationResult(
        holdout_event=holdout_event,
        handoff=handoff,
        gate=gate,
        session=session_result.session,
    )
