from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class DatasetRole(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    UNTOUCHED_VALIDATION = "UNTOUCHED_VALIDATION"
    FRESH_HOLDOUT = "FRESH_HOLDOUT"


class ExecutionSemantics(str, Enum):
    BAR_CLOSE_RESEARCH = "BAR_CLOSE_RESEARCH"
    TICK_FEASIBLE = "TICK_FEASIBLE"


class ContractViolation(ValueError):
    """Raised when a historical test contract is internally invalid."""


@dataclass(frozen=True)
class TestDataset:
    dataset_id: str
    role: DatasetRole
    data_revision: str
    start: str
    end: str
    source: str
    immutable: bool = False

    def validate(self) -> None:
        if not self.dataset_id or not self.data_revision or not self.source:
            raise ContractViolation("dataset identity, revision, and source are required")
        if self.start >= self.end:
            raise ContractViolation("dataset start must precede dataset end")
        if self.role in (DatasetRole.UNTOUCHED_VALIDATION, DatasetRole.FRESH_HOLDOUT):
            if not self.immutable:
                raise ContractViolation(
                    f"{self.role.value} dataset must be immutable"
                )


@dataclass(frozen=True)
class HistoricalTestSpec:
    test_id: str
    strategy_id: str
    strategy_revision: str
    dataset: TestDataset
    execution_semantics: ExecutionSemantics
    parameters: Mapping[str, Any] = field(default_factory=dict)
    objective: str = "DESCRIPTIVE_METRICS_ONLY"

    def validate(self) -> None:
        if not self.test_id or not self.strategy_id or not self.strategy_revision:
            raise ContractViolation("test and strategy identity are required")
        self.dataset.validate()
        if self.objective == "":
            raise ContractViolation("objective must be explicit")

    @property
    def is_holdout(self) -> bool:
        return self.dataset.role is DatasetRole.FRESH_HOLDOUT

    def as_dict(self) -> dict[str, Any]:
        return {
            "test_id": self.test_id,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "dataset": {
                "dataset_id": self.dataset.dataset_id,
                "role": self.dataset.role.value,
                "data_revision": self.dataset.data_revision,
                "start": self.dataset.start,
                "end": self.dataset.end,
                "source": self.dataset.source,
                "immutable": self.dataset.immutable,
            },
            "execution_semantics": self.execution_semantics.value,
            "parameters": dict(self.parameters),
            "objective": self.objective,
        }


def validate_test_spec(spec: HistoricalTestSpec) -> HistoricalTestSpec:
    spec.validate()
    return spec
