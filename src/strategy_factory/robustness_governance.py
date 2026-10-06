from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json

from .robustness import RobustnessMatrix
from .robustness_ledger import RobustnessMatrixLedger, RobustnessMatrixLedgerError
from .test_contract import DatasetRole


class RobustnessUsageError(ValueError):
    """Raised when robustness evidence violates dataset-role governance."""


class RobustnessUsageDisposition(str, Enum):
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class RobustnessUsage:
    matrix_fingerprint: str
    matrix_revision: str
    strategy_id: str
    dataset_role: DatasetRole
    purpose: str
    disposition: RobustnessUsageDisposition
    fingerprint: str

    @staticmethod
    def _payload(values: dict[str, object]) -> bytes:
        return json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

    def _fingerprint_payload(self) -> dict[str, object]:
        return {
            "matrix_fingerprint": self.matrix_fingerprint,
            "matrix_revision": self.matrix_revision,
            "strategy_id": self.strategy_id,
            "dataset_role": self.dataset_role.value,
            "purpose": self.purpose,
            "disposition": self.disposition.value,
        }

    def validate(self) -> None:
        if not self.matrix_fingerprint or not self.matrix_revision or not self.strategy_id:
            raise RobustnessUsageError("robustness usage identity is incomplete")
        if not self.purpose:
            raise RobustnessUsageError("robustness usage purpose is required")
        expected = hashlib.sha256(self._payload(self._fingerprint_payload())).hexdigest()
        if self.fingerprint != expected:
            raise RobustnessUsageError("robustness usage fingerprint mismatch")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {**self._fingerprint_payload(), "fingerprint": self.fingerprint}


class RobustnessUsageLedger:
    """Role-isolation ledger for descriptive robustness matrices."""

    def __init__(self) -> None:
        self._entries: list[RobustnessUsage] = []

    def record(
        self,
        matrix: RobustnessMatrix,
        *,
        ledger: RobustnessMatrixLedger,
        purpose: str,
    ) -> RobustnessUsage:
        try:
            matrix.validate()
        except Exception as exc:
            raise RobustnessUsageError(str(exc)) from exc
        if not purpose:
            raise RobustnessUsageError("robustness usage purpose is required")
        if not ledger.contains(matrix):
            raise RobustnessUsageError("robustness matrix is not registered in ledger")

        role = DatasetRole(matrix.dataset_role)
        blocked_purposes = {"DEVELOPMENT", "OPTIMIZATION", "PARAMETER_FIT"}
        if role in (DatasetRole.UNTOUCHED_VALIDATION, DatasetRole.FRESH_HOLDOUT) and purpose in blocked_purposes:
            raise RobustnessUsageError(
                f"{role.value} robustness evidence cannot be used for {purpose}"
            )

        entry = RobustnessUsage(
            matrix_fingerprint=matrix.fingerprint,
            matrix_revision=matrix.matrix_revision,
            strategy_id=matrix.strategy_id,
            dataset_role=role,
            purpose=purpose,
            disposition=RobustnessUsageDisposition.ALLOWED,
            fingerprint="",
        )
        fingerprint = hashlib.sha256(
            RobustnessUsage._payload(entry._fingerprint_payload())
        ).hexdigest()
        entry = RobustnessUsage(**{**entry.__dict__, "fingerprint": fingerprint})

        for existing in self._entries:
            if (
                existing.matrix_fingerprint == entry.matrix_fingerprint
                and existing.purpose == entry.purpose
            ):
                return existing

        self._entries.append(entry)
        return entry

    def entries(self) -> tuple[RobustnessUsage, ...]:
        return tuple(self._entries)

    def assert_clean(self) -> None:
        for entry in self._entries:
            entry.validate()
            if entry.disposition is RobustnessUsageDisposition.BLOCKED:
                raise RobustnessUsageError("robustness usage ledger contains blocked entries")

    def as_dict(self) -> list[dict[str, object]]:
        return [entry.as_dict() for entry in self._entries]
