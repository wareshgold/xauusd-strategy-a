from tests.fixtures.sp2l_trigger_semantics_research import RESEARCH_FIXTURES


def test_all_trigger_semantics_research_fixtures_are_deterministic():
    expected = {
        "T1_IMMEDIATE_TOUCH": 3,
        "T2_DELAYED_REACH": 4,
        "T3_EXACT_TOUCH": 3,
        "T4_PENETRATION": 3,
        "T5_CLOSE_ONLY": 3,
        "T6_MULTI_CANDLE_CORRECTION": 5,
    }
    assert set(RESEARCH_FIXTURES) == set(expected)
    for name, builder in RESEARCH_FIXTURES.items():
        first = builder()
        second = builder()
        assert first == second
        assert len(first) == expected[name]


def test_fixtures_expose_the_intended_buy_level_relationships():
    assert RESEARCH_FIXTURES["T1_IMMEDIATE_TOUCH"]()[-1]["low"] == 100
    assert RESEARCH_FIXTURES["T2_DELAYED_REACH"]()[-2]["low"] > 100
    assert RESEARCH_FIXTURES["T2_DELAYED_REACH"]()[-1]["low"] == 100
    assert RESEARCH_FIXTURES["T4_PENETRATION"]()[-1]["low"] < 100
    assert RESEARCH_FIXTURES["T5_CLOSE_ONLY"]()[-1]["low"] < 100
    assert RESEARCH_FIXTURES["T5_CLOSE_ONLY"]()[-1]["close"] > 100


# These tests validate fixture construction only. They intentionally do not
# assert which candidate trigger interpretation is canonical.
