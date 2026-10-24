"""Source-aligned synthetic parity fixtures for Strategy B vs RR2/TRAIL4.

These tests exercise small, explicitly sourced arithmetic/branch facts only. They
are not a full replay, do not choose canonical SP2L geometry, and do not model
broker fills or intrabar event ordering.
"""
from __future__ import annotations

import unittest


# Values transcribed from:
# Strategy B: scripts/strategy_b_pythontraderbot_live/SP2L_Advanced_Bot_Optimized.py
# RR2/TRAIL4: scripts/sp2l_v3_rr2_trail4_config.py
# These are test vectors, not a shared strategy configuration.
SOURCE_FIXTURES = [
    {
        "id": "UNIT-01-strategy-b-broker-point-conversion",
        "source": "Strategy B PGAP_POINTS=100; MAX_SL_DISTANCE_POINTS=1000",
        "broker_point": 0.01,
        "pgap_points": 100,
        "max_sl_points": 1000,
        "expected_pgap_price": 1.0,
        "expected_max_sl_price": 10.0,
    },
    {
        "id": "UNIT-02-broker-point-is-not-universal",
        "source": "Conversion formula is points multiplied by configured broker point",
        "broker_point": 0.001,
        "pgap_points": 100,
        "max_sl_points": 1000,
        "expected_pgap_price": 0.1,
        "expected_max_sl_price": 1.0,
    },
    {
        "id": "RR-03-distinct-tp-r",
        "strategy_b_tp_r": 0.9,
        "rr2_trail4_tp_r": 2.0,
        "risk": 2.0,
        "entry": 100.0,
        "expected_strategy_b_buy_tp": 101.8,
        "expected_rr2_buy_tp": 104.0,
    },
    {
        "id": "TRAIL-04-configured-distance-and-stop",
        "trail_pips": 4.0,
        "pip_size_price": 0.1,
        "buy_favorable_extreme": 105.0,
        "sell_favorable_extreme": 95.0,
        "expected_distance": 0.4,
        "expected_buy_stop": 104.6,
        "expected_sell_stop": 95.4,
    },
    {
        "id": "ENTRY-05-strategy-b-buy-requires-current-low-break",
        "previous_low": 100.0,
        "current_low_no_break": 100.0,
        "current_low_break": 99.5,
        "sl": 95.0,
        "max_sl_distance": 10.0,
        "expected_no_break": False,
        "expected_break": True,
        "expected_entry": 99.5,
        "expected_risk": 4.5,
    },
    {
        "id": "EXIT-06-same-ohcl-bar-does-not-order-events",
        "sl": 95.0,
        "tp": 105.0,
        "bar_low": 94.0,
        "bar_high": 106.0,
        "finer_grained_evidence": False,
        "expected_status": "AMBIGUOUS",
    },
]


def broker_points_to_price(points: float, broker_point: float) -> float:
    """Arithmetic conversion used by the Strategy B source."""
    return points * broker_point


def rr_target(entry: float, risk: float, tp_r: float, direction: str) -> float:
    """Pure arithmetic only; not an execution/fill model."""
    if direction == "BUY":
        return entry + tp_r * risk
    if direction == "SELL":
        return entry - tp_r * risk
    raise ValueError("direction must be BUY or SELL")


def configured_trail_stop(direction: str, favorable_extreme: float, distance: float) -> float:
    """Mirror the RR2/TRAIL4 config's trail_stop arithmetic."""
    if direction == "BUY":
        return favorable_extreme - distance
    if direction == "SELL":
        return favorable_extreme + distance
    raise ValueError("direction must be BUY or SELL")


def classify_same_bar_exit(sl: float, tp: float, low: float, high: float,
                           finer_grained_evidence: bool) -> str:
    """Evidence classifier: do not invent SL-vs-TP ordering from OHLC."""
    sl_touched = low <= sl <= high or low <= sl
    tp_touched = low <= tp <= high or high >= tp
    if sl_touched and tp_touched and not finer_grained_evidence:
        return "AMBIGUOUS"
    return "NEEDS_EVENT_SEQUENCE_REVIEW"


class StrategySourceParityFixtureTests(unittest.TestCase):
    def test_fixture_ids_are_unique(self):
        ids = [item["id"] for item in SOURCE_FIXTURES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_strategy_b_point_conversion_depends_on_broker_point(self):
        for fixture in SOURCE_FIXTURES[:2]:
            with self.subTest(fixture=fixture["id"]):
                self.assertAlmostEqual(
                    broker_points_to_price(fixture["pgap_points"], fixture["broker_point"]),
                    fixture["expected_pgap_price"],
                )
                self.assertAlmostEqual(
                    broker_points_to_price(fixture["max_sl_points"], fixture["broker_point"]),
                    fixture["expected_max_sl_price"],
                )
        # Same point counts, different symbol point => different price distances.
        self.assertNotEqual(
            SOURCE_FIXTURES[0]["expected_pgap_price"],
            SOURCE_FIXTURES[1]["expected_pgap_price"],
        )

    def test_tp_targets_keep_strategy_r_values_separate(self):
        fixture = SOURCE_FIXTURES[2]
        self.assertAlmostEqual(
            rr_target(fixture["entry"], fixture["risk"], fixture["strategy_b_tp_r"], "BUY"),
            fixture["expected_strategy_b_buy_tp"],
        )
        self.assertAlmostEqual(
            rr_target(fixture["entry"], fixture["risk"], fixture["rr2_trail4_tp_r"], "BUY"),
            fixture["expected_rr2_buy_tp"],
        )
        self.assertNotEqual(
            fixture["expected_strategy_b_buy_tp"], fixture["expected_rr2_buy_tp"]
        )

    def test_rr2_trail4_distance_and_directional_stop_arithmetic(self):
        fixture = SOURCE_FIXTURES[3]
        distance = fixture["trail_pips"] * fixture["pip_size_price"]
        self.assertAlmostEqual(distance, fixture["expected_distance"])
        self.assertAlmostEqual(
            configured_trail_stop("BUY", fixture["buy_favorable_extreme"], distance),
            fixture["expected_buy_stop"],
        )
        self.assertAlmostEqual(
            configured_trail_stop("SELL", fixture["sell_favorable_extreme"], distance),
            fixture["expected_sell_stop"],
        )

    def test_strategy_b_buy_entry_condition_is_a_low_break_not_a_fill_proof(self):
        fixture = SOURCE_FIXTURES[4]
        no_break = fixture["current_low_no_break"] < fixture["previous_low"]
        has_break = fixture["current_low_break"] < fixture["previous_low"]
        self.assertEqual(no_break, fixture["expected_no_break"])
        self.assertEqual(has_break, fixture["expected_break"])
        entry = fixture["current_low_break"]
        risk = entry - fixture["sl"]
        self.assertAlmostEqual(entry, fixture["expected_entry"])
        self.assertAlmostEqual(risk, fixture["expected_risk"])
        # This source condition alone is not an actual broker fill event.
        self.assertNotIn("fill", fixture)

    def test_same_bar_both_levels_touched_remains_ambiguous(self):
        fixture = SOURCE_FIXTURES[5]
        self.assertLessEqual(fixture["bar_low"], fixture["sl"])
        self.assertGreaterEqual(fixture["bar_high"], fixture["tp"])
        self.assertEqual(
            classify_same_bar_exit(
                fixture["sl"], fixture["tp"], fixture["bar_low"],
                fixture["bar_high"], fixture["finer_grained_evidence"],
            ),
            fixture["expected_status"],
        )


if __name__ == "__main__":
    unittest.main()
