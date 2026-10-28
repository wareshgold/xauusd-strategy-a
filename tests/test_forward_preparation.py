from __future__ import annotations

import hashlib
import pytest

from strategy_factory.forward_gate_factory import ForwardGateError
from strategy_factory.forward_preparation import (
    ForwardPreparationError,
    prepare_holdout_to_forward,
)
from strategy_factory.job_events import FactoryJobEventLedger

from test_holdout_factory import _context


def _prepared(tmp_path):
    runner, context = _context(tmp_path / "holdout")
    from strategy_factory.holdout_factory import HoldoutFactory

    holdout = HoldoutFactory(runner).prepare_and_run(context)
    events = FactoryJobEventLedger(path=None)
    return holdout, context, events


def _kwargs(holdout, context, events):
    return {
        "holdout_result": holdout,
        "events": events,
        "manifest_revision": "MANIFEST",
        "forward_session_id": "FORWARD-SESSION-001",
        "forward_dataset_id": "MT5-FORWARD-001",
        "forward_dataset_artifact_id": "MT5-FORWARD-ARTIFACT-001",
        "forward_dataset_content_sha256": "f" * 64,
        "holdout_dataset_content_sha256": context.holdout_dataset_content_sha256,
        "holdout_dataset_artifact_id": context.holdout_dataset_artifact_id,
    }


def test_holdout_to_forward_preparation_passes(tmp_path):
    holdout, context, events = _prepared(tmp_path)
    result = prepare_holdout_to_forward(**_kwargs(holdout, context, events))

    assert result.ready is True
    assert result.gate.passed is True
    assert result.session.production_decision is False
    assert result.handoff.source_station == "holdout"
    assert result.handoff.destination_station == "forward"
    assert result.holdout_event.event_type == "COMPLETED"
    assert result.holdout_event.station == "holdout"


@pytest.mark.parametrize(
    "mutation, message",
    [
        ({"holdout_dataset_content_sha256": "0" * 64}, "does not match"),
        ({"holdout_dataset_artifact_id": "WRONG-ARTIFACT"}, "does not match"),
    ],
)
def test_holdout_to_forward_rejects_invalid_holdout_identity(tmp_path, mutation, message):
    holdout, context, events = _prepared(tmp_path)
    kwargs = _kwargs(holdout, context, events)
    kwargs.update(mutation)

    with pytest.raises(ForwardPreparationError, match=message):
        prepare_holdout_to_forward(**kwargs)



def test_persisted_journal_snapshot_hash_is_bound_to_exact_read_only_bytes(tmp_path):
    holdout, context, _events = _prepared(tmp_path)
    journal_path = tmp_path / "factory_job_events.jsonl"
    events = FactoryJobEventLedger(path=journal_path)

    result = prepare_holdout_to_forward(**_kwargs(holdout, context, events))

    details = result.gate.gate.details
    assert details["source_event_ledger_source"] == "persisted_jsonl"
    assert details["source_event_ledger_path"] == str(journal_path)
    byte_size = details["source_event_ledger_byte_size"]
    final_bytes = journal_path.read_bytes()
    # The forward handoff event is appended after the gate. The exact prefix
    # audited by the gate must still be byte-for-byte present in the journal.
    audited_bytes = final_bytes[:byte_size]
    assert hashlib.sha256(audited_bytes).hexdigest() == details["source_event_ledger_sha256"]
    assert details["source_event_ledger_event_count"] == 1
    assert b"\n" in audited_bytes



def test_external_journal_corruption_is_rejected_before_any_append(tmp_path):
    holdout, context, _unused_events = _prepared(tmp_path)
    journal_path = tmp_path / "factory_job_events.jsonl"
    events = FactoryJobEventLedger(path=journal_path)
    events.append(
        event_type="QUEUED",
        job_id="UNRELATED-JOB",
        job_fingerprint="a" * 64,
        station="holdout",
        phase="HOLDOUT",
        detail="synthetic baseline",
    )
    baseline_events = events.entries()

    # Simulate another process corrupting the file after this ledger was loaded.
    with journal_path.open("ab") as handle:
        handle.write(b"{\n")
    corrupted_bytes = journal_path.read_bytes()

    with pytest.raises(
        ForwardPreparationError,
        match="failed pre-append integrity validation",
    ):
        prepare_holdout_to_forward(**_kwargs(holdout, context, events))

    assert journal_path.read_bytes() == corrupted_bytes
    assert events.entries() == baseline_events


def test_valid_but_divergent_journal_snapshot_is_rejected_before_append(tmp_path):
    holdout, context, _unused_events = _prepared(tmp_path)
    journal_path = tmp_path / "factory_job_events.jsonl"
    events = FactoryJobEventLedger(path=journal_path)
    events.append(
        event_type="QUEUED",
        job_id="BASELINE-JOB",
        job_fingerprint="a" * 64,
        station="holdout",
        phase="HOLDOUT",
        detail="original valid journal",
    )
    baseline_events = events.entries()

    replacement_path = tmp_path / "replacement.jsonl"
    replacement = FactoryJobEventLedger(path=replacement_path)
    replacement.append(
        event_type="QUEUED",
        job_id="BASELINE-JOB",
        job_fingerprint="a" * 64,
        station="holdout",
        phase="HOLDOUT",
        detail="different but structurally valid journal",
    )
    journal_path.write_bytes(replacement_path.read_bytes())
    divergent_bytes = journal_path.read_bytes()

    with pytest.raises(
        ForwardPreparationError,
        match="failed pre-append integrity validation",
    ):
        prepare_holdout_to_forward(**_kwargs(holdout, context, events))

    assert journal_path.read_bytes() == divergent_bytes
    assert events.entries() == baseline_events

def test_corrupt_persisted_journal_fails_closed_without_repair(tmp_path):
    holdout, context, _events = _prepared(tmp_path)
    journal_path = tmp_path / "factory_job_events.jsonl"

    class ExternallyCorruptedLedger(FactoryJobEventLedger):
        corrupted_bytes = None
        injected = False

        def entries(self):
            if self.path is not None and not self.injected:
                with self.path.open("ab") as handle:
                    handle.write(b"{\n")
                self.injected = True
                self.corrupted_bytes = self.path.read_bytes()
            return super().entries()

    events = ExternallyCorruptedLedger(path=journal_path)
    with pytest.raises(ForwardPreparationError, match="persisted event journal is not valid"):
        prepare_holdout_to_forward(**_kwargs(holdout, context, events))

    assert events.corrupted_bytes is not None
    assert journal_path.read_bytes() == events.corrupted_bytes
    assert [event.event_type for event in events.entries()] == ["COMPLETED"]

def test_holdout_to_forward_rejects_same_forward_dataset(tmp_path):
    holdout, context, events = _prepared(tmp_path)
    kwargs = _kwargs(holdout, context, events)
    kwargs["forward_dataset_id"] = holdout.result.record.dataset_id

    with pytest.raises(ForwardGateError, match="Forward dataset id must differ"):
        prepare_holdout_to_forward(**kwargs)


@pytest.mark.parametrize(
    "field, value, message",
    [
        ("strategy_revision_frozen", False, "frozen"),
        ("post_holdout_tuning", True, "post-holdout"),
    ],
)
def test_holdout_to_forward_rejects_frozen_boundary_breaks(
    tmp_path, field, value, message
):
    holdout, context, events = _prepared(tmp_path)
    kwargs = _kwargs(holdout, context, events)
    kwargs[field] = value

    with pytest.raises(ForwardPreparationError, match=message):
        prepare_holdout_to_forward(**kwargs)


def test_holdout_to_forward_rejects_manifest_drift(tmp_path):
    holdout, context, events = _prepared(tmp_path)
    kwargs = _kwargs(holdout, context, events)
    kwargs["manifest_revision"] = "MANIFEST-DRIFT"

    with pytest.raises(ForwardPreparationError, match="manifest_revision"):
        prepare_holdout_to_forward(**kwargs)


def test_holdout_to_forward_preserves_handoff_identity_into_session(tmp_path):
    holdout, context, events = _prepared(tmp_path)
    result = prepare_holdout_to_forward(**_kwargs(holdout, context, events))

    assert result.session.handoff_fingerprint == result.handoff.fingerprint
    assert result.session.strategy_id == holdout.result.record.strategy_id
    assert result.session.strategy_revision == holdout.result.record.strategy_revision
    assert result.session.manifest_revision == holdout.result.record.manifest_revision
    assert result.session.execution_semantics == holdout.result.record.execution_semantics
    assert result.session.holdout_dataset_id == holdout.result.record.dataset_id
    assert (
        result.session.holdout_dataset_artifact_id
        == result.handoff.dataset_artifact_id
    )
    assert (
        result.session.holdout_dataset_content_sha256
        == result.handoff.dataset_content_sha256
    )
    result.session.validate()


@pytest.mark.parametrize(
    "field, value, message",
    [
        (
            "forward_dataset_content_sha256",
            "a" * 64,
            "Forward dataset identity must differ",
        ),
        (
            "forward_dataset_artifact_id",
            "HOLDOUT-ARTIFACT",
            "Forward dataset artifact id must differ",
        ),
    ],
)
def test_holdout_to_forward_rejects_forward_dataset_reuse(
    tmp_path, field, value, message
):
    holdout, context, events = _prepared(tmp_path)
    kwargs = _kwargs(holdout, context, events)
    if field == "forward_dataset_content_sha256":
        kwargs[field] = context.holdout_dataset_content_sha256
    else:
        kwargs[field] = context.holdout_dataset_artifact_id

    with pytest.raises(ForwardGateError, match=message):
        prepare_holdout_to_forward(**kwargs)


def test_holdout_to_forward_rejects_strategy_revision_drift_in_source_record(
    tmp_path,
):
    from dataclasses import replace

    holdout, context, events = _prepared(tmp_path)
    tampered_record = replace(
        holdout.result.record,
        strategy_revision="REV-DRIFT",
    )
    tampered_result = replace(
        holdout,
        result=replace(holdout.result, record=tampered_record),
    )

    with pytest.raises(ValueError, match="record fingerprint mismatch"):
        prepare_holdout_to_forward(
            **_kwargs(tampered_result, context, events)
        )


def test_holdout_to_forward_never_authorizes_production(tmp_path):
    holdout, context, events = _prepared(tmp_path)
    result = prepare_holdout_to_forward(**_kwargs(holdout, context, events))

    assert result.session.production_decision is False
    assert result.gate.gate.details["production_decision"] is False
    assert all(
        event.station != "production"
        for event in events.entries()
    )
