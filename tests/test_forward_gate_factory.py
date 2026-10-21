from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path

import pytest

from strategy_factory.forward_gate_factory import (
    ForwardGateContext,
    ForwardGateError,
    ForwardGateFactory,
)
from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.handoff import build_research_handoff
from strategy_factory.test_contract import DatasetRole


def _base_context(holdout_record, holdout_event, handoff):
    return ForwardGateContext(
        manifest_revision="MANIFEST",
        readiness_snapshot=holdout_record._test_snapshot,
        handoff=handoff,
        source_record=holdout_record,
        source_event=holdout_event,
        forward_session_id="FWD-20261007-001",
        forward_dataset_id="MT5-FORWARD-001",
        forward_dataset_artifact_id="MT5-FORWARD-ARTIFACT-001",
        forward_dataset_content_sha256="d" * 64,
    )


def _fixture(tmp_path: Path):
    from strategy_factory.adapter import build_execution_receipt
    from strategy_factory.datasets import DatasetArtifact, DatasetRegistry
    from strategy_factory.evidence import EvidenceLedger
    from strategy_factory.metrics import ResearchMetrics
    from strategy_factory.jobs import ResearchJobSpec
    from strategy_factory.research_record import ResearchRecordLedger
    from strategy_factory.runner import ResearchJobRunner
    from strategy_factory.runs import ResearchRunLedger
    from strategy_factory.snapshot import ReadinessSnapshot
    from strategy_factory.usage import DatasetUsageLedger
    from strategy_factory.test_contract import ExecutionSemantics, HistoricalTestSpec, TestDataset

    raw = b'{"schema_version":1,"research_only":true,"bars":[9]}'
    path = tmp_path / "holdout.json"
    path.write_bytes(raw)
    sha = hashlib.sha256(raw).hexdigest()

    dataset = TestDataset(
        dataset_id="MT5-HOLDOUT-001",
        role=DatasetRole.FRESH_HOLDOUT,
        data_revision="MT5-M1-HOLDOUT",
        start="2026-10-07T00:00:00Z",
        end="2026-10-08T00:00:00Z",
        source="MT5:XAUUSD.ecn:M1",
        immutable=True,
    )
    spec = HistoricalTestSpec(
        test_id="HOLDOUT-TEST",
        strategy_id="SP2L-A",
        strategy_revision="REV-TEST",
        dataset=dataset,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"research_only": True},
    )

    registry = DatasetRegistry()
    usage = DatasetUsageLedger(registry)
    runs = ResearchRunLedger(registry, usage)
    evidence = EvidenceLedger(runs)
    records = ResearchRecordLedger()
    artifact = DatasetArtifact(
        artifact_id="MT5-HOLDOUT-ARTIFACT-001",
        location=str(path),
        content_sha256=sha,
        byte_size=len(raw),
        format="json",
    )
    registry.register(dataset, sha, lock=True, artifact=artifact)

    payload = ReadinessSnapshot._fingerprint_payload(
        snapshot_revision="SYNTH",
        strategy_id="SP2L-A",
        manifest_revision="MANIFEST",
        manifest_fingerprint="1" * 64,
        passport_fingerprint="2" * 64,
        source_ledger={"entries": [], "resolution_state": "SYNTHETIC_ONLY"},
        source_readiness={"status": "SYNTHETIC_ONLY"},
        passport_eligibility={"status": "SYNTHETIC_ONLY"},
    )
    snapshot = ReadinessSnapshot(
        snapshot_revision="SYNTH",
        strategy_id="SP2L-A",
        manifest_revision="MANIFEST",
        manifest_fingerprint="1" * 64,
        passport_fingerprint="2" * 64,
        source_ledger={"entries": [], "resolution_state": "SYNTHETIC_ONLY"},
        source_readiness={"status": "SYNTHETIC_ONLY"},
        passport_eligibility={"status": "SYNTHETIC_ONLY"},
        fingerprint=hashlib.sha256(payload).hexdigest(),
    )

    job = ResearchJobSpec.from_test_spec(
        spec,
        manifest_revision="MANIFEST",
        dataset_fingerprint=registry.get(dataset.dataset_id).fingerprint,
        job_id="HOLDOUT-001",
    )

    class Adapter:
        engine_revision = "HOLDOUT-TEST"
        def execute(self, spec):
            return build_execution_receipt(
                execution_id="EXEC-001",
                spec=spec,
                engine_revision=self.engine_revision,
                input_fingerprint="a" * 64,
                metrics=ResearchMetrics(
                    trades=2, decisive_trades=2, wins=1, losses=1, ambiguous=0,
                    win_rate=0.5, net_r=0.0, profit_factor=1.0,
                    max_drawdown_r=1.0, gross_profit_r=1.0, gross_loss_r=-1.0,
                ),
            )

    runner = ResearchJobRunner(runs=runs, evidence=evidence, records=records)
    result = runner.run(
        job=job,
        spec=spec,
        adapter=Adapter(),
        snapshot=snapshot,
        observed_content_sha256=sha,
        observed_artifact=artifact,
        evidence_id="HOLDOUT-EVIDENCE-001",
        purpose="FRESH_HOLDOUT",
    )
    # Keep the snapshot available without expanding the public production
    # context surface solely for this synthetic fixture.
    record = result.record
    object.__setattr__(record, "_test_snapshot", snapshot)

    events = FactoryJobEventLedger(path=None)
    event = events.append(
        event_type="COMPLETED",
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
        worker_id="worker",
        station="holdout",
        phase="FRESH_HOLDOUT",
        detail="done",
        output_artifact=result.evidence.evidence_id,
        research_run_fingerprint=result.run.fingerprint,
    )
    handoff = build_research_handoff(
        events=events,
        job_id=job.job_id,
        source_station="holdout",
        destination_station="forward",
        record=record,
        dataset_content_sha256=sha,
        dataset_artifact_id=artifact.artifact_id,
    )
    return snapshot, record, event, handoff


def _resign_snapshot(snapshot, **changes):
    updated = replace(snapshot, **changes)
    payload = type(updated)._fingerprint_payload(
        snapshot_revision=updated.snapshot_revision,
        strategy_id=updated.strategy_id,
        manifest_revision=updated.manifest_revision,
        manifest_fingerprint=updated.manifest_fingerprint,
        passport_fingerprint=updated.passport_fingerprint,
        source_ledger=updated.source_ledger,
        source_readiness=updated.source_readiness,
        passport_eligibility=updated.passport_eligibility,
    )
    return replace(updated, fingerprint=hashlib.sha256(payload).hexdigest())


def test_forward_gate_accepts_frozen_fresh_holdout(tmp_path):
    snapshot, record, event, handoff = _fixture(tmp_path)
    context = ForwardGateContext(
        manifest_revision="MANIFEST",
        readiness_snapshot=snapshot,
        handoff=handoff,
        source_record=record,
        source_event=event,
        forward_session_id="FWD-20261007-001",
        forward_dataset_id="MT5-FORWARD-001",
        forward_dataset_artifact_id="MT5-FORWARD-ARTIFACT-001",
        forward_dataset_content_sha256="d" * 64,
    )
    result = ForwardGateFactory().prepare(context)
    assert result.passed
    assert result.gate.details["production_decision"] is False


def test_forward_gate_rejects_wrong_route(tmp_path):
    snapshot, record, event, handoff = _fixture(tmp_path)
    bad = type(handoff)(
        **{**handoff.as_dict(include_fingerprint=False),
           "source_station": "robustness",
           "fingerprint": handoff.fingerprint}
    )
    with pytest.raises(Exception):
        ForwardGateFactory().prepare(
            ForwardGateContext("MANIFEST", snapshot, bad, record, event,
                                "FWD", "FWD-DATA", "FWD-ART", "d" * 64)
        )


def test_forward_gate_rejects_post_holdout_tuning(tmp_path):
    snapshot, record, event, handoff = _fixture(tmp_path)
    with pytest.raises(ForwardGateError, match="post-holdout"):
        ForwardGateFactory().prepare(
            ForwardGateContext("MANIFEST", snapshot, handoff, record, event,
                                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
                                post_holdout_tuning=True)
        )


def test_forward_gate_rejects_reused_holdout_identity(tmp_path):
    snapshot, record, event, handoff = _fixture(tmp_path)
    with pytest.raises(ForwardGateError, match="differ"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", snapshot, handoff, record, event,
                "FWD", record.dataset_id, "MT5-HOLDOUT-ARTIFACT-001", 
                handoff.dataset_content_sha256,
            )
        )


def test_forward_gate_rejects_unfrozen_strategy(tmp_path):
    snapshot, record, event, handoff = _fixture(tmp_path)
    with pytest.raises(ForwardGateError, match="frozen"):
        ForwardGateFactory().prepare(
            ForwardGateContext("MANIFEST", snapshot, handoff, record, event,
                                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
                                strategy_revision_frozen=False)
        )



def test_forward_gate_rejects_snapshot_manifest_revision_drift(tmp_path):
    snapshot, record, event, handoff = _fixture(tmp_path)
    drifted = _resign_snapshot(snapshot, manifest_revision="MANIFEST-DRIFT")

    with pytest.raises(ForwardGateError, match="manifest_revision.*snapshot"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", drifted, handoff, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
            )
        )


def test_forward_gate_rejects_snapshot_not_bound_to_holdout_record(tmp_path):
    snapshot, record, event, handoff = _fixture(tmp_path)
    altered = _resign_snapshot(
        snapshot, source_readiness={"status": "BLOCKED", "audit_probe": "changed"}
    )

    with pytest.raises(ForwardGateError, match="snapshot fingerprint"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", altered, handoff, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
            )
        )


def test_forward_gate_rejects_non_hex_forward_dataset_sha(tmp_path):
    snapshot, record, event, handoff = _fixture(tmp_path)

    with pytest.raises(ForwardGateError, match="lowercase hexadecimal SHA-256"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", snapshot, handoff, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "g" * 64,
            )
        )
