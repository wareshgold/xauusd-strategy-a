import unittest
from types import SimpleNamespace

from scripts.sp2l_v3_1_signal_observability_research import (
    install_signal_observability,
)


class SignalObservabilityResearchTests(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.runner = SimpleNamespace(
            rates=lambda symbol, count=10: [1, 2, 3],
            find_latest_candidate=lambda data, symbol: None,
        )
        self.restore = install_signal_observability(
            self.runner, self.events.append
        )

    def tearDown(self):
        self.restore()

    def test_rates_ok_preserves_return_value_and_emits_row_count(self):
        result = self.runner.rates("XAUUSD.ecn", 30)
        self.assertEqual(result, [1, 2, 3])
        self.assertEqual(self.events[-1]["event"], "RATES_OK")
        self.assertEqual(self.events[-1]["row_count"], 3)

    def test_rates_none_is_explicitly_unresolved(self):
        self.runner.rates = lambda symbol, count=10: None
        # Reinstall around the replacement to model the original callable.
        self.restore()
        self.restore = install_signal_observability(
            self.runner, self.events.append
        )
        self.assertIsNone(self.runner.rates("XAUUSD.ecn"))
        event = self.events[-1]
        self.assertEqual(event["event"], "RATES_UNAVAILABLE")
        self.assertIn("UPSTREAM_CAUSE_UNRESOLVED", event["interpretation"])

    def test_rates_exception_is_logged_and_reraised(self):
        def fail(symbol, count=10):
            raise RuntimeError("synthetic rates failure")
        self.runner.rates = fail
        self.restore()
        self.restore = install_signal_observability(
            self.runner, self.events.append
        )
        with self.assertRaisesRegex(RuntimeError, "synthetic rates failure"):
            self.runner.rates("XAUUSD.ecn")
        self.assertEqual(self.events[-1]["event"], "RATES_ERROR")

    def test_candidate_none_is_not_claimed_as_no_pattern(self):
        self.assertIsNone(
            self.runner.find_latest_candidate([1, 2], "XAUUSD.ecn")
        )
        event = self.events[-1]
        self.assertEqual(event["event"], "CANDIDATE_NONE")
        self.assertIn("does not distinguish", event["interpretation"])

    def test_candidate_found_records_trigger_time(self):
        candidate = {"trigger_time": 12345, "direction": "SELL"}
        self.runner.find_latest_candidate = lambda data, symbol: candidate
        self.restore()
        self.restore = install_signal_observability(
            self.runner, self.events.append
        )
        self.assertIs(
            self.runner.find_latest_candidate([1, 2], "XAUUSD.ecn"),
            candidate,
        )
        self.assertEqual(self.events[-1]["event"], "CANDIDATE_FOUND")
        self.assertEqual(self.events[-1]["trigger_time"], 12345)

    def test_candidate_exception_is_logged_and_reraised(self):
        def fail(data, symbol):
            raise ValueError("synthetic finder failure")
        self.runner.find_latest_candidate = fail
        self.restore()
        self.restore = install_signal_observability(
            self.runner, self.events.append
        )
        with self.assertRaisesRegex(ValueError, "synthetic finder failure"):
            self.runner.find_latest_candidate([1], "XAUUSD.ecn")
        self.assertEqual(self.events[-1]["event"], "CANDIDATE_ERROR")

    def test_restore_is_idempotent(self):
        wrapped_rates = self.runner.rates
        self.restore()
        self.restore()
        self.assertIsNot(self.runner.rates, wrapped_rates)
        self.assertEqual(self.runner.rates("XAUUSD.ecn"), [1, 2, 3])

    def test_observation_does_not_change_candidate_return(self):
        marker = {"trigger_time": 99}
        self.runner.find_latest_candidate = lambda data, symbol: marker
        self.restore()
        self.restore = install_signal_observability(
            self.runner, self.events.append
        )
        self.assertIs(
            self.runner.find_latest_candidate([1], "XAUUSD.ecn"), marker
        )


if __name__ == "__main__":
    unittest.main()
