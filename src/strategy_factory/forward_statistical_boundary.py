from __future__ import annotations

"""Fail-closed boundary between observed Forward facts and statistics.

This module intentionally does not derive R, win/loss, expectancy, or any
execution semantics from Forward observations. A statistical result may only
be consumed after an explicit, externally established trade-return mapping
exists.
"""

from dataclasses import dataclass
import hashlib
import json
from typing import Sequence

from .forward_observed_evidence import ForwardObservedEvidence, ForwardObservedEvidenceError
from .statistics import StatisticalValidationResult


class ForwardStatisticalBoundaryError(ValueError):
    """Raised when Forward observations are not sufficient for statistical use."""


@dataclass(frozen=True)
class ForwardStatisticalInput:
    """Explicit statistical input bound to immutable observed Forward evidence."""

    evidence_fingerprint: str
    dataset_role: str
    statistical_result: StatisticalValidationResult
    trade_returns_r: tuple[float, ...]
    mapping_revision: str
    mapping_source: str
    fingerprint: str

    @staticmethod
    def _payload(values: dict) -> bytes:
        return json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()

    def _fingerprint_payload(self) -> dict:
        return {
            "evidence_fingerprint": self.evidence_fingerprint,
            "dataset_role": self.dataset_role,
            "statistical_result": self.statistical_result.as_dict(),
            "trade_returns_r": list(self.trade_returns_r),
            "mapping_revision": self.mapping_revision,
            "mapping_source": self.mapping_source,
        }

    def validate(self, evidence: ForwardObservedEvidence) -> None:
        evidence.validate()
        if self.evidence_fingerprint != evidence.fingerprint:
            raise ForwardStatisticalBoundaryError(
                "statistical input is not bound to forward observed evidence"
            )
        if not self.mapping_revision or not self.mapping_source:
            raise ForwardStatisticalBoundaryError("trade-return mapping provenance is incomplete")
        self.statistical_result.validate()
        if len(self.trade_returns_r) != self.statistical_result.sample_size:
            raise ForwardStatisticalBoundaryError(
                "trade-return count does not match statistical sample size"
            )
        expected = hashlib.sha256(self._payload(self._fingerprint_payload())).hexdigest()
        if self.fingerprint != expected:
            raise ForwardStatisticalBoundaryError("forward statistical input fingerprint mismatch")


def require_explicit_r_mapping(
    evidence: ForwardObservedEvidence,
    *,
    statistical_result: StatisticalValidationResult | None = None,
    trade_returns_r: Sequence[float] | None = None,
    mapping_revision: str | None = None,
    mapping_source: str | None = None,
) -> ForwardStatisticalInput:
    """Create statistical input only when an explicit R mapping is supplied.

    No R values are derived from net, pips_result, entry/exit price, SL, TP,
    or any other Forward observation here.
    """
    evidence.validate()
    if statistical_result is None or trade_returns_r is None:
        raise ForwardStatisticalBoundaryError(
            "explicit trade-return mapping is required; Forward observations do not define R semantics"
        )
    returns = tuple(float(value) for value in trade_returns_r)
    if not mapping_revision or not mapping_source:
        raise ForwardStatisticalBoundaryError("trade-return mapping provenance is required")
    result = ForwardStatisticalInput(
        evidence_fingerprint=evidence.fingerprint,
        dataset_role=str(evidence.execution_semantics),
        statistical_result=statistical_result,
        trade_returns_r=returns,
        mapping_revision=mapping_revision,
        mapping_source=mapping_source,
        fingerprint="",
    )
    fingerprint = hashlib.sha256(
        result._payload(result._fingerprint_payload())
    ).hexdigest()
    final = ForwardStatisticalInput(**{**result.__dict__, "fingerprint": fingerprint})
    final.validate(evidence)
    return final
