from strategy_factory.starnet_adapter import build_world_state


def test_world_state_is_deterministically_sorted():
    state = build_world_state(
        [
            {
                "worker_id": "W02",
                "station": "stability",
                "state": "HEARTBEAT",
                "progress": 42,
            },
            {
                "worker_id": "W01",
                "station": "discovery",
                "state": "RUNNING",
                "progress": 12,
            },
        ]
    )

    assert [worker.worker_id for worker in state.workers] == ["W01", "W02"]
    assert state.production_locked is True
    assert state.buy_sell_generation == 0


def test_world_state_preserves_research_lifecycle_and_artifact():
    state = build_world_state(
        [
            {
                "worker_id": "W01",
                "station": "holdout",
                "state": "COMPLETED",
                "progress": 100,
                "job_id": "JOB-1",
                "job_type": "HISTORICAL_TEST",
                "phase": "HOLDOUT",
                "detail": "Research run accepted",
                "output_artifact": "evidence-123",
            }
        ]
    )

    worker = state.workers[0]
    assert worker.state == "COMPLETED"
    assert worker.output_artifact == "evidence-123"


def test_world_state_rejects_invalid_station():
    try:
        build_world_state(
            [
                {
                    "worker_id": "W01",
                    "station": "signals",
                    "state": "RUNNING",
                    "progress": 10,
                }
            ]
        )
    except ValueError as exc:
        assert "invalid Factory world station" in str(exc)
    else:
        raise AssertionError("invalid station must be rejected")


def test_world_state_rejects_invalid_progress():
    try:
        build_world_state(
            [
                {
                    "worker_id": "W01",
                    "station": "discovery",
                    "state": "RUNNING",
                    "progress": 101,
                }
            ]
        )
    except ValueError as exc:
        assert "progress" in str(exc)
    else:
        raise AssertionError("invalid progress must be rejected")


def test_world_handoffs_follow_authoritative_journal():
    from strategy_factory.job_events import FactoryJobEventLedger
    from strategy_factory.starnet_adapter import build_world_handoffs

    events = FactoryJobEventLedger(path=None)
    events.append(event_type="COMPLETED", job_id="JOB-1", job_fingerprint="a" * 64,
                   station="discovery", phase="DISCOVERY", output_artifact="EVIDENCE-1")
    accepted = events.append(event_type="HANDOFF_ACCEPTED", job_id="JOB-1", job_fingerprint="a" * 64,
                             station="stability", phase="STABILITY", output_artifact="EVIDENCE-1")

    handoffs = build_world_handoffs(events.entries())
    assert len(handoffs) == 1
    assert handoffs[0].source_station == "discovery"
    assert handoffs[0].destination_station == "stability"
    assert handoffs[0].output_artifact == "EVIDENCE-1"
    assert handoffs[0].event_fingerprint == accepted.event_fingerprint
