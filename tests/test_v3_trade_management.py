from strategy_factory.v3_exit_engine import V3ExitReplayEngine
from strategy_factory.v3_trade_management import V3TradeManagementEngine, normalize_policy


def bars(rows):
    fields = ("time", "open", "high", "low", "close", "tick_volume", "spread", "real_volume")
    return [dict(zip(fields, row)) for row in rows]


def candidate():
    return {
        "entry_idx": 0, "trigger_time": 1_800_000_000,
        "signal_time_utc": "2027-01-15T08:00:00+00:00",
        "direction": "BUY", "theoretical_entry": 100.0, "sl": 95.0, "risk": 5.0,
    }


def engine(m1):
    return V3ExitReplayEngine(
        bars=m1, population=[candidate()], mt5_point=0.01,
        contract_size=100.0, volume=0.01, engine_revision="MGMT-TEST-1",
        dataset_sha256="a" * 64, entry_population_sha256="b" * 64,
    )


def test_breakeven_is_applied_after_trigger_bar_and_effective_next_bar():
    m1 = bars([
        (1800000000, 100, 100, 100, 100, 1, 0, 0),
        (1800000060, 100, 103, 99, 102, 1, 0, 0),
        (1800000120, 102, 101, 99.5, 100.5, 1, 0, 0),
    ])
    result = V3TradeManagementEngine(engine(m1)).evaluate({
        "mode": "breakeven", "breakeven_trigger_r": 0.5,
    })
    trade = result.trades[0]
    assert trade["breakeven_activated"] is True
    assert trade["reason"] == "BREAKEVEN_SL"
    assert trade["exit_price"] == 100.0
    assert trade["realized_R"] == 0.0


def test_trailing_management_uses_price_points_and_next_bar_stop():
    m1 = bars([
        (1800000000, 100, 100, 100, 100, 1, 0, 0),
        (1800000060, 100, 103, 100.5, 102.9, 1, 0, 0),
        (1800000120, 102.9, 103, 102.7, 102.8, 1, 0, 0),
    ])
    result = V3TradeManagementEngine(engine(m1)).evaluate({
        "mode": "trailing", "trailing_activation_r": 0.5,
        "trailing_distance_points": 20,
    })
    trade = result.trades[0]
    assert trade["trailing_activated"] is True
    assert trade["reason"] == "TRAIL_SL"
    assert abs(trade["exit_price"] - 102.8) < 1e-12


def test_time_exit_uses_completed_bar_close_and_is_labeled_proxy():
    m1 = bars([
        (1800000000, 100, 100, 100, 100, 1, 0, 0),
        (1800000060, 100, 101, 99.5, 100.5, 1, 0, 0),
        (1800000120, 100.5, 101, 100, 100.8, 1, 0, 0),
    ])
    result = V3TradeManagementEngine(engine(m1)).evaluate({
        "mode": "time_exit", "time_exit_bars": 2,
    })
    trade = result.trades[0]
    assert trade["reason"] == "TIME_EXIT"
    assert trade["exit_price"] == 100.8
    assert trade["bars_held"] == 2


def test_management_policy_validation_rejects_incomplete_or_unknown_policy():
    for policy in (
        {"mode": "trailing", "trailing_activation_r": 1},
        {"mode": "breakeven"},
        {"mode": "unknown"},
        {"mode": "no_target", "target_rr": 2},
        {"mode": "time_exit", "time_exit_bars": 0},
    ):
        try:
            normalize_policy(policy)
        except ValueError:
            pass
        else:
            raise AssertionError(f"policy should be rejected: {policy}")


def test_management_variants_share_frozen_identity_and_are_comparable():
    m1 = bars([
        (1800000000, 100, 100, 100, 100, 1, 0, 0),
        (1800000060, 100, 103, 99, 102, 1, 0, 0),
        (1800000120, 102, 102, 99.5, 100, 1, 0, 0),
    ])
    base = engine(m1)
    lab = V3TradeManagementEngine(base)
    be = lab.evaluate({"mode": "breakeven", "breakeven_trigger_r": 0.5})
    no_target = lab.evaluate({"mode": "no_target"})
    comparison = base.compare(be, no_target)
    assert comparison["paired_trade_count"] == 1
    assert be.management_config["mode"] == "breakeven"
    assert lab.cache_entries == 2
