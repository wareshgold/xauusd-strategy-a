from sp2l_entry_invalidation_trigger_2x_discrimination_v1 import (
    entry_variants,
    invalidation_variants,
    trigger_variants,
    two_x_variants,
    discrimination_report,
)


def test_entry_variants_keep_leg2_distinct():
    for values in entry_variants().values():
        assert values["relevant_higher_low"] != values["leg2_start"]


def test_entry_fixture_exposes_competing_anchor_candidates():
    candidates = {name for name in entry_variants()}
    assert candidates == {"first_structural_low", "relevant_higher_low", "leg2_start"}


def test_invalidation_fixture_exposes_structural_vs_local_vs_fixed_distance():
    variants = invalidation_variants()
    assert set(variants) == {"structural_base_low", "entry_local_low", "fixed_distance"}
    assert variants["structural_base_low"]["sl"] == 100.0
    assert variants["entry_local_low"]["sl"] == 103.0


def test_trigger_fixture_contains_one_two_three_candle_forms():
    counts = {name: len(bars) for name, bars in trigger_variants().items()}
    assert counts == {"one_candle": 1, "two_candle": 2, "three_candle": 3}


def test_2x_fixture_does_not_select_a_formula():
    assert set(two_x_variants()) == {
        "half_target_from_entry",
        "two_r_from_entry",
        "half_range_reference",
    }


def test_report_keeps_unresolved_items_explicit():
    report = discrimination_report()
    assert "exact pending-limit price anchor" in report["unresolved"]
    assert "2X exact formula and reference levels" in report["unresolved"]
