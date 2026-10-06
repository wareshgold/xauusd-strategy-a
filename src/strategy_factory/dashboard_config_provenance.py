from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .dashboard_config import DashboardConfig, DashboardConfigError


class DashboardConfigProvenanceError(ValueError):
    """Raised when dashboard configuration provenance is invalid."""


@dataclass(frozen=True)
class DashboardConfigProvenance:
    provenance_revision: str
    config_revision: str
    config_fingerprint: str
    apply_mode: str
    fingerprint: str

    def _payload(self) -> dict[str, str]:
        return {
            "provenance_revision": self.provenance_revision,
            "config_revision": self.config_revision,
            "config_fingerprint": self.config_fingerprint,
            "apply_mode": self.apply_mode,
        }

    def validate(self) -> None:
        if not self.provenance_revision:
            raise DashboardConfigProvenanceError("provenance revision is required")
        if not self.config_revision:
            raise DashboardConfigProvenanceError("config revision is required")
        if not self.config_fingerprint:
            raise DashboardConfigProvenanceError("config fingerprint is required")
        if self.apply_mode != "STAGED_FORWARD_CONFIG":
            raise DashboardConfigProvenanceError("unsupported dashboard apply mode")
        expected = _fingerprint(self._payload())
        if self.fingerprint != expected:
            raise DashboardConfigProvenanceError("dashboard config provenance fingerprint mismatch")

    def as_dict(self) -> dict[str, str]:
        self.validate()
        return {**self._payload(), "fingerprint": self.fingerprint}


def _fingerprint(payload: dict[str, str]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def bind_dashboard_config(
    config: DashboardConfig,
    *,
    provenance_revision: str = "DASHBOARD-CONFIG-PROVENANCE-1",
) -> DashboardConfigProvenance:
    try:
        config.validate()
    except DashboardConfigError as exc:
        raise DashboardConfigProvenanceError(f"invalid dashboard config: {exc}") from exc

    draft = DashboardConfigProvenance(
        provenance_revision=provenance_revision,
        config_revision=config.revision,
        config_fingerprint=config.fingerprint,
        apply_mode=config.apply_mode,
        fingerprint="",
    )
    return DashboardConfigProvenance(
        provenance_revision=draft.provenance_revision,
        config_revision=draft.config_revision,
        config_fingerprint=draft.config_fingerprint,
        apply_mode=draft.apply_mode,
        fingerprint=_fingerprint(draft._payload()),
    )
