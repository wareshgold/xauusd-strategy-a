from .gate_status import GateState, ResearchGateStatus, production_ready


def test_current_research_state_is_not_production_ready():
    status = ResearchGateStatus(
        source_resolution=GateState.PARTIAL_PASS,
        synthetic_fixtures=GateState.PASS,
        frozen_geometry=GateState.BLOCKED,
        dev_validation=GateState.LOCKED,
        val_validation=GateState.LOCKED,
        fresh_holdout=GateState.LOCKED,
        production=GateState.LOCKED,
    )
    assert not production_ready(status)


def test_all_gates_must_pass_for_production():
    status = ResearchGateStatus(*([GateState.PASS] * 7))
    assert production_ready(status)
