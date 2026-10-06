from dataclasses import replace

import pytest

from strategy_factory.robustness import RobustnessMatrixError, build_robustness_matrix
from strategy_factory.robustness_ledger import RobustnessMatrixLedger, RobustnessMatrixLedgerError
from strategy_factory.robustness_governance import RobustnessUsageError, RobustnessUsageLedger
from strategy_factory.test_contract import ExecutionSemantics
from .test_robustness import _member


def _matrix(revision="MATRIX-001", role="DEVELOPMENT"):
    return build_robustness_matrix([
        _member("RUN-001", role=role),
        _member("RUN-002", role=role),
    ], matrix_revision=revision)


def test_ledger_records_and_is_idempotent():
    ledger = RobustnessMatrixLedger()
    matrix = _matrix()
    first = ledger.record(matrix)
    second = ledger.record(matrix)
    assert first == second
    assert len(ledger.entries()) == 1
    ledger.assert_clean()


def test_ledger_rejects_conflicting_same_revision():
    ledger = RobustnessMatrixLedger()
    ledger.record(_matrix("MATRIX-001"))
    with pytest.raises(RobustnessMatrixLedgerError, match="matrix_revision"):
        ledger.record(_matrix("MATRIX-001", role="DEVELOPMENT").__class__(
            **{**_matrix("MATRIX-001", role="DEVELOPMENT").__dict__, "fingerprint": "0" * 64}
        ))


def test_ledger_rejects_tampered_matrix():
    ledger = RobustnessMatrixLedger()
    matrix = _matrix()
    tampered = replace(matrix, fingerprint="0" * 64)
    with pytest.raises(RobustnessMatrixLedgerError, match="fingerprint"):
        ledger.record(tampered)


def test_governance_requires_ledger_registration():
    matrix = _matrix()
    usage = RobustnessUsageLedger()
    with pytest.raises(RobustnessUsageError, match="not registered"):
        usage.record(matrix, ledger=RobustnessMatrixLedger(), purpose="RESEARCH_REPORT")


def test_governance_blocks_validation_from_optimization():
    matrix = _matrix(role="UNTOUCHED_VALIDATION")
    ledger = RobustnessMatrixLedger()
    ledger.record(matrix)
    usage = RobustnessUsageLedger()
    with pytest.raises(RobustnessUsageError, match="cannot be used"):
        usage.record(matrix, ledger=ledger, purpose="OPTIMIZATION")


def test_governance_blocks_holdout_from_parameter_fit():
    matrix = _matrix(role="FRESH_HOLDOUT")
    ledger = RobustnessMatrixLedger()
    ledger.record(matrix)
    usage = RobustnessUsageLedger()
    with pytest.raises(RobustnessUsageError, match="cannot be used"):
        usage.record(matrix, ledger=ledger, purpose="PARAMETER_FIT")


def test_governance_allows_development_research():
    matrix = _matrix(role="DEVELOPMENT")
    ledger = RobustnessMatrixLedger()
    ledger.record(matrix)
    usage = RobustnessUsageLedger()
    entry = usage.record(matrix, ledger=ledger, purpose="RESEARCH_REPORT")
    assert entry.disposition.value == "ALLOWED"
    assert len(usage.entries()) == 1
    usage.assert_clean()


def test_governance_is_idempotent():
    matrix = _matrix()
    ledger = RobustnessMatrixLedger()
    ledger.record(matrix)
    usage = RobustnessUsageLedger()
    first = usage.record(matrix, ledger=ledger, purpose="RESEARCH_REPORT")
    second = usage.record(matrix, ledger=ledger, purpose="RESEARCH_REPORT")
    assert first == second
    assert len(usage.entries()) == 1
