from __future__ import annotations

"""Telemetry primitives for the SP2L Research Factory.

This module reports worker/job state only. It does not select research
candidates, define Strategy A geometry, or authorize production execution.
"""

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATUS_FILE = ROOT / "runtime" / "factory_worker_status.json"

VALID_STATES = {
    "QUEUED",
    "RUNNING",
    "HEARTBEAT",
    "COMPLETED",
    "FAILED",
    "IDLE",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalise_worker(worker: dict[str, Any]) -> dict[str, Any]:
    state = str(worker.get("state") or "IDLE").upper()
    if state not in VALID_STATES:
        raise ValueError(f"invalid worker state: {state}")

    progress = worker.get("progress")
    if progress is not None:
        progress = max(0.0, min(100.0, float(progress)))

    return {
        "worker_id": str(worker.get("worker_id") or "unknown"),
        "job_id": worker.get("job_id"),
        "job_type": worker.get("job_type"),
        "station": worker.get("station"),
        "phase": worker.get("phase"),
        "state": state,
        "started_utc": worker.get("started_utc"),
        "heartbeat_utc": worker.get("heartbeat_utc") or utc_now(),
        "progress": progress,
        "detail": worker.get("detail"),
        "output_artifact": worker.get("output_artifact"),
        "error": worker.get("error"),
    }


def publish_workers(
    workers: list[dict[str, Any]],
    path: Path = DEFAULT_STATUS_FILE,
) -> None:
    """Atomically publish the current worker roster for the read-only dashboard."""
    payload = {
        "schema_version": 1,
        "published_utc": utc_now(),
        "workers": [_normalise_worker(w) for w in workers],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=".factory_worker_status.",
        suffix=".tmp",
        dir=path.parent,
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
