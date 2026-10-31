"""Persistent state helpers for Factory orchestration only."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FactoryRunState:
    run_id: str
    stages: dict[str, str] = field(default_factory=dict)
    workers: dict[str, str] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)

    def update_stage(self, stage: str, status: str) -> None:
        self.stages[stage] = status

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "stages": dict(self.stages),
            "workers": dict(self.workers),
            "artifacts": list(self.artifacts),
        }
