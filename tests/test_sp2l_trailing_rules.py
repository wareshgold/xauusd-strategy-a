import unittest

from sp2l_trailing_rules import (
    normalize_trailing_sl,
    should_retry_trailing,
    trailing_sl_is_placeable,
)


class TrailingRulesTests(unittest.TestCase):
    def test_buy_sl_rounds_down_to_tick(self):
        self.assertEqual(normalize_trailing_sl("BUY", 3962.907, 0.01, 2), 3962.90)

    def test_sell_sl_rounds_up_to_tick(self):
        self.assertEqual(normalize_trailing_sl("SELL", 3954.773, 0.01, 2), 3954.78)

    def test_invalid_tick_size_rejected(self):
        with self.assertRaises(ValueError):
            normalize_trailing_sl("BUY", 10.0, 0.0, 2)

    def test_buy_requires_sl_below_bid_and_min_distance(self):
        self.assertTrue(trailing_sl_is_placeable("BUY", 100.0, 100.2, 100.21, 0.1))
        self.assertFalse(trailing_sl_is_placeable("BUY", 100.1, 100.2, 100.21, 0.1))
        self.assertFalse(trailing_sl_is_placeable("BUY", 100.2, 100.2, 100.21, 0.0))

    def test_sell_requires_sl_above_ask_and_min_distance(self):
        self.assertTrue(trailing_sl_is_placeable("SELL", 100.3, 100.0, 100.1, 0.1))
        self.assertFalse(trailing_sl_is_placeable("SELL", 100.2, 100.0, 100.1, 0.1))
        self.assertFalse(trailing_sl_is_placeable("SELL", 100.1, 100.0, 100.1, 0.0))

    def test_retry_invalid_stops_is_bounded(self):
        self.assertTrue(should_retry_trailing(10016, 1, 3))
        self.assertTrue(should_retry_trailing(10016, 2, 3))
        self.assertFalse(should_retry_trailing(10016, 3, 3))

    def test_non_transient_retcodes_are_not_retried(self):
        self.assertFalse(should_retry_trailing(10009, 1, 3))
        self.assertFalse(should_retry_trailing(None, 1, 3))


if __name__ == "__main__":
    unittest.main()
