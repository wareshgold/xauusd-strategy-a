from __future__ import annotations

import pytest

from strategy_factory.worker_state import WorkerLifecycle, WorkerStatus


def test_worker_lifecycle_accepts_happy_path_and_records_events():
    worker = WorkerLifecycle(worker_id="validator-01", job_id="JOB-001")

    for status in (
        WorkerStatus.CLAIMED,
        WorkerStatus.RUNNING,
        WorkerStatus.VALIDATING,
        WorkerStatus.PASSED,
    ):
        worker.transition(status)

    payload = worker.to_dict()
    assert payload["status"] == "PASSED"
    assert [event["status"] for event in payload["events"]] == [
        "CLAIMED", "RUNNING", "VALIDATING", "PASSED"
    ]
    assert payload["events"][0]["previous_status"] == "IDLE"


def test_worker_lifecycle_rejects_skipped_and_terminal_transitions():
    worker = WorkerLifecycle(worker_id="worker-02", job_id="JOB-002")

    with pytest.raises(ValueError, match="Invalid worker transition"):
        worker.transition(WorkerStatus.RUNNING)

    worker.transition(WorkerStatus.CLAIMED)
    worker.transition(WorkerStatus.RUNNING)
    worker.transition(WorkerStatus.VALIDATING)
    worker.transition(WorkerStatus.PASSED)

    with pytest.raises(ValueError, match="Invalid worker transition"):
        worker.transition(WorkerStatus.CLAIMED)


def test_failed_job_requires_reason_and_can_be_marked_for_replay():
    worker = WorkerLifecycle(worker_id="worker-03", job_id="JOB-003")
    worker.transition(WorkerStatus.CLAIMED)

    with pytest.raises(ValueError, match="reason is required"):
        worker.transition(WorkerStatus.FAILED)

    worker.transition(WorkerStatus.FAILED, reason="validation process exited")
    worker.transition(WorkerStatus.REPLAY_READY, reason="same input identity retained")
    worker.transition(WorkerStatus.CLAIMED)

    assert worker.status is WorkerStatus.CLAIMED
    assert worker.events[1].reason == "validation process exited"
    assert worker.events[2].status == "REPLAY_READY"


def test_unknown_status_is_rejected_without_mutating_state():
    worker = WorkerLifecycle(worker_id="worker-04", job_id="JOB-004")

    with pytest.raises(ValueError, match="Unknown worker status"):
        worker.transition("MAGICALLY_APPROVED")

    assert worker.status is WorkerStatus.IDLE
    assert worker.events == []
