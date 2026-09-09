from sp2l_data_contract import QualityState, aggregate_fixed_bucket, audit_ohlc


def row(ts, o, h, l, c):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c}


def test_valid_ohlc_passes():
    report = audit_ohlc([row("2026-01-01T00:00:00Z", 1, 3, 0, 2)])
    assert report.state is QualityState.PASS


def test_duplicate_timestamp_blocks():
    rows = [
        row("2026-01-01T00:00:00Z", 1, 3, 0, 2),
        row("2026-01-01T00:00:00Z", 2, 4, 1, 3),
    ]
    assert audit_ohlc(rows).state is QualityState.BLOCKED


def test_invalid_ohlc_blocks():
    assert audit_ohlc([row("t", 1, 0, 0, 1)]).state is QualityState.BLOCKED


def test_fixed_bucket_is_deterministic():
    rows = [
        row("t0", 10, 12, 9, 11),
        row("t1", 11, 15, 10, 14),
        row("t2", 14, 16, 13, 15),
    ]
    assert aggregate_fixed_bucket(rows) == {
        "timestamp": "t0", "open": 10, "high": 16, "low": 9, "close": 15
    }
