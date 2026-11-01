from strategy_factory.v3_exit_engine import V3ExitReplayEngine


def bars(rows):
    fields = ("time", "open", "high", "low", "close", "tick_volume", "spread", "real_volume")
    return [dict(zip(fields, row)) for row in rows]


def candidate(entry_idx=0):
    return {
        "entry_idx": entry_idx,
        "trigger_time": 1_800_000_000,
        "signal_time_utc": "2027-01-15T08:00:00+00:00",
        "direction": "BUY",
        "theoretical_entry": 100.0,
        "sl": 95.0,
        "risk": 5.0,
    }


def engine(m1, population=None):
    return V3ExitReplayEngine(
        bars=m1,
        population=population or [candidate()],
        mt5_point=0.01,
        contract_size=100.0,
        volume=0.01,
        engine_revision="TEST-V3-ENGINE-1",
        dataset_sha256="a" * 64,
        entry_population_sha256="b" * 64,
    )


def test_in_memory_engine_replays_and_caches_exact_parameter_tuple():
    m1 = bars([
        (1_800_000_000, 100, 100, 100, 100, 1, 0, 0),
        (1_800_000_060, 100, 102, 99, 101.9, 1, 0, 0),
        (1_800_000_120, 101.9, 102, 101.7, 101.8, 1, 0, 0),
    ])
    lab = engine(m1)

    first = lab.evaluate(rr=5, activation_points=100, distance_points=20)
    second = lab.evaluate(rr=5, activation_points=100, distance_points=20)

    assert first is not second
    assert first == second
    assert lab.cache_entries == 1
    assert first.summary["signals"] == 1
    assert first.summary["decisive"] == 1
    assert first.trades[0]["reason"] == "TRAIL_SL"
    assert first.trades[0]["realized_R"] == 0.36
    first.trades[0]["reason"] = "MUTATED_BY_CALLER"
    third = lab.evaluate(rr=5, activation_points=100, distance_points=20)
    assert third.trades[0]["reason"] == "TRAIL_SL"


def test_engine_marks_same_bar_stop_and_target_as_ambiguous():
    m1 = bars([
        (1_800_000_000, 100, 100, 100, 100, 1, 0, 0),
        (1_800_000_060, 100, 111, 94, 105, 1, 0, 0),
    ])
    result = engine(m1).evaluate(rr=2, activation_points=None, distance_points=None)

    assert result.trades[0]["ambiguous"] is True
    assert result.trades[0]["reason"] == "SL_AND_TP_SAME_BAR"
    assert result.trades[0]["realized_R"] is None
    assert result.summary["decisive"] == 0


def test_engine_keeps_open_trade_across_missing_m1_interval_ambiguous():
    m1 = bars([
        (1_800_000_000, 100, 100, 100, 100, 1, 0, 0),
        (1_800_000_060, 100, 101, 99, 100, 1, 0, 0),
        (1_800_000_180, 100, 111, 99, 105, 1, 0, 0),
    ])
    result = engine(m1).evaluate(rr=2, activation_points=None, distance_points=None)

    assert result.trades[0]["ambiguous"] is True
    assert result.trades[0]["reason"] == "M1_GAP_WHILE_OPEN"
    assert result.trades[0]["realized_R"] is None


def test_variant_comparison_reports_paired_trade_outcome_changes():
    m1 = bars([
        (1_800_000_000, 100, 100, 100, 100, 1, 0, 0),
        (1_800_000_060, 100, 106, 99, 105, 1, 0, 0),
    ])
    lab = engine(m1)
    left = lab.evaluate(rr=1, activation_points=None, distance_points=None)
    right = lab.evaluate(rr=2, activation_points=None, distance_points=None)

    comparison = lab.compare(left, right)
    assert comparison["paired_trade_count"] == 1
    assert comparison["changed_outcome_count"] == 1
    assert comparison["paired_trades"][0]["left_reason"] == "TP"
    assert comparison["paired_trades"][0]["right_reason"] == "OPEN_OR_UNRESOLVED"
    assert comparison["paired_trades"][0]["delta_R"] is None


def test_engine_rejects_non_chronological_bars():
    m1 = bars([
        (1_800_000_060, 100, 100, 100, 100, 1, 0, 0),
        (1_800_000_000, 100, 101, 99, 100, 1, 0, 0),
    ])
    try:
        engine(m1)
    except ValueError as exc:
        assert "strictly chronological" in str(exc)
    else:
        raise AssertionError("expected non-chronological M1 bars to be rejected")

def test_comparison_rejects_variant_from_another_dataset_session():
    m1 = bars([
        (1_800_000_000, 100, 100, 100, 100, 1, 0, 0),
        (1_800_000_060, 100, 106, 99, 105, 1, 0, 0),
    ])
    first_engine = engine(m1)
    first = first_engine.evaluate(rr=1, activation_points=None, distance_points=None)
    second_engine = V3ExitReplayEngine(
        bars=m1,
        population=[candidate()],
        mt5_point=0.01,
        contract_size=100.0,
        volume=0.01,
        engine_revision="TEST-V3-ENGINE-1",
        dataset_sha256="c" * 64,
        entry_population_sha256="b" * 64,
    )
    second = second_engine.evaluate(rr=2, activation_points=None, distance_points=None)

    try:
        first_engine.compare(first, second)
    except ValueError as exc:
        assert "exact research session" in str(exc)
    else:
        raise AssertionError("expected cross-session variant comparison to be rejected")
