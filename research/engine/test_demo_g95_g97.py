from .demo_observability import HealthState, evaluate_health
from .demo_safety_rehearsal import RehearsalResult, rehearse


def test_g95_healthy_rehearsal_passes():
    health = evaluate_health(journal_ok=True, reconciliation_ok=True, connected=True)
    result = rehearse(health)
    assert result.result is RehearsalResult.PASS


def test_g96_degraded_rehearsal_blocks():
    health = evaluate_health(journal_ok=True, reconciliation_ok=False, connected=True)
    result = rehearse(health)
    assert result.result is RehearsalResult.BLOCK


def test_g97_journal_failure_blocks():
    health = evaluate_health(journal_ok=False, reconciliation_ok=True, connected=True)
    result = rehearse(health)
    assert result.result is RehearsalResult.BLOCK
