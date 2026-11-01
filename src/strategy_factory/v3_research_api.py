from __future__ import annotations

"""In-process application service for the interactive V3 research workbench.

This is deliberately a service boundary, not an HTTP server. It owns only
session/variant handles for the lifetime of the process. It does not persist
artifacts, select winners, promote evidence, or emit production signals.
"""

import hashlib
import json
from typing import Any

from .v3_exit_engine import V3ExitEngineError, V3ExitVariant
from .v3_management_engine import V3ManagementVariant
from .v3_research_session import V3ResearchSession, V3ResearchSessionError


class V3ResearchAPIError(ValueError):
    """Raised for invalid research API requests or unknown handles."""


class V3ResearchAPI:
    """Small, deterministic facade over provenance-bound V3 research sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, V3ResearchSession] = {}
        self._variants: dict[str, V3ExitVariant] = {}
        self._management_variants: dict[str, V3ManagementVariant] = {}

    @property
    def session_count(self) -> int:
        return len(self._sessions)

    @property
    def variant_count(self) -> int:
        return len(self._variants) + len(self._management_variants)

    def create_session(self, **config: Any) -> dict[str, Any]:
        try:
            session = V3ResearchSession(**config)
        except (TypeError, ValueError, OSError) as exc:
            raise V3ResearchAPIError(f"cannot create research session: {exc}") from exc
        session_id = session.session_fingerprint
        existing = self._sessions.get(session_id)
        if existing is not None:
            return self.describe_session(session_id)
        self._sessions[session_id] = session
        return self.describe_session(session_id)

    def describe_session(self, session_id: str) -> dict[str, Any]:
        session = self._require_session(session_id)
        result = session.manifest()
        result.update({
            "session_id": session_id,
            "api_scope": "PROCESS_LOCAL",
            "persistence": "NONE",
            "variant_count": sum(
                1 for variant in (*self._variants.values(), *self._management_variants.values())
                if variant.session_fingerprint == session_id
            ),
        })
        return result

    def evaluate(
        self,
        session_id: str,
        *,
        rr: float,
        activation_points: float | None,
        distance_points: float | None,
    ) -> dict[str, Any]:
        session = self._require_session(session_id)
        try:
            variant = session.evaluate(
                rr=rr,
                activation_points=activation_points,
                distance_points=distance_points,
            )
        except (TypeError, ValueError) as exc:
            raise V3ResearchAPIError(f"variant evaluation rejected: {exc}") from exc
        variant_id = self._variant_id(variant)
        self._variants[variant_id] = variant
        return {
            "research_only": True,
            "canonical": False,
            "validation_status": "NOT_VALIDATED",
            "session_id": session_id,
            "variant_id": variant_id,
            "variant": {
                "name": variant.name,
                "rr": variant.rr,
                "activation_points": variant.activation_points,
                "distance_points": variant.distance_points,
                "summary": dict(variant.summary),
                "trades": [dict(row) for row in variant.trades],
            },
            "cache_entries": session.cache_entries,
        }

    def evaluate_management(self, session_id: str, spec: dict[str, Any]) -> dict[str, Any]:
        session = self._require_session(session_id)
        try:
            variant = session.evaluate_management(spec)
        except (TypeError, ValueError) as exc:
            raise V3ResearchAPIError(f"management evaluation rejected: {exc}") from exc
        identity = {"session_fingerprint": variant.session_fingerprint, "spec": variant.spec}
        variant_id = hashlib.sha256(
            json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        self._management_variants[variant_id] = variant
        return {
            "research_only": True, "canonical": False, "validation_status": "NOT_VALIDATED",
            "session_id": session_id, "variant_id": variant_id,
            "variant": {"name": variant.name, "management": dict(variant.spec),
                        "summary": dict(variant.summary), "trades": [dict(row) for row in variant.trades]},
            "cache_entries": session.management_engine.cache_entries,
        }

    def compare(self, session_id: str, left_variant_id: str, right_variant_id: str) -> dict[str, Any]:
        session = self._require_session(session_id)
        try:
            if left_variant_id in self._management_variants and right_variant_id in self._management_variants:
                left = self._require_management_variant(left_variant_id, session_id)
                right = self._require_management_variant(right_variant_id, session_id)
                paired = session.compare_management(left, right)
            elif left_variant_id in self._variants and right_variant_id in self._variants:
                left = self._require_variant(left_variant_id, session_id)
                right = self._require_variant(right_variant_id, session_id)
                paired = session.compare(left, right)
            elif left_variant_id in self._variants and right_variant_id in self._management_variants:
                left = self._require_variant(left_variant_id, session_id)
                right = self._require_management_variant(right_variant_id, session_id)
                paired = self._compare_cross_engine(left, right)
            elif left_variant_id in self._management_variants and right_variant_id in self._variants:
                left = self._require_management_variant(left_variant_id, session_id)
                right = self._require_variant(right_variant_id, session_id)
                paired = self._compare_cross_engine(left, right)
            else:
                raise V3ResearchAPIError("unknown or expired comparison variant_id")
        except (TypeError, ValueError) as exc:
            raise V3ResearchAPIError(f"paired comparison rejected: {exc}") from exc
        return {
            "research_only": True, "canonical": False, "validation_status": "NOT_VALIDATED",
            "session_id": session_id, "comparison": paired,
        }

    @staticmethod
    def _compare_cross_engine(left: Any, right: Any) -> dict[str, Any]:
        if left.session_fingerprint != right.session_fingerprint:
            raise V3ResearchAPIError("variants do not belong to the same research session")
        if len(left.trades) != len(right.trades):
            raise V3ResearchAPIError("variants do not share the same frozen population")
        paired = []
        for index, (a, b) in enumerate(zip(left.trades, right.trades)):
            identity_a = (int(a["trigger_time"]), str(a["direction"]), float(a["theoretical_entry"]),
                          float(a["initial_sl"]), float(a["risk"]))
            identity_b = (int(b["trigger_time"]), str(b["direction"]), float(b["theoretical_entry"]),
                          float(b["initial_sl"]), float(b["risk"]))
            if identity_a != identity_b:
                raise V3ResearchAPIError("frozen trade identity mismatch")
            paired.append({
                "population_index": index, "trigger_time": identity_a[0],
                "left_variant": left.name, "right_variant": right.name,
                "left_reason": a["reason"], "right_reason": b["reason"],
                "left_ambiguous": a["ambiguous"], "right_ambiguous": b["ambiguous"],
                "left_realized_R": a["realized_R"], "right_realized_R": b["realized_R"],
                "delta_R": b["realized_R"] - a["realized_R"]
                if a["realized_R"] is not None and b["realized_R"] is not None else None,
                "outcome_changed": (a["reason"], a["ambiguous"], a["realized_R"])
                != (b["reason"], b["ambiguous"], b["realized_R"]),
            })
        return {"left_variant": left.name, "right_variant": right.name,
                "paired_trade_count": len(paired),
                "changed_outcome_count": sum(row["outcome_changed"] for row in paired),
                "paired_trades": paired}

    def _require_management_variant(self, variant_id: str, session_id: str) -> V3ManagementVariant:
        try:
            variant = self._management_variants[variant_id]
        except KeyError as exc:
            raise V3ResearchAPIError("unknown or expired management variant_id") from exc
        if variant.session_fingerprint != session_id:
            raise V3ResearchAPIError("variant belongs to a different research session")
        return variant

    def _require_session(self, session_id: str) -> V3ResearchSession:
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise V3ResearchAPIError("unknown or expired process-local session_id") from exc

    def _require_variant(self, variant_id: str, session_id: str) -> V3ExitVariant:
        try:
            variant = self._variants[variant_id]
        except KeyError as exc:
            raise V3ResearchAPIError("unknown or expired variant_id") from exc
        if variant.session_fingerprint != session_id:
            raise V3ResearchAPIError("variant belongs to a different research session")
        return variant

    @staticmethod
    def _variant_id(variant: V3ExitVariant) -> str:
        identity = {
            "session_fingerprint": variant.session_fingerprint,
            "rr": variant.rr,
            "activation_points": variant.activation_points,
            "distance_points": variant.distance_points,
        }
        return hashlib.sha256(
            json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
