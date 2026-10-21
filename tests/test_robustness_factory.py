from __future__ import annotations

import hashlib

from strategy_factory.adapter import build_execution_receipt
from strategy_factory.datasets import DatasetArtifact, DatasetRegistry
from strategy_factory.evidence import EvidenceLedger
from strategy_factory.handoff import build_research_handoff
from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.research_record import ResearchRecordLedger
from strategy_factory.robustness_factory import (
    RobustnessFactory,
    RobustnessFactoryContext,
    RobustnessFactoryError,
)
from strategy_factory.runs import ResearchRunLedger
from strategy_factory.snapshot import ReadinessSnapshot
from strategy_factory.test_contract import (
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
)
from strategy_factory.usage import DatasetUsageLedger
from strategy_factory.runner import ResearchJobRunner


def _snapshot(spec, *, snapshot_revision="SYNTH"):
    ledger = {"entries": [], "resolution_state": "SYNTHETIC_ONLY"}
    readiness = {"status": "SYNTHETIC_ONLY"}
    eligibility = {"status": "SYNTHETIC_ONLY"}
    payload = ReadinessSnapshot._fingerprint_payload(
        snapshot_revision=snapshot_revision,
        strategy_id=spec.strategy_id,
        manifest_revision="MANIFEST",
        manifest_fingerprint="1" * 64,
        passport_fingerprint="2" * 64,
        source_ledger=ledger,
        source_readiness=readiness,
        passport_eligibility=eligibility,
    )
    return ReadinessSnapshot(
        snapshot_revision=snapshot_revision,
        strategy_id=spec.strategy_id,
        manifest_revision="MANIFEST",
        manifest_fingerprint="1" * 64,
        passport_fingerprint="2" * 64,
        source_ledger=ledger,
        source_readiness=readiness,
        passport_eligibility=eligibility,
        fingerprint=hashlib.sha256(payload).hexdigest(),
    )


class FakeAdapter:
    engine_revision = "ROBUSTNESS-TEST"

    def execute(self, spec):
        return build_execution_receipt(
            execution_id="ROBUSTNESS-EXEC",
            spec=spec,
            engine_revision=self.engine_revision,
            input_fingerprint="a" * 64,
            metrics=ResearchMetrics(
                trades=2, decisive_trades=2, wins=1, losses=1, ambiguous=0,
                win_rate=0.5, net_r=0.0, profit_factor=1.0,
                max_drawdown_r=1.0, gross_profit_r=1.0, gross_loss_r=-1.0,
            ),
        )


def _context(tmp_path, *, wrong_sha=False):
    raw = b'{"schema_version":1,"research_only":true,"bars":[]}'
    path = tmp_path / "m1.json"
    path.write_bytes(raw)
    sha = hashlib.sha256(raw).hexdigest()
    artifact_id = "MT5-M1-ROBUST"

    dataset = TestDataset(
        dataset_id="MT5-DEV-001",
        role=DatasetRole.DEVELOPMENT,
        data_revision="MT5-M1-TEST",
        start="2026-10-05T00:00:00Z",
        end="2026-10-07T05:30:00Z",
        source="MT5:XAUUSD.ecn:M1",
    )
    spec = HistoricalTestSpec(
        test_id="ROBUSTNESS_FACTORY_TEST",
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
    registry.register(dataset, sha, lock=True, artifact=DatasetArtifact(
        artifact_id=artifact_id, location=str(path), content_sha256=sha,
        byte_size=len(raw), format="json",
    ))
    job = ResearchJobSpec.from_test_spec(
        spec, manifest_revision="MANIFEST",
        dataset_fingerprint=registry.get(dataset.dataset_id).fingerprint,
        job_id="STABILITY-001",
    )
    upstream = ResearchJobRunner(runs=runs, evidence=evidence, records=records)
    upstream_result = upstream.run(
        job=job, spec=spec, adapter=FakeAdapter(), snapshot=_snapshot(spec),
        observed_content_sha256=sha,
        observed_artifact=registry.get(dataset.dataset_id).artifact,
        evidence_id="STABILITY-EVIDENCE-001",
        purpose="STABILITY",
    )

    events = FactoryJobEventLedger(path=None)
    event = events.append(
        event_type="COMPLETED", job_id=job.job_id, job_fingerprint=job.fingerprint,
        worker_id="worker", station="stability", phase="STABILITY",
        detail="done", output_artifact=upstream_result.evidence.evidence_id,
        research_run_fingerprint=upstream_result.run.fingerprint,
    )
    handoff_sha = ("b" * 64) if wrong_sha else sha
    handoff = build_research_handoff(
        events=events, job_id=job.job_id, source_station="stability",
        destination_station="robustness", record=upstream_result.record,
        dataset_content_sha256=handoff_sha, dataset_artifact_id=artifact_id,
    )

    # Use a correctly wired fresh runner for the downstream Robustness job.
    registry2 = DatasetRegistry()
    usage2 = DatasetUsageLedger(registry2)
    runs2 = ResearchRunLedger(registry2, usage2)
    evidence2 = EvidenceLedger(runs2)
    records2 = ResearchRecordLedger()
    runner = ResearchJobRunner(runs=runs2, evidence=evidence2, records=records2)

    return runner, RobustnessFactoryContext(
        spec=spec, manifest_revision="MANIFEST", job_id="ROBUSTNESS-001",
        readiness_snapshot=_snapshot(spec), handoff=handoff,
        source_record=upstream_result.record, source_event=event,
        dataset_artifact_path=path, dataset_artifact_id=artifact_id,
        dataset_content_sha256=sha, adapter=FakeAdapter(),
    )


def test_robustness_factory_is_dataset_bound(tmp_path):
    runner, context = _context(tmp_path)
    result = RobustnessFactory(runner).prepare_and_run(context)
    assert result.result.accepted is True
    assert result.result.dataset_provenance.status.value == "PASS"


def test_robustness_factory_blocks_dataset_mismatch(tmp_path):
    runner, context = _context(tmp_path, wrong_sha=True)
    try:
        RobustnessFactory(runner).prepare_and_run(context)
    except RobustnessFactoryError as exc:
        assert "dataset SHA" in str(exc)
    else:
        raise AssertionError("dataset mismatch must be rejected")

def test_robustness_factory_rejects_readiness_snapshot_drift(tmp_path):
    from dataclasses import replace

    runner, context = _context(tmp_path)
    drifted = replace(
        context,
        readiness_snapshot=_snapshot(context.spec, snapshot_revision="DRIFTED"),
    )
    try:
        RobustnessFactory(runner).prepare_and_run(drifted)
    except RobustnessFactoryError as exc:
        assert "snapshot fingerprint" in str(exc)
    else:
        raise AssertionError("snapshot drift must be rejected")
