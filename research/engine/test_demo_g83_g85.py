from datetime import datetime, timezone

import pytest

from .demo_event_ordering import EventOrderGuard
from .demo_recovery_journal import RecoveryJournal
from .demo_restart_recovery import recover_order
from .demo_order_state_machine import OrderTransition
from .models import OrderStatus


def test_g83_journal_is_sequenced_and_append_only():
    journal = RecoveryJournal()
    ts = datetime(2026, 9, 9, tzinfo=timezone.utc)
    first = journal.append(ts, "o1", "SUBMIT")
    second = journal.append(ts, "o1", "FILL")
    assert first.sequence == 1
    assert second.sequence == 2
    assert [e.event for e in journal.events()] == ["SUBMIT", "FILL"]


def test_g84_rejects_out_of_order_events():
    guard = EventOrderGuard()
    guard.accept("SUBMIT", 1)
    with pytest.raises(ValueError):
        guard.accept("FILL", 3)
    assert guard.next_sequence == 2


def test_g85_restart_rebuilds_terminal_state_from_journal():
    journal = RecoveryJournal()
    ts = datetime(2026, 9, 9, tzinfo=timezone.utc)
    journal.append(ts, "o2", "SUBMIT")
    journal.append(ts, "o2", "FILL")
    recovered = recover_order("o2", journal.events())
    assert recovered.state.status is OrderStatus.FILLED


def test_g85_recovery_does_not_invent_unknown_events():
    journal = RecoveryJournal()
    ts = datetime(2026, 9, 9, tzinfo=timezone.utc)
    journal.append(ts, "o3", "UNKNOWN")
    recovered = recover_order("o3", journal.events())
    assert recovered.state.status is OrderStatus.PENDING
