from datetime import datetime, timezone
import pytest
from .demo_event_ordering import EventOrderGuard
from .demo_recovery_journal import RecoveryJournal
from .demo_restart_recovery import recover_order
from .models import OrderStatus

def test_journal_ordering():
    j = RecoveryJournal(); t = datetime(2026,9,9,tzinfo=timezone.utc)
    assert j.append(t,'x','SUBMIT').sequence == 1
    assert j.append(t,'x','FILL').sequence == 2

def test_order_guard_rejects_gap():
    g = EventOrderGuard(); g.accept('SUBMIT',1)
    with pytest.raises(ValueError): g.accept('FILL',3)

def test_restart_recovery():
    j = RecoveryJournal(); t = datetime(2026,9,9,tzinfo=timezone.utc)
    j.append(t,'x','SUBMIT'); j.append(t,'x','FILL')
    assert recover_order('x',j.events()).state.status is OrderStatus.FILLED
