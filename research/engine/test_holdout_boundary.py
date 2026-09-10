from .holdout_boundary import HoldoutDecision, HoldoutInput, decide_holdout


def base(**overrides):
    value = dict(
        dataset_fingerprint="dataset-sha",
        window_id="FRESH_HOLDOUT_01",
        touched=False,
        results_recorded=False,
        specification_version="spec-v1",
    )
    value.update(overrides)
    return HoldoutInput(**value)


def test_pristine_holdout_passes_boundary_check():
    assert decide_holdout(base()) is HoldoutDecision.PASS


def test_touched_holdout_blocks():
    assert decide_holdout(base(touched=True)) is HoldoutDecision.BLOCK


def test_missing_identity_is_unknown():
    assert decide_holdout(base(dataset_fingerprint="")) is HoldoutDecision.UNKNOWN


def test_recorded_holdout_results_are_not_pristine():
    assert decide_holdout(base(results_recorded=True)) is HoldoutDecision.UNKNOWN


def test_missing_specification_identity_is_unknown():
    assert decide_holdout(base(specification_version="")) is HoldoutDecision.UNKNOWN
