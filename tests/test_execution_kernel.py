import pytest

from strategy_factory.execution_kernel import (
    AmbiguityPolicy,
    EntryInstruction,
    ExecutionKernelError,
    HistoricalExecutionKernel,
    MarketEvent,
    Side,
)
from strategy_factory.test_contract import ExecutionSemantics


def instruction(side=Side.BUY):
    return EntryInstruction(
        trade_id="T1",
        side=side,
        entry_price=100.0,
        stop_loss=99.0 if side is Side.BUY else 101.0,
        take_profit=102.0 if side is Side.BUY else 98.0,
        risk_price=1.0,
    )


def test_tick_order_is_causal_and_target_can_win_before_later_stop():
    result = HistoricalExecutionKernel().execute(
        semantics=ExecutionSemantics.TICK_FEASIBLE,
        instructions=[instruction()],
        events=[
            MarketEvent("2026-01-01T00:00:00Z", 0, bid=100.0, ask=100.0),
            MarketEvent("2026-01-01T00:00:01Z", 1, bid=102.0, ask=102.0),
            MarketEvent("2026-01-01T00:00:02Z", 2, bid=99.0, ask=99.0),
        ],
    )
    assert result.trades[0].exit_reason == "TARGET"
    assert result.metrics.net_r == 2.0


def test_same_bar_range_is_ambiguous_when_both_levels_are_hit_and_blocked():
    result = HistoricalExecutionKernel().execute(
        semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        instructions=[instruction()],
        events=[
            MarketEvent("2026-01-01T00:00:00Z", 0, high=103.0, low=98.0),
        ],
        ambiguity_policy=AmbiguityPolicy.BLOCK,
    )
    assert result.trades[0].ambiguous is True
    assert result.metrics.ambiguous == 1
    assert result.metrics.decisive_trades == 0


def test_same_bar_policy_is_explicit_and_changes_only_declared_semantics():
    kernel = HistoricalExecutionKernel()
    stop = kernel.execute(
        semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        instructions=[instruction()],
        events=[MarketEvent("2026-01-01T00:00:00Z", 0, high=103.0, low=98.0)],
        ambiguity_policy=AmbiguityPolicy.STOP_FIRST,
    )
    target = kernel.execute(
        semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        instructions=[instruction()],
        events=[MarketEvent("2026-01-01T00:00:00Z", 0, high=103.0, low=98.0)],
        ambiguity_policy=AmbiguityPolicy.TARGET_FIRST,
    )
    assert stop.metrics.net_r == -1.0
    assert target.metrics.net_r == 2.0


def test_sell_tick_hits_stop_then_does_not_look_ahead():
    result = HistoricalExecutionKernel().execute(
        semantics=ExecutionSemantics.TICK_FEASIBLE,
        instructions=[instruction(Side.SELL)],
        events=[
            MarketEvent("2026-01-01T00:00:00Z", 0, bid=100.0, ask=100.0),
            MarketEvent("2026-01-01T00:00:01Z", 1, bid=101.0, ask=101.0),
            MarketEvent("2026-01-01T00:00:02Z", 2, bid=98.0, ask=98.0),
        ],
    )
    assert result.trades[0].exit_reason == "STOP"
    assert result.metrics.net_r == -1.0


def test_events_must_be_strictly_chronological():
    with pytest.raises(ExecutionKernelError):
        HistoricalExecutionKernel().execute(
            semantics=ExecutionSemantics.TICK_FEASIBLE,
            instructions=[instruction()],
            events=[
                MarketEvent("2026-01-01T00:00:01Z", 1, bid=100, ask=100),
                MarketEvent("2026-01-01T00:00:00Z", 0, bid=100, ask=100),
            ],
        )


def test_execution_semantics_must_be_explicit():
    with pytest.raises(ExecutionKernelError):
        HistoricalExecutionKernel().execute(
            semantics="M1",
            instructions=[instruction()],
            events=[],
        )


def test_no_entry_means_no_trade():
    result = HistoricalExecutionKernel().execute(
        semantics=ExecutionSemantics.TICK_FEASIBLE,
        instructions=[instruction()],
        events=[MarketEvent("2026-01-01T00:00:00Z", 0, bid=99, ask=99)],
    )
    assert result.trades == ()
    assert result.metrics.trades == 0


def test_metrics_include_drawdown_and_profit_factor():
    result = HistoricalExecutionKernel().execute(
        semantics=ExecutionSemantics.TICK_FEASIBLE,
        instructions=[
            EntryInstruction("W", Side.BUY, 100, 99, 102, 1),
            EntryInstruction("L", Side.BUY, 100, 99, 102, 1),
        ],
        events=[
            MarketEvent("2026-01-01T00:00:00Z", 0, bid=100, ask=100),
            MarketEvent("2026-01-01T00:00:01Z", 1, bid=102, ask=102),
            MarketEvent("2026-01-01T00:00:02Z", 2, bid=99, ask=99),
        ],
    )
    assert result.metrics.trades == 2
    assert result.metrics.net_r == 4.0
