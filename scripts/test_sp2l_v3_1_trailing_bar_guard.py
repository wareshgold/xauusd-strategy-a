"""Regression tests for V3.1's post-entry trailing-bar guard."""
import unittest

from sp2l_v3_1_rr4_act40_config import completed_bar_is_after_position


class CompletedBarEntryGuardTests(unittest.TestCase):
    def test_bar_ending_before_entry_is_rejected(self):
        # 07:41 candle; position opened at 07:41:27 server time.
        self.assertFalse(completed_bar_is_after_position(1793605260, 1793605287, 1793605287000))

    def test_same_entry_minute_is_rejected(self):
        # Even if entry occurs at the first second of the minute, wait for
        # the next fully completed M1 candle (conservative boundary policy).
        self.assertFalse(completed_bar_is_after_position(1793605260, 1793605260, 1793605260000))

    def test_first_full_bar_after_entry_is_accepted(self):
        self.assertTrue(completed_bar_is_after_position(1793605320, 1793605287, 1793605287000))

    def test_seconds_fallback_when_milliseconds_are_missing(self):
        self.assertFalse(completed_bar_is_after_position(1793605260, 1793605287, 0))
        self.assertTrue(completed_bar_is_after_position(1793605320, 1793605287, 0))

    def test_invalid_or_missing_timestamps_fail_closed(self):
        self.assertFalse(completed_bar_is_after_position(0, 1793605287, 1793605287000))
        self.assertFalse(completed_bar_is_after_position(1793605320, 0, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
