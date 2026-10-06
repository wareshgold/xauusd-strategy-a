from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .adapter import build_execution_receipt
from .execution import ExecutionReceipt
from .metrics import ResearchMetrics
from .test_contract import ExecutionSemantics, HistoricalTestSpec


class SyntheticExecutionError(ValueError):
    """Raised when a controlled synthetic execution cannot be produced."""


def _canonical(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as exc:
        raise SyntheticExecutionError("synthetic execution inputs must be JSON-serializable") from exc


@dataclass(frozen=True)
class SyntheticExecutionFixture:
    """Controlled execution outcome for infrastructure tests only."""

    fixture_id: str
    execution_semantics: ExecutionSemantics
    metrics: ResearchMetrics

    def validate(self) -> None:
        if not self.fixture_id:
            raise SyntheticExecutionError("fixture_id is required")
        if not isinstance(self.execution_semantics, ExecutionSemantics):
            raise SyntheticExecutionError("fixture execution_semantics must be explicit")
        self.metrics.validate()

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "fixture_id": self.fixture_id,
            "execution_semantics": self.execution_semantics.value,
            "metrics": self.metrics.as_dict(),
        }


class SyntheticExecutionAdapter:
    """Deterministic adapter backed by one controlled synthetic fixture."""

    def __init__(
        self,
        fixture: SyntheticExecutionFixture,
        *,
        engine_revision: str = "SYNTHETIC-ENGINE-V1",
    ) -> None:
        fixture.validate()
        if not engine_revision:
            raise SyntheticExecutionError("engine_revision is required")
        self.fixture = fixture
        self.engine_revision = engine_revision

    def _identity(self, spec: HistoricalTestSpec) -> dict[str, Any]:
        spec.validate()
        return {
            "fixture": self.fixture.as_dict(),
            "engine_revision": self.engine_revision,
            "test_id": spec.test_id,
            "strategy_id": spec.strategy_id,
            "strategy_revision": spec.strategy_revision,
            "dataset_id": spec.dataset.dataset_id,
            "data_revision": spec.dataset.data_revision,
            "dataset_range": [spec.dataset.start, spec.dataset.end],
            "dataset_source": spec.dataset.source,
            "execution_semantics": spec.execution_semantics.value,
            "parameters": dict(spec.parameters),
            "objective": spec.objective,
        }

    def execute(self, spec: HistoricalTestSpec) -> ExecutionReceipt:
        spec.validate()
        if spec.execution_semantics is not self.fixture.execution_semantics:
            raise SyntheticExecutionError(
                "synthetic fixture execution semantics do not match test specification"
            )

        identity = _canonical(self._identity(spec))
        digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()

        return build_execution_receipt(
            execution_id=f"SYNTH-{digest[:16]}",
            spec=spec,
            engine_revision=self.engine_revision,
            input_fingerprint=digest,
            metrics=self.fixture.metrics,
        )
