from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .metrics import ResearchMetrics
from .runs import ResearchRunError, ResearchRunIdentity
from .test_contract import ExecutionSemantics, HistoricalTestSpec


class ExecutionContractError(ValueError):
    """Raised when a historical execution receipt is invalid."""


@dataclass(frozen=True)
class ExecutionArtifact:
    """A local artifact produced by an execution and independently observed by the Runner."""

    artifact_id: str
    artifact_role: str
    local_path: str
    content_sha256: str
    byte_size: int

    def validate(self) -> None:
        if not all(isinstance(value, str) and value for value in (
            self.artifact_id, self.artifact_role, self.local_path
        )):
            raise ExecutionContractError("execution output artifact identity is incomplete")
        if (not isinstance(self.content_sha256, str) or len(self.content_sha256) != 64 or
                any(ch not in "0123456789abcdef" for ch in self.content_sha256)):
            raise ExecutionContractError("execution output artifact SHA-256 is invalid")
        if isinstance(self.byte_size, bool) or not isinstance(self.byte_size, int) or self.byte_size < 0:
            raise ExecutionContractError("execution output artifact byte size is invalid")

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "artifact_id": self.artifact_id,
            "artifact_role": self.artifact_role,
            "local_path": self.local_path,
            "content_sha256": self.content_sha256,
            "byte_size": self.byte_size,
        }


@dataclass(frozen=True)
class ExecutionReceipt:
    """Immutable declaration of how one historical test was actually executed.

    This is a contract boundary, not an execution engine. It records the
    execution semantics claimed by the adapter so downstream evidence cannot
    silently relabel BAR_CLOSE_RESEARCH as TICK_FEASIBLE (or vice versa).
    """

    execution_id: str
    test_id: str
    strategy_revision: str
    execution_semantics: ExecutionSemantics
    engine_revision: str
    input_fingerprint: str
    completed: bool
    metrics: ResearchMetrics
    receipt_schema_version: int = 1
    dataset_content_sha256: str | None = None
    output_artifact: ExecutionArtifact | None = None
    input_artifacts: tuple[ExecutionArtifact, ...] = ()

    def validate(self) -> None:
        required = (
            self.execution_id,
            self.test_id,
            self.strategy_revision,
            self.engine_revision,
            self.input_fingerprint,
        )
        if any(not value for value in required):
            raise ExecutionContractError("execution receipt identity is incomplete")
        if not isinstance(self.execution_semantics, ExecutionSemantics):
            raise ExecutionContractError("execution_semantics must be explicit")
        if isinstance(self.receipt_schema_version, bool) or not isinstance(self.receipt_schema_version, int) or self.receipt_schema_version not in {1, 2, 3}:
            raise ExecutionContractError("receipt_schema_version must be 1, 2, or 3")
        if self.receipt_schema_version == 1 and self.dataset_content_sha256 is not None:
            raise ExecutionContractError("legacy receipt schema v1 cannot carry dataset_content_sha256")
        if self.receipt_schema_version in {2, 3} and self.dataset_content_sha256 is not None:
            digest = self.dataset_content_sha256
            if not isinstance(digest, str) or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
                raise ExecutionContractError("dataset_content_sha256 must be a lowercase SHA-256 hex digest or null")
        if self.receipt_schema_version == 2 and self.output_artifact is not None:
            raise ExecutionContractError("receipt schema v2 cannot carry output_artifact")
        if self.receipt_schema_version == 3:
            if self.dataset_content_sha256 is None:
                raise ExecutionContractError("receipt schema v3 requires dataset_content_sha256")
            if self.output_artifact is None:
                raise ExecutionContractError("receipt schema v3 requires output_artifact")
        if not isinstance(self.input_artifacts, tuple):
            raise ExecutionContractError("execution input_artifacts must be an immutable tuple")
        if self.receipt_schema_version == 2 and self.input_artifacts:
            raise ExecutionContractError("receipt schema v2 cannot carry input_artifacts")
        for artifact in self.input_artifacts:
            if not isinstance(artifact, ExecutionArtifact):
                raise ExecutionContractError("execution input artifact must use the typed artifact contract")
            artifact.validate()
        if len({artifact.artifact_id for artifact in self.input_artifacts}) != len(self.input_artifacts):
            raise ExecutionContractError("execution input artifact IDs must be unique")
        if self.output_artifact is not None:
            if not isinstance(self.output_artifact, ExecutionArtifact):
                raise ExecutionContractError("execution output artifact must use the typed artifact contract")
            self.output_artifact.validate()
        if not self.completed:
            raise ExecutionContractError("incomplete execution cannot produce accepted evidence")
        self.metrics.validate()

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        payload = {
            "execution_id": self.execution_id,
            "test_id": self.test_id,
            "strategy_revision": self.strategy_revision,
            "execution_semantics": self.execution_semantics.value,
            "engine_revision": self.engine_revision,
            "input_fingerprint": self.input_fingerprint,
            "completed": self.completed,
            "metrics": self.metrics.as_dict(),
            "receipt_schema_version": self.receipt_schema_version,
        }
        if self.receipt_schema_version in {2, 3}:
            payload["dataset_content_sha256"] = self.dataset_content_sha256
        if self.receipt_schema_version == 3:
            payload["output_artifact"] = self.output_artifact.as_dict()
            payload["input_artifacts"] = [artifact.as_dict() for artifact in self.input_artifacts]
        return payload


def validate_execution_binding(
    *,
    spec: HistoricalTestSpec,
    run: ResearchRunIdentity,
    receipt: ExecutionReceipt,
) -> None:
    """Require the receipt, test spec, and research run to agree exactly."""

    spec.validate()
    run.validate()
    receipt.validate()

    if receipt.test_id != spec.test_id:
        raise ExecutionContractError("execution test_id does not match test specification")
    if receipt.strategy_revision != spec.strategy_revision:
        raise ExecutionContractError("execution strategy_revision does not match test specification")
    if receipt.execution_semantics is not spec.execution_semantics:
        raise ExecutionContractError("execution semantics do not match test specification")
    if run.strategy_revision != spec.strategy_revision:
        raise ExecutionContractError("research run strategy_revision does not match test specification")
    if run.execution_semantics is not spec.execution_semantics:
        raise ExecutionContractError("research run execution semantics do not match test specification")


def execution_gate(
    *,
    spec: HistoricalTestSpec | None,
    run: ResearchRunIdentity | None,
    receipt: ExecutionReceipt | None,
) -> "GateResult":
    from .models import GateResult, GateStatus

    if spec is None or run is None or receipt is None:
        return GateResult(
            name="EXECUTION_CONTRACT",
            status=GateStatus.BLOCKED,
            evidence="Historical execution spec, research run, and execution receipt are required.",
            details={
                "spec_present": spec is not None,
                "run_present": run is not None,
                "receipt_present": receipt is not None,
            },
        )
    try:
        validate_execution_binding(spec=spec, run=run, receipt=receipt)
    except (ExecutionContractError, ResearchRunError, ValueError) as exc:
        return GateResult(
            name="EXECUTION_CONTRACT",
            status=GateStatus.FAIL,
            evidence="Historical execution does not match its declared contract.",
            details={"error": str(exc)},
        )
    return GateResult(
        name="EXECUTION_CONTRACT",
        status=GateStatus.PASS,
        evidence="Historical execution matches the declared execution semantics.",
        details={
            "test_id": spec.test_id,
            "execution_id": receipt.execution_id,
            "execution_semantics": receipt.execution_semantics.value,
        },
    )
