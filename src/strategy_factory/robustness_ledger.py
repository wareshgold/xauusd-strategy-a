from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .robustness import RobustnessMatrix, RobustnessMatrixError


class RobustnessMatrixLedgerError(ValueError):
    """Raised when a robustness matrix ledger entry is invalid or conflicting."""


@dataclass(frozen=True)
class RobustnessMatrixLedgerEntry:
    matrix_fingerprint: str
    matrix_revision: str
    strategy_id: str
    strategy_revision: str
    manifest_revision: str
    dataset_role: str
    execution_semantics: str
    member_count: int
    fingerprint: str

    @staticmethod
    def _payload(values: dict[str, object]) -> bytes:
        return json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

    def _fingerprint_payload(self) -> dict[str, object]:
        return {
            "matrix_fingerprint": self.matrix_fingerprint,
            "matrix_revision": self.matrix_revision,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "manifest_revision": self.manifest_revision,
            "dataset_role": self.dataset_role,
            "execution_semantics": self.execution_semantics,
            "member_count": self.member_count,
        }

    def validate(self) -> None:
        if not self.matrix_fingerprint or not self.matrix_revision:
            raise RobustnessMatrixLedgerError("robustness matrix ledger identity is incomplete")
        if self.member_count < 2:
            raise RobustnessMatrixLedgerError("robustness matrix ledger member_count must be at least two")
        expected = hashlib.sha256(self._payload(self._fingerprint_payload())).hexdigest()
        if self.fingerprint != expected:
            raise RobustnessMatrixLedgerError("robustness matrix ledger fingerprint mismatch")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {**self._fingerprint_payload(), "fingerprint": self.fingerprint}


class RobustnessMatrixLedger:
    """Append-only registry for immutable robustness matrices."""

    def __init__(self) -> None:
        self._entries: list[RobustnessMatrixLedgerEntry] = []

    def record(self, matrix: RobustnessMatrix) -> RobustnessMatrixLedgerEntry:
        try:
            matrix.validate()
        except RobustnessMatrixError as exc:
            raise RobustnessMatrixLedgerError(str(exc)) from exc

        candidate = RobustnessMatrixLedgerEntry(
            matrix_fingerprint=matrix.fingerprint,
            matrix_revision=matrix.matrix_revision,
            strategy_id=matrix.strategy_id,
            strategy_revision=matrix.strategy_revision,
            manifest_revision=matrix.manifest_revision,
            dataset_role=matrix.dataset_role,
            execution_semantics=matrix.execution_semantics,
            member_count=matrix.member_count,
            fingerprint="",
        )
        fingerprint = hashlib.sha256(
            RobustnessMatrixLedgerEntry._payload(candidate._fingerprint_payload())
        ).hexdigest()
        candidate = RobustnessMatrixLedgerEntry(**{**candidate.__dict__, "fingerprint": fingerprint})

        for existing in self._entries:
            if existing.matrix_fingerprint == candidate.matrix_fingerprint:
                return existing
            if existing.matrix_revision == candidate.matrix_revision:
                raise RobustnessMatrixLedgerError(
                    "conflicting robustness matrix already recorded for matrix_revision"
                )

        self._entries.append(candidate)
        return candidate

    def contains(self, matrix: RobustnessMatrix) -> bool:
        return any(
            entry.matrix_fingerprint == matrix.fingerprint
            and entry.matrix_revision == matrix.matrix_revision
            for entry in self._entries
        )

    def entries(self) -> tuple[RobustnessMatrixLedgerEntry, ...]:
        return tuple(self._entries)

    def assert_clean(self) -> None:
        for entry in self._entries:
            entry.validate()

    def as_dict(self) -> list[dict[str, object]]:
        return [entry.as_dict() for entry in self._entries]
