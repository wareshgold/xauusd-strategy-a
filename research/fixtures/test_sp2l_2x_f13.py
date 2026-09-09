from sp2l_2x_f13 import TwoXInterpretation, classify, f13_cases


def test_both_source_supported_2x_interpretations_are_retained():
    cases = f13_cases()
    assert {c.interpretation for c in cases} == {
        TwoXInterpretation.HALF_TARGET,
        TwoXInterpretation.SECOND_POSITION_RISK_REWARD,
    }


def test_no_formula_is_invented_by_fixture():
    for case in f13_cases():
        assert classify(case) is case.interpretation


def test_interpretations_are_not_forced_equal():
    half, second = f13_cases()
    assert (half.second_entry, half.second_stop) != (second.second_entry, second.second_stop)
