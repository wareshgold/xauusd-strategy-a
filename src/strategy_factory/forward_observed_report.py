from __future__ import annotations

"""Deterministic research-only report for observed Forward evidence.

This module composes immutable observed evidence with descriptive observed
statistics. It never derives R, canonical win/loss semantics, profitability,
parameter choices, or production authorization.
"""

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .forward_observed_evidence import ForwardObservedEvidence
from .forward_observed_statistics import ForwardObservedStatistics, build_forward_observed_statistics


class ForwardObservedReportError(ValueError):
    """Raised when an observed Forward report is invalid."""


@dataclass(frozen=True)
class ForwardObservedReport:
    """Immutable, provenance-bound observed Forward report."""

    report_revision: str
    evidence_fingerprint: str
    session_id: str
    session_fingerprint: str
    handoff_fingerprint: str
    strategy_revision: str
    manifest_revision: str
    execution_semantics: str
    broker_server: str
    symbol: str
    reconciliation_id: str
    observed_positions: int
    matched_positions: int
    mismatched_positions: int
    evidence: dict[str, Any]
    statistics: dict[str, Any]
    canonical_eligible: bool
    production_eligible: bool
    status: str
    fingerprint: str

    @staticmethod
    def _payload(values: dict[str, Any]) -> bytes:
        return json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

    def _fingerprint_payload(self) -> dict[str, Any]:
        return {
            "report_revision": self.report_revision,
            "evidence_fingerprint": self.evidence_fingerprint,
            "session_id": self.session_id,
            "session_fingerprint": self.session_fingerprint,
            "handoff_fingerprint": self.handoff_fingerprint,
            "strategy_revision": self.strategy_revision,
            "manifest_revision": self.manifest_revision,
            "execution_semantics": self.execution_semantics,
            "broker_server": self.broker_server,
            "symbol": self.symbol,
            "reconciliation_id": self.reconciliation_id,
            "observed_positions": self.observed_positions,
            "matched_positions": self.matched_positions,
            "mismatched_positions": self.mismatched_positions,
            "evidence": self.evidence,
            "statistics": self.statistics,
            "canonical_eligible": self.canonical_eligible,
            "production_eligible": self.production_eligible,
            "status": self.status,
        }

    def validate(self, evidence: ForwardObservedEvidence, statistics: ForwardObservedStatistics) -> None:
        evidence.validate()
        statistics.validate(evidence)
        if self.report_revision != "FORWARD-OBSERVED-REPORT-1":
            raise ForwardObservedReportError("unsupported Forward observed report revision")
        if self.evidence_fingerprint != evidence.fingerprint:
            raise ForwardObservedReportError("report is not bound to Forward observed evidence")
        identity = {
            "session_id": evidence.session_id,
            "session_fingerprint": evidence.session_fingerprint,
            "handoff_fingerprint": evidence.handoff_fingerprint,
            "strategy_revision": evidence.strategy_revision,
            "manifest_revision": evidence.manifest_revision,
            "execution_semantics": evidence.execution_semantics,
            "broker_server": evidence.broker_server,
            "symbol": evidence.symbol,
            "reconciliation_id": evidence.reconciliation_id,
            "observed_positions": evidence.observed_positions,
            "matched_positions": evidence.matched_positions,
            "mismatched_positions": evidence.mismatched_positions,
        }
        for name, expected in identity.items():
            if getattr(self, name) != expected:
                raise ForwardObservedReportError(f"report identity drift: {name}")
        if self.evidence != evidence.as_dict():
            raise ForwardObservedReportError("report evidence payload drift")
        if self.statistics != statistics.as_dict():
            raise ForwardObservedReportError("report statistics payload drift")
        if self.canonical_eligible is not False or self.production_eligible is not False:
            raise ForwardObservedReportError("observed Forward report cannot be canonical or production eligible")
        if self.status != "OBSERVED_FORWARD_RESEARCH":
            raise ForwardObservedReportError("unexpected observed Forward report status")
        expected = hashlib.sha256(self._payload(self._fingerprint_payload())).hexdigest()
        if self.fingerprint != expected:
            raise ForwardObservedReportError("Forward observed report fingerprint mismatch")

    def as_dict(self) -> dict[str, Any]:
        self.validate_for_export()
        return {**self._fingerprint_payload(), "fingerprint": self.fingerprint}

    def validate_for_export(self) -> None:
        if not self.fingerprint:
            raise ForwardObservedReportError("report fingerprint is missing")


def build_forward_observed_report(
    evidence: ForwardObservedEvidence,
    *,
    statistics: ForwardObservedStatistics | None = None,
    confidence_level: float = 0.95,
    report_revision: str = "FORWARD-OBSERVED-REPORT-1",
) -> ForwardObservedReport:
    """Compose deterministic observed evidence + observed statistics."""
    evidence.validate()
    stats = statistics or build_forward_observed_statistics(evidence, confidence_level=confidence_level)
    stats.validate(evidence)
    report = ForwardObservedReport(
        report_revision=report_revision,
        evidence_fingerprint=evidence.fingerprint,
        session_id=evidence.session_id,
        session_fingerprint=evidence.session_fingerprint,
        handoff_fingerprint=evidence.handoff_fingerprint,
        strategy_revision=evidence.strategy_revision,
        manifest_revision=evidence.manifest_revision,
        execution_semantics=evidence.execution_semantics,
        broker_server=evidence.broker_server,
        symbol=evidence.symbol,
        reconciliation_id=evidence.reconciliation_id,
        observed_positions=evidence.observed_positions,
        matched_positions=evidence.matched_positions,
        mismatched_positions=evidence.mismatched_positions,
        evidence=evidence.as_dict(),
        statistics=stats.as_dict(),
        canonical_eligible=False,
        production_eligible=False,
        status="OBSERVED_FORWARD_RESEARCH",
        fingerprint="",
    )
    fingerprint = hashlib.sha256(report._payload(report._fingerprint_payload())).hexdigest()
    final = ForwardObservedReport(**{**report.__dict__, "fingerprint": fingerprint})
    final.validate(evidence, stats)
    return final
