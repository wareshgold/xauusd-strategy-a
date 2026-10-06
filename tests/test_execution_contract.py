import pytest

from strategy_factory.execution import (
    ExecutionContractError,
    ExecutionReceipt,
    execution_gate,
    validate_execution_binding,
)
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.models import GateStatus
from strategy_factory.test_contract import ExecutionSemantics, HistoricalTestSpec, TestDataset, DatasetRole
from strategy_factory.runs import ResearchRunLedger
from strategy_factory.datasets import DatasetRegistry
from strategy_factory.usage import DatasetUsageLedger


def metric():
    return ResearchMetrics(10, 10, 6, 4, 0, .6, 2.5, 1.4, 1.2, 6.0, -3.5)


def setup():
    dataset=TestDataset("D1", DatasetRole.DEVELOPMENT, "R1", "2026-01-01", "2026-02-01", "FIXTURE")
    spec=HistoricalTestSpec("T1","SP2L-A","S1",dataset,ExecutionSemantics.TICK_FEASIBLE)
    registry=DatasetRegistry()
    registry.register(dataset,"a"*64)
    usage=DatasetUsageLedger(registry)
    runs=ResearchRunLedger(registry,usage)
    run=runs.create(spec,manifest_revision="M1",run_id="RUN1",observed_fingerprint="a"*64)
    receipt=ExecutionReceipt("EX1","T1","S1",ExecutionSemantics.TICK_FEASIBLE,"ENGINE1","a"*64,True,metric())
    return spec,run,receipt


def test_exact_execution_binding_passes():
    spec,run,receipt=setup()
    validate_execution_binding(spec=spec,run=run,receipt=receipt)


def test_semantics_mismatch_is_rejected():
    spec,run,receipt=setup()
    bad=ExecutionReceipt("EX1","T1","S1",ExecutionSemantics.BAR_CLOSE_RESEARCH,"ENGINE1","a"*64,True,metric())
    with pytest.raises(ExecutionContractError):
        validate_execution_binding(spec=spec,run=run,receipt=bad)


def test_incomplete_execution_is_rejected():
    spec,run,receipt=setup()
    bad=ExecutionReceipt("EX1","T1","S1",ExecutionSemantics.TICK_FEASIBLE,"ENGINE1","a"*64,False,metric())
    with pytest.raises(ExecutionContractError):
        bad.validate()


def test_strategy_revision_mismatch_is_rejected():
    spec,run,receipt=setup()
    bad=ExecutionReceipt("EX1","T1","OTHER","ENGINE1","a"*64,True,metric())
    with pytest.raises(Exception):
        validate_execution_binding(spec=spec,run=run,receipt=bad)


def test_execution_gate_blocks_missing_inputs():
    assert execution_gate(spec=None,run=None,receipt=None).status is GateStatus.BLOCKED


def test_execution_gate_passes_exact_binding():
    spec,run,receipt=setup()
    assert execution_gate(spec=spec,run=run,receipt=receipt).status is GateStatus.PASS


def test_execution_gate_fails_semantics_mismatch():
    spec,run,receipt=setup()
    bad=ExecutionReceipt("EX1","T1","S1",ExecutionSemantics.BAR_CLOSE_RESEARCH,"ENGINE1","a"*64,True,metric())
    assert execution_gate(spec=spec,run=run,receipt=bad).status is GateStatus.FAIL
