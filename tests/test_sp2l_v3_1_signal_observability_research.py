import unittest
from types import SimpleNamespace

from scripts.sp2l_v3_1_signal_observability_research import (
    install_signal_observability,
)


class SignalObservabilityResearchTests(unittest.TestCase):
    def make_runner(self, rates=None, finder=None):
        return SimpleNamespace(
            rates=rates or (lambda symbol, count=10: [1, 2, 3]),
            find_latest_candidate=finder or (lambda data, symbol: None),
        )

    def test_rates_ok_preserves_return_value_and_emits_row_count(self):
        events = []
        runner = self.make_runner()
        restore = install_signal_observability(runner, events.append)
        try:
            result = runner.rates("XAUUSD.ecn", 30)
            self.assertEqual(result, [1, 2, 3])
            self.assertEqual(events[-1]["event"], "RATES_OK")
            self.assertEqual(events[-1]["row_count"], 3)
        finally:
            restore()

    def test_rates_none_is_explicitly_unresolved(self):
        events = []
        runner = self.make_runner(rates=lambda symbol, count=10: None)
        restore = install_signal_observability(runner, events.append)
        try:
            self.assertIsNone(runner.rates("XAUUSD.ecn"))
            event = events[-1]
            self.assertEqual(event["event"], "RATES_UNAVAILABLE")
            self.assertIn("UPSTREAM_CAUSE_UNRESOLVED", event["interpretation"])
        finally:
            restore()

    def test_rates_exception_is_logged_and_reraised(self):
        events = []
        def fail(symbol, count=10):
            raise RuntimeError("synthetic rates failure")
        runner = self.make_runner(rates=fail)
        restore = install_signal_observability(runner, events.append)
        try:
            with self.assertRaisesRegex(RuntimeError, "synthetic rates failure"):
                runner.rates("XAUUSD.ecn")
            self.assertEqual(events[-1]["event"], "RATES_ERROR")
        finally:
            restore()

    def test_candidate_none_is_not_claimed_as_no_pattern(self):
        events = []
        runner = self.make_runner()
        restore = install_signal_observability(runner, events.append)
        try:
            self.assertIsNone(
                runner.find_latest_candidate([1, 2], "XAUUSD.ecn")
            )
            event = events[-1]
            self.assertEqual(event["event"], "CANDIDATE_NONE")
            self.assertIn("does not distinguish", event["interpretation"])
        finally:
            restore()

    def test_candidate_found_records_trigger_time(self):
        events = []
        candidate = {"trigger_time": 12345, "direction": "SELL"}
        runner = self.make_runner(
            finder=lambda data, symbol: candidate
        )
        restore = install_signal_observability(runner, events.append)
        try:
            self.assertIs(
                runner.find_latest_candidate([1, 2], "XAUUSD.ecn"),
                candidate,
            )
            self.assertEqual(events[-1]["event"], "CANDIDATE_FOUND")
            self.assertEqual(events[-1]["trigger_time"], 12345)
        finally:
            restore()

    def test_candidate_exception_is_logged_and_reraised(self):
        events = []
        def fail(data, symbol):
            raise ValueError("synthetic finder failure")
        runner = self.make_runner(finder=fail)
        restore = install_signal_observability(runner, events.append)
        try:
            with self.assertRaisesRegex(ValueError, "synthetic finder failure"):
                runner.find_latest_candidate([1], "XAUUSD.ecn")
            self.assertEqual(events[-1]["event"], "CANDIDATE_ERROR")
        finally:
            restore()

    def test_restore_is_idempotent(self):
        events = []
        runner = self.make_runner()
        original_rates = runner.rates
        restore = install_signal_observability(runner, events.append)
        wrapped_rates = runner.rates
        self.assertIsNot(wrapped_rates, original_rates)
        restore()
        restore()
        self.assertIs(runner.rates, original_rates)
        self.assertEqual(runner.rates("XAUUSD.ecn"), [1, 2, 3])

    def test_observation_does_not_change_candidate_return(self):
        events = []
        marker = {"trigger_time": 99}
        runner = self.make_runner(finder=lambda data, symbol: marker)
        restore = install_signal_observability(runner, events.append)
        try:
            self.assertIs(
                runner.find_latest_candidate([1], "XAUUSD.ecn"), marker
            )
        finally:
            restore()


if __name__ == "__main__":
    unittest.main()
