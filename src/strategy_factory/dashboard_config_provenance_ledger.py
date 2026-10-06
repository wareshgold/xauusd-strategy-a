from __future__ import annotations

from dataclasses import dataclass

from .dashboard_config_provenance import (
    DashboardConfigProvenance,
    DashboardConfigProvenanceError,
)


class DashboardConfigProvenanceLedgerError(ValueError):
    """Raised when dashboard configuration provenance cannot be recorded."""


@dataclass(frozen=True)
class DashboardConfigProvenanceLedgerEntry:
    provenance: DashboardConfigProvenance

    def validate(self) -> None:
        self.provenance.validate()


class DashboardConfigProvenanceLedger:
    """Immutable in-memory registry keyed by configuration revision.

    This records configuration identity only. It does not authorize execution,
    infer canonical rules, or select BUY/SELL decisions.
    """

    def __init__(self) -> None:
        self._entries: dict[str, DashboardConfigProvenanceLedgerEntry] = {}

    def record(self, provenance: DashboardConfigProvenance) -> DashboardConfigProvenanceLedgerEntry:
        try:
            provenance.validate()
        except DashboardConfigProvenanceError as exc:
            raise DashboardConfigProvenanceLedgerError(str(exc)) from exc

        key = provenance.config_revision
        existing = self._entries.get(key)
        if existing is not None:
            if existing.provenance == provenance:
                return existing
            raise DashboardConfigProvenanceLedgerError(
                f"conflicting dashboard configuration provenance for revision {key}"
            )

        entry = DashboardConfigProvenanceLedgerEntry(provenance)
        self._entries[key] = entry
        return entry

    def get(self, config_revision: str) -> DashboardConfigProvenanceLedgerEntry:
        try:
            return self._entries[config_revision]
        except KeyError as exc:
            raise DashboardConfigProvenanceLedgerError(
                f"dashboard configuration revision not registered: {config_revision}"
            ) from exc

    def contains(self, config_revision: str) -> bool:
        return config_revision in self._entries

    def as_dict(self) -> list[dict[str, str]]:
        return [
            self._entries[key].provenance.as_dict()
            for key in sorted(self._entries)
        ]
