from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Stage(str, Enum):
    STRATEGY_LAB = "1_STRATEGY_LAB"
    STRATEGY_ENGINE = "2_STRATEGY_ENGINE"
    TEST_FACTORY = "3_TEST_FACTORY"
    OPTIMIZATION = "3B_OPTIMIZATION"
    FORWARD_VALIDATION = "4_FORWARD_VALIDATION"
    PRODUCTION = "PRODUCTION"


class GateStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"


@dataclass(frozen=True)
class GateResult:
    name: str
    status: GateStatus
    evidence: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StrategyPassport:
    strategy_id: str
    source_revision: str
    geometry_revision: str
    code_revision: str
    data_revision: str
    execution_model: str
    parameter_set: dict[str, Any]
    canonical: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "source_revision": self.source_revision,
            "geometry_revision": self.geometry_revision,
            "code_revision": self.code_revision,
            "data_revision": self.data_revision,
            "execution_model": self.execution_model,
            "parameter_set": self.parameter_set,
            "canonical": self.canonical,
        }
