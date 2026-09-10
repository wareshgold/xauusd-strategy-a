from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class RecoveryFingerprint:
    order_id: str
    state: str
    sequence: int | None


def fingerprint(value: RecoveryFingerprint) -> str:
    payload = {"order_id": value.order_id, "state": value.state, "sequence": value.sequence}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()
