import pytest

from .demo_observability import HealthState, evaluate_health
from .demo_observability_report import build_report


def test_g92_journal_failure_blocks():
    health = evaluate_health(journal_ok=False, reconciliation_ok=True, connected=True)
    assert health.state is HealthState.BLOCKED


def test_g92_disconnect_or_reconciliation_failure_degrades():
    assert evaluate_health(journal_ok=True, reconciliation_ok=True, connected=False).state is HealthState.DEGRADED
    assert evaluate_health(journal_ok=True, reconciliation_ok=False, connected=True).state is HealthState.DEGRADED


def test_g92_healthy_prerequisites():
    assert evaluate_health(journal_ok=True, reconciliation_ok=True, connected=True).state is HealthState.HEALTHY


def test_g93_report_rejects_negative_counts():
    health = evaluate_health(journal_ok=True, reconciliation_ok=True, connected=True)
    with pytest.raises(ValueError):
        build_report(health, open_orders=-1, journal_events=0, last_sequence=None)


def test_g94_report_preserves_audit_fields():
    health = evaluate_health(journal_ok=True, reconciliation_ok=True, connected=True)
    report = build_report(health, open_orders=2, journal_events=9, last_sequence=9)
    assert report.open_orders == 2
    assert report.journal_events == 9
    assert report.last_sequence == 9
