from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from strategy_factory.adapter import build_execution_receipt
from strategy_factory.datasets import DatasetArtifact, DatasetRegistry
from strategy_factory.evidence import EvidenceLedger
from strategy_factory.execution import ExecutionReceipt
from strategy_factory.handoff import ResearchHandoff, build_research_handoff
from strategy_factory.job_events import FactoryJobEvent, FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.usage import DatasetUsageLedger
from strategy_factory.research_record import ResearchRecord
from strategy_factory.runs import ResearchRunLedger
from strategy_factory.runner import ResearchJobRunner
from strategy_factory.snapshot import ReadinessSnapshot
from strategy_factory.test_contract import (
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
)
from strategy_factory.validation_factory import (
    ValidationFactory,
    ValidationFactoryContext,
    ValidationFactoryError,
)


class FakeAdapter:
    engine_revision = "TEST-VALIDATION-1"

    def execute(self, spec: HistoricalTestSpec) -> ExecutionReceipt:
        metrics = ResearchMetrics(
            trades=2,
            decisive_trades=2,
            wins=1,
            losses=1,
            ambiguous=0,
            win_rate=0.5,
            net_r=0.0,
            profit_factor=1.0,
            max_drawdown_r=1.0,
            gross_profit_r=1.0,
            gross_loss_r=-1.0,
        )
        return build_execution_receipt(
            execution_id="VALIDATION-EXEC-1",
            spec=spec,
            engine_revision=self.engine_revision,
            input_fingerprint="a" * 64,
            metrics=metrics,
        )


def _context(tmp_path: Path, *, same_dataset: bool = False):
    discovery_sha = "1" * 64
    validation_bytes = b"validation-dataset"
    validation_sha = hashlib.sha256(validation_bytes).hexdigest()
    source_artifact = DatasetArtifact(
        artifact_id="MT5-M1-" + discovery_sha[:16],
        location="discovery.json",
        content_sha256=discovery_sha,
        byte_size=1,
        format="json",
    )
    validation_artifact_id = (
        source_artifact.artifact_id if same_dataset else "MT5-M1-" + validation_sha[:16]
    )

    dataset_path = tmp_path / "validation.json"
    dataset_path.write_bytes(validation_bytes)

    dataset_registry = DatasetRegistry()
    runs = ResearchRunLedger(dataset_registry, DatasetUsageLedger(dataset_registry))
    evidence = EvidenceLedger(runs)
    runner = ResearchJobRunner(runs=runs, evidence=evidence)

    source_dataset = TestDataset(
        dataset_id="DEV-M1",
        role=DatasetRole.DEVELOPMENT,
        data_revision="DEV-1",
        start="2026-10-05T00:00:00+00:00",
        end="2026-10-07T00:00:00+00:00",
        source="MT5",
        immutable=True,
    )
    source_spec = HistoricalTestSpec(
        test_id="DISCOVERY-1",
        strategy_id="SP2L-A",
        strategy_revision="FROZEN-1",
        dataset=source_dataset,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
    )
    source_job = ResearchJobSpec.from_test_spec(
        source_spec,
        manifest_revision="M-1",
        dataset_fingerprint="2" * 64,
        job_id="DISCOVERY-1",
    )

    source_event = FactoryJobEvent(
        sequence=1,
        event_type="COMPLETED",
        job_id="DISCOVERY-1",
        job_fingerprint=source_job.fingerprint,
        worker_id="worker-1",
        station="stability",
        phase="STABILITY",
        detail="Stability completed",
        output_artifact="EVIDENCE-DISCOVERY-1",
        occurred_utc="2026-10-07T00:00:00+00:00",
        event_fingerprint="",
        research_run_fingerprint="3" * 64,
    )
    event_payload = source_event.as_dict(include_fingerprint=False)
    source_event = FactoryJobEvent(
        **event_payload,
        event_fingerprint=hashlib.sha256(
            __import__("json").dumps(
                event_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            ).encode()
        ).hexdigest(),
    )

    metrics = ResearchMetrics(
        trades=1, decisive_trades=1, wins=1, losses=0, ambiguous=0,
        win_rate=1.0, net_r=1.0, profit_factor=1.0, max_drawdown_r=0.0,
        gross_profit_r=1.0, gross_loss_r=0.0,
    )
    # Build a real immutable source record through the existing ledgers so the
    # test exercises the handoff contract rather than fabricating its fingerprint.
    source_run = runs.create(
        source_spec,
        manifest_revision="M-1",
        run_id="DISCOVERY-1",
        observed_fingerprint=discovery_sha,
        purpose="STABILITY",
        artifact=source_artifact,
    )
    receipt = build_execution_receipt(
        execution_id="STABILITY-1",
        spec=source_spec,
        engine_revision="TEST-STABILITY-1",
        input_fingerprint="b" * 64,
        metrics=metrics,
    )
    evidence_bundle = evidence.record(
        __import__("strategy_factory.evidence", fromlist=["EvidenceBundle"]).EvidenceBundle(
            evidence_id="EVIDENCE-DISCOVERY-1",
            run_id=source_run.run_id,
            run_fingerprint=source_run.fingerprint,
            result_revision="TEST",
            metrics=metrics,
            result={"execution_id": receipt.execution_id},
        )
    )
    from strategy_factory.audit import bind_research_audit
    audit = bind_research_audit(
        source_run,
        ReadinessSnapshot(
            snapshot_revision="R-1",
            snapshot_id="SNAP-1",
            strategy_id="SP2L-A",
            strategy_revision="FROZEN-1",
            source_ledger_revision="SOURCE-1",
            source_meaning_status="BLOCKED",
            frozen_geometry_status="BLOCKED",
            production_status="NOT_ELIGIBLE",
            missing_questions=("Q1",),
        ),
        evidence_bundle,
    )
    from strategy_factory.research_provenance import evaluate_research_provenance
    provenance = evaluate_research_provenance(
        spec=source_spec,
        job=source_job,
        run=source_run,
        receipt=receipt,
        evidence=evidence_bundle,
        audit=audit,
        snapshot=audit.snapshot,
        dataset_provenance=__import__(
            "strategy_factory.dataset_provenance",
            fromlist=["evaluate_dataset_provenance"],
        ).evaluate_dataset_provenance(
            source_spec, dataset_registry, discovery_sha, observed_artifact=source_artifact
        ),
    )
    source_record = __import__(
        "strategy_factory.research_record",
        fromlist=["ResearchRecord"],
    ).ResearchRecord.from_components(
        source_run, evidence_bundle, audit.snapshot, audit, provenance
    )
    source_record = __import__(
        "strategy_factory.research_record",
        fromlist=["ResearchRecordLedger"],
    ).ResearchRecordLedger().record(source_record)

    events = FactoryJobEventLedger()
    # The event is deliberately bound to the actual source run fingerprint.
    source_event_payload = source_event.as_dict(include_fingerprint=False)
    source_event = FactoryJobEvent(
        **source_event_payload,
        research_run_fingerprint=source_record.run_fingerprint,
        event_fingerprint=hashlib.sha256(
            __import__("json").dumps(
                {**source_event_payload, "research_run_fingerprint": source_record.run_fingerprint},
                sort_keys=True, separators=(",", ":"), ensure_ascii=True
            ).encode()
        ).hexdigest(),
    )
    events.append(source_event)
    handoff = build_research_handoff(
        events=events,
        job_id="DISCOVERY-1",
        source_station="stability",
        destination_station="validation",
        record=source_record,
        dataset_content_sha256=discovery_sha,
        dataset_artifact_id=source_artifact.artifact_id,
    )

    validation_dataset = TestDataset(
        dataset_id="VALIDATION-M1",
        role=DatasetRole.UNTOUCHED_VALIDATION,
        data_revision="VAL-1",
        start="2026-10-08T00:00:00+00:00",
        end="2026-10-09T00:00:00+00:00",
        source="MT5",
        immutable=True,
    )
    spec = HistoricalTestSpec(
        test_id="VALIDATION-1",
        strategy_id="SP2L-A",
        strategy_revision="FROZEN-1",
        dataset=validation_dataset,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
    )
    if same_dataset:
        validation_sha = discovery_sha

    context = ValidationFactoryContext(
        spec=spec,
        manifest_revision="M-1",
        job_id="VALIDATION-1",
        readiness_snapshot=audit.snapshot,
        handoff=handoff,
        source_record=source_record,
        source_event=source_event,
        validation_dataset_artifact_path=dataset_path,
        validation_dataset_artifact_id=validation_artifact_id,
        validation_dataset_content_sha256=validation_sha,
        adapter=FakeAdapter(),
    )
    return runner, context


def test_validation_factory_requires_untouched_immutable_dataset(tmp_path: Path):
    runner, context = _context(tmp_path)
    result = ValidationFactory(runner).prepare_and_run(context)
    assert result.result.accepted is True
    assert result.result.provenance.status.value == "PASS"


def test_validation_factory_blocks_dataset_reuse(tmp_path: Path):
    runner, context = _context(tmp_path, same_dataset=True)
    with pytest.raises(ValidationFactoryError, match="must differ"):
        ValidationFactory(runner).prepare_and_run(context)
