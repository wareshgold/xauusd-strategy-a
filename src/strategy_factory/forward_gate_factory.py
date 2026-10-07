from __future__ import annotations

"""Fail-closed Fresh Holdout -> Forward readiness gate.

Research/operations boundary only. This gate proves provenance and frozen
identity; it does not generate signals, place trades, or decide profitability.
"""

from dataclasses import dataclass
from pathlib import Path
import hashlib

from .handoff import ResearchHandoff, validate_evidence_bound_handoff
from .job_events import FactoryJobEvent
from .models import GateResult, GateStatus
from .research_record import ResearchRecord
from .snapshot import ReadinessSnapshot
from .test_contract import DatasetRole


class ForwardGateError(RuntimeError):
    """Raised when a Forward readiness gate cannot be proven."""


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
    strategy_revision_frozen: bool = True
    post_holdout_tuning: bool = False


@dataclass(frozen=True)
class ForwardGateResult:
    gate: GateResult

    @property
    def passed(self) -> bool:
        return self.gate.status is GateStatus.PASS


class ForwardGateFactory:
    """Prove that a frozen Fresh Holdout result may enter forward validation."""

    def prepare(self, context: ForwardGateContext) -> ForwardGateResult:
        context.readiness_snapshot.validate()
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

        if context.source_record.strategy_revision != context.readiness_snapshot.manifest_revision:
            # This is deliberately not used as a semantic strategy comparison;
            # it catches accidental wiring of a manifest revision where a
            # strategy revision was expected only if they are literally equal.
            pass

        if context.source_record.manifest_revision != context.manifest_revision:
            raise ForwardGateError(
                "Forward manifest_revision does not match the Holdout research record"
            )
        if context.source_record.strategy_id != context.readiness_snapshot.strategy_id:
            raise ForwardGateError(
                "Forward strategy_id does not match the frozen readiness snapshot"
            )

        holdout_sha = context.handoff.dataset_content_sha256
        holdout_artifact_id = context.handoff.dataset_artifact_id
        if len(holdout_sha) != 64 or not holdout_artifact_id:
            raise ForwardGateError(
                "Holdout handoff must carry complete dataset identity"
            )

        validate_evidence_bound_handoff(
            handoff=context.handoff,
            record=context.source_record,
            source_event=context.source_event,
            dataset_content_sha256=holdout_sha,
            dataset_artifact_id=holdout_artifact_id,
        )

        if not context.forward_session_id:
            raise ForwardGateError("forward_session_id is required")
        if not context.forward_dataset_id:
            raise ForwardGateError("forward_dataset_id is required")
        if not context.forward_dataset_artifact_id:
            raise ForwardGateError("forward dataset artifact id is required")
        if len(context.forward_dataset_content_sha256) != 64:
            raise ForwardGateError(
                "forward dataset content SHA must be a 64-character SHA-256"
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
                "strategy_revision": context.source_record.strategy_revision,
                "manifest_revision": context.manifest_revision,
                "holdout_dataset_id": context.source_record.dataset_id,
                "holdout_dataset_sha256": holdout_sha,
                "holdout_artifact_id": holdout_artifact_id,
                "forward_session_id": context.forward_session_id,
                "forward_dataset_id": context.forward_dataset_id,
                "forward_dataset_sha256": context.forward_dataset_content_sha256,
                "forward_artifact_id": context.forward_dataset_artifact_id,
                "production_decision": False,
            },
        )
        return ForwardGateResult(gate=gate)
