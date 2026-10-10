from __future__ import annotations

import hashlib
import json

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.orchestrator import FactoryOrchestrator
from strategy_factory.research_record import ResearchRecord
from strategy_factory.research_provenance import ResearchProvenanceStatus
from strategy_factory.worker import FactoryWorker, FactoryWorkerFleet


def _pass_record() -> ResearchRecord:
    record0 = ResearchRecord(
        record_revision="RESEARCH-RECORD-1",
        run_id="RUN-HANDOFF-TELEMETRY",
        run_fingerprint="b" * 64,
        evidence_id="EVIDENCE-HANDOFF-TELEMETRY",
        evidence_fingerprint="c" * 64,
        snapshot_fingerprint="d" * 64,
        audit_fingerprint="e" * 64,
        strategy_id="SP2L",
        strategy_revision="REV-1",
        manifest_revision="MANIFEST-1",
        dataset_id="DATA-1",
        dataset_role="RESEARCH",
        data_revision="DATA-REV-1",
        dataset_fingerprint="f" * 64,
        execution_semantics="HISTORICAL",
        provenance_status=ResearchProvenanceStatus.PASS,
        provenance_reasons=(),
        fingerprint="",
    )
    payload = json.dumps(
        record0.as_dict(include_fingerprint=False),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return ResearchRecord.from_dict(
        {
            **record0.as_dict(include_fingerprint=False),
            "fingerprint": hashlib.sha256(payload).hexdigest(),
        }
    )


def test_handoff_telemetry_failure_does_not_hide_durable_handoff(monkeypatch):
    ledger = FactoryJobEventLedger(path=None)
    record = _pass_record()
    ledger.append(
        event_type="COMPLETED",
        job_id=record.run_id,
        job_fingerprint=record.run_fingerprint,
        station="discovery",
        phase="DISCOVERY",
        output_artifact=record.evidence_id,
        research_run_fingerprint=record.run_fingerprint,
    )
    fleet = FactoryWorkerFleet(workers=[FactoryWorker(worker_id="W01")])
    orchestrator = FactoryOrchestrator(fleet=fleet, events=ledger)

    def fail_publish():
        raise OSError("injected handoff telemetry publish failure")

    monkeypatch.setattr(fleet, "publish", fail_publish)

    handoff = orchestrator.handoff(
        record=record,
        source_station="discovery",
        destination_station="stability",
    )

    assert handoff.output_artifact == record.evidence_id
    assert [event.event_type for event in ledger.entries()] == [
        "COMPLETED",
        "HANDOFF_ACCEPTED",
    ]
    assert orchestrator.telemetry_errors == [
        {
            "job_id": record.run_id,
            "worker_id": "",
            "operation": "publish_after_handoff",
            "error_type": "OSError",
            "error": "injected handoff telemetry publish failure",
        }
    ]
