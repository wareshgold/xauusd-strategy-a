from scripts.sp2l_strategy_a_v2_detector import detect_setup, find_first_entry


def c(t, o, h, l, close):
    return {"time": t, "open": o, "high": h, "low": l, "close": close}


def test_buy_v2_setup_and_trigger():
    candles = [
        c(1, 100.0, 101.0, 99.9, 100.8),
        c(2, 102.0, 105.0, 101.9, 104.0),
        c(3, 106.0, 108.0, 105.5, 107.0),
        c(4, 106.8, 107.5, 106.0, 106.2),
        c(5, 106.0, 107.0, 105.0, 105.5),
    ]
    # Before=1, Spike=2, After=3: after.low=105.5 > before.high+1=102.
    setup = detect_setup(candles[:3])
    assert setup is not None
    assert setup["direction"] == "BUY"
    assert setup["sl"] == 99.9

    entry = find_first_entry(candles, 2, setup)
    assert entry is not None
    assert entry["entry_index"] == 4
    assert entry["entry"] == 105.0
    assert entry["risk"] == 5.1
    assert entry["tp"] == 110.1


def test_sell_v2_setup_and_trigger():
    candles = [
        c(1, 100.0, 100.1, 98.9, 99.2),
        c(2, 98.0, 98.1, 95.0, 96.0),
        c(3, 94.0, 94.5, 92.0, 93.0),
        c(4, 93.2, 94.0, 93.0, 93.8),
        c(5, 94.0, 95.0, 93.5, 94.5),
    ]
    setup = detect_setup(candles[:3])
    assert setup is not None
    assert setup["direction"] == "SELL"
    assert setup["sl"] == 100.1

    entry = find_first_entry(candles, 2, setup)
    assert entry is not None
    assert entry["entry_index"] == 4
    assert entry["entry"] == 95.0
    assert entry["risk"] == 5.1
    assert entry["tp"] == 89.9


def test_first_invalid_trigger_rejects_setup():
    candles = [
        c(1, 100.0, 101.0, 99.9, 100.8),
        c(2, 102.0, 105.0, 101.9, 104.0),
        c(3, 106.0, 108.0, 105.5, 107.0),
        c(4, 100.0, 107.5, 90.0, 100.0),
        c(5, 99.0, 100.0, 89.0, 99.5),
    ]
    setup = detect_setup(candles[:3])
    assert setup is not None
    assert find_first_entry(candles, 2, setup) is None
