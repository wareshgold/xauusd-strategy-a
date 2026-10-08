from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .external_strategy import ExternalStrategyError, ExternalStrategyReference
from .metrics import ResearchMetrics
from .test_contract import ExecutionSemantics, TestDataset


class StrategyComparisonError(ValueError):
    """Raised when a 1v1 strategy comparison is not provenance-compatible."""


@dataclass(frozen=True)
class ComparisonMetrics:
    """Descriptive metrics intentionally excluding canonical R conclusions."""

    trades: int
    decisive_trades: int
    wins: int
    losses: int
    ambiguous: int
    win_rate: float
    profit_factor: float | None

    @classmethod
    def from_research_metrics(cls, metrics: ResearchMetrics) -> "ComparisonMetrics":
        metrics.validate()
        return cls(
            trades=metrics.trades,
            decisive_trades=metrics.decisive_trades,
            wins=metrics.wins,
            losses=metrics.losses,
            ambiguous=metrics.ambiguous,
            win_rate=metrics.win_rate,
            profit_factor=metrics.profit_factor,
        )

    def validate(self) -> None:
        counts = (self.trades, self.decisive_trades, self.wins, self.losses, self.ambiguous)
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in counts):
            raise StrategyComparisonError("comparison counts must be non-negative integers")
        if self.wins + self.losses != self.decisive_trades:
            raise StrategyComparisonError("wins + losses must equal decisive_trades")
        if self.decisive_trades + self.ambiguous != self.trades:
            raise StrategyComparisonError("decisive_trades + ambiguous must equal trades")
        if not 0.0 <= self.win_rate <= 1.0:
            raise StrategyComparisonError("win_rate must be between 0 and 1")
        if self.profit_factor is not None and self.profit_factor < 0:
            raise StrategyComparisonError("profit_factor cannot be negative")

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "trades": self.trades,
            "decisive_trades": self.decisive_trades,
            "wins": self.wins,
            "losses": self.losses,
            "ambiguous": self.ambiguous,
            "win_rate": self.win_rate,
            "profit_factor": self.profit_factor,
        }


@dataclass(frozen=True)
class StrategyComparisonParticipant:
    strategy_id: str
    strategy_revision: str
    metrics: ComparisonMetrics
    external_reference: ExternalStrategyReference | None = None

    def validate(self) -> None:
        if not self.strategy_id or not self.strategy_revision:
            raise StrategyComparisonError("strategy identity is required")
        self.metrics.validate()
        if self.external_reference is not None:
            self.external_reference.validate()
            if self.external_reference.strategy_id != self.strategy_id:
                raise StrategyComparisonError(
                    "external reference strategy_id does not match participant"
                )

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "metrics": self.metrics.as_dict(),
            "external_reference": (
                None if self.external_reference is None
                else self.external_reference.as_dict()
            ),
        }


@dataclass(frozen=True)
class OneVsOneStrategyComparison:
    """Immutable 1v1 report. It describes differences but never picks a winner."""

    comparison_revision: str
    dataset: TestDataset
    execution_semantics: ExecutionSemantics
    baseline: StrategyComparisonParticipant
    challenger: StrategyComparisonParticipant
    metric_deltas: dict[str, float | None]
    fingerprint: str

    @staticmethod
    def _payload(value: dict[str, Any]) -> bytes:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")

    def _fingerprint_payload(self) -> dict[str, Any]:
        return {
            "comparison_revision": self.comparison_revision,
            "dataset": {\n                "dataset_id": self.dataset.dataset_id,\n                "role": self.dataset.role.value,\n                "data_revision": self.dataset.data_revision,\n                "start": self.dataset.start,\n                "end": self.dataset.end,\n                "source": self.dataset.source,\n                "immutable": self.dataset.immutable,\n            },
            "execution_semantics": self.execution_semantics.value,
            "baseline": self.baseline.as_dict(),
            "challenger": self.challenger.as_dict(),
            "metric_deltas": dict(self.metric_deltas),
        }

    def validate(self) -> None:
        self.dataset.validate()
        if not isinstance(self.execution_semantics, ExecutionSemantics):
            raise StrategyComparisonError("execution semantics must be explicit")
        self.baseline.validate()
        self.challenger.validate()
        if self.baseline.strategy_id == self.challenger.strategy_id:
            raise StrategyComparisonError("1v1 participants must be distinct")
        expected = hashlib.sha256(self._payload(self._fingerprint_payload())).hexdigest()
        if self.fingerprint != expected:
            raise StrategyComparisonError("strategy comparison fingerprint mismatch")

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            **self._fingerprint_payload(),
            "fingerprint": self.fingerprint,
            "decision": "DESCRIPTIVE_ONLY",
            "winner": None,
            "production_eligible": False,
        }


def build_one_vs_one_comparison(
    *,
    dataset: TestDataset,
    execution_semantics: ExecutionSemantics,
    baseline: StrategyComparisonParticipant,
    challenger: StrategyComparisonParticipant,
    comparison_revision: str = "STRATEGY-1V1-COMPARISON-1",
) -> OneVsOneStrategyComparison:
    dataset.validate()
    if not isinstance(execution_semantics, ExecutionSemantics):
        raise StrategyComparisonError("execution semantics must be explicit")
    baseline.validate()
    challenger.validate()
    if baseline.strategy_id == challenger.strategy_id:
        raise StrategyComparisonError("1v1 participants must be distinct")

    b = baseline.metrics
    c = challenger.metrics
    deltas = {
        "trades": float(c.trades - b.trades),
        "decisive_trades": float(c.decisive_trades - b.decisive_trades),
        "wins": float(c.wins - b.wins),
        "losses": float(c.losses - b.losses),
        "ambiguous": float(c.ambiguous - b.ambiguous),
        "win_rate": c.win_rate - b.win_rate,
        "profit_factor": (
            None
            if b.profit_factor is None or c.profit_factor is None
            else c.profit_factor - b.profit_factor
        ),
    }

    draft = OneVsOneStrategyComparison(
        comparison_revision=comparison_revision,
        dataset=dataset,
        execution_semantics=execution_semantics,
        baseline=baseline,
        challenger=challenger,
        metric_deltas=deltas,
        fingerprint="",
    )
    fingerprint = hashlib.sha256(
        draft._payload(draft._fingerprint_payload())
    ).hexdigest()
    return OneVsOneStrategyComparison(
        comparison_revision=draft.comparison_revision,
        dataset=draft.dataset,
        execution_semantics=draft.execution_semantics,
        baseline=draft.baseline,
        challenger=draft.challenger,
        metric_deltas=draft.metric_deltas,
        fingerprint=fingerprint,
    )
