from __future__ import annotations

"""Deterministic, development-only candidate matrix and descriptive ranking.

This module schedules explicitly declared research variants. It does not
define SP2L geometry, infer fills, select a canonical strategy, or authorize
production/forward execution. Optimization results are hypotheses only.
"""

from dataclasses import dataclass
from itertools import product
import hashlib
import json
import math
from typing import Any, Callable, Mapping

from .test_contract import DatasetRole, ExecutionSemantics, TestDataset


class CandidateLabError(ValueError):
    """Raised when a candidate search violates its declared research boundary."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _finite_number(value: float, name: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise CandidateLabError(f"{name} must be numeric")
    if not math.isfinite(float(value)):
        raise CandidateLabError(f"{name} must be finite")


@dataclass(frozen=True)
class CandidatePlan:
    """A frozen, finite candidate matrix on DEVELOPMENT data only."""

    plan_id: str
    strategy_family: str
    base_revision: str
    dataset: TestDataset
    dataset_content_sha256: str
    execution_semantics: ExecutionSemantics
    execution_fingerprint: str
    fixed_parameters: Mapping[str, Any]
    parameter_grid: Mapping[str, tuple[Any, ...]]
    geometry_fingerprint: str
    source_resolution_fingerprint: str
    max_candidates: int = 64

    def validate(self) -> None:
        self.dataset.validate()
        if self.dataset.role is not DatasetRole.DEVELOPMENT:
            raise CandidateLabError(
                "candidate optimization is allowed only on DEVELOPMENT data"
            )
        if not self.dataset.immutable:
            raise CandidateLabError(
                "candidate matrix requires an immutable development dataset"
            )
        if not all((self.plan_id, self.strategy_family, self.base_revision)):
            raise CandidateLabError("plan and strategy identity are required")
        if len(self.dataset_content_sha256) != 64:
            raise CandidateLabError("dataset content SHA-256 is required")
        if not self.execution_fingerprint:
            raise CandidateLabError("execution fingerprint is required")
        if not self.geometry_fingerprint or not self.source_resolution_fingerprint:
            raise CandidateLabError(
                "geometry and source-resolution fingerprints must be explicitly supplied"
            )
        if not isinstance(self.execution_semantics, ExecutionSemantics):
            raise CandidateLabError("execution semantics must be explicit")
        if not self.parameter_grid:
            raise CandidateLabError("at least one declared parameter dimension is required")
        if self.max_candidates < 1:
            raise CandidateLabError("max_candidates must be positive")
        keys = tuple(sorted(self.parameter_grid))
        if any(not isinstance(k, str) or not k for k in keys):
            raise CandidateLabError("parameter names must be non-empty strings")
        if set(keys) & set(self.fixed_parameters):
            raise CandidateLabError("a parameter cannot be both fixed and optimized")
        count = 1
        for key in keys:
            values = self.parameter_grid[key]
            if not values:
                raise CandidateLabError(f"parameter grid {key!r} cannot be empty")
            serialized = [_canonical_bytes(v) for v in values]
            if len(set(serialized)) != len(serialized):
                raise CandidateLabError(f"parameter grid {key!r} contains duplicates")
            count *= len(values)
        if count > self.max_candidates:
            raise CandidateLabError(
                f"candidate matrix has {count} variants; limit is {self.max_candidates}"
            )

    @property
    def fingerprint(self) -> str:
        self.validate()
        return _sha256({
            "plan_id": self.plan_id,
            "strategy_family": self.strategy_family,
            "base_revision": self.base_revision,
            "dataset": {
                "dataset_id": self.dataset.dataset_id,
                "role": self.dataset.role.value,
                "data_revision": self.dataset.data_revision,
                "start": self.dataset.start,
                "end": self.dataset.end,
                "source": self.dataset.source,
                "immutable": self.dataset.immutable,
            },
            "dataset_content_sha256": self.dataset_content_sha256,
            "execution_semantics": self.execution_semantics.value,
            "execution_fingerprint": self.execution_fingerprint,
            "fixed_parameters": dict(self.fixed_parameters),
            "parameter_grid": {k: list(self.parameter_grid[k]) for k in sorted(self.parameter_grid)},
            "geometry_fingerprint": self.geometry_fingerprint,
            "source_resolution_fingerprint": self.source_resolution_fingerprint,
            "max_candidates": self.max_candidates,
        })

    def candidates(self) -> tuple["ResearchCandidate", ...]:
        self.validate()
        keys = tuple(sorted(self.parameter_grid))
        result = []
        for index, values in enumerate(product(*(self.parameter_grid[k] for k in keys)), start=1):
            parameters = dict(self.fixed_parameters)
            parameters.update(dict(zip(keys, values)))
            candidate_id = f"{self.plan_id}-C{index:03d}"
            identity = {
                "candidate_id": candidate_id,
                "strategy_family": self.strategy_family,
                "base_revision": self.base_revision,
                "plan_fingerprint": self.fingerprint,
                "parameters": parameters,
            }
            result.append(ResearchCandidate(
                candidate_id=candidate_id,
                strategy_family=self.strategy_family,
                base_revision=self.base_revision,
                parameters=parameters,
                plan_fingerprint=self.fingerprint,
                candidate_fingerprint=_sha256(identity),
                dataset_fingerprint=self.dataset_content_sha256,
                execution_fingerprint=self.execution_fingerprint,
                geometry_fingerprint=self.geometry_fingerprint,
                source_resolution_fingerprint=self.source_resolution_fingerprint,
            ))
        return tuple(result)


@dataclass(frozen=True)
class ResearchCandidate:
    candidate_id: str
    strategy_family: str
    base_revision: str
    parameters: Mapping[str, Any]
    plan_fingerprint: str
    candidate_fingerprint: str
    dataset_fingerprint: str
    execution_fingerprint: str
    geometry_fingerprint: str
    source_resolution_fingerprint: str

    def validate(self) -> None:
        if not all((
            self.candidate_id, self.strategy_family, self.base_revision,
            self.plan_fingerprint, self.candidate_fingerprint,
            self.dataset_fingerprint, self.execution_fingerprint,
            self.geometry_fingerprint, self.source_resolution_fingerprint,
        )):
            raise CandidateLabError("candidate provenance is incomplete")
        expected = _sha256({
            "candidate_id": self.candidate_id,
            "strategy_family": self.strategy_family,
            "base_revision": self.base_revision,
            "plan_fingerprint": self.plan_fingerprint,
            "parameters": dict(self.parameters),
        })
        if expected != self.candidate_fingerprint:
            raise CandidateLabError("candidate fingerprint mismatch")


@dataclass(frozen=True)
class CandidateObservation:
    """Metrics emitted by a real, separately implemented candidate adapter."""

    candidate: ResearchCandidate
    trades: int
    wins: int
    losses: int
    ambiguous: int
    net_pnl_cash: float
    profit_factor: float | None
    max_drawdown_cash: float
    costs_included: bool
    result_fingerprint: str

    def validate(self) -> None:
        self.candidate.validate()
        counts = (self.trades, self.wins, self.losses, self.ambiguous)
        if any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in counts):
            raise CandidateLabError("trade counts must be non-negative integers")
        if self.wins + self.losses + self.ambiguous != self.trades:
            raise CandidateLabError("wins + losses + ambiguous must equal trades")
        _finite_number(self.net_pnl_cash, "net_pnl_cash")
        _finite_number(self.max_drawdown_cash, "max_drawdown_cash")
        if self.max_drawdown_cash < 0:
            raise CandidateLabError("max_drawdown_cash must be non-negative")
        if self.profit_factor is not None:
            _finite_number(self.profit_factor, "profit_factor")
            if self.profit_factor < 0:
                raise CandidateLabError("profit_factor must be non-negative")
        if not self.costs_included:
            raise CandidateLabError("ranking requires results net of declared trading costs")
        if not self.result_fingerprint:
            raise CandidateLabError("result fingerprint is required")

    @property
    def win_rate(self) -> float:
        decisive = self.wins + self.losses
        return self.wins / decisive if decisive else 0.0


@dataclass(frozen=True)
class CandidateAssessment:
    """Transparent descriptive assessment; deliberately contains no winner."""

    objective: str
    candidate_rows: tuple[dict[str, Any], ...]
    compared_candidates: int
    common_dataset_fingerprint: str
    common_execution_fingerprint: str
    multiple_candidates_tested: int
    decision: str = "DESCRIPTIVE_RESEARCH_ONLY"
    recommended_for_validation: tuple[str, ...] = ()
    winner: None = None
    production_eligible: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "objective": self.objective,
            "candidate_rows": [dict(row) for row in self.candidate_rows],
            "compared_candidates": self.compared_candidates,
            "common_dataset_fingerprint": self.common_dataset_fingerprint,
            "common_execution_fingerprint": self.common_execution_fingerprint,
            "multiple_candidates_tested": self.multiple_candidates_tested,
            "decision": self.decision,
            "recommended_for_validation": list(self.recommended_for_validation),
            "winner": self.winner,
            "production_eligible": self.production_eligible,
        }


_ALLOWED_OBJECTIVES = {
    "NET_PNL_AFTER_COSTS",
    "PROFIT_FACTOR",
    "WIN_RATE",
    "LOWEST_DRAWDOWN_AFTER_COSTS",
}

def run_candidate_matrix(
    plan: CandidatePlan,
    execute_candidate: Callable[[ResearchCandidate], CandidateObservation],
) -> tuple[CandidateObservation, ...]:
    """Execute each predeclared candidate in deterministic order.

    The injected adapter owns strategy execution and market semantics. This
    runner only enforces plan identity and complete, one-result-per-candidate
    accounting; it does not fabricate fills or metrics.
    """
    candidates = plan.candidates()
    observations = []
    for candidate in candidates:
        observation = execute_candidate(candidate)
        if not isinstance(observation, CandidateObservation):
            raise CandidateLabError("candidate adapter must return CandidateObservation")
        observation.validate()
        if observation.candidate.candidate_fingerprint != candidate.candidate_fingerprint:
            raise CandidateLabError("candidate adapter returned a result for a different candidate")
        if observation.candidate.plan_fingerprint != plan.fingerprint:
            raise CandidateLabError("candidate adapter returned a result from a different plan")
        if observation.candidate.dataset_fingerprint != plan.dataset_content_sha256:
            raise CandidateLabError("candidate adapter changed the declared dataset identity")
        if observation.candidate.execution_fingerprint != plan.execution_fingerprint:
            raise CandidateLabError("candidate adapter changed the declared execution profile")
        observations.append(observation)
    if len(observations) != len(candidates):
        raise CandidateLabError("candidate matrix did not produce one result per candidate")
    return tuple(observations)



def assess_candidates(
    observations: tuple[CandidateObservation, ...] | list[CandidateObservation],
    *,
    objective: str,
    minimum_trades: int = 30,
    validation_shortlist_size: int = 3,
) -> CandidateAssessment:
    """Sort a development-only candidate matrix by an explicit descriptive objective.

    This is not a statistical acceptance test. It returns a small shortlist for
    later untouched validation, never a canonical winner or a production decision.
    """
    if objective not in _ALLOWED_OBJECTIVES:
        raise CandidateLabError(f"unsupported objective: {objective}")
    if minimum_trades < 1 or validation_shortlist_size < 1:
        raise CandidateLabError("minimum trades and shortlist size must be positive")
    rows = tuple(observations)
    if not rows:
        raise CandidateLabError("at least one candidate result is required")
    for row in rows:
        row.validate()
    first = rows[0].candidate
    for row in rows[1:]:
        candidate = row.candidate
        if candidate.dataset_fingerprint != first.dataset_fingerprint:
            raise CandidateLabError("candidate results do not share the same dataset bytes")
        if candidate.execution_fingerprint != first.execution_fingerprint:
            raise CandidateLabError("candidate results do not share execution semantics/config")
        if candidate.geometry_fingerprint != first.geometry_fingerprint:
            raise CandidateLabError("candidate results do not share frozen geometry")
        if candidate.source_resolution_fingerprint != first.source_resolution_fingerprint:
            raise CandidateLabError("candidate results do not share source-resolution evidence")
    ids = [row.candidate.candidate_id for row in rows]
    if len(set(ids)) != len(ids):
        raise CandidateLabError("duplicate candidate result detected")

    def score(row: CandidateObservation) -> float:
        if objective == "NET_PNL_AFTER_COSTS":
            return row.net_pnl_cash
        if objective == "PROFIT_FACTOR":
            return row.profit_factor if row.profit_factor is not None else float("-inf")
        if objective == "WIN_RATE":
            return row.win_rate
        return -row.max_drawdown_cash

    ranked = sorted(rows, key=lambda row: (-score(row), row.candidate.candidate_id))
    report_rows = []
    eligible = []
    for rank, row in enumerate(ranked, start=1):
        enough_data = row.trades >= minimum_trades
        report_rows.append({
            "rank_by_declared_objective": rank,
            "candidate_id": row.candidate.candidate_id,
            "candidate_fingerprint": row.candidate.candidate_fingerprint,
            "parameters": dict(row.candidate.parameters),
            "trades": row.trades,
            "wins": row.wins,
            "losses": row.losses,
            "ambiguous": row.ambiguous,
            "win_rate": row.win_rate,
            "net_pnl_cash_after_costs": row.net_pnl_cash,
            "profit_factor": row.profit_factor,
            "max_drawdown_cash": row.max_drawdown_cash,
            "minimum_trade_count_met": enough_data,
            "eligible_for_untouched_validation_shortlist": enough_data,
            "result_fingerprint": row.result_fingerprint,
        })
        if enough_data:
            eligible.append(row.candidate.candidate_id)

    return CandidateAssessment(
        objective=objective,
        candidate_rows=tuple(report_rows),
        compared_candidates=len(rows),
        common_dataset_fingerprint=first.dataset_fingerprint,
        common_execution_fingerprint=first.execution_fingerprint,
        multiple_candidates_tested=len(rows),
        recommended_for_validation=tuple(eligible[:validation_shortlist_size]),
    )
