from datetime import datetime, timezone

import numpy as np

from scripts.run_sp2l_continuous_poll_forensics import serialize_bar


def _sample_row():
    return np.array(
        (
            1780000000,
            4280.10,
            4282.50,
            4279.80,
            4281.90,
            123,
            7,
            456,
        ),
        dtype=[
            ("time", "i8"),
            ("open", "f8"),
            ("high", "f8"),
            ("low", "f8"),
            ("close", "f8"),
            ("tick_volume", "i8"),
            ("spread", "i8"),
            ("real_volume", "i8"),
        ],
    )


def test_serialize_bar_preserves_raw_timestamp_and_utc_interpretation():
    result = serialize_bar(_sample_row())

    assert result["time_raw"] == 1780000000
    assert result["time_utc_interpreted"] == (
        datetime.fromtimestamp(1780000000, timezone.utc).isoformat()
    )


def test_serialize_bar_preserves_ohlc_values():
    result = serialize_bar(_sample_row())

    assert result["open"] == 4280.10
    assert result["high"] == 4282.50
    assert result["low"] == 4279.80
    assert result["close"] == 4281.90


def test_serialize_bar_normalizes_volume_fields_to_int():
    result = serialize_bar(_sample_row())

    assert isinstance(result["tick_volume"], int)
    assert isinstance(result["spread"], int)
    assert isinstance(result["real_volume"], int)


def test_serialize_bar_is_deterministic():
    row = _sample_row()

    assert serialize_bar(row) == serialize_bar(row)
