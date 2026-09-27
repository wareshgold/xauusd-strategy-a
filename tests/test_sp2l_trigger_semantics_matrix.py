"""Deterministic comparison matrix for unresolved SP2L trigger semantics.

This is diagnostic only. No interpretation is canonical.
"""
from tests.fixtures.sp2l_trigger_semantics_research import RESEARCH_FIXTURES


def _touch_or_penetration(c, ref_low):
    return c["low"] <= ref_low


def _close(c, ref_low):
    return c["close"] <= ref_low


def _immediate_trigger(candles):
    ref = candles[0]["low"]
    c = candles[2]
    return _touch_or_penetration(c, ref)


def _scan_trigger(candles, predicate):
    ref = candles[0]["low"]
    return any(predicate(c, ref) for c in candles[2:])


def evaluate_matrix():
    return {
        "A_immediate_touch_penetration": {
            name: _immediate_trigger(builder())
            for name, builder in RESEARCH_FIXTURES.items()
        },
        "B_immediate_close": {
            name: _close(builder()[2], builder()[0]["low"])
            for name, builder in RESEARCH_FIXTURES.items()
        },
        "C_scan_touch_penetration": {
            name: _scan_trigger(builder(), _touch_or_penetration)
            for name, builder in RESEARCH_FIXTURES.items()
        },
        "D_scan_close": {
            name: _scan_trigger(builder(), _close)
            for name, builder in RESEARCH_FIXTURES.items()
        },
    }


def test_matrix_is_deterministic():
    assert evaluate_matrix() == evaluate_matrix()


def test_matrix_preserves_the_intended_semantic_separations():
    m = evaluate_matrix()

    assert m["A_immediate_touch_penetration"]["T1_IMMEDIATE_TOUCH"] is True
    assert m["A_immediate_touch_penetration"]["T2_DELAYED_REACH"] is False

    assert m["C_scan_touch_penetration"]["T2_DELAYED_REACH"] is True
    assert m["C_scan_touch_penetration"]["T6_MULTI_CANDLE_CORRECTION"] is True

    assert m["B_immediate_close"]["T5_CLOSE_ONLY"] is False
    assert m["C_scan_touch_penetration"]["T5_CLOSE_ONLY"] is True

    assert m["D_scan_close"]["T5_CLOSE_ONLY"] is False


# This matrix is a research instrument. It does not select a canonical rule.
