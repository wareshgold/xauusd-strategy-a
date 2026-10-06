from __future__ import annotations

from dataclasses import dataclass

from .dashboard_config_provenance_ledger import DashboardConfigProvenanceLedger
from .research_run_config_binding import (
    ResearchRunConfigBinding,
    ResearchRunConfigBindingError,
)
from .runs import ResearchRunIdentity


class ResearchRunConfigBindingLedgerError(ValueError):
    """Raised when a research-run configuration binding cannot be recorded."""


@dataclass(frozen=True)
class ResearchRunConfigBindingLedgerEntry:
    binding: ResearchRunConfigBinding

    def validate(self) -> None:
        self.binding.validate()


class ResearchRunConfigBindingLedger:
    """Immutable in-memory ledger binding one run to one staged config identity."""

    def __init__(self, config_ledger: DashboardConfigProvenanceLedger | None = None) -> None:
        self.config_ledger = config_ledger
        self._records: dict[str, ResearchRunConfigBindingLedgerEntry] = {}

    def record(
        self,
        run: ResearchRunIdentity,
        binding: ResearchRunConfigBinding,
    ) -> ResearchRunConfigBindingLedgerEntry:
        try:
            run.validate()
            binding.validate()
        except Exception as exc:
            raise ResearchRunConfigBindingLedgerError(str(exc)) from exc

        if binding.run_id != run.run_id or binding.run_fingerprint != run.fingerprint:
            raise ResearchRunConfigBindingLedgerError(
                "binding does not match research run identity"
            )

        if self.config_ledger is not None:
            try:
                registered = self.config_ledger.get(binding.config_revision).provenance
            except Exception as exc:
                raise ResearchRunConfigBindingLedgerError(
                    f"dashboard configuration provenance is not registered: {binding.config_revision}"
                ) from exc
            if registered.fingerprint != binding.config_provenance_fingerprint:
                raise ResearchRunConfigBindingLedgerError(
                    "binding does not match registered dashboard configuration provenance"
                )

        existing = self._records.get(run.run_id)
        if existing is not None:
            if existing.binding == binding:
                return existing
            raise ResearchRunConfigBindingLedgerError(
                f"conflicting dashboard configuration binding for run {run.run_id}"
            )

        entry = ResearchRunConfigBindingLedgerEntry(binding)
        self._records[run.run_id] = entry
        return entry

    def get(self, run_id: str) -> ResearchRunConfigBindingLedgerEntry:
        try:
            return self._records[run_id]
        except KeyError as exc:
            raise ResearchRunConfigBindingLedgerError(
                f"dashboard configuration binding for run {run_id!r} is not registered"
            ) from exc

    def as_dict(self) -> list[dict[str, str]]:
        return [self._records[key].binding.as_dict() for key in sorted(self._records)]
