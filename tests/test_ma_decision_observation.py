"""Synthetic fixtures for the standalone MA decision-observation builder."""
import unittest

from scripts.research.ma_decision_observation import build_observation_record


class TestMADecisionObservation(unittest.TestCase):
    def setUp(self):
        self.base = dict(
            candidate_id="cand-001",
            process_session_id="session-001",
            poll_sequence=17,
            trigger_time_server_epoch=120,
            current_m1_bar_open_server_epoch=180,
            last_completed_m1_bar_open_server_epoch=120,
            last_completed_m1_bar_close_server_epoch=180,
            server_utc_offset_seconds=None,
            bars_snapshot=[
                {"time": 60, "open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5},
                {"time": 120, "open": 1.5, "high": 2.5, "low": 1.0, "close": 2.0},
                {"time": 180, "open": 2.0, "high": 2.2, "low": 1.8, "close": 2.1},
            ],
            decision_observed_at_utc="2026-11-14T08:00:12.345Z",
            decision_monotonic_ns=987654321,
        )

    def test_trigger_time_is_separate_from_decision_time(self):
        record = build_observation_record(**self.base)
        self.assertEqual(record["trigger_time_server_epoch"], 120)
        self.assertEqual(record["decision_observed_at_utc"], "2026-11-14T08:00:12.345Z")
        self.assertEqual(record["decision_monotonic_ns"], 987654321)

    def test_valid_explicit_bar_boundary_is_research_alignable(self):
        record = build_observation_record(**self.base)
        self.assertEqual(record["alignment_status"], "READY_FOR_RESEARCH_ALIGNMENT")

    def test_missing_server_offset_stays_null(self):
        record = build_observation_record(**self.base)
        self.assertIsNone(record["server_utc_offset_seconds"])

    def test_missing_completed_bar_boundary_fails_closed(self):
        args = dict(self.base, last_completed_m1_bar_close_server_epoch=None)
        record = build_observation_record(**args)
        self.assertEqual(record["alignment_status"], "UNRESOLVED")

    def test_inconsistent_completed_bar_boundary_fails_closed(self):
        args = dict(self.base, last_completed_m1_bar_close_server_epoch=181)
        record = build_observation_record(**args)
        self.assertEqual(record["alignment_status"], "UNRESOLVED")

    def test_out_of_order_snapshot_fails_closed(self):
        args = dict(self.base, bars_snapshot=list(reversed(self.base["bars_snapshot"])))
        record = build_observation_record(**args)
        self.assertEqual(record["alignment_status"], "UNRESOLVED")

    def test_snapshot_with_intervening_bar_after_declared_completed_bar_fails_closed(self):
        args = dict(
            self.base,
            current_m1_bar_open_server_epoch=240,
            last_completed_m1_bar_open_server_epoch=120,
            last_completed_m1_bar_close_server_epoch=180,
            bars_snapshot=[
                {"time": 60, "open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5},
                {"time": 120, "open": 1.5, "high": 2.5, "low": 1.0, "close": 2.0},
                {"time": 180, "open": 2.0, "high": 2.2, "low": 1.8, "close": 2.1},
                {"time": 240, "open": 2.1, "high": 2.3, "low": 1.9, "close": 2.2},
            ],
        )
        record = build_observation_record(**args)
        self.assertEqual(record["alignment_status"], "UNRESOLVED")

    def test_snapshot_hash_changes_when_bar_changes(self):
        first = build_observation_record(**self.base)
        changed_bars = [dict(row) for row in self.base["bars_snapshot"]]
        changed_bars[1]["close"] = 2.01
        second = build_observation_record(**dict(self.base, bars_snapshot=changed_bars))
        self.assertNotEqual(first["bar_snapshot_sha256"], second["bar_snapshot_sha256"])

    def test_correlation_fields_are_preserved(self):
        record = build_observation_record(**self.base)
        self.assertEqual(record["candidate_id"], "cand-001")
        self.assertEqual(record["process_session_id"], "session-001")
        self.assertEqual(record["poll_sequence"], 17)

    def test_invalid_utc_label_rejected(self):
        with self.assertRaises(ValueError):
            build_observation_record(**dict(self.base, decision_observed_at_utc="2026-11-14T08:00:12+02:00"))

    def test_malformed_timestamp_with_z_suffix_rejected(self):
        with self.assertRaises(ValueError):
            build_observation_record(**dict(self.base, decision_observed_at_utc="not-a-timestampZ"))

    def test_empty_timestamp_rejected_instead_of_replaced_with_now(self):
        with self.assertRaises(ValueError):
            build_observation_record(**dict(self.base, decision_observed_at_utc=""))

    def test_invalid_poll_sequence_rejected(self):
        with self.assertRaises(ValueError):
            build_observation_record(**dict(self.base, poll_sequence=-1))


if __name__ == "__main__":
    unittest.main()
