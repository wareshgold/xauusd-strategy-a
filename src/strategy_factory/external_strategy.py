from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json


class ExternalStrategyError(ValueError):
    """Raised when an external strategy reference is not immutable enough for research."""


@dataclass(frozen=True)
class ExternalStrategyReference:
    """Immutable provenance for a third-party strategy implementation.

    This is a reference boundary only. It never promotes the external code to
    canonical Strategy A and never changes the current internal strategy.
    """

    strategy_id: str
    upstream_repository: str
    upstream_path: str
    upstream_ref: str
    upstream_blob_sha: str
    implementation_role: str = "EXTERNAL_REFERENCE"

    def validate(self) -> None:
        if not all(
            isinstance(value, str) and value
            for value in (
                self.strategy_id,
                self.upstream_repository,
                self.upstream_path,
                self.upstream_ref,
                self.upstream_blob_sha,
                self.implementation_role,
            )
        ):
            raise ExternalStrategyError("external strategy reference identity is incomplete")
        if len(self.upstream_blob_sha) != 40:
            raise ExternalStrategyError("upstream_blob_sha must be a Git blob SHA")
        if self.implementation_role != "EXTERNAL_REFERENCE":
            raise ExternalStrategyError("external strategy cannot be promoted through this boundary")

    @property
    def fingerprint(self) -> str:
        self.validate()
        payload = json.dumps(
            {
                "strategy_id": self.strategy_id,
                "upstream_repository": self.upstream_repository,
                "upstream_path": self.upstream_path,
                "upstream_ref": self.upstream_ref,
                "upstream_blob_sha": self.upstream_blob_sha,
                "implementation_role": self.implementation_role,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def as_dict(self) -> dict[str, str]:
        self.validate()
        return {
            "strategy_id": self.strategy_id,
            "upstream_repository": self.upstream_repository,
            "upstream_path": self.upstream_path,
            "upstream_ref": self.upstream_ref,
            "upstream_blob_sha": self.upstream_blob_sha,
            "implementation_role": self.implementation_role,
            "fingerprint": self.fingerprint,
        }
