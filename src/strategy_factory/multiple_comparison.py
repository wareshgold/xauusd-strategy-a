from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from math import isfinite


class MultipleComparisonError(ValueError):
    """Raised when multiple-comparison inputs are invalid."""


@dataclass(frozen=True)
class MultipleComparisonResult:
    """Deterministic p-value adjustment; descriptive only, never a winner selector."""

    method: str
    family_size: int
    raw_p_values: tuple[float, ...]
    adjusted_p_values: tuple[float, ...]
    fingerprint: str

    def validate(self) -> None:
        if self.method not in {"BONFERRONI", "HOLM"}:
            raise MultipleComparisonError("unsupported multiple-comparison method")
        if self.family_size < 1 or self.family_size != len(self.raw_p_values):
            raise MultipleComparisonError("family_size does not match p-values")
        if len(self.adjusted_p_values) != self.family_size:
            raise MultipleComparisonError("adjusted p-value count does not match family_size")
        if any(not isfinite(p) or not 0.0 <= p <= 1.0 for p in self.raw_p_values):
            raise MultipleComparisonError("raw p-values must be finite and between 0 and 1")
        if any(not isfinite(p) or not 0.0 <= p <= 1.0 for p in self.adjusted_p_values):
            raise MultipleComparisonError("adjusted p-values must be finite and between 0 and 1")
        payload = self._fingerprint_payload()
        expected = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if self.fingerprint != expected:
            raise MultipleComparisonError("multiple-comparison fingerprint mismatch")

    def _fingerprint_payload(self) -> dict[str, object]:
        return {
            "method": self.method,
            "family_size": self.family_size,
            "raw_p_values": list(self.raw_p_values),
            "adjusted_p_values": list(self.adjusted_p_values),
        }

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {**self._fingerprint_payload(), "fingerprint": self.fingerprint}


def _bonferroni(values: tuple[float, ...]) -> tuple[float, ...]:
    n = len(values)
    return tuple(min(1.0, p * n) for p in values)


def _holm(values: tuple[float, ...]) -> tuple[float, ...]:
    ordered = sorted(enumerate(values), key=lambda item: (item[1], item[0]))
    adjusted = [0.0] * len(values)
    running = 0.0
    n = len(values)
    for rank, (index, p_value) in enumerate(ordered):
        candidate = min(1.0, (n - rank) * p_value)
        running = max(running, candidate)
        adjusted[index] = running
    return tuple(adjusted)


def adjust_p_values(p_values: tuple[float, ...] | list[float], *, method: str = "HOLM") -> MultipleComparisonResult:
    values = tuple(float(p) for p in p_values)
    if not values:
        raise MultipleComparisonError("at least one p-value is required")
    if method not in {"BONFERRONI", "HOLM"}:
        raise MultipleComparisonError("unsupported multiple-comparison method")
    if any(not isfinite(p) or not 0.0 <= p <= 1.0 for p in values):
        raise MultipleComparisonError("p-values must be finite and between 0 and 1")
    adjusted = _bonferroni(values) if method == "BONFERRONI" else _holm(values)
    payload = {
        "method": method,
        "family_size": len(values),
        "raw_p_values": list(values),
        "adjusted_p_values": list(adjusted),
    }
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    result = MultipleComparisonResult(method, len(values), values, adjusted, fingerprint)
    result.validate()
    return result
