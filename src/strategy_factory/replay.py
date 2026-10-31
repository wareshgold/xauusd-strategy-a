"""Deterministic replay identity records for Factory orchestration.

This module records replay provenance only. It does not execute jobs, alter
strategy rules, or infer whether a candidate is valid.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re

from strategy_factory.worker_state import WorkerLifecycle, WorkerStatus


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class ReplayRequest:
    replay_id: str
    job_id: str
    input_sha256: str
    failed_worker_id: str
    failure_reason: str

    @classmethod
    def from_failed_job(
        cls, worker: WorkerLifecycle, *, input_sha256: str
    ) -> "ReplayRequest":
        """Build a stable replay request from a failed job and its original input hash."""
        if not _SHA256_RE.fullmatch(input_sha256):
            raise ValueError("input_sha256 must be a lowercase 64-character SHA-256 hex digest")
        if worker.status not in {WorkerStatus.FAILED, WorkerStatus.REPLAY_READY}:
            raise ValueError("replay request requires a FAILED or REPLAY_READY worker")

        failures = [
            event for event in worker.events
            if event.status == WorkerStatus.FAILED.value
        ]
        if not failures or not failures[-1].reason:
            raise ValueError("failed worker must have a recorded failure reason")

        identity = {
            "job_id": worker.job_id,
            "input_sha256": input_sha256,
        }
        replay_id = hashlib.sha256(
            json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

        return cls(
            replay_id=replay_id,
            job_id=worker.job_id,
            input_sha256=input_sha256,
            failed_worker_id=worker.worker_id,
            failure_reason=failures[-1].reason,
        )

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
