from dataclasses import replace

import pytest

from strategy_factory.robustness import build_robustness_matrix
from strategy_factory.robustness_ledger import RobustnessMatrixLedger, RobustnessMatrixLedgerError
from strategy_factory.robustness_governance import RobustnessUsageError, RobustnessUsageLedger
from test_robustness import _member


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
    first = _matrix("MATRIX-001")
    ledger.record(first)
    second = build_robustness_matrix([
        _member("RUN-001", strategy_revision="RESEARCH-ALT"),
        _member("RUN-002", strategy_revision="RESEARCH-ALT"),
    ], matrix_revision="MATRIX-001")
    with pytest.raises(RobustnessMatrixLedgerError, match="matrix_revision"):
        ledger.record(second)

