from __future__ import annotations

"""Research-only contract for entering a demo forward-validation session.

This module binds an already-PASSed Fresh Holdout -> Forward gate to an
immutable session identity. It does not run a strategy, generate BUY/SELL
decisions, place orders, or modify the existing MT5 forward runner.
"""

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json

from .forward_gate_factory import ForwardGateResult
from .models import GateStatus
from .research_record import ResearchRecord
from .manifest import StrategyManifest
from .models import StrategyPassport
from .snapshot import ReadinessSnapshot, validate_readiness_snapshot_against_sources
from .source_ledger import SourceResolutionLedger
from .dataset_provenance import DatasetProvenanceStatus
from .test_contract import DatasetRole
from .holdout_factory import HoldoutFactoryResult
from .trust_anchor import TrustAnchorError, verify_signed_evidence
from .trust_audit import TrustAuditError, append_verification_audit


class ForwardSessionError(ValueError):
    """Raised when a demo forward-validation session cannot be frozen."""


@dataclass(frozen=True)
class DemoForwardSession:
    session_revision: str
    session_id: str
    lifecycle_state: str
    gate_evidence: str
    gate_fingerprint: str
    handoff_fingerprint: str
    strategy_id: str
    strategy_revision: str
    manifest_revision: str
    execution_semantics: str
    holdout_dataset_id: str
    holdout_dataset_artifact_id: str
    holdout_dataset_content_sha256: str
    forward_dataset_id: str
    forward_dataset_artifact_id: str
    forward_dataset_content_sha256: str
    post_holdout_tuning: bool
    production_decision: bool
    fingerprint: str
    readiness_snapshot_fingerprint: str | None = None
    readiness_snapshot: ReadinessSnapshot | None = None
    readiness_manifest: StrategyManifest | None = None
    readiness_passport: StrategyPassport | None = None
    readiness_ledger: SourceResolutionLedger | None = None
    holdout_result: HoldoutFactoryResult | None = None
    trust_envelope_path: str | None = None
    holdout_artifact_path: str | None = None
    source_event_ledger_prefix_sha256: str | None = None
    source_event_ledger_prefix_byte_size: int | None = None
    source_event_ledger_sequence_boundary: int | None = None
    source_event_ledger_prefix_source: str | None = None

    def _payload(self) -> dict[str, object]:
        return {
            "session_revision": self.session_revision,
            "session_id": self.session_id,
            "lifecycle_state": self.lifecycle_state,
            "gate_evidence": self.gate_evidence,
            "gate_fingerprint": self.gate_fingerprint,
            "handoff_fingerprint": self.handoff_fingerprint,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "manifest_revision": self.manifest_revision,
            "execution_semantics": self.execution_semantics,
            "holdout_dataset_id": self.holdout_dataset_id,
            "holdout_dataset_artifact_id": self.holdout_dataset_artifact_id,
            "holdout_dataset_content_sha256": self.holdout_dataset_content_sha256,
            "forward_dataset_id": self.forward_dataset_id,
            "forward_dataset_artifact_id": self.forward_dataset_artifact_id,
            "forward_dataset_content_sha256": self.forward_dataset_content_sha256,
            "post_holdout_tuning": self.post_holdout_tuning,
            "production_decision": self.production_decision,
            "readiness_snapshot_fingerprint": self.readiness_snapshot_fingerprint,
            "trust_envelope_path": self.trust_envelope_path,
            "holdout_artifact_path": self.holdout_artifact_path,
            "source_event_ledger_prefix_sha256": self.source_event_ledger_prefix_sha256,
            "source_event_ledger_prefix_byte_size": self.source_event_ledger_prefix_byte_size,
            "source_event_ledger_sequence_boundary": self.source_event_ledger_sequence_boundary,
            "source_event_ledger_prefix_source": self.source_event_ledger_prefix_source,
        }

    def validate(self) -> None:
        if not self.session_id or not self.strategy_id or not self.strategy_revision:
            raise ForwardSessionError("forward session identity is incomplete")
        if self.lifecycle_state != "PREPARED":
            raise ForwardSessionError("forward session lifecycle must be PREPARED")
        if not self.strategy_id or not self.strategy_revision:
            raise ForwardSessionError("forward session identity is incomplete")
        if not self.manifest_revision or not self.execution_semantics:
            raise ForwardSessionError("forward session contract is incomplete")
        if len(self.gate_fingerprint) != 64:
            raise ForwardSessionError("gate_fingerprint must be SHA-256")
        if len(self.handoff_fingerprint) != 64:
            raise ForwardSessionError("handoff_fingerprint must be SHA-256")
        if len(self.holdout_dataset_content_sha256) != 64:
            raise ForwardSessionError("holdout dataset SHA must be SHA-256")
        if len(self.forward_dataset_content_sha256) != 64:
            raise ForwardSessionError("forward dataset SHA must be SHA-256")
        if not self.holdout_dataset_id or not self.holdout_dataset_artifact_id:
            raise ForwardSessionError("holdout dataset identity is incomplete")
        if not self.forward_dataset_id or not self.forward_dataset_artifact_id:
            raise ForwardSessionError("forward dataset identity is incomplete")
        if self.post_holdout_tuning:
            raise ForwardSessionError("post-holdout tuning is forbidden in a frozen forward session")
        if self.production_decision:
            raise ForwardSessionError("forward session cannot authorize production decisions")
        expected = hashlib.sha256(
            json.dumps(self._payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest()
        if self.fingerprint != expected:
            raise ForwardSessionError("forward session fingerprint mismatch")

    def _validate_holdout_binding(self) -> None:
        """Revalidate the accepted Holdout result carried through gate/session."""
        holdout = self.holdout_result
        if holdout is None:
            raise ForwardSessionError(
                "forward session requires the completed HoldoutFactoryResult binding"
            )
        run_result = holdout.result
        run = run_result.run
        record = run_result.record
        provenance = run_result.dataset_provenance
        if not run_result.accepted or provenance.status is not DatasetProvenanceStatus.PASS:
            raise ForwardSessionError(
                "forward session requires an accepted Holdout result with PASS dataset provenance"
            )
        if (
            holdout.job.job_id != run_result.job_id
            or holdout.job.job_id != run.run_id
            or run.dataset_role != DatasetRole.FRESH_HOLDOUT.value
            or run.dataset_id != record.dataset_id
            or run.artifact_id != provenance.observed_artifact_id
            or provenance.dataset_id != run.dataset_id
            or provenance.registered_fingerprint != run.dataset_fingerprint
            or provenance.observed_fingerprint != run.dataset_fingerprint
            or provenance.registered_artifact_id != run.artifact_id
            or provenance.observed_artifact_id != run.artifact_id
            or record.snapshot_fingerprint != self.readiness_snapshot_fingerprint
            or record.strategy_id != self.strategy_id
            or record.strategy_revision != self.strategy_revision
            or record.manifest_revision != self.manifest_revision
            or record.execution_semantics != self.execution_semantics
            or record.dataset_id != self.holdout_dataset_id
            or run.artifact_id != self.holdout_dataset_artifact_id
            or holdout.holdout_dataset_content_sha256 != self.holdout_dataset_content_sha256
        ):
            raise ForwardSessionError(
                "carried Holdout result does not match the frozen forward session identity"
            )

    def validate_for_runtime(self, *, audit_phase: str | None = None) -> None:
        """Require independently recomputable source readiness and Holdout provenance."""
        self.validate()
        self._validate_holdout_binding()
        if not self.trust_envelope_path or not self.holdout_artifact_path:
            raise ForwardSessionError(
                "forward runtime requires a signed evidence envelope and the actual Holdout artifact path"
            )
        expected_bindings = {
            "source_event_ledger_prefix_sha256": self.source_event_ledger_prefix_sha256,
            "source_event_ledger_prefix_byte_size": self.source_event_ledger_prefix_byte_size,
            "source_event_ledger_sequence_boundary": self.source_event_ledger_sequence_boundary,
            "source_event_ledger_prefix_source": self.source_event_ledger_prefix_source,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "manifest_revision": self.manifest_revision,
            "execution_semantics": self.execution_semantics,
            "readiness_snapshot_fingerprint": self.readiness_snapshot_fingerprint,
            "holdout_dataset_id": self.holdout_dataset_id,
            "holdout_artifact_id": self.holdout_dataset_artifact_id,
            "holdout_dataset_role": "FRESH_HOLDOUT",
            "forward_session_id": self.session_id,
            "holdout_run_id": self.holdout_result.result.run.run_id,
            "holdout_run_fingerprint": self.holdout_result.result.record.run_fingerprint,
            "holdout_evidence_id": self.holdout_result.result.record.evidence_id,
            "holdout_evidence_fingerprint": self.holdout_result.result.record.evidence_fingerprint,
            "holdout_audit_fingerprint": self.holdout_result.result.record.audit_fingerprint,
            "holdout_record_fingerprint": self.holdout_result.result.record.fingerprint,
            "holdout_dataset_fingerprint": self.holdout_result.result.run.dataset_fingerprint,
            "holdout_artifact_byte_size": Path(self.holdout_artifact_path).stat().st_size,
        }
        try:
            verification = verify_signed_evidence(
                Path(self.trust_envelope_path),
                expected_bindings=expected_bindings,
                artifact_path=Path(self.holdout_artifact_path),
            )
            if audit_phase is not None:
                append_verification_audit(
                    phase=audit_phase,
                    session_id=self.session_id,
                    envelope_path=Path(self.trust_envelope_path),
                    artifact_path=Path(self.holdout_artifact_path),
                    verification=verification,
                )
        except (TrustAnchorError, TrustAuditError) as exc:
            raise ForwardSessionError(
                f"forward runtime signed evidence verification/audit failed: {exc}"
            ) from exc
        if (
            self.readiness_snapshot is None
            or self.readiness_manifest is None
            or self.readiness_passport is None
            or self.readiness_ledger is None
        ):
            raise ForwardSessionError(
                "forward runtime requires authoritative readiness snapshot, Manifest, Passport, and Source Ledger"
            )
        if self.readiness_snapshot.fingerprint != self.readiness_snapshot_fingerprint:
            raise ForwardSessionError(
                "forward session readiness snapshot fingerprint mismatch"
            )
        try:
            validate_readiness_snapshot_against_sources(
                self.readiness_snapshot,
                self.readiness_manifest,
                self.readiness_passport,
                self.readiness_ledger,
            )
        except ValueError as exc:
            raise ForwardSessionError(
                "forward session readiness snapshot does not match source inputs"
            ) from exc
        readiness = self.readiness_snapshot.source_readiness
        eligibility = self.readiness_snapshot.passport_eligibility
        if (
            readiness.get("status") != "PASS"
            or readiness.get("frozen_geometry_blocked") is not False
            or readiness.get("canonical_strategy_eligible") is not True
            or eligibility.get("source_status") != "PASS"
            or eligibility.get("frozen_geometry") != "READY"
            or eligibility.get("canonical_strategy") != "ELIGIBLE"
        ):
            raise ForwardSessionError(
                "forward runtime requires source PASS, unblocked frozen geometry, and canonical eligibility"
            )
        if (
            self.readiness_manifest.strategy_id != self.strategy_id
            or self.readiness_manifest.revision != self.manifest_revision
            or self.readiness_passport.strategy_id != self.strategy_id
        ):
            raise ForwardSessionError(
                "forward runtime readiness sources do not match the frozen session identity"
            )

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {**self._payload(), "fingerprint": self.fingerprint}


@dataclass(frozen=True)
class DemoForwardSessionResult:
    session: DemoForwardSession

    @property
    def ready(self) -> bool:
        return True


class DemoForwardSessionFactory:
    """Freeze a gated demo-forward contract without executing it."""

    def prepare(
        self,
        *,
        gate: ForwardGateResult,
        source_record: ResearchRecord,
        session_id: str,
        forward_dataset_id: str,
        forward_dataset_artifact_id: str,
        forward_dataset_content_sha256: str,
        post_holdout_tuning: bool = False,
        session_revision: str = "DEMO-FORWARD-SESSION-1",
        trust_envelope_path: str | None = None,
        holdout_artifact_path: str | None = None,
    ) -> DemoForwardSessionResult:
        source_record.validate()

        if gate.gate.status is not GateStatus.PASS:
            raise ForwardSessionError("Demo forward session requires Forward Gate PASS")
        if gate.holdout_result is None:
            raise ForwardSessionError(
                "Demo forward session requires the completed HoldoutFactoryResult binding"
            )

        if gate.gate.name != "FRESH_HOLDOUT_TO_FORWARD":
            raise ForwardSessionError("Demo forward session requires the Fresh Holdout-to-Forward gate")

        if not session_id:
            raise ForwardSessionError("session_id is required")
        if not forward_dataset_id or not forward_dataset_artifact_id:
            raise ForwardSessionError("forward dataset identity is required")
        if (
            not isinstance(forward_dataset_content_sha256, str)
            or len(forward_dataset_content_sha256) != 64
            or any(char not in "0123456789abcdef" for char in forward_dataset_content_sha256)
        ):
            raise ForwardSessionError(
                "forward dataset SHA must be a lowercase hexadecimal SHA-256"
            )
        if post_holdout_tuning:
            raise ForwardSessionError("post-holdout tuning is forbidden")

        details = gate.gate.details
        if details.get("source_station") != "holdout" or details.get("destination_station") != "forward":
            raise ForwardSessionError("Forward Gate route is not Fresh Holdout-to-Forward")
        if details.get("production_decision") is not False:
            raise ForwardSessionError("Forward Gate does not prove a non-production boundary")
        handoff_fingerprint = str(details.get("handoff_fingerprint", ""))
        if (
            len(handoff_fingerprint) != 64
            or any(char not in "0123456789abcdef" for char in handoff_fingerprint)
        ):
            raise ForwardSessionError("Forward Gate lacks a valid Holdout handoff fingerprint")
        if details.get("strategy_revision") != source_record.strategy_revision:
            raise ForwardSessionError("Forward Gate strategy revision does not match Holdout record")
        if details.get("manifest_revision") != source_record.manifest_revision:
            raise ForwardSessionError("Forward Gate manifest revision does not match Holdout record")
        if details.get("holdout_dataset_id") != source_record.dataset_id:
            raise ForwardSessionError("Forward Gate Holdout dataset does not match source record")

        ledger_prefix_sha = details.get("source_event_ledger_prefix_sha256")
        ledger_prefix_size = details.get("source_event_ledger_prefix_byte_size")
        ledger_sequence_boundary = details.get("source_event_ledger_sequence_boundary")
        ledger_prefix_source = details.get("source_event_ledger_prefix_source")
        if (
            not isinstance(ledger_prefix_sha, str)
            or len(ledger_prefix_sha) != 64
            or any(char not in "0123456789abcdef" for char in ledger_prefix_sha)
            or not isinstance(ledger_prefix_size, int)
            or ledger_prefix_size < 0
            or not isinstance(ledger_sequence_boundary, int)
            or ledger_sequence_boundary < 0
            or ledger_prefix_source not in {"persisted_jsonl", "in_memory"}
        ):
            raise ForwardSessionError("Forward Gate lacks a valid signed source event-ledger boundary")

        holdout_sha = str(details.get("holdout_dataset_sha256", ""))
        holdout_artifact_id = str(details.get("holdout_artifact_id", ""))
        if (
            len(holdout_sha) != 64
            or any(char not in "0123456789abcdef" for char in holdout_sha)
            or not holdout_artifact_id
        ):
            raise ForwardSessionError("Forward Gate lacks complete Holdout dataset identity")

        # Reject Holdout reuse before comparing requested Forward identity with
        # the gate, so the failure explains the actual provenance violation.
        if forward_dataset_id == source_record.dataset_id:
            raise ForwardSessionError("forward dataset must differ from Holdout dataset")
        if forward_dataset_artifact_id == holdout_artifact_id:
            raise ForwardSessionError("forward artifact must differ from Holdout artifact")
        if forward_dataset_content_sha256 == holdout_sha:
            raise ForwardSessionError("forward dataset must differ from Holdout dataset")

        if details.get("forward_session_id") != session_id:
            raise ForwardSessionError("Forward Gate session id does not match requested session")
        if details.get("forward_dataset_id") != forward_dataset_id:
            raise ForwardSessionError("Forward Gate dataset id does not match requested Forward dataset")
        if details.get("forward_artifact_id") != forward_dataset_artifact_id:
            raise ForwardSessionError("Forward Gate artifact id does not match requested Forward artifact")
        if details.get("forward_dataset_sha256") != forward_dataset_content_sha256:
            raise ForwardSessionError("Forward Gate dataset SHA does not match requested Forward dataset")

        draft = DemoForwardSession(
            session_revision=session_revision,
            session_id=session_id,
            lifecycle_state="PREPARED",
            gate_evidence=gate.gate.evidence,
            gate_fingerprint=_fingerprint_gate(gate),
            handoff_fingerprint=handoff_fingerprint,
            strategy_id=source_record.strategy_id,
            strategy_revision=source_record.strategy_revision,
            manifest_revision=source_record.manifest_revision,
            execution_semantics=source_record.execution_semantics,
            holdout_dataset_id=source_record.dataset_id,
            holdout_dataset_artifact_id=holdout_artifact_id,
            holdout_dataset_content_sha256=holdout_sha,
            forward_dataset_id=forward_dataset_id,
            forward_dataset_artifact_id=forward_dataset_artifact_id,
            forward_dataset_content_sha256=forward_dataset_content_sha256,
            post_holdout_tuning=False,
            production_decision=False,
            fingerprint="",
            readiness_snapshot_fingerprint=(
                gate.readiness_snapshot.fingerprint
                if gate.readiness_snapshot is not None
                else None
            ),
            readiness_snapshot=gate.readiness_snapshot,
            readiness_manifest=gate.readiness_manifest,
            readiness_passport=gate.readiness_passport,
            readiness_ledger=gate.readiness_ledger,
            holdout_result=gate.holdout_result,
            trust_envelope_path=trust_envelope_path,
            holdout_artifact_path=holdout_artifact_path,
            source_event_ledger_prefix_sha256=ledger_prefix_sha,
            source_event_ledger_prefix_byte_size=ledger_prefix_size,
            source_event_ledger_sequence_boundary=ledger_sequence_boundary,
            source_event_ledger_prefix_source=ledger_prefix_source,
        )
        fingerprint = hashlib.sha256(
            json.dumps(draft._payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest()
        session = DemoForwardSession(
            **{
                **draft._payload(),
                "fingerprint": fingerprint,
                "readiness_snapshot": draft.readiness_snapshot,
                "readiness_manifest": draft.readiness_manifest,
                "readiness_passport": draft.readiness_passport,
                "readiness_ledger": draft.readiness_ledger,
                "holdout_result": draft.holdout_result,
                "trust_envelope_path": draft.trust_envelope_path,
                "holdout_artifact_path": draft.holdout_artifact_path,
            }
        )
        session.validate()
        return DemoForwardSessionResult(session=session)


def _fingerprint_gate(gate: ForwardGateResult) -> str:
    payload = {
        "name": gate.gate.name,
        "status": gate.gate.status.value,
        "evidence": gate.gate.evidence,
        "details": gate.gate.details,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()
