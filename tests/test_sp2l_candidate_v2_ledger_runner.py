from scripts.sp2l_candidate_ledger import candidate_manifest, record_signal


def test_candidate_manifest_contains_execution_contract():
    manifest = candidate_manifest(
        candidate_id="V2-CANDIDATE-001",
        detector_sha="detector-sha",
        configuration={"p_gap_price": 1.0, "tp_r": 1.0},
        dataset={"symbol_used": "XAUUSD.ecn", "timeframe": "M1"},
        execution_convention={
            "same_bar_sl_tp": "SL_FIRST",
            "entry_bar_exit": "disabled",
        },
    )

    assert manifest.canonical is False
    assert manifest.configuration["p_gap_price"] == 1.0
    assert manifest.execution_convention["same_bar_sl_tp"] == "SL_FIRST"


def test_signal_id_is_stable_for_same_candidate_setup():
    kwargs = dict(
        candidate_id="V2-CANDIDATE-001",
        direction="BUY",
        before_spike_time=100,
        spike_time=101,
        after_spike_time=102,
        entry_time=103,
        entry=100.0,
        sl=95.0,
        tp=105.0,
        risk=5.0,
        status="ACCEPTED",
    )

    first = record_signal(**kwargs)
    second = record_signal(**kwargs)

    assert first.signal_id == second.signal_id
    assert first.setup_key == ("BUY", 100, 101, 102)
