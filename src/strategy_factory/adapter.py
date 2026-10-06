from __future__ import annotations

from typing import Any, Mapping, Protocol

from .execution import ExecutionContractError, ExecutionReceipt
from .metrics import ResearchMetrics
from .test_contract import ExecutionSemantics, HistoricalTestSpec


class ExecutionAdapter(Protocol):
    """Portable boundary between an execution engine and the Factory.

    Implementations may run locally, on a VPS, or in a CI/cloud worker.
    They must not define strategy geometry or silently change test semantics.
    """

    engine_revision: str

    def execute(self, spec: HistoricalTestSpec) -> ExecutionReceipt:
        ...


class ExecutionAdapterError(ExecutionContractError):
    """Raised when an execution adapter output cannot be accepted."""


def build_execution_receipt(
    *,
    execution_id: str,
    spec: HistoricalTestSpec,
    engine_revision: str,
    input_fingerprint: str,
    metrics: ResearchMetrics,
    completed: bool = True,
) -> ExecutionReceipt:
    """Convert a completed engine result into the canonical Factory receipt."""
    spec.validate()
    receipt = ExecutionReceipt(
        execution_id=execution_id,
        test_id=spec.test_id,
        strategy_revision=spec.strategy_revision,
        execution_semantics=spec.execution_semantics,
        engine_revision=engine_revision,
        input_fingerprint=input_fingerprint,
        completed=completed,
        metrics=metrics,
    )
    receipt.validate()
    return receipt


def validate_adapter_output(
    *,
    spec: HistoricalTestSpec,
    receipt: ExecutionReceipt,
) -> None:
    """Require adapter output to preserve the test specification exactly."""
    spec.validate()
    receipt.validate()

    if receipt.test_id != spec.test_id:
        raise ExecutionAdapterError(
            "adapter output test_id does not match test specification"
        )
    if receipt.strategy_revision != spec.strategy_revision:
        raise ExecutionAdapterError(
            "adapter output strategy_revision does not match test specification"
        )
    if receipt.execution_semantics is not spec.execution_semantics:
        raise ExecutionAdapterError(
            "adapter output execution semantics do not match test specification"
        )


def adapter_semantics(
    spec: HistoricalTestSpec,
) -> ExecutionSemantics:
    """Return the execution semantics the adapter is required to preserve."""
    spec.validate()
    return spec.execution_semantics
