from __future__ import annotations

"""Preflight gate for deciding whether two strategy adapters are comparable.

This module does not backtest strategies. It prevents Factory from treating
different source/execution semantics as a fair 1v1 comparison.
"""

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any


class AdapterReadinessError(ValueError):
    """Raised when adapter provenance or capability declarations are invalid."""


class DataCapability(str, Enum):
    M1_OHLC = "M1_OHLC"
    TICK_BID_ASK = "TICK_BID_ASK"


class AdapterStatus(str, Enum):
    READY = "READY"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class StrategyAdapterManifest:
    strategy_id: str
    strategy_revision: str
    source_repository: str
    source_path: str
    source_blob_sha: str
    implementation_role: str
    required_data: DataCapability
    uses_forming_candle: bool
    entry_semantics: str
    exit_semantics: str
    cost_model_fingerprint: str | None
    supports_trade_ledger: bool

    def validate(self) -> None:
        required = (
            self.strategy_id, self.strategy_revision, self.source_repository,
            self.source_path, self.source_blob_sha, self.implementation_role,
            self.entry_semantics, self.exit_semantics,
        )
        if not all(isinstance(v, str) and v for v in required):
            raise AdapterReadinessError("adapter manifest provenance/semantics are incomplete")
        if len(self.source_blob_sha) != 40:
            raise AdapterReadinessError("source_blob_sha must be a Git blob SHA")
        if not isinstance(self.required_data, DataCapability):
            raise AdapterReadinessError("required_data must be explicit")
        if not isinstance(self.uses_forming_candle, bool):
            raise AdapterReadinessError("uses_forming_candle must be explicit")
        if not isinstance(self.supports_trade_ledger, bool):
            raise AdapterReadinessError("supports_trade_ledger must be explicit")

    @property
    def fingerprint(self) -> str:
        self.validate()
        payload = {
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "source_repository": self.source_repository,
            "source_path": self.source_path,
            "source_blob_sha": self.source_blob_sha,
            "implementation_role": self.implementation_role,
            "required_data": self.required_data.value,
            "uses_forming_candle": self.uses_forming_candle,
            "entry_semantics": self.entry_semantics,
            "exit_semantics": self.exit_semantics,
            "cost_model_fingerprint": self.cost_model_fingerprint,
            "supports_trade_ledger": self.supports_trade_ledger,
        }
        return hashlib.sha256(json.dumps(
            payload, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class AdapterReadinessReport:
    status: AdapterStatus
    baseline_fingerprint: str
    challenger_fingerprint: str
    dataset_capability: DataCapability
    reasons: tuple[str, ...]
    allowed_use: str = "RESEARCH_PREFLIGHT_ONLY"
    winner: None = None
    production_eligible: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "baseline_fingerprint": self.baseline_fingerprint,
            "challenger_fingerprint": self.challenger_fingerprint,
            "dataset_capability": self.dataset_capability.value,
            "reasons": list(self.reasons),
            "allowed_use": self.allowed_use,
            "winner": None,
            "production_eligible": False,
        }


def assess_adapter_readiness(
    *,
    baseline: StrategyAdapterManifest,
    challenger: StrategyAdapterManifest,
    dataset_capability: DataCapability,
    common_execution_fingerprint: str | None,
) -> AdapterReadinessReport:
    """Fail closed unless declared adapters can share the requested data/execution.

    Matching declarations do not prove an adapter correct; they only remove
    known preflight blockers. Source and fixture parity tests remain required.
    """
    baseline.validate()
    challenger.validate()
    if baseline.strategy_id == challenger.strategy_id:
        raise AdapterReadinessError("comparison participants must be distinct")
    if not isinstance(dataset_capability, DataCapability):
        raise AdapterReadinessError("dataset capability must be explicit")

    reasons: list[str] = []
    if dataset_capability is DataCapability.M1_OHLC:
        if (baseline.required_data is DataCapability.TICK_BID_ASK
                or challenger.required_data is DataCapability.TICK_BID_ASK):
            reasons.append("DATA_CAPABILITY_MISMATCH: tick Bid/Ask data required")
        if baseline.uses_forming_candle or challenger.uses_forming_candle:
            reasons.append(
                "FORMING_CANDLE_PATH_UNAVAILABLE: M1 OHLC cannot reconstruct intrabar state"
            )
    if not common_execution_fingerprint:
        reasons.append("COMMON_EXECUTION_PROFILE_MISSING")
    if baseline.entry_semantics != challenger.entry_semantics:
        reasons.append("ENTRY_SEMANTICS_DIFFER")
    if baseline.exit_semantics != challenger.exit_semantics:
        reasons.append("EXIT_SEMANTICS_DIFFER")
    if baseline.cost_model_fingerprint is None or challenger.cost_model_fingerprint is None:
        reasons.append("COST_MODEL_UNVERIFIED")
    elif baseline.cost_model_fingerprint != challenger.cost_model_fingerprint:
        reasons.append("COST_MODELS_DIFFER")
    if not baseline.supports_trade_ledger or not challenger.supports_trade_ledger:
        reasons.append("TRADE_LEDGER_UNAVAILABLE")

    return AdapterReadinessReport(
        status=AdapterStatus.BLOCKED if reasons else AdapterStatus.READY,
        baseline_fingerprint=baseline.fingerprint,
        challenger_fingerprint=challenger.fingerprint,
        dataset_capability=dataset_capability,
        reasons=tuple(reasons),
    )
