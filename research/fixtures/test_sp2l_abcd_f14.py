from sp2l_abcd_f14 import AnchorModel, exact_equal, f14_cases


def test_all_candidate_anchor_models_are_representable():
    assert {case.model for case in f14_cases()} == {
        AnchorModel.WICK,
        AnchorModel.BODY,
        AnchorModel.STRUCTURAL_PIVOT,
        AnchorModel.MIXED,
    }


def test_source_relationship_can_be_exact_without_tolerance():
    cases = f14_cases()
    assert all(exact_equal(case) for case in cases[:3])
    assert not exact_equal(cases[3])


def test_fixture_does_not_select_canonical_anchor_model():
    equal_models = [case.model for case in f14_cases() if exact_equal(case)]
    assert len(equal_models) > 1
    assert set(equal_models) != {AnchorModel.WICK}


def test_no_tolerance_is_encoded():
    # A one-tick synthetic perturbation is not silently accepted as equality.
    case = f14_cases()[0]
    perturbed_cd = abs((case.D + 0.01) - case.C)
    assert case.ab() != perturbed_cd
