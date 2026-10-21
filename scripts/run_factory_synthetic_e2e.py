from __future__ import annotations

"""Run one complete synthetic Factory job through the real research wiring.

This is a wiring/integration demonstration only. It uses a deterministic
synthetic adapter and isolated demo telemetry/journal files. It does not
evaluate Strategy A geometry, consume Holdout/Forward data, start MT5, or
create production BUY/SELL decisions.
"""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from strategy_factory.adapter import build_execution_receipt  # noqa: E402
from strategy_factory.datasets import DatasetRegistry, fingerprint_dataset  # noqa: E402
from strategy_factory.evidence import EvidenceLedger  # noqa: E402
from strategy_factory.job_events import FactoryJobEventLedger  # noqa: E402
from strategy_factory.jobs import ResearchJobSpec  # noqa: E402
from strategy_factory.metrics import ResearchMetrics  # noqa: E402
from strategy_factory.orchestrator import (  # noqa: E402
    FactoryOrchestrator,
    RunnerExecutionContext,
    build_runner_executor,
)
from strategy_factory.research_record import ResearchRecordLedger  # noqa: E402
from strategy_factory.runs import ResearchRunLedger  # noqa: E402
from strategy_factory.snapshot import ReadinessSnapshot  # noqa: E402
from strategy_factory.test_contract import (  # noqa: E402
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
)
from strategy_factory.telemetry import publish_workers  # noqa: E402
from strategy_factory.usage import DatasetUsageLedger  # noqa: E402
from strategy_factory.worker import FactoryWorker, FactoryWorkerFleet  # noqa: E402

DEFAULT_STATUS = ROOT / "runtime" / "factory_synthetic_e2e_status.json"
DEFAULT_JOURNAL = ROOT / "runtime" / "factory_synthetic_e2e_job_events.jsonl"
LIVE_STATUS = ROOT / "runtime" / "factory_worker_status.json"
LIVE_JOURNAL = ROOT / "runtime" / "factory_job_events.jsonl"
PRESERVED_DEMO_STATUS = ROOT / "runtime" / "factory_demo_status.json"


class DeterministicSyntheticAdapter:
    """Return a fixed receipt for wiring validation; never defines SP2L rules."""

    engine_revision = "SYNTHETIC-ENGINE-1"

    def __init__(self, input_fingerprint: str) -> None:
        self.input_fingerprint = input_fingerprint

    def execute(self, spec: HistoricalTestSpec):
        return build_execution_receipt(
            execution_id=f"EXEC-{spec.test_id}",
            spec=spec,
            engine_revision=self.engine_revision,
            input_fingerprint=self.input_fingerprint,
            metrics=ResearchMetrics(
                trades=4,
                decisive_trades=4,
                wins=3,
                losses=1,
                ambiguous=0,
                win_rate=0.75,
                net_r=2.0,
                profit_factor=3.0,
                max_drawdown_r=1.0,
                gross_profit_r=3.0,
                gross_loss_r=-1.0,
            ),
        )


def _readiness_snapshot(spec: HistoricalTestSpec) -> ReadinessSnapshot:
    source_ledger = {"entries": [], "resolution_state": "SYNTHETIC_ONLY"}
    source_readiness = {"status": "SYNTHETIC_ONLY"}
    passport_eligibility = {"status": "SYNTHETIC_ONLY"}
    manifest_fingerprint = "1" * 64
    passport_fingerprint = "2" * 64
    payload = ReadinessSnapshot._fingerprint_payload(
        snapshot_revision="READINESS-SNAPSHOT-SYNTH-E2E-1",
        strategy_id=spec.strategy_id,
        manifest_revision="MANIFEST-SYNTH-E2E-1",
        manifest_fingerprint=manifest_fingerprint,
        passport_fingerprint=passport_fingerprint,
        source_ledger=source_ledger,
        source_readiness=source_readiness,
        passport_eligibility=passport_eligibility,
    )
    return ReadinessSnapshot(
        snapshot_revision="READINESS-SNAPSHOT-SYNTH-E2E-1",
        strategy_id=spec.strategy_id,
        manifest_revision="MANIFEST-SYNTH-E2E-1",
        manifest_fingerprint=manifest_fingerprint,
        passport_fingerprint=passport_fingerprint,
        source_ledger=source_ledger,
        source_readiness=source_readiness,
        passport_eligibility=passport_eligibility,
        fingerprint=hashlib.sha256(payload).hexdigest(),
    )


def _build_spec_and_job(run_id: str):
    payload = b"SP2L-FACTORY-SYNTHETIC-FIXTURE-V1\n"
    content_sha256 = hashlib.sha256(payload).hexdigest()
    dataset = TestDataset(
        dataset_id="SYNTHETIC-FIXTURE-E2E-001",
        role=DatasetRole.DEVELOPMENT,
        data_revision="FIXTURE-E2E-1",
        start="2026-01-01T00:00:00Z",
        end="2026-01-02T00:00:00Z",
        source="synthetic://sp2l/factory-e2e-v1",
    )
    spec = HistoricalTestSpec(
        test_id="SYNTHETIC_FACTORY_E2E_V1",
        strategy_id="SP2L-A",
        strategy_revision="REV-SYNTH-E2E-1",
        dataset=dataset,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"research_only": True, "fixture_only": True},
    )
    dataset_fingerprint = fingerprint_dataset(dataset, content_sha256)
    job = ResearchJobSpec.from_test_spec(
        spec,
        manifest_revision="MANIFEST-SYNTH-E2E-1",
        dataset_fingerprint=dataset_fingerprint,
        job_id=run_id,
    )
    return payload, content_sha256, spec, job, dataset_fingerprint


def run_synthetic_e2e(
    *,
    status_path: Path = DEFAULT_STATUS,
    journal_path: Path = DEFAULT_JOURNAL,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Execute a single synthetic job and persist its demo-only observability."""
    status_path = Path(status_path).resolve()
    journal_path = Path(journal_path).resolve()
    protected_paths = {
        LIVE_STATUS.resolve(),
        LIVE_JOURNAL.resolve(),
        PRESERVED_DEMO_STATUS.resolve(),
    }
    if status_path in protected_paths or journal_path in protected_paths:
        raise ValueError(
            "synthetic E2E refuses to overwrite live or pre-existing Factory runtime paths; "
            "use the dedicated synthetic_e2e paths or another isolated location"
        )
    if status_path == journal_path:
        raise ValueError("demo status and journal must use separate files")

    timestamp = now or datetime.now(timezone.utc)
    if timestamp.tzinfo is None or timestamp.utcoffset() != timezone.utc.utcoffset(timestamp):
        raise ValueError("run timestamp must be timezone-aware UTC")
    run_id = f"SYNTH-E2E-{timestamp.strftime('%Y%m%dT%H%M%S%fZ')}"
    payload, content_sha256, spec, job, dataset_fingerprint = _build_spec_and_job(run_id)
    if hashlib.sha256(payload).hexdigest() != content_sha256:
        raise AssertionError("synthetic fixture content hash mismatch")

    registry = DatasetRegistry()
    registry.register(spec.dataset, content_sha256)
    usage = DatasetUsageLedger(registry)
    runs = ResearchRunLedger(registry, usage)
    evidence = EvidenceLedger(runs)
    records = ResearchRecordLedger()
    from strategy_factory.runner import ResearchJobRunner

    runner = ResearchJobRunner(runs=runs, evidence=evidence, records=records)
    adapter = DeterministicSyntheticAdapter(content_sha256)
    snapshot = _readiness_snapshot(spec)
    worker = FactoryWorker("SYNTH-W01")
    fleet = FactoryWorkerFleet([worker], status_path=status_path)
    events = FactoryJobEventLedger(path=journal_path)
    orchestrator = FactoryOrchestrator(fleet=fleet, events=events)

    orchestrator.submit(
        job,
        station="discovery",
        phase="SYNTHETIC_E2E",
        detail="Synthetic-only Factory end-to-end wiring run",
    )
    context = RunnerExecutionContext(
        spec=spec,
        adapter=adapter,
        snapshot=snapshot,
        observed_content_sha256=content_sha256,
        evidence_id=f"SYNTH-EVIDENCE-{run_id}",
    )
    result = orchestrator.run_next(
        worker_id=worker.worker_id,
        execute=build_runner_executor(runner, context),
    )
    record = records.get(job.job_id)
    record.validate()
    handoff = orchestrator.handoff(
        record=record,
        source_station="discovery",
        destination_station="stability",
        detail="Synthetic-only evidence-bound wiring handoff",
        dataset_content_sha256=content_sha256,
        dataset_artifact_id=spec.dataset.dataset_id,
    )
    handoff.validate()
    # Publish the final roster explicitly after the accepted handoff.
    publish_workers([worker.as_dict()], path=status_path)

    return {
        "mode": "SYNTHETIC_ONLY",
        "run_id": run_id,
        "strategy_id": spec.strategy_id,
        "strategy_revision": spec.strategy_revision,
        "dataset_id": spec.dataset.dataset_id,
        "dataset_fingerprint": dataset_fingerprint,
        "dataset_content_sha256": content_sha256,
        "result_accepted": bool(result.get("accepted")),
        "evidence_id": record.evidence_id,
        "provenance_status": record.provenance_status.value,
        "handoff_accepted": bool(handoff),
        "event_types": [event.event_type for event in events.for_job(job.job_id)],
        "worker_state": worker.state,
        "worker_output_artifact": worker.output_artifact,
        "status_path": str(status_path),
        "journal_path": str(journal_path),
        "production_decisions": 0,
        "strategy_edge_claim": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status-file", type=Path, default=DEFAULT_STATUS)
    parser.add_argument("--journal-file", type=Path, default=DEFAULT_JOURNAL)
    args = parser.parse_args(argv)
    report = run_synthetic_e2e(status_path=args.status_file, journal_path=args.journal_file)
    print("SP2L FACTORY — SYNTHETIC END-TO-END RUN")
    print("Scope: software wiring only; no canonical geometry or strategy-edge claim")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("Dashboard mode: set SP2L_FACTORY_DEMO=1 and open the configured dashboard URL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
