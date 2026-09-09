from sp2l_bearish_f15 import Direction, f15_cases, structural_mirror


def test_bullish_and_bearish_cases_exist():
    bullish, bearish = f15_cases()
    assert bullish.direction is Direction.BULLISH
    assert bearish.direction is Direction.BEARISH


def test_pending_order_is_directionally_mirrored():
    bullish, bearish = f15_cases()
    assert bullish.pending_order == "buy_limit"
    assert bearish.pending_order == "sell_limit"


def test_structural_invalidation_is_directionally_mirrored():
    bullish, bearish = f15_cases()
    assert bullish.invalidation_relation == "below_structural_low"
    assert bearish.invalidation_relation == "above_structural_high"


def test_mirror_preserves_sequence_without_claiming_new_geometry():
    bullish, bearish = f15_cases()
    assert structural_mirror(bullish, bearish)
