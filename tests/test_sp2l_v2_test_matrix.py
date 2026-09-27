from datetime import date

from scripts.sp2l_v2_test_matrix import build_matrix, weekly_ranges


def test_weekly_ranges_are_monday_based():
    weeks = list(weekly_ranges(date(2026, 1, 1), date(2026, 1, 20)))
    assert weeks[0][0].weekday() == 0
    assert all((end - start).days == 7 for start, end in weeks)


def test_primary_matrix_covers_all_four_windows():
    cases = build_matrix(date(2026, 1, 1), date(2026, 1, 31))
    primary = [c for c in cases if c.population == "PRIMARY"]
    assert {c.symbol for c in primary} == {"XAUUSD"}
    assert {c.timeframe for c in primary} == {"M1"}
    assert {c.session_start_utc for c in primary} == {None, "07:00", "08:00", "13:00"}
    assert len(primary) % 4 == 0


def test_robustness_variants_are_not_primary():
    cases = build_matrix(date(2026, 1, 1), date(2026, 1, 31))
    robust = [c for c in cases if c.population == "ROBUSTNESS_DIAGNOSTIC"]
    assert robust
    assert all(c.population != "PRIMARY" for c in robust)
    assert any(c.symbol == "BTCUSD" for c in robust)
    assert any(c.timeframe == "M15" for c in robust)
