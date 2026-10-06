import pytest

from strategy_factory.adapter import (
    ExecutionAdapterError,
    adapter_semantics,
    build_execution_receipt,
    validate_adapter_output,
)
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.test_contract import DatasetRole, ExecutionSemantics, HistoricalTestSpec, TestDataset


METRICS = ResearchMetrics(10, 10, 6, 4, 0, 0.6, 2.5, 1.4, 1.2, 6.0, -3.5)


def spec(semantics=ExecutionSemantics.TICK_FEASIBLE):
    dataset = TestDataset(
        "D1", DatasetRole.DEVELOPMENT, "R1",
        "2026-01-01", "2026-02-01", "FIXTURE"
    )
    return HistoricalTestSpec(
        "T1", "SP2L-A", "S1", dataset, semantics
    )


def test_build_receipt_preserves_spec_identity():
    s = spec()
    receipt = build_execution_receipt(
        execution_id="EX1",
        spec=s,
        engine_revision="ENGINE1",
        input_fingerprint="a" * 64,
        metrics=METRICS,
    )
    assert receipt.test_id == s.test_id
    assert receipt.strategy_revision == s.strategy_revision
    assert receipt.execution_semantics is s.execution_semantics
    assert receipt.metrics == METRICS


def test_adapter_output_exact_binding_passes():
    s = spec()
    receipt = build_execution_receipt(
        execution_id="EX1", spec=s, engine_revision="ENGINE1",
        input_fingerprint="a" * 64, metrics=METRICS,
    )
    validate_adapter_output(spec=s, receipt=receipt)


def test_adapter_semantics_mismatch_is_rejected():
    s = spec(ExecutionSemantics.TICK_FEASIBLE)
    other = spec(ExecutionSemantics.BAR_CLOSE_RESEARCH)
    receipt = build_execution_receipt(
        execution_id="EX1", spec=other, engine_revision="ENGINE1",
        input_fingerprint="a" * 64, metrics=METRICS,
    )
    with pytest.raises(ExecutionAdapterError):
        validate_adapter_output(spec=s, receipt=receipt)


def test_adapter_test_id_mismatch_is_rejected():
    s = spec()
    receipt = build_execution_receipt(
        execution_id="EX1", spec=s, engine_revision="ENGINE1",
        input_fingerprint="a" * 64, metrics=METRICS,
    )
    bad = receipt.__class__(
        "EX1", "OTHER", receipt.strategy_revision, receipt.execution_semantics,
        receipt.engine_revision, receipt.input_fingerprint, True, receipt.metrics
    )
    with pytest.raises(ExecutionAdapterError):
        validate_adapter_output(spec=s, receipt=bad)


def test_adapter_strategy_revision_mismatch_is_rejected():
    s = spec()
    receipt = build_execution_receipt(
        execution_id="EX1", spec=s, engine_revision="ENGINE1",
        input_fingerprint="a" * 64, metrics=METRICS,
    )
    bad = receipt.__class__(
        "EX1", "T1", "OTHER", receipt.execution_semantics,
        receipt.engine_revision, receipt.input_fingerprint, True, receipt.metrics
    )
    with pytest.raises(ExecutionAdapterError):
        validate_adapter_output(spec=s, receipt=bad)


def test_incomplete_execution_cannot_be_adapted():
    s = spec()
    with pytest.raises(Exception):
        build_execution_receipt(
            execution_id="EX1", spec=s, engine_revision="ENGINE1",
            input_fingerprint="a" * 64, metrics=METRICS, completed=False,
        )


def test_adapter_semantics_are_taken_from_spec():
    assert adapter_semantics(spec()) is ExecutionSemantics.TICK_FEASIBLE
    assert adapter_semantics(spec(ExecutionSemantics.BAR_CLOSE_RESEARCH)) is ExecutionSemantics.BAR_CLOSE_RESEARCH


def test_receipt_requires_explicit_engine_revision():
    s = spec()
    with pytest.raises(Exception):
        build_execution_receipt(
            execution_id="EX1", spec=s, engine_revision="",
            input_fingerprint="a" * 64, metrics=METRICS,
        )


def test_receipt_requires_input_identity():
    s = spec()
    with pytest.raises(Exception):
        build_execution_receipt(
            execution_id="EX1", spec=s, engine_revision="ENGINE1",
            input_fingerprint="", metrics=METRICS,
        )
