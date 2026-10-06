from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .gates import code_gate, forward_gate, source_gate, validation_gate
from .models import GateResult, GateStatus, StrategyPassport


@dataclass
class ResearchRun:
    passport: StrategyPassport
    gates: list[GateResult] = field(default_factory=list)

    @property
    def production_eligible(self) -> bool:
        return len(self.gates) == 4 and all(
            gate.status is GateStatus.PASS for gate in self.gates
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "passport": self.passport.as_dict(),
            "gates": [
                {
                    "name": gate.name,
                    "status": gate.status.value,
                    "evidence": gate.evidence,
                    "details": gate.details,
                }
                for gate in self.gates
            ],
            "production_eligible": self.production_eligible,
        }


class StrategyResearchFactory:
    """Research-only gate orchestrator.

    It deliberately does not contain strategy geometry, signal generation,
    optimization objectives, MT5 order logic, or production decision logic.
    Those belong to separately versioned components.
    """

    def __init__(self, passport: StrategyPassport) -> None:
        self.run = ResearchRun(passport=passport)

    def evaluate_source(self, *, source_resolved: bool, unresolved_items: list[str]) -> GateResult:
        result = source_gate(
            source_resolved=source_resolved,
            unresolved_items=unresolved_items,
        )
        self._replace("1_STRATEGY_LAB", result)
        return result

    def evaluate_code(self, *, fixtures_passed: int, fixtures_total: int) -> GateResult:
        result = code_gate(
            fixtures_passed=fixtures_passed,
            fixtures_total=fixtures_total,
            code_revision=self.run.passport.code_revision,
        )
        self._replace("2_STRATEGY_ENGINE", result)
        return result

    def evaluate_validation(
        self,
        *,
        development_pass: bool,
        untouched_validation_pass: bool,
        robustness_pass: bool,
        fresh_holdout_pass: bool,
    ) -> GateResult:
        result = validation_gate(
            development_pass=development_pass,
            untouched_validation_pass=untouched_validation_pass,
            robustness_pass=robustness_pass,
            fresh_holdout_pass=fresh_holdout_pass,
        )
        self._replace("3_TEST_FACTORY", result)
        return result

    def evaluate_forward(self, *, python_mt5_reconciled: bool, forward_pass: bool) -> GateResult:
        result = forward_gate(
            python_mt5_reconciled=python_mt5_reconciled,
            forward_pass=forward_pass,
        )
        self._replace("4_FORWARD_VALIDATION", result)
        return result

    def _replace(self, stage_name: str, result: GateResult) -> None:
        self.run.gates = [
            gate for gate in self.run.gates if gate.name != stage_name
        ]
        self.run.gates.append(result)
