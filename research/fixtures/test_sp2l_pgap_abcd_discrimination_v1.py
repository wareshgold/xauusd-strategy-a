from sp2l_pgap_abcd_discrimination_v1 import abcd_variants, ab_length, cd_length, pgap_variants


def test_pgap_fixture_keeps_bo_and_follow_through_separate():
    variants = pgap_variants()
    assert variants["V1_BO_FT_nonoverlap"][2].c > variants["V1_BO_FT_nonoverlap"][1].h
    assert variants["V1_BO_FT_nonoverlap"][3].l > variants["V1_BO_FT_nonoverlap"][2].h
    assert variants["V2_BO_FT_overlap"][3].l <= variants["V2_BO_FT_overlap"][2].h


def test_abcd_exact_relationship_has_no_tolerance():
    variants = abcd_variants()
    assert ab_length(variants["pivot_wick"]) == cd_length(variants["pivot_wick"])
    assert ab_length(variants["pivot_body"]) == cd_length(variants["pivot_body"])
    assert ab_length(variants["mixed_anchor"]) != cd_length(variants["mixed_anchor"])
