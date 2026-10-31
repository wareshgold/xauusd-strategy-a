from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path

import pytest

from strategy_factory.forward_gate_factory import (
    ForwardGateContext,
    ForwardGateError,
    ForwardGateFactory,
)
from strategy_factory.job_events import FactoryJobEvent, FactoryJobEventLedger
from strategy_factory.handoff import build_research_handoff
from strategy_factory.holdout_factory import HoldoutFactoryResult
from strategy_factory.models import GateStatus
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



def _ledger_evidence(events):
    serialized = "".join(
        json.dumps(event.as_dict(), ensure_ascii=False, separators=(",", ":")) + "\n"
        for event in events
    ).encode("utf-8")
    return {
        "source_event_ledger_sha256": hashlib.sha256(serialized).hexdigest(),
        "source_event_ledger_byte_size": len(serialized),
        "source_event_ledger_source": "in_memory",
        "source_event_ledger_path": None,
    }


def _fixture(tmp_path: Path):
    from strategy_factory.adapter import build_execution_receipt
    from strategy_factory.datasets import DatasetArtifact, DatasetRegistry
    from strategy_factory.evidence import EvidenceLedger
    from strategy_factory.metrics import ResearchMetrics
    from strategy_factory.manifest import EvidenceStatus, RuleAuthority, StrategyManifest, StrategyRule
    from strategy_factory.models import StrategyPassport
    from strategy_factory.jobs import ResearchJobSpec
    from strategy_factory.research_record import ResearchRecordLedger
    from strategy_factory.runner import ResearchJobRunner
    from strategy_factory.runs import ResearchRunLedger
    from strategy_factory.snapshot import ReadinessSnapshot, build_readiness_snapshot
    from strategy_factory.source_ledger import SourceResolutionLedger
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

    readiness_manifest = StrategyManifest(
        strategy_id="SP2L-A",
        revision="MANIFEST",
        rules=[StrategyRule(
            rule_id="SYNTHETIC-TEST-RULE",
            name="Synthetic test-only rule",
            authority=RuleAuthority.CANONICAL,
            evidence_status=EvidenceStatus.SOURCE_CONFIRMED,
        )],
    )
    readiness_passport = StrategyPassport(
        strategy_id="SP2L-A",
        source_revision="MANIFEST",
        geometry_revision="SYNTHETIC-TEST-GEOMETRY",
        code_revision="SYNTHETIC-TEST-CODE",
        data_revision="SYNTHETIC-TEST-DATA",
        execution_model="BAR_CLOSE_RESEARCH_ONLY",
        parameter_set={"synthetic_test_only": True},
        canonical=True,
    )
    readiness_ledger = SourceResolutionLedger()
    snapshot = build_readiness_snapshot(readiness_manifest, readiness_passport, readiness_ledger)
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
    object.__setattr__(snapshot, "_test_readiness_sources", (readiness_manifest, readiness_passport, readiness_ledger))

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
    holdout_result = HoldoutFactoryResult(
        job=job,
        result=result,
        holdout_dataset_content_sha256=sha,
    )
    return snapshot, record, event, handoff, holdout_result, events.entries()


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
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
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
        readiness_manifest=readiness_manifest,
        readiness_passport=readiness_passport,
        readiness_ledger=readiness_ledger,
        holdout_result=holdout_result,
                source_event_ledger_snapshot=ledger_snapshot,
                **_ledger_evidence(ledger_snapshot),
    )
    result = ForwardGateFactory().prepare(context)
    assert result.passed
    assert result.gate.details["production_decision"] is False


def test_forward_gate_rejects_correctly_fingerprinted_blocked_readiness(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    blocked = _resign_snapshot(
        snapshot,
        source_readiness={
            "status": "BLOCKED",
            "frozen_geometry_blocked": True,
            "canonical_strategy_eligible": False,
            "production_eligible": False,
        },
        passport_eligibility={
            "source_status": "BLOCKED",
            "frozen_geometry": "BLOCKED",
            "canonical_strategy": "NOT_ELIGIBLE",
            "production": "NOT_ELIGIBLE",
            "blocking_reasons": ["SOURCE_READINESS_BLOCKED"],
        },
    )
    context = ForwardGateContext(
        manifest_revision="MANIFEST",
        readiness_snapshot=blocked,
        handoff=handoff,
        source_record=record,
        source_event=event,
        forward_session_id="FWD-20261007-001",
        forward_dataset_id="MT5-FORWARD-001",
        forward_dataset_artifact_id="MT5-FORWARD-ARTIFACT-001",
        forward_dataset_content_sha256="d" * 64,
        holdout_result=holdout_result,
        source_event_ledger_snapshot=ledger_snapshot,
        **_ledger_evidence(ledger_snapshot),
    )
    with pytest.raises(ForwardGateError, match="source readiness PASS"):
        ForwardGateFactory().prepare(context)


def test_forward_gate_rejects_wrong_route(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    bad = type(handoff)(
        **{**handoff.as_dict(include_fingerprint=False),
           "source_station": "robustness",
           "fingerprint": handoff.fingerprint}
    )
    with pytest.raises(Exception):
        ForwardGateFactory().prepare(
            ForwardGateContext("MANIFEST", snapshot, bad, record, event,
                                "FWD", "FWD-DATA", "FWD-ART", "d" * 64, holdout_result=holdout_result, source_event_ledger_snapshot=ledger_snapshot, **_ledger_evidence(ledger_snapshot))
        )


def test_forward_gate_rejects_post_holdout_tuning(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    with pytest.raises(ForwardGateError, match="post-holdout"):
        ForwardGateFactory().prepare(
            ForwardGateContext("MANIFEST", snapshot, handoff, record, event,
                                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
                holdout_result=holdout_result,
                source_event_ledger_snapshot=ledger_snapshot,
                **_ledger_evidence(ledger_snapshot),
                                post_holdout_tuning=True)
        )


def test_forward_gate_rejects_reused_holdout_identity(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    with pytest.raises(ForwardGateError, match="differ"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", snapshot, handoff, record, event,
                "FWD", record.dataset_id, "MT5-HOLDOUT-ARTIFACT-001", 
                handoff.dataset_content_sha256,
                holdout_result=holdout_result,
                source_event_ledger_snapshot=ledger_snapshot,
                **_ledger_evidence(ledger_snapshot),
            )
        )


def test_forward_gate_rejects_unfrozen_strategy(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    with pytest.raises(ForwardGateError, match="frozen"):
        ForwardGateFactory().prepare(
            ForwardGateContext("MANIFEST", snapshot, handoff, record, event,
                                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
                holdout_result=holdout_result,
                source_event_ledger_snapshot=ledger_snapshot,
                **_ledger_evidence(ledger_snapshot),
                                strategy_revision_frozen=False)
        )



def test_forward_gate_rejects_snapshot_manifest_revision_drift(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    drifted = _resign_snapshot(snapshot, manifest_revision="MANIFEST-DRIFT")

    with pytest.raises(ForwardGateError, match="manifest_revision.*snapshot"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", drifted, handoff, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
                holdout_result=holdout_result,
                source_event_ledger_snapshot=ledger_snapshot,
                **_ledger_evidence(ledger_snapshot),
            )
        )


def test_forward_gate_rejects_snapshot_not_bound_to_holdout_record(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    altered = _resign_snapshot(
        snapshot, source_readiness={"status": "BLOCKED", "audit_probe": "changed"}
    )

    with pytest.raises(ForwardGateError, match="snapshot fingerprint"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", altered, handoff, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
                holdout_result=holdout_result,
                source_event_ledger_snapshot=ledger_snapshot,
                **_ledger_evidence(ledger_snapshot),
            )
        )


def test_forward_gate_rejects_non_hex_forward_dataset_sha(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)

    with pytest.raises(ForwardGateError, match="lowercase hexadecimal SHA-256"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", snapshot, handoff, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "g" * 64,
                holdout_result=holdout_result,
                source_event_ledger_snapshot=ledger_snapshot,
                **_ledger_evidence(ledger_snapshot),
            )
        )




def test_forward_gate_requires_independent_holdout_result_binding(tmp_path):
    snapshot, record, event, handoff, _holdout_result, ledger_snapshot = _fixture(tmp_path)
    with pytest.raises(ForwardGateError, match="HoldoutFactoryResult binding"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", snapshot, handoff, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
            )
        )


def test_forward_gate_rejects_holdout_result_record_mismatch(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    result_with_other_record = replace(
        holdout_result.result, record=replace(record, run_id="OTHER-RUN")
    )
    mismatched_result = replace(holdout_result, result=result_with_other_record)
    with pytest.raises(ForwardGateError, match="does not match the Forward source record"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", snapshot, handoff, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
                holdout_result=mismatched_result,
                source_event_ledger_snapshot=ledger_snapshot,
                **_ledger_evidence(ledger_snapshot),
            )
        )


def test_forward_gate_rejects_holdout_handoff_sha_mismatch(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    payload = handoff.as_dict(include_fingerprint=False)
    payload["dataset_content_sha256"] = "e" * 64
    fingerprint = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()
    altered = replace(handoff, dataset_content_sha256="e" * 64, fingerprint=fingerprint)
    with pytest.raises(ForwardGateError, match="independently observed Holdout result SHA"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", snapshot, altered, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
                holdout_result=holdout_result,
                source_event_ledger_snapshot=ledger_snapshot,
                **_ledger_evidence(ledger_snapshot),
            )
        )


def test_forward_gate_rejects_holdout_handoff_artifact_mismatch(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    payload = handoff.as_dict(include_fingerprint=False)
    payload["dataset_artifact_id"] = "OTHER-ARTIFACT"
    fingerprint = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()
    altered = replace(handoff, dataset_artifact_id="OTHER-ARTIFACT", fingerprint=fingerprint)
    with pytest.raises(ForwardGateError, match="artifact id does not match"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", snapshot, altered, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
                holdout_result=holdout_result,
                source_event_ledger_snapshot=ledger_snapshot,
                **_ledger_evidence(ledger_snapshot),
            )
        )



def test_forward_gate_rejects_unaccepted_holdout_result(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    rejected_run = replace(
        holdout_result.result,
        gates=(replace(holdout_result.result.gates[0], status=GateStatus.FAIL),)
        + holdout_result.result.gates[1:],
    )
    rejected_holdout = replace(holdout_result, result=rejected_run)
    with pytest.raises(ForwardGateError, match="accepted Holdout result"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", snapshot, handoff, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
                holdout_result=rejected_holdout,
                source_event_ledger_snapshot=ledger_snapshot,
                **_ledger_evidence(ledger_snapshot),
            )
        )


def test_forward_gate_rejects_holdout_dataset_id_mismatch(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    altered_run = replace(holdout_result.result.run, dataset_id="OTHER-DATASET")
    altered_result = replace(
        holdout_result,
        result=replace(holdout_result.result, run=altered_run),
    )
    with pytest.raises(ForwardGateError, match="identities do not agree"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", snapshot, handoff, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
                holdout_result=altered_result,
                source_event_ledger_snapshot=ledger_snapshot,
                **_ledger_evidence(ledger_snapshot),
            )
        )


def test_forward_gate_rejects_holdout_composite_fingerprint_mismatch(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    altered_run = replace(
        holdout_result.result.run,
        dataset_fingerprint="f" * 64,
    )
    altered_result = replace(
        holdout_result,
        result=replace(holdout_result.result, run=altered_run),
    )
    with pytest.raises(ForwardGateError, match="identities do not agree"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", snapshot, handoff, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
                holdout_result=altered_result,
                source_event_ledger_snapshot=ledger_snapshot,
                **_ledger_evidence(ledger_snapshot),
            )
        )



def test_forward_gate_requires_event_ledger_snapshot(tmp_path):
    snapshot, record, event, handoff, holdout_result, _ledger_snapshot = _fixture(tmp_path)
    with pytest.raises(ForwardGateError, match="requires a validated source event ledger snapshot"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", snapshot, handoff, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
                holdout_result=holdout_result,
            )
        )



def test_forward_gate_requires_valid_byte_level_ledger_evidence(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    with pytest.raises(ForwardGateError, match="byte-level event-ledger snapshot evidence"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", snapshot, handoff, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
                holdout_result=holdout_result,
                source_event_ledger_snapshot=ledger_snapshot,
                source_event_ledger_sha256="not-a-sha",
                source_event_ledger_byte_size=12,
                source_event_ledger_source="in_memory",
            )
        )


def test_forward_gate_rejects_duplicate_holdout_completions_in_snapshot(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    duplicate = replace(
        event, sequence=2, occurred_utc="2026-10-08T00:00:00+00:00",
        event_fingerprint="",
    )
    duplicate = replace(
        duplicate,
        event_fingerprint=hashlib.sha256(
            json.dumps(duplicate.as_dict(include_fingerprint=False), sort_keys=True,
                       separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest(),
    )
    duplicate.validate()
    with pytest.raises(ForwardGateError, match="exactly one matching Holdout completion"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", snapshot, handoff, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
                holdout_result=holdout_result,
                source_event_ledger_snapshot=ledger_snapshot + (duplicate,),
                **_ledger_evidence(ledger_snapshot + (duplicate,)),
            )
        )


def test_forward_gate_rejects_invalid_event_ledger_sequence_without_mutation(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    before = ledger_snapshot
    with pytest.raises(ForwardGateError, match="snapshot is invalid"):
        ForwardGateFactory().prepare(
            ForwardGateContext(
                "MANIFEST", snapshot, handoff, record, event,
                "FWD", "FWD-DATA", "FWD-ART", "d" * 64,
                holdout_result=holdout_result,
                source_event_ledger_snapshot=(replace(event, sequence=2),),
                **_ledger_evidence((replace(event, sequence=2),)),
            )
        )
    assert ledger_snapshot == before


def test_handoff_rejects_duplicate_completed_events_for_source_station(tmp_path):
    from strategy_factory.handoff import ResearchHandoffError, build_research_handoff

    snapshot, record, original_event, _handoff, _holdout_result, _ledger_snapshot = _fixture(tmp_path)
    events = FactoryJobEventLedger(path=None)
    for _ in range(2):
        events.append(
            event_type="COMPLETED",
            job_id=record.run_id,
            job_fingerprint=original_event.job_fingerprint,
            worker_id="worker",
            station="holdout",
            phase="FRESH_HOLDOUT",
            detail="synthetic duplicate completion",
            output_artifact=record.evidence_id,
            research_run_fingerprint=record.run_fingerprint,
        )

    before = events.entries()
    with pytest.raises(ResearchHandoffError, match="duplicate completion events"):
        build_research_handoff(
            events=events,
            job_id=record.run_id,
            source_station="holdout",
            destination_station="forward",
            record=record,
            dataset_content_sha256="a" * 64,
            dataset_artifact_id="HOLDOUT-ARTIFACT-SYNTHETIC",
        )

    assert events.entries() == before


def test_forward_gate_rejects_readiness_snapshot_mismatched_to_source_inputs(tmp_path):
    snapshot, record, event, handoff, holdout_result, ledger_snapshot = _fixture(tmp_path)
    manifest, passport, ledger = snapshot._test_readiness_sources
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
        readiness_manifest=replace(manifest, revision="MANIFEST-DRIFT"),
        readiness_passport=passport,
        readiness_ledger=ledger,
        holdout_result=holdout_result,
        source_event_ledger_snapshot=ledger_snapshot,
        **_ledger_evidence(ledger_snapshot),
    )
    with pytest.raises(ForwardGateError, match="does not match source inputs"):
        ForwardGateFactory().prepare(context)
