import pytest
from dataclasses import replace

from strategy_factory.multiple_comparison import (
    MultipleComparisonError,
    adjust_p_values,
)


def test_bonferroni_is_deterministic_and_capped():
    result = adjust_p_values((0.01, 0.20, 0.80), method="BONFERRONI")
    assert result.adjusted_p_values == (0.03, 0.6, 1.0)
    assert result.family_size == 3
    result.validate()


def test_holm_preserves_original_order_and_monotonic_adjustment():
    result = adjust_p_values((0.04, 0.01, 0.03), method="HOLM")
    assert result.adjusted_p_values == (0.06, 0.03, 0.06)
    result.validate()


def test_holm_tie_order_is_deterministic():
    first = adjust_p_values((0.01, 0.01, 0.2), method="HOLM")
    second = adjust_p_values((0.01, 0.01, 0.2), method="HOLM")
    assert first == second


def test_rejects_invalid_p_values():
    with pytest.raises(MultipleComparisonError, match="between 0 and 1"):
        adjust_p_values((0.1, 1.1))


def test_rejects_empty_family():
    with pytest.raises(MultipleComparisonError, match="at least one"):
        adjust_p_values(())


def test_rejects_tampered_result():
    result = adjust_p_values((0.01, 0.02))
    tampered = replace(result, fingerprint="0" * 64)
    with pytest.raises(MultipleComparisonError, match="fingerprint"):
        tampered.validate()


def test_unsupported_method_is_rejected():
    with pytest.raises(MultipleComparisonError, match="unsupported"):
        adjust_p_values((0.1,), method="NONE")
