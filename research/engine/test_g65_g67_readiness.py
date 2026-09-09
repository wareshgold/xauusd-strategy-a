from .gate_status import GateState, ResearchGateStatus, production_ready


def test_blocked_geometry_keeps_production_locked():
    status = ResearchGateStatus(
        GateState.PARTIAL_PASS,
        GateState.PASS,
        GateState.BLOCKED,
        GateState.LOCKED,
        GateState.LOCKED,
        GateState.LOCKED,
        GateState.LOCKED,
    )
    assert production_ready(status) is False
