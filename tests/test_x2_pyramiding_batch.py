from scripts.run_sp2l_x2_pyramiding_batch import (
    _leg_state, cohort_drawdown, configurations, summarize,
)


def test_eight_expected_x1_and_x2_configurations():
    rows = configurations()
    assert len(rows) == 8
    assert sum(x["kind"] == "X1_ONLY" for x in rows) == 2
    assert sum(x["kind"] == "X1_X2" for x in rows) == 6
    assert {x["threshold"] for x in rows if x["kind"] == "X1_X2"} == {1.0, 1.5, 2.0}


def test_same_minute_cohort_drawdown_is_row_order_invariant():
    events = [
        ("2026-01-01T00:00:00+00:00", 10.0),
        ("2026-01-01T00:00:59+00:00", -5.0),
        ("2026-01-02T00:00:00+00:00", -5.0),
    ]
    assert cohort_drawdown(events) == 5.0
    assert cohort_drawdown(list(reversed(events))) == 5.0


def test_gap_exposure_is_not_lost_inside_ambiguous_state():
    leg = {"reason": "M1_GAP_WHILE_OPEN", "ambiguous": True, "realized_usd": None}
    assert _leg_state(leg) == "GAP_EXPOSED"


def test_ambiguous_combined_signal_is_excluded_from_portfolio_pnl():
    rows = [
        {
            "combined_decisive": True, "combined_ambiguous": False,
            "combined_state": "DECISIVE", "combined_gross_usd": 5.0,
            "initial_risk_usd": 1.0, "x1_state": "DECISIVE",
            "x2_state": "NOT_OPENED", "x1": {"exit_time_utc": "2026-01-01T00:00:00+00:00",
            "realized_usd": 5.0}, "x2": None, "x2_opportunities": 0,
        },
        {
            "combined_decisive": False, "combined_ambiguous": True,
            "combined_state": "AMBIGUOUS", "combined_gross_usd": None,
            "initial_risk_usd": 1.0, "x1_state": "DECISIVE",
            "x2_state": "NOT_OPENED", "x2_status": "AMBIGUOUS", "x1": {"exit_time_utc": "2026-01-01T00:00:00+00:00",
            "realized_usd": 20.0}, "x2": None, "x2_opportunities": 1,
        },
    ]
    summary = summarize(rows, "X1_X2")
    assert summary["combined_decisive"] == 1
    assert summary["combined_ambiguous"] == 1
    assert summary["gross_usd"] == 5.0
    assert summary["combined_gap_exposed"] == 0
    assert summary["x2_ambiguous"] == 1
    assert summary["x2_admissions"] == 0
