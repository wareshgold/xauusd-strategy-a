"""Immutable provenance record for acquired market-data artifacts."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json


@dataclass(frozen=True)
class AcquisitionManifest:
    provider: str
    instrument: str
    interval: str
    requested_start_utc: str
    requested_end_utc: str
    actual_first_timestamp_utc: str | None
    actual_last_timestamp_utc: str | None
    row_count: int
    request_timestamp_utc: str
    source_timezone: str
    source_version: str
    raw_sha256: str
    normalized_sha256: str
    response_metadata: dict

    def canonical_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))


def fingerprint_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()
