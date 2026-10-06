from dataclasses import replace
import pytest

from strategy_factory.multiple_comparison import adjust_p_values
from strategy_factory.statistical_comparison_evidence import bind_statistical_comparison_evidence
from strategy_factory.statistical_comparison_evidence_ledger import (
    StatisticalComparisonEvidenceLedger,
    StatisticalComparisonEvidenceLedgerError,
)


def _evidence():
    from test_statistical_comparison_evidence import _comparison
    comparison = _comparison()
    adjustment = adjust_p_values((0.01,), method="HOLM")
    return bind_statistical_comparison_evidence(comparison, adjustment)


def test_ledger_records_and_is_idempotent():
    evidence = _evidence()
    ledger = StatisticalComparisonEvidenceLedger()
    first = ledger.record(evidence)
    second = ledger.record(evidence)
    assert first == second
    assert ledger.contains(evidence)
    assert len(ledger.entries()) == 1


def test_tampered_evidence_is_rejected():
    evidence = _evidence()
    tampered = replace(evidence, fingerprint="0" * 64)
    with pytest.raises(StatisticalComparisonEvidenceLedgerError, match="fingerprint"):
        StatisticalComparisonEvidenceLedger().record(tampered)


def test_conflicting_evidence_for_same_comparison_is_rejected():
    evidence = _evidence()
    alternate = bind_statistical_comparison_evidence(
        __import__("test_statistical_comparison_evidence", fromlist=["_comparison"])._comparison(),
        adjust_p_values((0.02,), method="HOLM"),
    )
    ledger = StatisticalComparisonEvidenceLedger()
    ledger.record(evidence)
    with pytest.raises(StatisticalComparisonEvidenceLedgerError, match="conflicting"):
        ledger.record(alternate)


def test_ledger_entries_are_immutable():
    evidence = _evidence()
    entry = StatisticalComparisonEvidenceLedger().record(evidence)
    with pytest.raises(Exception):
        entry.family_size = 99
