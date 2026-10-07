from __future__ import annotations

import hashlib

from strategy_factory.adapter import build_execution_receipt
from strategy_factory.datasets import DatasetArtifact, DatasetRegistry
from strategy_factory.evidence import EvidenceLedger
from strategy_factory.handoff import build_research_handoff
from strategy_factory.holdout_factory import (
    HoldoutFactory,
    HoldoutFactoryContext,
    HoldoutFactoryError,
)
from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.research_record import ResearchRecordLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.runs import ResearchRunLedger
from strategy_factory.runner import ResearchJobRunner
from strategy_factory.snapshot import ReadinessSnapshot
from strategy_factory.test_contract import (
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
)
from strategy_factory.usage import DatasetUsageLedger


def _snapshot(spec):
    ledger = {"entries": [], "resolution_state": "SYNTHETIC_ONLY"}
    readiness = {"status": "SYNTHETIC_ONLY"}
    eligibility = {"status": "SYNTHETIC_ONLY"}
    payload = ReadinessSnapshot._fingerprint_payload(
        snapshot_revision="SYNTH",
        strategy_id=spec.strategy_id,
        manifest_revision="MANIFEST",
        manifest_fingerprint="1" * 64,
        passport_fingerprint="2" * 64,
        source_ledger=ledger,
        source_readiness=readiness,
        passport_eligibility=eligibility,
    )
    return ReadinessSnapshot(
        snapshot_revision="SYNTH",
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
    engine_revision = "HOLDOUT-TEST"

    def execute(self, spec):
        return build_execution_receipt(
            execution_id="HOLDOUT-EXEC",
            spec=spec,
            engine_revision=self.engine_revision,
            input_fingerprint="a" * 64,
            metrics=ResearchMetrics(
                trades=2, decisive_trades=2, wins=1, losses=1, ambiguous=0,
                win_rate=0.5, net_r=0.0, profit_factor=1.0,
                max_drawdown_r=1.0, gross_profit_r=1.0, gross_loss_r=-1.0,
            ),
        )


def _context(tmp_path, *, same_dataset=False, frozen=True, strategy_revision="REV-TEST"):
    tmp_path.mkdir(parents=True, exist_ok=True)
    raw_source = b'{"schema_version":1,"research_only":true,"bars":[1]}'
    raw_holdout = b'{"schema_version":1,"research_only":true,"bars":[2]}'
    source_path = tmp_path / "robustness.json"
    holdout_path = tmp_path / "holdout.json"
    source_path.write_bytes(raw_source)
    holdout_path.write_bytes(raw_source if same_dataset else raw_holdout)

    source_sha = hashlib.sha256(raw_source).hexdigest()
    holdout_sha = hashlib.sha256(holdout_path.read_bytes()).hexdigest()
    source_artifact_id = "MT5-ROBUST-001"
    holdout_artifact_id = source_artifact_id if same_dataset else "MT5-HOLDOUT-001"

    source_dataset = TestDataset(
        dataset_id="MT5-ROBUST-001",
        role=DatasetRole.DEVELOPMENT,
        data_revision="MT5-M1-ROBUST",
        start="2026-10-05T00:00:00Z",
        end="2026-10-07T05:30:00Z",
        source="MT5:XAUUSD.ecn:M1",
    )
    holdout_dataset = TestDataset(
        dataset_id="MT5-HOLDOUT-001",
        role=DatasetRole.FRESH_HOLDOUT,
        data_revision="MT5-M1-HOLDOUT",
        start="2026-10-07T05:31:00Z",
        end="2026-10-08T05:30:00Z",
        source="MT5:XAUUSD.ecn:M1",
        immutable=True,
    )
    source_spec = HistoricalTestSpec(
        test_id="ROBUSTNESS_TEST",
        strategy_id="SP2L-A",
        strategy_revision="REV-TEST",
        dataset=source_dataset,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"research_only": True},
    )
    holdout_spec = HistoricalTestSpec(
        test_id="HOLDOUT_FACTORY_TEST",
        strategy_id="SP2L-A",
        strategy_revision=strategy_revision,
        dataset=holdout_dataset,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"research_only": True},
    )

    registry = DatasetRegistry()
    usage = DatasetUsageLedger(registry)
    runs = ResearchRunLedger(registry, usage)
    evidence = EvidenceLedger(runs)
    records = ResearchRecordLedger()
    registry.register(
        source_dataset,
        source_sha,
        lock=True,
        artifact=DatasetArtifact(
            artifact_id=source_artifact_id,
            location=str(source_path),
            content_sha256=source_sha,
            byte_size=len(raw_source),
            format="json",
        ),
    )
    upstream_job = ResearchJobSpec.from_test_spec(
        source_spec,
        manifest_revision="MANIFEST",
        dataset_fingerprint=registry.get(source_dataset.dataset_id).fingerprint,
        job_id="ROBUSTNESS-001",
    )
    upstream_runner = ResearchJobRunner(runs=runs, evidence=evidence, records=records)
    upstream_result = upstream_runner.run(
        job=upstream_job,
        spec=source_spec,
        adapter=FakeAdapter(),
        snapshot=_snapshot(source_spec),
        observed_content_sha256=source_sha,
        observed_artifact=registry.get(source_dataset.dataset_id).artifact,
        evidence_id="ROBUSTNESS-EVIDENCE-001",
        purpose="ROBUSTNESS",
    )

    events = FactoryJobEventLedger(path=None)
    event = events.append(
        event_type="COMPLETED",
        job_id=upstream_job.job_id,
        job_fingerprint=upstream_job.fingerprint,
        worker_id="worker",
        station="robustness",
        phase="ROBUSTNESS",
        detail="done",
        output_artifact=upstream_result.evidence.evidence_id,
        research_run_fingerprint=upstream_result.run.fingerprint,
    )
    handoff = build_research_handoff(
        events=events,
        job_id=upstream_job.job_id,
        source_station="robustness",
        destination_station="holdout",
        record=upstream_result.record,
        dataset_content_sha256=source_sha,
        dataset_artifact_id=source_artifact_id,
    )

    registry2 = DatasetRegistry()
    usage2 = DatasetUsageLedger(registry2)
    runs2 = ResearchRunLedger(registry2, usage2)
    evidence2 = EvidenceLedger(runs2)
    records2 = ResearchRecordLedger()
    runner = ResearchJobRunner(runs=runs2, evidence=evidence2, records=records2)

    return runner, HoldoutFactoryContext(
        spec=holdout_spec,
        manifest_revision="MANIFEST",
        job_id="HOLDOUT-001",
        readiness_snapshot=_snapshot(holdout_spec),
        handoff=handoff,
        source_record=upstream_result.record,
        source_event=event,
        holdout_dataset_artifact_path=holdout_path,
        holdout_dataset_artifact_id=holdout_artifact_id,
        holdout_dataset_content_sha256=holdout_sha,
        adapter=FakeAdapter(),
        strategy_revision_frozen=frozen,
    )


def test_holdout_factory_accepts_fresh_immutable_dataset(tmp_path):
    runner, context = _context(tmp_path)
    result = HoldoutFactory(runner).prepare_and_run(context)
    assert result.result.accepted is True
    assert result.result.dataset_provenance.status.value == "PASS"


def test_holdout_factory_rejects_reused_dataset(tmp_path):
    runner, context = _context(tmp_path, same_dataset=True)
    try:
        HoldoutFactory(runner).prepare_and_run(context)
    except HoldoutFactoryError as exc:
        assert "differ" in str(exc)
    else:
        raise AssertionError("reused Robustness dataset must be rejected")


def test_holdout_factory_rejects_unfrozen_revision(tmp_path):
    runner, context = _context(tmp_path, frozen=False)
    try:
        HoldoutFactory(runner).prepare_and_run(context)
    except HoldoutFactoryError as exc:
        assert "frozen" in str(exc)
    else:
        raise AssertionError("unfrozen Strategy revision must be rejected")


def test_holdout_factory_rejects_revision_mismatch(tmp_path):
    runner, context = _context(tmp_path, strategy_revision="TUNED-REV")
    try:
        HoldoutFactory(runner).prepare_and_run(context)
    except HoldoutFactoryError as exc:
        assert "strategy_revision" in str(exc)
    else:
        raise AssertionError("holdout must use the frozen upstream revision")


def test_holdout_factory_is_deterministic(tmp_path):
    runner1, context1 = _context(tmp_path / "one")
    result1 = HoldoutFactory(runner1).prepare_and_run(context1)

    runner2, context2 = _context(tmp_path / "two")
    result2 = HoldoutFactory(runner2).prepare_and_run(context2)

    assert result1.job.as_dict() == result2.job.as_dict()
    assert result1.job.fingerprint == result2.job.fingerprint
