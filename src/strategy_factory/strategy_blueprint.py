from __future__ import annotations

"""Source-agnostic strategy blueprint for the external discovery track."""

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

from .adapter_readiness import DataCapability
from .candidate_lab import CandidatePlan, CandidateLabError
from .strategy_intake import StrategySourceIntake
from .test_contract import ExecutionSemantics, TestDataset


class StrategyBlueprintError(ValueError):
    """Raised when an external strategy blueprint is not test-ready."""


def _json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise StrategyBlueprintError(
            "rule specification and parameters must be finite JSON-compatible values"
        ) from exc


@dataclass(frozen=True)
class ExternalStrategyBlueprint:
    """Explicit, noncanonical strategy definition ready for a research plan.

    rule_spec describes this candidate's rules; it is not SP2L geometry.
    Unresolved source interpretation blocks plan construction until resolved.
    """

    blueprint_id: str
    strategy_family: str
    revision: str
    intake: StrategySourceIntake
    rule_spec: Mapping[str, Any]
    required_data: DataCapability
    execution_semantics: ExecutionSemantics
    entry_semantics: str
    exit_semantics: str
    cost_model_fingerprint: str
    fixed_parameters: Mapping[str, Any]
    parameter_grid: Mapping[str, tuple[Any, ...]]
    unresolved_questions: tuple[str] = ()
    max_candidates: int = 64

    def validate(self) -> None:
        if not all(
            isinstance(value, str) and value.strip()
            for value in (
                self.blueprint_id, self.strategy_family, self.revision,
                self.entry_semantics, self.exit_semantics,
                self.cost_model_fingerprint,
            )
        ):
            raise StrategyBlueprintError(
                "blueprint identity and execution/cost semantics are required"
            )
        self.intake.validate()
        if not isinstance(self.required_data, DataCapability):
            raise StrategyBlueprintError("required_data capability must be explicit")
        if not isinstance(self.execution_semantics, ExecutionSemantics):
            raise StrategyBlueprintError("execution semantics must be explicit")
        if not isinstance(self.rule_spec, Mapping) or not self.rule_spec:
            raise StrategyBlueprintError("an explicit non-empty rule_spec is required")
        _json_bytes(dict(self.rule_spec))
        _json_bytes(dict(self.fixed_parameters))
        if not isinstance(self.parameter_grid, Mapping) or not self.parameter_grid:
            raise StrategyBlueprintError(
                "at least one finite parameter-grid dimension is required"
            )
        if not isinstance(self.unresolved_questions, tuple):
            raise StrategyBlueprintError("unresolved_questions must be a tuple")
        if any(not isinstance(q, str) or not q.strip() for q in self.unresolved_questions):
            raise StrategyBlueprintError("unresolved questions must be non-empty strings")
        if self.max_candidates < 1:
            raise StrategyBlueprintError("max_candidates must be positive")

    @property
    def rule_spec_fingerprint(self) -> str:
        self.validate()
        return sha256(_json_bytes(dict(self.rule_spec))).hexdigest()

    @property
    def fingerprint(self) -> str:
        self.validate()
        payload = {
            "blueprint_id": self.blueprint_id,
            "strategy_family": self.strategy_family,
            "revision": self.revision,
            "intake_fingerprint": self.intake.fingerprint,
            "rule_spec": dict(self.rule_spec),
            "rule_spec_fingerprint": self.rule_spec_fingerprint,
            "required_data": self.required_data.value,
            "execution_semantics": self.execution_semantics.value,
            "entry_semantics": self.entry_semantics,
            "exit_semantics": self.exit_semantics,
            "cost_model_fingerprint": self.cost_model_fingerprint,
            "fixed_parameters": dict(self.fixed_parameters),
            "parameter_grid": {
                key: list(self.parameter_grid[key])
                for key in sorted(self.parameter_grid)
            },
            "unresolved_questions": list(self.unresolved_questions),
            "max_candidates": self.max_candidates,
        }
        return sha256(_json_bytes(payload)).hexdigest()

    @property
    def research_draft_only(self) -> bool:
        self.validate()
        return True

    def to_candidate_plan(
        self,
        *,
        dataset: TestDataset,
        dataset_content_sha256: str,
        execution_fingerprint: str,
    ) -> CandidatePlan:
        """Build a development-only generic plan; unresolved rules block execution."""
        self.validate()
        if self.unresolved_questions:
            raise StrategyBlueprintError(
                "unresolved strategy questions block candidate-plan construction"
            )
        if not execution_fingerprint or not execution_fingerprint.strip():
            raise StrategyBlueprintError("execution profile fingerprint is required")
        try:
            plan = CandidatePlan(
                plan_id=self.blueprint_id,
                strategy_family=self.strategy_family,
                base_revision=self.revision,
                dataset=dataset,
                dataset_content_sha256=dataset_content_sha256,
                execution_semantics=self.execution_semantics,
                execution_fingerprint=execution_fingerprint,
                fixed_parameters=dict(self.fixed_parameters),
                parameter_grid={
                    key: tuple(values) for key, values in self.parameter_grid.items()
                },
                geometry_fingerprint=self.rule_spec_fingerprint,
                source_resolution_fingerprint=None,
                max_candidates=self.max_candidates,
                provenance_mode="EXTERNAL",
                external_source_fingerprint=self.fingerprint,
            )
            plan.validate()
        except CandidateLabError as exc:
            raise StrategyBlueprintError(
                f"candidate plan is not valid: {exc}"
            ) from exc
        return plan

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "blueprint_id": self.blueprint_id,
            "strategy_family": self.strategy_family,
            "revision": self.revision,
            "intake_fingerprint": self.intake.fingerprint,
            "rule_spec": dict(self.rule_spec),
            "rule_spec_fingerprint": self.rule_spec_fingerprint,
            "required_data": self.required_data.value,
            "execution_semantics": self.execution_semantics.value,
            "entry_semantics": self.entry_semantics,
            "exit_semantics": self.exit_semantics,
            "cost_model_fingerprint": self.cost_model_fingerprint,
            "fixed_parameters": dict(self.fixed_parameters),
            "parameter_grid": {
                key: list(self.parameter_grid[key])
                for key in sorted(self.parameter_grid)
            },
            "unresolved_questions": list(self.unresolved_questions),
            "fingerprint": self.fingerprint,
            "research_draft_only": True,
            "canonical": False,
            "backtest_approved": False,
            "forward_approved": False,
            "production_eligible": False,
        }
