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
from .v3_research_session import V3ResearchSession, V3ResearchSessionError


class V3ResearchAPIError(ValueError):
    """Raised for invalid research API requests or unknown handles."""


class V3ResearchAPI:
    """Small, deterministic facade over provenance-bound V3 research sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, V3ResearchSession] = {}
        self._variants: dict[str, V3ExitVariant] = {}

    @property
    def session_count(self) -> int:
        return len(self._sessions)

    @property
    def variant_count(self) -> int:
        return len(self._variants)

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
                1 for variant in self._variants.values()
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
                "management_config": variant.management_config,
                "summary": dict(variant.summary),
                "spread_sensitivity": session.flat_spread_sensitivity(variant.summary),
                "trades": [dict(row) for row in variant.trades],
            },
            "cache_entries": session.cache_entries,
        }

    def evaluate_management(self, session_id: str, policy: dict[str, Any]) -> dict[str, Any]:
        session = self._require_session(session_id)
        try:
            variant = session.evaluate_management(policy)
        except (TypeError, ValueError) as exc:
            raise V3ResearchAPIError(f"management evaluation rejected: {exc}") from exc
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
                "management_config": dict(variant.management_config or {}),
                "summary": dict(variant.summary),
                "trades": [dict(row) for row in variant.trades],
            },
            "cache_entries": session.cache_entries,
        }

    def compare(self, session_id: str, left_variant_id: str, right_variant_id: str) -> dict[str, Any]:
        session = self._require_session(session_id)
        left = self._require_variant(left_variant_id, session_id)
        right = self._require_variant(right_variant_id, session_id)
        try:
            paired = session.compare(left, right)
        except (TypeError, ValueError) as exc:
            raise V3ResearchAPIError(f"paired comparison rejected: {exc}") from exc
        return {
            "research_only": True,
            "canonical": False,
            "validation_status": "NOT_VALIDATED",
            "session_id": session_id,
            "comparison": paired,
        }

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
            "management_config": variant.management_config,
        }
        return hashlib.sha256(
            json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
