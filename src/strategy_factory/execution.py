from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .metrics import ResearchMetrics
from .runs import ResearchRunError, ResearchRunIdentity
from .test_contract import ExecutionSemantics, HistoricalTestSpec


class ExecutionContractError(ValueError):
    """Raised when a historical execution receipt is invalid."""


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
        if not self.completed:
            raise ExecutionContractError("incomplete execution cannot produce accepted evidence")
        self.metrics.validate()

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "execution_id": self.execution_id,
            "test_id": self.test_id,
            "strategy_revision": self.strategy_revision,
            "execution_semantics": self.execution_semantics.value,
            "engine_revision": self.engine_revision,
            "input_fingerprint": self.input_fingerprint,
            "completed": self.completed,
            "metrics": self.metrics.as_dict(),
        }


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
