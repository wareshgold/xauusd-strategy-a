from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .dashboard_config_provenance import (
    DashboardConfigProvenance,
    DashboardConfigProvenanceError,
)
from .runs import ResearchRunError, ResearchRunIdentity


class ResearchRunConfigBindingError(ValueError):
    """Raised when a research-run/configuration binding is invalid."""


@dataclass(frozen=True)
class ResearchRunConfigBinding:
    binding_revision: str
    run_id: str
    run_fingerprint: str
    config_revision: str
    config_fingerprint: str
    config_provenance_fingerprint: str
    fingerprint: str

    def _payload(self) -> dict[str, str]:
        return {
            "binding_revision": self.binding_revision,
            "run_id": self.run_id,
            "run_fingerprint": self.run_fingerprint,
            "config_revision": self.config_revision,
            "config_fingerprint": self.config_fingerprint,
            "config_provenance_fingerprint": self.config_provenance_fingerprint,
        }

    def validate(self) -> None:
        if not self.binding_revision:
            raise ResearchRunConfigBindingError("binding revision is required")
        if not self.run_id or not self.run_fingerprint:
            raise ResearchRunConfigBindingError("research run identity is required")
        if not self.config_revision or not self.config_fingerprint:
            raise ResearchRunConfigBindingError("dashboard configuration identity is required")
        if not self.config_provenance_fingerprint:
            raise ResearchRunConfigBindingError("dashboard configuration provenance is required")
        expected = _fingerprint(self._payload())
        if self.fingerprint != expected:
            raise ResearchRunConfigBindingError("research-run config binding fingerprint mismatch")

    def as_dict(self) -> dict[str, str]:
        self.validate()
        return {**self._payload(), "fingerprint": self.fingerprint}


def _fingerprint(payload: dict[str, str]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def bind_research_run_config(
    run: ResearchRunIdentity,
    config_provenance: DashboardConfigProvenance,
    *,
    binding_revision: str = "RESEARCH-RUN-CONFIG-BINDING-1",
) -> ResearchRunConfigBinding:
    try:
        run.validate()
    except ResearchRunError as exc:
        raise ResearchRunConfigBindingError(f"invalid research run: {exc}") from exc
    try:
        config_provenance.validate()
    except DashboardConfigProvenanceError as exc:
        raise ResearchRunConfigBindingError(
            f"invalid dashboard configuration provenance: {exc}"
        ) from exc

    draft = ResearchRunConfigBinding(
        binding_revision=binding_revision,
        run_id=run.run_id,
        run_fingerprint=run.fingerprint,
        config_revision=config_provenance.config_revision,
        config_fingerprint=config_provenance.config_fingerprint,
        config_provenance_fingerprint=config_provenance.fingerprint,
        fingerprint="",
    )
    return ResearchRunConfigBinding(
        **{**draft._payload(), "fingerprint": _fingerprint(draft._payload())}
    )
