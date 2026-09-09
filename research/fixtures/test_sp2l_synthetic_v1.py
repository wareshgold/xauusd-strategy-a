from sp2l_synthetic_v1 import build_suite


def test_suite_is_deterministic():
    a = [f.record() for f in build_suite()]
    b = [f.record() for f in build_suite()]
    assert a == b


def test_entry_and_leg2_are_distinct():
    fixture = next(f for f in build_suite() if f.fixture_id == "F03")
    assert fixture.candidates["entry_candidate"] != fixture.candidates["leg2_start_candidate"]
    assert "do not alias coordinates" in fixture.invariants


def test_wick_and_body_are_distinct():
    fixture = next(f for f in build_suite() if f.fixture_id == "F05")
    assert fixture.candidates["wick_low"] != fixture.candidates["body_low"]
    assert fixture.candidates["wick_high"] != fixture.candidates["body_high"]


def test_replacement_threshold_is_not_invented():
    fixture = next(f for f in build_suite() if f.fixture_id == "F06")
    assert "replacement threshold remains unresolved" in fixture.invariants
