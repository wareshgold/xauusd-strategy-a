from strategy_factory.handoff import (
    HANDOFF_ROUTES,
    ResearchHandoffError,
    build_research_handoff,
)
from strategy_factory.job_events import FactoryJobEventLedger


def test_handoff_requires_completed_source_artifact():
    events = FactoryJobEventLedger(path=None)
    events.append(
        event_type="QUEUED",
        job_id="JOB-1",
        job_fingerprint="a" * 64,
        station="discovery",
        phase="DISCOVERY",
    )
    try:
        build_research_handoff(
            events=events,
            job_id="JOB-1",
            source_station="discovery",
            destination_station="stability",
        )
    except ResearchHandoffError as exc:
        assert "completed job event" in str(exc)
    else:
        raise AssertionError("expected missing completed artifact to block handoff")


def test_handoff_binds_to_completed_artifact_and_route():
    events = FactoryJobEventLedger(path=None)
    events.append(
        event_type="QUEUED",
        job_id="JOB-1",
        job_fingerprint="a" * 64,
        station="discovery",
        phase="DISCOVERY",
    )
    events.append(
        event_type="COMPLETED",
        job_id="JOB-1",
        job_fingerprint="a" * 64,
        station="discovery",
        phase="DISCOVERY",
        output_artifact="EVIDENCE-1",
    )

    handoff = build_research_handoff(
        events=events,
        job_id="JOB-1",
        source_station="discovery",
        destination_station="stability",
    )
    handoff.validate()
    assert handoff.output_artifact == "EVIDENCE-1"
    assert handoff.source_event_fingerprint
    assert ("discovery", "stability") in HANDOFF_ROUTES


def test_undeclared_route_is_blocked():
    events = FactoryJobEventLedger(path=None)
    try:
        build_research_handoff(
            events=events,
            job_id="JOB-1",
            source_station="discovery",
            destination_station="forward",
        )
    except ResearchHandoffError as exc:
        assert "route is not declared" in str(exc)
    else:
        raise AssertionError("expected undeclared route to block handoff")
