import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from sp2l_trail_broker_telemetry import execute_and_verify_trailing_request


def context(attempt_id="attempt-1", attempt_number=1):
    return {
        "trail_cycle_id": "XAUUSD:26092301:12345:1793626380",
        "trail_attempt_id": attempt_id,
        "position_ticket": 12345,
        "position_identifier": 98765,
        "symbol": "XAUUSD.ecn",
        "magic": 26092301,
        "direction": "BUY",
        "completed_bar_time": 1793626380,
        "entry": 3902.0,
        "position_time_msc": 1793626300123,
        "attempt_number": attempt_number,
        "old_sl": 3900.0,
        "requested_sl": 3902.5,
        "tp": 3910.0,
        "bid": 3903.0,
        "ask": 3903.1,
        "point": 0.01,
        "tick_size": 0.01,
        "digits": 2,
        "stops_level": 0,
        "freeze_level": 0,
        "min_distance": 0.0,
    }


class FakeMT5:
    TRADE_RETCODE_DONE = 10009

    def __init__(self, response, positions):
        self.response = response
        self.positions = positions
        self.sent = []
        self.queries = []
        self.query_error = None

    def order_send(self, request):
        self.sent.append(dict(request))
        return self.response

    def positions_get(self, *, ticket):
        self.queries.append(ticket)
        if isinstance(self.positions, Exception):
            raise self.positions
        return self.positions

    def last_error(self):
        return (1, "fake MT5 error")


def response(retcode=10009, comment="done"):
    return SimpleNamespace(retcode=retcode, comment=comment)


def position(ticket=12345, sl=3902.5, tp=3910.0):
    return SimpleNamespace(ticket=ticket, identifier=98765, sl=sl, tp=tp)


class TrailBrokerTelemetryTests(unittest.TestCase):
    def run_case(self, api, ctx=None, logger=None):
        events = []
        callback = logger or events.append
        result, evidence = execute_and_verify_trailing_request(
            api,
            callback,
            {"action": 6, "symbol": "XAUUSD.ecn", "position": 12345,
             "sl": 3902.5, "tp": 3910.0},
            ctx or context(),
        )
        return result, evidence, events

    def test_done_and_matching_readback_confirms(self):
        api = FakeMT5(response(), [position()])
        result, evidence, events = self.run_case(api)
        self.assertEqual(evidence["verification_status"], "CONFIRMED_MATCH")
        self.assertTrue(evidence["api_success"])
        self.assertEqual(api.sent.__len__(), 1)
        self.assertEqual(api.queries, [12345])
        self.assertEqual(
            [event["event"] for event in events],
            ["TRAIL_REQUEST", "TRAIL_RESPONSE",
             "TRAIL_BROKER_OBSERVATION", "TRAIL_VERIFICATION"],
        )

    def test_done_with_different_readback_is_mismatch(self):
        api = FakeMT5(response(), [position(sl=3902.0)])
        _, evidence, _ = self.run_case(api)
        self.assertEqual(evidence["verification_status"], "OBSERVED_MISMATCH")

    def test_non_done_response_does_not_change_readback_classification(self):
        api = FakeMT5(response(10016, "Invalid stops"), [position(sl=3900.0)])
        _, evidence, events = self.run_case(api)
        self.assertFalse(evidence["api_success"])
        self.assertEqual(evidence["verification_status"], "OBSERVED_MISMATCH")
        self.assertEqual(events[1]["retcode"], 10016)

    def test_none_response_records_last_error_and_still_reads_position(self):
        api = FakeMT5(None, [position(sl=3900.0)])
        _, evidence, events = self.run_case(api)
        self.assertFalse(evidence["api_success"])
        self.assertIn("last_error", events[1])
        self.assertEqual(evidence["verification_status"], "OBSERVED_MISMATCH")
        self.assertEqual(api.queries, [12345])

    def test_none_readback_is_observation_failed(self):
        api = FakeMT5(response(), None)
        _, evidence, events = self.run_case(api)
        self.assertEqual(evidence["query_outcome"], "QUERY_FAILED")
        self.assertEqual(evidence["verification_status"], "OBSERVATION_FAILED")
        self.assertIn("last_error", events[2])

    def test_readback_exception_is_observation_failed(self):
        api = FakeMT5(response(), RuntimeError("readback unavailable"))
        _, evidence, events = self.run_case(api)
        self.assertEqual(evidence["verification_status"], "OBSERVATION_FAILED")
        self.assertIn("readback unavailable", events[2]["last_error"])

    def test_empty_readback_is_position_not_found(self):
        api = FakeMT5(response(), [])
        _, evidence, _ = self.run_case(api)
        self.assertEqual(evidence["verification_status"], "POSITION_NOT_FOUND")

    def test_wrong_ticket_is_position_not_found(self):
        api = FakeMT5(response(), [position(ticket=777)])
        _, evidence, _ = self.run_case(api)
        self.assertEqual(evidence["verification_status"], "POSITION_NOT_FOUND")

    def test_tick_precision_tolerance(self):
        api = FakeMT5(response(), [position(sl=3902.504)])
        _, evidence, _ = self.run_case(api)
        self.assertEqual(evidence["verification_status"], "CONFIRMED_MATCH")

    def test_each_retry_has_distinct_attempt_id_same_cycle(self):
        api = FakeMT5(response(), [position()])
        ctx1, ctx2 = context("attempt-1", 1), context("attempt-2", 2)
        _, first, _ = self.run_case(api, ctx1)
        _, second, _ = self.run_case(api, ctx2)
        self.assertEqual(first["trail_cycle_id"], second["trail_cycle_id"])
        self.assertNotEqual(first["trail_attempt_id"], second["trail_attempt_id"])

    def test_telemetry_logger_failure_does_not_prevent_send_or_readback(self):
        api = FakeMT5(response(), [position()])
        def broken_logger(_event):
            raise OSError("disk full")
        _, evidence, events = self.run_case(api, logger=broken_logger)
        self.assertEqual(evidence["verification_status"], "CONFIRMED_MATCH")
        self.assertEqual(len(api.sent), 1)
        self.assertEqual(api.queries, [12345])
        self.assertEqual(events, [])
        self.assertEqual(evidence["telemetry_write_failures"], 4)

    def test_helper_never_retries_order_send(self):
        api = FakeMT5(response(10016, "Invalid stops"), [position(sl=3900.0)])
        self.run_case(api)
        self.assertEqual(len(api.sent), 1)


if __name__ == "__main__":
    unittest.main()
