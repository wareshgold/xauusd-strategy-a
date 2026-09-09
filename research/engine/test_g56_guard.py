from .g56_guard import strategy_a_execution_gate


def test_g56_execution_gate_is_closed():
    assert strategy_a_execution_gate() is False
