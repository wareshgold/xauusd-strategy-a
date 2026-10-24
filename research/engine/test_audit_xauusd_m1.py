import json
from pathlib import Path

from audit_xauusd_m1 import audit, derive_m5


def write_dataset(tmp_path: Path):
    candles = []
    for i in range(10):
        minute = i
        candles.append({
            "timestamp": f"2026-01-01 00:{minute:02d}:00",
            "open": 100 + i,
            "high": 101 + i,
            "low": 99 + i,
            "close": 100.5 + i,
        })
    p = tmp_path / "m1.json"
    p.write_text(json.dumps({"symbol":"XAU/USD","timeframe":"1min","source":"twelvedata","timezone":"UTC","candles":candles}))
    return p


def test_derive_m5_is_deterministic(tmp_path):
    p = write_dataset(tmp_path)
    candles = json.loads(p.read_text())["candles"]
    derived = derive_m5(candles)
    assert len(derived) == 2
    assert derived[0]["timestamp"] == "2026-01-01 00:00:00"
    assert derived[0]["open"] == 100
    assert derived[0]["high"] == 105
    assert derived[0]["low"] == 99
    assert derived[0]["close"] == 104.5


def test_audit_clean_dataset(tmp_path):
    p = write_dataset(tmp_path)
    report = audit(p, None)
    assert report["candle_count"] == 10
    assert report["duplicate_timestamps"] == 0
    assert report["non_monotonic_pairs"] == 0
    assert report["missing_or_non_1m_intervals"] == 0
    assert report["invalid_ohlc"] == 0
    assert report["non_positive_prices"] == 0


def test_audit_detects_gap_and_bad_ohlc(tmp_path):
    p = write_dataset(tmp_path)
    payload = json.loads(p.read_text())
    payload["candles"][5]["timestamp"] = "2026-01-01 00:07:00"
    payload["candles"][6]["high"] = 90
    p.write_text(json.dumps(payload))
    report = audit(p, None)
    assert report["missing_or_non_1m_intervals"] > 0
    assert report["invalid_ohlc"] > 0
