from __future__ import annotations

import hashlib
from pathlib import Path

from strategy_factory.handoff import (
    ResearchHandoffError,
    build_research_handoff,
)
from strategy_factory.job_events import FactoryJobEvent, FactoryJobEventLedger
from strategy_factory.research_record import ResearchRecord
from strategy_factory.models import GateStatus
from strategy_factory.research_record import ResearchRecord
from strategy_factory.test_contract import DatasetRole


def _record():
    # Minimal object is deliberately avoided; handoff validation must consume
    # a real ResearchRecord in production. This test focuses on dataset-bound
    # handoff identity construction.
    raise NotImplementedError


def test_handoff_requires_dataset_identity_fields():
    event = FactoryJobEvent(
        sequence=1,
        event_type="COMPLETED",
        job_id="JOB-1",
        job_fingerprint="a" * 64,
        worker_id="worker",
        station="discovery",
        phase="DISCOVERY",
        detail="done",
        output_artifact="EVIDENCE-1",
        occurred_utc="2026-10-07T00:00:00+00:00",
        event_fingerprint="",
        research_run_fingerprint="b" * 64,
    )
    event_fp = hashlib.sha256(
        event.as_dict(include_fingerprint=False).encode()
        if isinstance(event.as_dict(include_fingerprint=False), str)
        else str(event.as_dict(include_fingerprint=False)).encode()
    ).hexdigest()
    # Use the ledger to obtain the canonical event fingerprint.
    ledger = FactoryJobEventLedger(path=None)
    ledger.append(
        event_type="COMPLETED",
        job_id="JOB-1",
        job_fingerprint="a" * 64,
        worker_id="worker",
        station="discovery",
        phase="DISCOVERY",
        detail="done",
        output_artifact="EVIDENCE-1",
        research_run_fingerprint="b" * 64,
    )
    handoff = build_research_handoff(
        events=ledger,
        job_id="JOB-1",
        source_station="discovery",
        destination_station="stability",
        dataset_content_sha256="c" * 64,
        dataset_artifact_id="MT5-M1-TEST",
    )
    assert handoff.dataset_content_sha256 == "c" * 64
    assert handoff.dataset_artifact_id == "MT5-M1-TEST"
