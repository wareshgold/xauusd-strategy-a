from datetime import datetime, timezone, timedelta

import pytest

from .demo_event_order import OrderedEvent, order_events
from .demo_recovery_journal import RecoveryJournal
from .demo_replay_audit import audit_replay
from .demo_recovery_audit import audit_recovery
from .models import OrderStatus


def test_g89_replay_is_sequence_deterministic():
    t = datetime(2026, 9, 10, tzinfo=timezone.utc)
    events = [
        OrderedEvent(2, t + timedelta(seconds=2), "FILL", "o1"),
        OrderedEvent(1, t, "SUBMIT", "o1"),
    ]
    audit = audit_replay(events)
    assert audit.valid
    assert [e.sequence for e in audit.ordered] == [1, 2]


def test_g89_sequence_gap_fails_closed():
    t = datetime(2026, 9, 10, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        audit_replay([OrderedEvent(1, t, "SUBMIT", "o1"), OrderedEvent(3, t, "FILL", "o1")])


def test_g90_restart_recovery_audit_reconstructs_filled():
    journal = RecoveryJournal()
    t = datetime(2026, 9, 10, tzinfo=timezone.utc)
    journal.append(t, "o1", "SUBMIT")
    journal.append(t, "o1", "FILL")
    audit = audit_recovery("o1", journal.events())
    assert audit.recovered_status is OrderStatus.FILLED
    assert audit.event_count == 2


def test_g91_empty_journal_is_not_success():
    journal = RecoveryJournal()
    audit = audit_recovery("missing", journal.events())
    assert audit.recovered_status is not OrderStatus.FILLED
