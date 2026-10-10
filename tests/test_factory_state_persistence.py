from strategy_factory.run_state import FactoryRunState


def test_factory_run_state_updates_stage():
    state = FactoryRunState(run_id="RUN-001")
    state.update_stage("SOURCE", "PASS")

    assert state.to_dict()["stages"]["SOURCE"] == "PASS"
