from .reproducibility_boundary import ReproducibilityDecision, ReproducibilityInput, decide_reproducibility


def base(**overrides):
    value = dict(
        dataset_fingerprint_match=True,
        specification_version_match=True,
        source_provenance_match=True,
        deterministic_execution=True,
        output_fingerprint_match=True,
    )
    value.update(overrides)
    return ReproducibilityInput(**value)


def test_complete_reproducibility_passes():
    assert decide_reproducibility(base()) is ReproducibilityDecision.PASS


def test_dataset_mismatch_blocks():
    assert decide_reproducibility(base(dataset_fingerprint_match=False)) is ReproducibilityDecision.BLOCK


def test_specification_mismatch_blocks():
    assert decide_reproducibility(base(specification_version_match=False)) is ReproducibilityDecision.BLOCK


def test_source_provenance_mismatch_blocks():
    assert decide_reproducibility(base(source_provenance_match=False)) is ReproducibilityDecision.BLOCK


def test_nondeterministic_execution_blocks():
    assert decide_reproducibility(base(deterministic_execution=False)) is ReproducibilityDecision.BLOCK


def test_output_mismatch_blocks():
    assert decide_reproducibility(base(output_fingerprint_match=False)) is ReproducibilityDecision.BLOCK
