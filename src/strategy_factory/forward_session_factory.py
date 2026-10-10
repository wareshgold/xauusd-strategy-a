from __future__ import annotations

"""Research-only contract for entering a demo forward-validation session.

This module binds an already-PASSed Fresh Holdout -> Forward gate to an
immutable session identity. It does not run a strategy, generate BUY/SELL
decisions, place orders, or modify the existing MT5 forward runner.
"""

from dataclasses import dataclass
import hashlib
import json

from .forward_gate_factory import ForwardGateResult
from .models import GateStatus
from .research_record import ResearchRecord


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
    ) -> DemoForwardSessionResult:
        source_record.validate()

        if gate.gate.status is not GateStatus.PASS:
            raise ForwardSessionError("Demo forward session requires Forward Gate PASS")

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
        if details.get("production_decision") is not False:
            raise ForwardSessionError("Forward Gate does not prove a non-production boundary")
        handoff_fingerprint = str(details.get("handoff_fingerprint", ""))
        if len(handoff_fingerprint) != 64:
            raise ForwardSessionError("Forward Gate lacks Holdout handoff fingerprint")
        if details.get("strategy_revision") != source_record.strategy_revision:
            raise ForwardSessionError("Forward Gate strategy revision does not match Holdout record")
        if details.get("manifest_revision") != source_record.manifest_revision:
            raise ForwardSessionError("Forward Gate manifest revision does not match Holdout record")
        if details.get("holdout_dataset_id") != source_record.dataset_id:
            raise ForwardSessionError("Forward Gate Holdout dataset does not match source record")

        if details.get("forward_session_id") != session_id:
            raise ForwardSessionError("Forward Gate session id does not match requested session")
        if details.get("forward_dataset_id") != forward_dataset_id:
            raise ForwardSessionError("Forward Gate dataset id does not match requested Forward dataset")
        if details.get("forward_artifact_id") != forward_dataset_artifact_id:
            raise ForwardSessionError("Forward Gate artifact id does not match requested Forward artifact")
        if details.get("forward_dataset_sha256") != forward_dataset_content_sha256:
            raise ForwardSessionError("Forward Gate dataset SHA does not match requested Forward dataset")

        holdout_sha = str(details.get("holdout_dataset_sha256", ""))
        holdout_artifact_id = str(details.get("holdout_artifact_id", ""))
        if len(holdout_sha) != 64 or not holdout_artifact_id:
            raise ForwardSessionError("Forward Gate lacks complete Holdout dataset identity")

        if forward_dataset_id == source_record.dataset_id:
            raise ForwardSessionError("forward dataset must differ from Holdout dataset")
        if forward_dataset_artifact_id == holdout_artifact_id:
            raise ForwardSessionError("forward artifact must differ from Holdout artifact")
        if forward_dataset_content_sha256 == holdout_sha:
            raise ForwardSessionError("forward dataset must differ from Holdout dataset")

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
        )
        fingerprint = hashlib.sha256(
            json.dumps(draft._payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest()
        session = DemoForwardSession(**{**draft._payload(), "fingerprint": fingerprint})
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
