from __future__ import annotations

from strategy_factory.forward_preparation import prepare_holdout_to_forward
from strategy_factory.forward_runtime_bridge import run_bound_forward
from strategy_factory.holdout_factory import HoldoutFactory
from strategy_factory.job_events import FactoryJobEventLedger

from test_forward_preparation import _kwargs
from test_holdout_factory import _context


def test_factory_fresh_holdout_to_forward_e2e_preserves_research_lock(tmp_path):
    runner, context = _context(tmp_path / "holdout")

    holdout = HoldoutFactory(runner).prepare_and_run(context)
    assert holdout.result.accepted is True
    assert holdout.result.record.dataset_role == "FRESH_HOLDOUT"
    assert holdout.result.record.strategy_revision == context.spec.strategy_revision

    events = FactoryJobEventLedger(path=None)
    result = prepare_holdout_to_forward(
        **_kwargs(holdout, context, events)
    )

    assert result.ready is True
    assert result.gate.passed is True
    assert result.session.production_decision is False
    assert result.session.handoff_fingerprint == result.handoff.fingerprint
    assert result.session.lifecycle_state == "PREPARED"

    assert result.handoff.source_station == "holdout"
    assert result.handoff.destination_station == "forward"
    assert result.handoff.dataset_content_sha256 == context.holdout_dataset_content_sha256
    assert result.handoff.dataset_artifact_id == context.holdout_dataset_artifact_id

    assert [event.event_type for event in events.entries()] == [
        "COMPLETED",
        "HANDOFF_ACCEPTED",
    ]


def test_factory_full_provenance_chain_reaches_reconciliation(tmp_path):
    runner, context = _context(tmp_path / "full-chain")

    holdout = HoldoutFactory(runner).prepare_and_run(context)
    events = FactoryJobEventLedger(path=None)
    prepared = prepare_holdout_to_forward(
        **_kwargs(holdout, context, events)
    )

    observed_runner_result = {"observed_positions": 3}

    def run_forward():
        return observed_runner_result

    def reconcile(result):
        assert result is observed_runner_result
        return {
            "reconciliation_id": "RECON-FULL-CHAIN-1",
            "broker_server": "SYNTHETIC-MT5",
            "symbol": "XAUUSD.ecn",
            "observed_positions": result["observed_positions"],
            "matched_positions": 3,
            "mismatched_positions": 0,
        }

    runtime = run_bound_forward(
        session=prepared.session,
        run_forward=run_forward,
        reconcile=reconcile,
        started_utc="2026-10-08T01:00:00Z",
        running_utc="2026-10-08T01:01:00Z",
        completed_utc="2026-10-08T01:02:00Z",
    )

    handoff_fp = prepared.handoff.fingerprint
    session_fp = prepared.session.fingerprint

    assert prepared.gate.gate.details["handoff_fingerprint"] == handoff_fp
    assert prepared.session.handoff_fingerprint == handoff_fp

    assert runtime.session_id == prepared.session.session_id
    assert runtime.session_fingerprint == session_fp
    assert runtime.handoff_fingerprint == handoff_fp

    assert [event.state.value for event in runtime.lifecycle_events] == [
        "STARTED",
        "RUNNING",
        "COMPLETED",
    ]
    assert all(event.session_fingerprint == session_fp for event in runtime.lifecycle_events)
    assert all(event.handoff_fingerprint == handoff_fp for event in runtime.lifecycle_events)
    assert all(event.strategy_revision == prepared.session.strategy_revision for event in runtime.lifecycle_events)
    assert all(event.manifest_revision == prepared.session.manifest_revision for event in runtime.lifecycle_events)
    assert all(event.execution_semantics == prepared.session.execution_semantics for event in runtime.lifecycle_events)
    assert all(event.post_holdout_tuning is False for event in runtime.lifecycle_events)
    assert all(event.production_decision is False for event in runtime.lifecycle_events)

    receipt = runtime.reconciliation
    assert receipt.session_id == prepared.session.session_id
    assert receipt.session_fingerprint == session_fp
    assert receipt.handoff_fingerprint == handoff_fp
    assert receipt.observed_positions == 3
    assert receipt.matched_positions == 3
    assert receipt.mismatched_positions == 0
    assert receipt.reconciled is True

    assert runtime.runner_result is observed_runner_result
