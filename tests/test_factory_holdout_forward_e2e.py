from __future__ import annotations

from strategy_factory.forward_preparation import prepare_holdout_to_forward
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
    assert result.session.lifecycle_state == "PREPARED"

    assert result.handoff.source_station == "holdout"
    assert result.handoff.destination_station == "forward"
    assert result.handoff.dataset_content_sha256 == context.holdout_dataset_content_sha256
    assert result.handoff.dataset_artifact_id == context.holdout_dataset_artifact_id

    assert [event.event_type for event in events.entries()] == [
        "COMPLETED",
        "HANDOFF_ACCEPTED",
    ]
