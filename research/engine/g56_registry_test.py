from .source_discrimination_g56 import unresolved_blockers


def test_g56_critical_blockers_remain_registered():
    assert unresolved_blockers() == ("B1", "B2", "B4", "B6")
