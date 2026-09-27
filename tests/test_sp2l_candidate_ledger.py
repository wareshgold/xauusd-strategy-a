from scripts.sp2l_candidate_ledger import (
    candidate_manifest,
    compare_signals,
    record_signal,
)


def test_manifest_is_stable_and_never_canonical():
    a = candidate_manifest(
        candidate_id="V2-CANDIDATE-001",
        detector_sha="abc123",
        configuration={"p_gap": 1.0, "tp_r": 1.0},
        dataset={"symbol": "XAUUSD.ecn", "timeframe": "M1"},
        execution_convention={"same_bar": "SL_FIRST"},
    )
    b = candidate_manifest(
        candidate_id="V2-CANDIDATE-001",
        detector_sha="abc123",
        configuration={"tp_r": 1.0, "p_gap": 1.0},
        dataset={"timeframe": "M1", "symbol": "XAUUSD.ecn"},
        execution_convention={"same_bar": "SL_FIRST"},
    )

    assert a.canonical is False
    assert a.stable_id() == b.stable_id()


def test_signal_comparison_detects_added_and_changed_setups():
    common_left = record_signal(
        candidate_id="A",
        direction="BUY",
        before_spike_time=1,
        spike_time=2,
        after_spike_time=3,
        entry_time=4,
        entry=100.0,
        sl=95.0,
        tp=105.0,
        risk=5.0,
        status="ACCEPTED",
    )
    common_right = record_signal(
        candidate_id="B",
        direction="BUY",
        before_spike_time=1,
        spike_time=2,
        after_spike_time=3,
        entry_time=5,
        entry=101.0,
        sl=95.0,
        tp=107.0,
        risk=6.0,
        status="ACCEPTED",
    )
    left_only = record_signal(
        candidate_id="A",
        direction="SELL",
        before_spike_time=10,
        spike_time=11,
        after_spike_time=12,
        entry_time=13,
        entry=90.0,
        sl=95.0,
        tp=85.0,
        risk=5.0,
        status="ACCEPTED",
    )
    right_only = record_signal(
        candidate_id="B",
        direction="BUY",
        before_spike_time=20,
        spike_time=21,
        after_spike_time=22,
        entry_time=23,
        entry=110.0,
        sl=105.0,
        tp=115.0,
        risk=5.0,
        status="ACCEPTED",
    )

    result = compare_signals(
        [common_left, left_only],
        [common_right, right_only],
    )

    assert result["left_total"] == 2
    assert result["right_total"] == 2
    assert result["common"] == 1
    assert result["left_only"] == 1
    assert result["right_only"] == 1
    assert result["changed_common"] == 1
