import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from sp2l_trailing_state import (
    load_trailing_state,
    save_trailing_state,
    trailing_record_matches,
    update_favorable_extreme,
)


class TrailingStateTests(unittest.TestCase):
    def test_buy_extreme_never_moves_down(self):
        first = update_favorable_extreme("BUY", 100.0, 100.0, 101.0, 99.5)
        second = update_favorable_extreme("BUY", 100.0, first, 100.6, 99.8)
        self.assertEqual(first, 101.0)
        self.assertEqual(second, 101.0)

    def test_sell_extreme_never_moves_up(self):
        first = update_favorable_extreme("SELL", 100.0, 100.0, 100.5, 99.0)
        second = update_favorable_extreme("SELL", 100.0, first, 100.2, 99.4)
        self.assertEqual(first, 99.0)
        self.assertEqual(second, 99.0)

    def test_entry_is_floor_or_ceiling_for_extreme(self):
        self.assertEqual(update_favorable_extreme("BUY", 100.0, 100.0, 99.0, 98.0), 100.0)
        self.assertEqual(update_favorable_extreme("SELL", 100.0, 100.0, 102.0, 101.0), 100.0)

    def test_invalid_direction_and_non_finite_values_rejected(self):
        with self.assertRaises(ValueError):
            update_favorable_extreme("FLAT", 100.0, 100.0, 101.0, 99.0)
        with self.assertRaises(ValueError):
            update_favorable_extreme("BUY", 100.0, 100.0, float("nan"), 99.0)

    def test_record_identity_prevents_ticket_reuse(self):
        record = {
            "symbol": "XAUUSD.ecn", "magic": 26092301, "direction": "BUY",
            "entry": 100.0, "position_time_msc": 123000,
            "favorable_extreme": 101.0,
        }
        self.assertTrue(trailing_record_matches(
            record, symbol="XAUUSD.ecn", magic=26092301, direction="BUY",
            entry=100.0, position_time_msc=123000,
        ))
        self.assertFalse(trailing_record_matches(
            record, symbol="XAUUSD.ecn", magic=26092301, direction="BUY",
            entry=100.0, position_time_msc=124000,
        ))

    def test_state_round_trip_and_atomic_replace(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "runtime" / "trailing.json"
            expected = {
                "123": {
                    "symbol": "XAUUSD.ecn", "magic": 26092301, "direction": "BUY",
                    "entry": 100.0, "position_time_msc": 123000,
                    "favorable_extreme": 101.0, "last_completed_bar_time": 124,
                }
            }
            save_trailing_state(path, expected)
            self.assertEqual(load_trailing_state(path), expected)
            self.assertEqual(json.loads(path.read_text())["schema_version"], 1)

    def test_corrupt_state_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "trailing.json"
            path.write_text("{broken", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                load_trailing_state(path)


if __name__ == "__main__":
    unittest.main()
