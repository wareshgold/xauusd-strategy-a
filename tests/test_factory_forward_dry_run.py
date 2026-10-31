from __future__ import annotations

import hashlib
from types import SimpleNamespace

from strategy_factory.dataset_provenance import DatasetProvenanceStatus
from pathlib import Path

from strategy_factory.forward_gate_factory import ForwardGateResult
from strategy_factory.forward_orchestration import run_factory_bound_forward
from strategy_factory.forward_runtime_adapter import (
    require_runner_process_success,
    run_existing_forward_runner_dry_run,
    run_existing_forward_runner_production_dry_run,
    runner_process_reconciliation,
)
from strategy_factory.forward_session_factory import DemoForwardSessionFactory
from strategy_factory.models import GateResult, GateStatus, StrategyPassport
from strategy_factory.manifest import EvidenceStatus, RuleAuthority, StrategyManifest, StrategyRule
from strategy_factory.snapshot import build_readiness_snapshot
from strategy_factory.source_ledger import SourceResolutionLedger


class SyntheticHoldoutRecord:
    strategy_id = "SP2L-A"
    strategy_revision = "REV-DRY-RUN-1"
    manifest_revision = "MANIFEST-DRY-RUN-1"
    execution_semantics = "BAR_CLOSE_RESEARCH"
    dataset_id = "HOLDOUT-DRY-RUN-1"

    def validate(self):
        return None


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _readiness_bundle(record):
    manifest = StrategyManifest(
        strategy_id=record.strategy_id,
        revision=record.manifest_revision,
        rules=[
            StrategyRule(
                rule_id="SYNTHETIC-RUNTIME-RULE",
                name="Synthetic test-only rule",
                authority=RuleAuthority.CANONICAL,
                evidence_status=EvidenceStatus.SOURCE_CONFIRMED,
            )
        ],
    )
    passport = StrategyPassport(
        strategy_id=record.strategy_id,
        source_revision=record.manifest_revision,
        geometry_revision="SYNTHETIC-TEST-GEOMETRY",
        code_revision="SYNTHETIC-TEST-CODE",
        data_revision="SYNTHETIC-TEST-DATA",
        execution_model="BAR_CLOSE_RESEARCH_ONLY",
        parameter_set={"synthetic_test_only": True},
        canonical=True,
    )
    ledger = SourceResolutionLedger()
    snapshot = build_readiness_snapshot(manifest, passport, ledger)
    return snapshot, manifest, passport, ledger


def _synthetic_holdout_result(record, snapshot, content_sha, artifact_id):
    record.snapshot_fingerprint = snapshot.fingerprint
    dataset_fingerprint = _sha(b"synthetic-holdout-dataset-fingerprint")
    run = SimpleNamespace(
        run_id=record.run_id,
        dataset_role="FRESH_HOLDOUT",
        dataset_id=record.dataset_id,
        artifact_id=artifact_id,
        dataset_fingerprint=dataset_fingerprint,
    )
    provenance = SimpleNamespace(
        status=DatasetProvenanceStatus.PASS,
        observed_artifact_id=artifact_id,
        registered_artifact_id=artifact_id,
        dataset_id=record.dataset_id,
        registered_fingerprint=dataset_fingerprint,
        observed_fingerprint=dataset_fingerprint,
    )
    result = SimpleNamespace(
        accepted=True,
        job_id=record.run_id,
        run=run,
        record=record,
        dataset_provenance=provenance,
    )
    job = SimpleNamespace(job_id=record.run_id)
    return SimpleNamespace(
        job=job,
        result=result,
        holdout_dataset_content_sha256=content_sha,
    )


def _session():
    record = SyntheticHoldoutRecord()
    readiness_snapshot, readiness_manifest, readiness_passport, readiness_ledger = _readiness_bundle(record)
    holdout_sha = _sha(b"dry-run-holdout")
    holdout_artifact = "HOLDOUT-DRY-RUN-ART-1"
    holdout_result = _synthetic_holdout_result(record, readiness_snapshot, holdout_sha, holdout_artifact)
    gate = ForwardGateResult(
        holdout_result=holdout_result,
        readiness_snapshot=readiness_snapshot,
        readiness_manifest=readiness_manifest,
        readiness_passport=readiness_passport,
        readiness_ledger=readiness_ledger,
        gate=GateResult(
            name="FRESH_HOLDOUT_TO_FORWARD",
            status=GateStatus.PASS,
            evidence="dry-run-evidence",
            details={
                "source_station": "holdout",
                "destination_station": "forward",
                "forward_session_id": "FORWARD-DRY-RUN-SESSION-1",
                "forward_dataset_id": "FORWARD-DRY-RUN-DATA-1",
                "forward_artifact_id": "FORWARD-DRY-RUN-ART-1",
                "forward_dataset_sha256": _sha(b"dry-run-forward"),
                "strategy_revision": record.strategy_revision,
                "manifest_revision": record.manifest_revision,
                "holdout_dataset_id": record.dataset_id,
                "holdout_dataset_sha256": holdout_sha,
                "holdout_artifact_id": holdout_artifact,
                "handoff_fingerprint": _sha(b"dry-run-handoff"),
                "production_decision": False,
            },
        )
    )
    return DemoForwardSessionFactory().prepare(
        gate=gate,
        source_record=record,
        session_id="FORWARD-DRY-RUN-SESSION-1",
        forward_dataset_id="FORWARD-DRY-RUN-DATA-1",
        forward_dataset_artifact_id="FORWARD-DRY-RUN-ART-1",
        forward_dataset_content_sha256=_sha(b"dry-run-forward"),
    ).session


def test_end_to_end_factory_dry_run_uses_process_adapter_without_mt5():
    process_result = run_existing_forward_runner_dry_run(duration_seconds=1)
    require_runner_process_success(process_result)

    process_facts = runner_process_reconciliation(process_result)
    assert process_result.returncode == 0
    assert "SP2L_FACTORY_DRY_RUN=1" in process_result.stdout
    assert "FORWARD_TEST_SECONDS=1" in process_result.stdout
    assert "observed_positions" not in process_facts

    def reconcile(result):
        assert result is process_result
        return {
            "reconciliation_id": "RECON-DRY-RUN-1",
            "broker_server": "SYNTHETIC-MT5",
            "symbol": "XAUUSD.ecn",
            "observed_positions": 0,
            "matched_positions": 0,
            "mismatched_positions": 0,
            "detail": "synthetic broker observation; no MT5 access",
        }

    result = run_factory_bound_forward(
        session=_session(),
        run_forward=lambda: process_result,
        reconcile=reconcile,
        started_utc="2026-10-07T07:00:00Z",
        running_utc="2026-10-07T07:00:01Z",
        completed_utc="2026-10-07T07:00:02Z",
    )

    assert result.reconciled is True
    assert result.production_decision is False
    assert result.runtime.runner_result is process_result
    assert [event.state.value for event in result.runtime.lifecycle_events] == [
        "STARTED",
        "RUNNING",
        "COMPLETED",
    ]


def test_production_like_dry_run_forces_execution_off(tmp_path: Path):
    runner = tmp_path / "runner.py"
    runner.write_text(
        "import os\n"
        "print(os.getenv('SP2L_FACTORY_DRY_RUN'))\n"
        "print(os.getenv('LIVE_TRADING_ENABLE'))\n"
        "print(os.getenv('ALLOW_REAL_EXECUTION'))\n",
        encoding="utf-8",
    )

    result = run_existing_forward_runner_production_dry_run(
        repo_root=tmp_path,
        duration_seconds=1,
        runner_relative_path="runner.py",
        env_overrides={
            "SP2L_FACTORY_DRY_RUN": "0",
            "LIVE_TRADING_ENABLE": "true",
            "ALLOW_REAL_EXECUTION": "true",
        },
    )

    require_runner_process_success(result)
    assert result.stdout.splitlines() == ["1", "false", "false"]
