from scripts.sp2l_forward_diagnostic_gate import ForwardDiagnosticGate


def test_first_diagnostic_is_allowed_and_repeats_are_rate_limited():
    now = [10.0]
    gate = ForwardDiagnosticGate(clock=lambda: now[0])

    assert gate.should_log("XAUUSD:RATES_UNAVAILABLE")
    assert not gate.should_log("XAUUSD:RATES_UNAVAILABLE")
    now[0] += 59.9
    assert not gate.should_log("XAUUSD:RATES_UNAVAILABLE")
    now[0] += 0.2
    assert gate.should_log("XAUUSD:RATES_UNAVAILABLE")


def test_different_reasons_have_independent_rate_limits():
    gate = ForwardDiagnosticGate(clock=lambda: 10.0)

    assert gate.should_log("XAUUSD:RATES_UNAVAILABLE")
    assert gate.should_log("XAUUSD:CANDIDATE_SCAN_EMPTY")
    assert not gate.should_log("XAUUSD:RATES_UNAVAILABLE")


def test_interval_can_be_overridden():
    now = [10.0]
    gate = ForwardDiagnosticGate(clock=lambda: now[0])

    assert gate.should_log("clock", interval_seconds=300)
    now[0] += 299
    assert not gate.should_log("clock", interval_seconds=300)
    now[0] += 1
    assert gate.should_log("clock", interval_seconds=300)
