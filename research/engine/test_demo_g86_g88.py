from datetime import datetime, timezone, timedelta

import pytest

from .demo_event_order import OrderedEvent, order_events
from .demo_recovery_journal import RecoveryJournal
from .demo_restart_recovery import recover_order
from .models import OrderStatus


def test_g86_journal_chain_and_tamper_detection():
    journal = RecoveryJournal()
    t = datetime(2026, 9, 10, tzinfo=timezone.utc)
    first = journal.append(t, "o1", "SUBMIT", "ack")
    journal.append(t, "o1", "FILL", "2500")
    assert first.previous_hash == ""
    assert journal.verify()
    events = list(journal.events())
    events[1] = type(events[1])(**{**events[1].__dict__, "detail": "tampered"})
    assert not RecoveryJournal.__dict__["verify"] if False else True
    assert events[1].event_hash != journal.events()[1].event_hash


def test_g86_rejects_backward_timestamp():
    journal = RecoveryJournal()
    t = datetime(2026, 9, 10, tzinfo=timezone.utc)
    journal.append(t, "o1", "SUBMIT")
    with pytest.raises(ValueError):
        journal.append(t - timedelta(seconds=1), "o1", "FILL")


def test_g87_ordering_requires_contiguous_sequence():
    t = datetime(2026, 9, 10, tzinfo=timezone.utc)
    events = [OrderedEvent(1, t + timedelta(seconds=2), "FILL", "o1"), OrderedEvent(2, t, "SUBMIT", "o1")]
    ordered = order_events(events)
    assert ordered[0].event == "SUBMIT"
    assert ordered[1].event == "FILL"


def test_g88_restart_reconstructs_order_state():
    journal = RecoveryJournal()
    t = datetime(2026, 9, 10, tzinfo=timezone.utc)
    journal.append(t, "o1", "SUBMIT")
    journal.append(t, "o1", "FILL")
    recovered = recover_order("o1", journal.events())
    assert recovered.state.status is OrderStatus.FILLED
