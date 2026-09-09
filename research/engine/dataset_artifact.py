"""Deterministic dataset artifact identity helpers.

Strategy-neutral: this module records dataset provenance and fingerprints only.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class DatasetArtifact:
    provider: str
    instrument: str
    interval: str
    requested_start_utc: str | None
    requested_end_utc: str | None
    retrieval_timestamp_utc: str
    source_timezone: str | None
    source_version: str | None
    row_count: int
    actual_start_utc: str | None
    actual_end_utc: str | None
    raw_sha256: str
    normalized_sha256: str
    quality_status: str

    def canonical_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))

    def fingerprint(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def fingerprint_bytes(data: bytes) -> str:
    """Return the SHA-256 fingerprint of an exact byte sequence."""
    return hashlib.sha256(data).hexdigest()


def canonicalize_json(payload: object) -> bytes:
    """Serialize JSON deterministically for provenance when raw bytes are unavailable."""
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
