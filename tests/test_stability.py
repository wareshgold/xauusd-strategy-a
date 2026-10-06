from dataclasses import replace
import pytest

from strategy_factory.stability import (
    StabilityContractError,
    StabilitySegment,
    evaluate_stability,
)


def segments():
    return (
        StabilitySegment("S1", "London", 10, 0.2, 0.6),
        StabilitySegment("S2", "New York", 8, -0.1, 0.5),
        StabilitySegment("S3", "Overlap", 12, 0.4, 0.75),
    )


def test_stability_profile_is_deterministic_and_descriptive():
    a = evaluate_stability(segments())
    b = evaluate_stability(segments())
    assert a == b
    assert a.min_mean_r == -0.1
    assert a.max_mean_r == 0.4
    assert a.mean_r_range == 0.5
    assert a.average_segment_mean_r == pytest.approx(1 / 6)
    assert a.canonical_eligible is False
    assert a.production_eligible is False


def test_duplicate_segment_ids_are_rejected():
    s = segments()
    with pytest.raises(StabilityContractError, match="unique"):
        evaluate_stability((s[0], replace(s[1], segment_id="S1")))


def test_invalid_segment_is_rejected():
    with pytest.raises(StabilityContractError, match="win_rate"):
        evaluate_stability((StabilitySegment("S1", "bad", 10, 0.1, 1.1),))


def test_empty_profile_is_rejected():
    with pytest.raises(StabilityContractError, match="at least one"):
        evaluate_stability(())


def test_tampering_is_detected():
    profile = evaluate_stability(segments())
    with pytest.raises(StabilityContractError, match="range mismatch"):
        replace(profile, mean_r_range=999.0).validate()
