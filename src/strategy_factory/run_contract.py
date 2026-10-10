"""Deterministic identity contract for Strategy Factory runs.

This module only tracks orchestration identity. It does not define
strategy geometry, execution rules, or production authority.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class FactoryRunContract:
    run_id: str
    git_sha: str
    dataset_identity: str
    strategy_revision: str
    created_at: str

    @classmethod
    def create(
        cls,
        run_id: str,
        git_sha: str,
        dataset_identity: str,
        strategy_revision: str,
    ) -> "FactoryRunContract":
        return cls(
            run_id=run_id,
            git_sha=git_sha,
            dataset_identity=dataset_identity,
            strategy_revision=strategy_revision,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
