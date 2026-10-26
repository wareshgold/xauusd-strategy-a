from __future__ import annotations

import pytest

from strategy_factory.synthetic_fixtures import (
    FixtureStatus,
    TickQuote,
    classify_outcome_sensitivity,
    preserve_source_order,
    resolve_sl_tp_order,
    select_completed_bar,
)


def test_equal_timestamp_quotes_preserve_input_order_without_deduplication():
    quotes = (
        TickQuote(time_msc=1000, source_row=7, bid=2300.01, ask=2300.21),
        TickQuote(time_msc=1000, source_row=8, bid=2300.03, ask=2300.23),
        TickQuote(time_msc=1001, source_row=9, bid=2300.02, ask=2300.22),
    )
    result = preserve_source_order(quotes)
    assert result == quotes
    assert [q.source_row for q in result] == [7, 8, 9]
    assert len(result) == 3


def test_source_order_rejects_backward_time_instead_of_sorting():
    quotes = (
        TickQuote(time_msc=1001, source_row=1, bid=2300.01, ask=2300.21),
        TickQuote(time_msc=1000, source_row=2, bid=2300.02, ask=2300.22),
    )
    with pytest.raises(ValueError, match="timestamps moved backwards"):
        preserve_source_order(quotes)


def test_source_order_requires_unique_increasing_row_ordinals():
    quotes = (
        TickQuote(time_msc=1000, source_row=4, bid=2300.01, ask=2300.21),
        TickQuote(time_msc=1000, source_row=4, bid=2300.02, ask=2300.22),
    )
    with pytest.raises(ValueError, match="source_row must be strictly increasing"):
        preserve_source_order(quotes)


def test_different_outcomes_for_same_timestamp_order_are_flagged():
    assert classify_outcome_sensitivity(("SL", "TP")) is FixtureStatus.ORDER_SENSITIVE
    assert classify_outcome_sensitivity(("SL", "SL")) is FixtureStatus.DETERMINISTIC
    assert classify_outcome_sensitivity(()) is FixtureStatus.UNRESOLVED


def test_ohlc_touching_both_sl_and_tp_is_ambiguous_without_ordered_ticks():
    assert resolve_sl_tp_order(None, ohlc_touches_both=True) == (
        FixtureStatus.AMBIGUOUS,
        None,
    )


def test_explicit_tick_order_resolves_first_touch_only():
    assert resolve_sl_tp_order(("TP", "SL")) == (
        FixtureStatus.DETERMINISTIC,
        "TP",
    )
    assert resolve_sl_tp_order(("SL", "TP")) == (
        FixtureStatus.DETERMINISTIC,
        "SL",
    )


def test_unknown_hit_vocabulary_does_not_create_a_result():
    assert resolve_sl_tp_order(("ENTRY",)) == (FixtureStatus.UNRESOLVED, None)


def test_forming_bar_is_not_selected_as_completed():
    bars = [
        {"time": 10, "high": 2301.0, "low": 2299.0, "completed": True},
        {"time": 11, "high": 2302.0, "low": 2298.0, "completed": False},
    ]
    assert select_completed_bar(bars) is None


def test_latest_explicitly_completed_bar_is_selected():
    bars = [
        {"time": 10, "high": 2301.0, "low": 2299.0, "completed": True},
        {"time": 11, "high": 2302.0, "low": 2298.0, "completed": True},
    ]
    assert select_completed_bar(bars) == bars[-1]


def test_no_bar_is_unresolved():
    assert select_completed_bar([]) is None
