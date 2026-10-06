from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .manifest import EvidenceStatus, RuleAuthority, StrategyManifest


class CompilationBlocked(RuntimeError):
    """Raised when research material is not eligible for deterministic compilation."""


@dataclass(frozen=True)
class CompiledStrategy:
    strategy_id: str
    manifest_revision: str
    rules: tuple[str, ...]
    parameter_set: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "manifest_revision": self.manifest_revision,
            "rules": list(self.rules),
            "parameter_set": self.parameter_set,
        }


class StrategyCompiler:
    """Compile only an explicitly canonical, fully resolved manifest.

    This compiler contains no SP2L geometry and never infers missing rules.
    """

    def compile(
        self,
        manifest: StrategyManifest,
        *,
        parameter_set: dict[str, Any] | None = None,
    ) -> CompiledStrategy:
        if not manifest.canonical_ready:
            raise CompilationBlocked(
                "Manifest is not canonical-ready; unresolved or non-canonical "
                "rules cannot be compiled."
            )

        for rule in manifest.rules:
            if rule.authority is not RuleAuthority.CANONICAL:
                raise CompilationBlocked(
                    f"Rule {rule.rule_id} is not canonical."
                )
            if rule.evidence_status is not EvidenceStatus.SOURCE_CONFIRMED:
                raise CompilationBlocked(
                    f"Rule {rule.rule_id} lacks fully source-confirmed status."
                )

        return CompiledStrategy(
            strategy_id=manifest.strategy_id,
            manifest_revision=manifest.revision,
            rules=tuple(rule.rule_id for rule in manifest.rules),
            parameter_set=dict(parameter_set or {}),
        )
