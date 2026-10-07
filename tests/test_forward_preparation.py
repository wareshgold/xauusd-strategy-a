from __future__ import annotations

import pytest

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


def test_holdout_to_forward_rejects_same_forward_dataset(tmp_path):
    holdout, context, events = _prepared(tmp_path)
    kwargs = _kwargs(holdout, context, events)
    kwargs["forward_dataset_id"] = context.holdout_dataset_artifact_id

    with pytest.raises(Exception, match="Forward dataset"):
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
