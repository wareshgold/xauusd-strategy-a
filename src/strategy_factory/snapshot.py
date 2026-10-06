from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .manifest import StrategyManifest
from .models import StrategyPassport
from .passport_gate import PassportEligibility, evaluate_passport_eligibility
from .readiness import SourceReadiness, evaluate_source_readiness
from .source_ledger import SourceResolutionLedger


@dataclass(frozen=True)
class ReadinessSnapshot:
    """Immutable, deterministic audit record of Factory readiness."""

    snapshot_revision: str
    strategy_id: str
    manifest_revision: str
    manifest_fingerprint: str
    passport_fingerprint: str
    source_ledger: dict[str, Any]
    source_readiness: dict[str, Any]
    passport_eligibility: dict[str, Any]
    fingerprint: str

    @staticmethod
    def _fingerprint_payload(
        *,
        snapshot_revision: str,
        strategy_id: str,
        manifest_revision: str,
        manifest_fingerprint: str,
        passport_fingerprint: str,
        source_ledger: dict[str, Any],
        source_readiness: dict[str, Any],
        passport_eligibility: dict[str, Any],
    ) -> bytes:
        payload = {
            "snapshot_revision": snapshot_revision,
            "strategy_id": strategy_id,
            "manifest_revision": manifest_revision,
            "manifest_fingerprint": manifest_fingerprint,
            "passport_fingerprint": passport_fingerprint,
            "source_ledger": source_ledger,
            "source_readiness": source_readiness,
            "passport_eligibility": passport_eligibility,
        }
        return json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")

    def validate(self) -> None:
        expected = hashlib.sha256(
            self._fingerprint_payload(
                snapshot_revision=self.snapshot_revision,
                strategy_id=self.strategy_id,
                manifest_revision=self.manifest_revision,
                manifest_fingerprint=self.manifest_fingerprint,
                source_ledger=self.source_ledger,
                source_readiness=self.source_readiness,
                passport_eligibility=self.passport_eligibility,
            )
        ).hexdigest()
        if self.fingerprint != expected:
            raise ValueError("readiness snapshot fingerprint mismatch")

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "snapshot_revision": self.snapshot_revision,
            "strategy_id": self.strategy_id,
            "manifest_revision": self.manifest_revision,
            "manifest_fingerprint": self.manifest_fingerprint,
            "passport_fingerprint": self.passport_fingerprint,
            "source_ledger": self.source_ledger,
            "source_readiness": self.source_readiness,
            "passport_eligibility": self.passport_eligibility,
            "fingerprint": self.fingerprint,
        }


def manifest_fingerprint(manifest: StrategyManifest) -> str:
    payload = json.dumps(
        manifest.as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def passport_fingerprint(passport: StrategyPassport) -> str:
    payload = json.dumps(
        passport.as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_readiness_snapshot(
    manifest: StrategyManifest,
    passport: StrategyPassport,
    ledger: SourceResolutionLedger,
    *,
    snapshot_revision: str = "READINESS-SNAPSHOT-1",
) -> ReadinessSnapshot:
    if passport.strategy_id != manifest.strategy_id:
        raise ValueError("passport strategy_id does not match manifest")

    readiness: SourceReadiness = evaluate_source_readiness(manifest, ledger)
    eligibility: PassportEligibility = evaluate_passport_eligibility(
        passport, manifest, ledger
    )
    mf = manifest_fingerprint(manifest)
    pf = passport_fingerprint(passport)
    ledger_dict = ledger.as_dict()
    readiness_dict = readiness.as_dict()
    eligibility_dict = eligibility.as_dict()

    fingerprint = hashlib.sha256(
        ReadinessSnapshot._fingerprint_payload(
            snapshot_revision=snapshot_revision,
            strategy_id=manifest.strategy_id,
            manifest_revision=manifest.revision,
            manifest_fingerprint=mf,
            source_ledger=ledger_dict,
            source_readiness=readiness_dict,
            passport_eligibility=eligibility_dict,
        )
    ).hexdigest()

    snapshot = ReadinessSnapshot(
        snapshot_revision=snapshot_revision,
        strategy_id=manifest.strategy_id,
        manifest_revision=manifest.revision,
        manifest_fingerprint=mf,
        source_ledger=ledger_dict,
        source_readiness=readiness_dict,
        passport_eligibility=eligibility_dict,
        fingerprint=fingerprint,
    )
    snapshot.validate()
    return snapshot
