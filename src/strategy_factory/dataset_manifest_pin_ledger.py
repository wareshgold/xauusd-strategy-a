from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable

from .dataset_manifest import DatasetManifest, DatasetManifestError


class DatasetManifestPinLedgerError(ValueError):
    """Raised when a persisted manifest pin ledger is invalid."""


@dataclass(frozen=True)
class DatasetManifestPin:
    sequence: int
    dataset_id: str
    manifest_fingerprint: str
    previous_pin_fingerprint: str
    pin_fingerprint: str

    def payload(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "dataset_id": self.dataset_id,
            "manifest_fingerprint": self.manifest_fingerprint,
            "previous_pin_fingerprint": self.previous_pin_fingerprint,
        }

    def expected_fingerprint(self) -> str:
        raw = json.dumps(self.payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def validate(self, expected_sequence: int, previous_fingerprint: str) -> None:
        if self.sequence != expected_sequence:
            raise DatasetManifestPinLedgerError("pin ledger sequence is not contiguous")
        if not self.dataset_id:
            raise DatasetManifestPinLedgerError("pin ledger dataset_id is empty")
        for name, value in (
            ("manifest_fingerprint", self.manifest_fingerprint),
            ("previous_pin_fingerprint", self.previous_pin_fingerprint),
            ("pin_fingerprint", self.pin_fingerprint),
        ):
            if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                raise DatasetManifestPinLedgerError(f"{name} must be a lowercase SHA-256 digest")
        if self.previous_pin_fingerprint != previous_fingerprint:
            raise DatasetManifestPinLedgerError("pin ledger chain link mismatch")
        if self.pin_fingerprint != self.expected_fingerprint():
            raise DatasetManifestPinLedgerError("pin ledger record fingerprint mismatch")


class DatasetManifestPinLedger:
    """Deterministic serialized pin history verified against an external tip pin.

    The serialized ledger is durable only when the caller stores it durably.
    Authenticity requires the expected tip fingerprint to come from an
    independently controlled trust channel; a value stored beside this file
    is not an independent trust anchor.
    """

    REVISION = "DATASET-MANIFEST-PIN-LEDGER-1"
    GENESIS = "0" * 64

    def __init__(self, pins: Iterable[DatasetManifestPin] = ()) -> None:
        self._pins = list(pins)
        self.validate()

    @property
    def pins(self) -> tuple[DatasetManifestPin, ...]:
        return tuple(self._pins)

    @property
    def tip_fingerprint(self) -> str:
        return self._pins[-1].pin_fingerprint if self._pins else self.GENESIS

    def validate(self) -> None:
        previous = self.GENESIS
        seen: set[str] = set()
        for index, pin in enumerate(self._pins, start=1):
            pin.validate(index, previous)
            if pin.dataset_id in seen:
                raise DatasetManifestPinLedgerError("dataset_id already pinned; ledger is append-only")
            seen.add(pin.dataset_id)
            previous = pin.pin_fingerprint

    def append(self, manifest: DatasetManifest) -> DatasetManifestPin:
        manifest.validate()
        if any(pin.dataset_id == manifest.dataset_id for pin in self._pins):
            raise DatasetManifestPinLedgerError("dataset_id already pinned; ledger is append-only")
        draft = DatasetManifestPin(
            sequence=len(self._pins) + 1,
            dataset_id=manifest.dataset_id,
            manifest_fingerprint=manifest.fingerprint,
            previous_pin_fingerprint=self.tip_fingerprint,
            pin_fingerprint="",
        )
        pin = DatasetManifestPin(**{**draft.payload(), "pin_fingerprint": draft.expected_fingerprint()})
        pin.validate(len(self._pins) + 1, self.tip_fingerprint)
        self._pins.append(pin)
        return pin

    def verify_external_tip(self, expected_tip_fingerprint: str) -> None:
        if len(expected_tip_fingerprint) != 64 or any(char not in "0123456789abcdef" for char in expected_tip_fingerprint):
            raise DatasetManifestPinLedgerError("expected external tip must be a lowercase SHA-256 digest")
        self.validate()
        if self.tip_fingerprint != expected_tip_fingerprint:
            raise DatasetManifestPinLedgerError("ledger tip does not match externally trusted tip")

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "ledger_revision": self.REVISION,
            "pins": [{**pin.payload(), "pin_fingerprint": pin.pin_fingerprint} for pin in self._pins],
            "tip_fingerprint": self.tip_fingerprint,
        }

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    @classmethod
    def from_json(cls, raw: str, *, expected_external_tip_fingerprint: str) -> "DatasetManifestPinLedger":
        try:
            data = json.loads(raw)
            if data.get("ledger_revision") != cls.REVISION:
                raise DatasetManifestPinLedgerError("unsupported pin ledger revision")
            pins = [DatasetManifestPin(**item) for item in data["pins"]]
            ledger = cls(pins)
            if data.get("tip_fingerprint") != ledger.tip_fingerprint:
                raise DatasetManifestPinLedgerError("serialized tip fingerprint mismatch")
            ledger.verify_external_tip(expected_external_tip_fingerprint)
            return ledger
        except DatasetManifestPinLedgerError:
            raise
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise DatasetManifestPinLedgerError("invalid serialized pin ledger") from exc
