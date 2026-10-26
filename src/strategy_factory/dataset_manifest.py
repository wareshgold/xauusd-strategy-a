from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping


class DatasetManifestError(ValueError):
    """Raised when a dataset manifest or its external pin is invalid."""


@dataclass(frozen=True)
class DatasetManifest:
    """Content-addressed dataset identity intended for external pinning.

    A fingerprint proves internal consistency, not who trusted or published the
    manifest. Holdout use therefore requires a separately supplied trusted pin.
    """

    manifest_revision: str
    dataset_id: str
    dataset_role: str
    data_revision: str
    dataset_fingerprint: str
    immutable: bool
    artifact_id: str | None = None
    artifact_sha256: str | None = None
    fingerprint: str = ""

    def payload(self) -> dict[str, Any]:
        return {
            "manifest_revision": self.manifest_revision,
            "dataset_id": self.dataset_id,
            "dataset_role": self.dataset_role,
            "data_revision": self.data_revision,
            "dataset_fingerprint": self.dataset_fingerprint,
            "immutable": self.immutable,
            "artifact_id": self.artifact_id,
            "artifact_sha256": self.artifact_sha256,
        }

    def expected_fingerprint(self) -> str:
        raw = json.dumps(self.payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def validate(self) -> None:
        if not all((self.manifest_revision, self.dataset_id, self.dataset_role, self.data_revision)):
            raise DatasetManifestError("dataset manifest identity is incomplete")
        for field_name, value in (
            ("dataset_fingerprint", self.dataset_fingerprint),
            ("artifact_sha256", self.artifact_sha256),
        ):
            if value is not None and (
                len(value) != 64 or any(char not in "0123456789abcdef" for char in value.lower())
            ):
                raise DatasetManifestError(f"{field_name} must be a SHA-256 hex digest")
        if self.artifact_id is not None and not self.artifact_sha256:
            raise DatasetManifestError("artifact SHA-256 is required when artifact_id is present")
        if self.dataset_role in {"UNTOUCHED_VALIDATION", "FRESH_HOLDOUT"} and not self.immutable:
            raise DatasetManifestError("validation/holdout dataset manifest must be immutable")
        if self.fingerprint != self.expected_fingerprint():
            raise DatasetManifestError("dataset manifest fingerprint mismatch")

    @classmethod
    def create(
        cls,
        *,
        manifest_revision: str,
        dataset_id: str,
        dataset_role: str,
        data_revision: str,
        dataset_fingerprint: str,
        immutable: bool,
        artifact_id: str | None = None,
        artifact_sha256: str | None = None,
    ) -> "DatasetManifest":
        draft = cls(
            manifest_revision=manifest_revision,
            dataset_id=dataset_id,
            dataset_role=dataset_role,
            data_revision=data_revision,
            dataset_fingerprint=dataset_fingerprint,
            immutable=immutable,
            artifact_id=artifact_id,
            artifact_sha256=artifact_sha256,
        )
        manifest = cls(**draft.payload(), fingerprint=draft.expected_fingerprint())
        manifest.validate()
        return manifest

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {**self.payload(), "fingerprint": self.fingerprint}


class DatasetManifestRegistry:
    """Append-only manifest registry checked against externally trusted pins.

    The caller must obtain trusted_pins from a separately controlled source
    (for example, a reviewed release artifact or protected registry). Passing
    an untrusted caller-generated pin does not create authenticity.
    """

    def __init__(self, trusted_pins: Mapping[str, str]) -> None:
        self._trusted_pins = dict(trusted_pins)
        self._manifests: dict[str, DatasetManifest] = {}
        for dataset_id, fingerprint in self._trusted_pins.items():
            if not dataset_id or len(fingerprint) != 64 or any(c not in "0123456789abcdef" for c in fingerprint.lower()):
                raise DatasetManifestError("trusted pin must map dataset_id to a SHA-256 fingerprint")

    def register(self, manifest: DatasetManifest) -> DatasetManifest:
        manifest.validate()
        trusted = self._trusted_pins.get(manifest.dataset_id)
        if trusted is None:
            raise DatasetManifestError("dataset manifest has no external trusted pin")
        if trusted != manifest.fingerprint:
            raise DatasetManifestError("dataset manifest does not match external trusted pin")
        existing = self._manifests.get(manifest.dataset_id)
        if existing is not None and existing != manifest:
            raise DatasetManifestError("registered dataset manifest is immutable")
        self._manifests[manifest.dataset_id] = manifest
        return manifest

    def get(self, dataset_id: str) -> DatasetManifest:
        try:
            return self._manifests[dataset_id]
        except KeyError as exc:
            raise DatasetManifestError(f"dataset manifest {dataset_id!r} is not registered") from exc

    def validate_record(self, record: Any, expected_role: str) -> None:
        manifest = self.get(record.dataset_id)
        manifest.validate()
        if self._trusted_pins.get(manifest.dataset_id) != manifest.fingerprint:
            raise DatasetManifestError("dataset manifest external pin mismatch")
        if manifest.dataset_role != expected_role or record.dataset_role != expected_role:
            raise DatasetManifestError("dataset manifest role mismatch")
        if manifest.dataset_fingerprint != record.dataset_fingerprint:
            raise DatasetManifestError("dataset manifest fingerprint does not match research record")
        if manifest.data_revision != record.data_revision:
            raise DatasetManifestError("dataset manifest revision does not match research record")
        if not manifest.immutable:
            raise DatasetManifestError("dataset manifest is not immutable")
