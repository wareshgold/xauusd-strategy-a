"""Deterministic consistency tests for the shared SP2L research detector."""

from __future__ import annotations

import numpy as np

from sp2l_author_replica_detector import detect


def bar(t, o, h, l, c):
    return (t, o, h, l, c)


def fixture(rows):
    return np.array(
        rows,
        dtype=[
            ("time", "i8"),
            ("open", "f8"),
            ("high", "f8"),
            ("low", "f8"),
            ("close", "f8"),
        ],
    )


def main():
    buy = fixture([
        bar(1, 100, 102, 99, 101),
        bar(2, 102, 107, 101, 106),
        bar(3, 106, 108, 104, 107),
        bar(4, 105, 107, 102, 106),
        bar(5, 106, 107, 101, 106),
    ])
    sell = fixture([
        bar(1, 101, 102, 99, 100),
        bar(2, 100, 101, 94, 95),
        bar(3, 95, 97, 93, 94),
        bar(4, 96, 99, 95, 95),
        bar(5, 95, 97, 94, 96),
    ])

    buy_result = detect(buy)
    sell_result = detect(sell)

    assert buy_result == {
        "direction": "BUY",
        "signal_time": 4,
        "entry": 102.0,
        "sl": 101.0,
        "risk": 1.0,
        "tp": 103.0,
    }
    assert sell_result == {
        "direction": "SELL",
        "signal_time": 4,
        "entry": 99.0,
        "sl": 101.0,
        "risk": 2.0,
        "tp": 97.0,
    }

    neutral = fixture([
        bar(1, 100, 101, 99, 100),
        bar(2, 100, 101, 99, 100),
        bar(3, 100, 101, 99, 100),
        bar(4, 100, 101, 99, 100),
        bar(5, 100, 101, 99, 100),
    ])
    assert detect(neutral) is None

    print("SP2L_AUTHOR_REPLICA_DETECTOR_CONSISTENCY=PASS")
    print({"buy": buy_result, "sell": sell_result, "neutral": None})


if __name__ == "__main__":
    main()
