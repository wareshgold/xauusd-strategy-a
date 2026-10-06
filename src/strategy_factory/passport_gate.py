from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .manifest import StrategyManifest
from .models import StrategyPassport
from .readiness import SourceReadiness, evaluate_source_readiness
from .source_ledger import SourceResolutionLedger


@dataclass(frozen=True)
class PassportEligibility:
    """Deterministic audit result for a strategy passport.

    This gate only evaluates readiness and identity. It never changes the
    passport, promotes rules, resolves source questions, or evaluates
    performance.
    """

    strategy_id: str
    passport_source_revision: str
    manifest_revision: str
    source_status: str
    frozen_geometry: str
    canonical_strategy: str
    production: str
    blocking_reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "passport_source_revision": self.passport_source_revision,
            "manifest_revision": self.manifest_revision,
            "source_status": self.source_status,
            "frozen_geometry": self.frozen_geometry,
            "canonical_strategy": self.canonical_strategy,
            "production": self.production,
            "blocking_reasons": list(self.blocking_reasons),
        }


def evaluate_passport_eligibility(
    passport: StrategyPassport,
    manifest: StrategyManifest,
    ledger: SourceResolutionLedger,
) -> PassportEligibility:
    """Evaluate passport eligibility against the current source evidence."""

    if passport.strategy_id != manifest.strategy_id:
        raise ValueError(
            "passport strategy_id does not match manifest strategy_id"
        )

    readiness: SourceReadiness = evaluate_source_readiness(manifest, ledger)
    reasons: list[str] = []

    if readiness.status.value != "PASS":
        reasons.append("SOURCE_READINESS_BLOCKED")
    if readiness.frozen_geometry_blocked:
        reasons.append("FROZEN_GEOMETRY_BLOCKED")
    if not manifest.canonical_ready:
        reasons.append("MANIFEST_NOT_CANONICAL_READY")

    result = PassportEligibility(
        strategy_id=passport.strategy_id,
        passport_source_revision=passport.source_revision,
        manifest_revision=manifest.revision,
        source_status=readiness.status.value,
        frozen_geometry="BLOCKED" if readiness.frozen_geometry_blocked else "READY",
        canonical_strategy="ELIGIBLE" if readiness.canonical_strategy_eligible else "NOT_ELIGIBLE",
        production="ELIGIBLE" if readiness.production_eligible else "NOT_ELIGIBLE",
        blocking_reasons=tuple(dict.fromkeys(reasons)),
    )
    return result
