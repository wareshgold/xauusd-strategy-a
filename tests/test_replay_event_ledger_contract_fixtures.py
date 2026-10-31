"""Synthetic event-ledger contract fixtures; no broker or strategy execution."""
from __future__ import annotations

import unittest


EVENT_TYPES = {
    "SIGNAL_CANDIDATE", "ORDER_SUBMITTED", "ORDER_REJECTED",
    "ORDER_CANCELLED", "ORDER_EXPIRED", "ENTRY_FILL",
    "SL_UPDATE_SUBMITTED", "SL_UPDATE_CONFIRMED", "SL_UPDATE_REJECTED",
    "EXIT_FILL", "DATA_END", "OPEN_AT_END", "UNKNOWN", "AMBIGUOUS",
}

PROFILES = {
    "strategy_b_live_market_deal": {
        "strategy_id": "strategy_b",
        "entry_path": "market_deal_after_forming_candle_trigger",
        "order_mode": "market_deal",
        "source_ref": "synthetic:strategy-b-source-audit",
    },
    "strategy_a_rr2_trail4_research": {
        "strategy_id": "strategy_a_rr2_trail4",
        "entry_path": "pending_limit_research",
        "order_mode": "pending_limit",
        "source_ref": "synthetic:rr2-trail4-config-audit",
    },
}

FIXTURES = [
    {
        "id": "LEDGER-01-candidate-is-not-fill",
        "events": [
            {"event_type": "SIGNAL_CANDIDATE", "event_time_utc": "2026-01-01T00:00:00Z",
             "source_event_ref": "synthetic:candidate-1"},
        ],
        "expected_entry_status": "UNKNOWN",
    },
    {
        "id": "LEDGER-02-terminal-rejection-no-fill",
        "events": [
            {"event_type": "ORDER_REJECTED", "event_time_utc": "2026-01-01T00:00:01Z",
             "source_event_ref": "synthetic:terminal-rejection-1",
             "terminal_for_order": True, "partial_fill_possible": False},
        ],
        "expected_entry_status": "NOT_FILLED",
    },
    {
        "id": "LEDGER-03-repeated-candidates-not-fill-count",
        "events": [
            {"event_type": "SIGNAL_CANDIDATE", "source_event_ref": "synthetic:candidate-2a"},
            {"event_type": "SIGNAL_CANDIDATE", "source_event_ref": "synthetic:candidate-2b"},
        ],
        "expected_candidate_count": 2,
        "expected_fill_count": 0,
        "deduplication_key_evidenced": False,
    },
    {
        "id": "LEDGER-04-sl-update-before-exit-by-evidenced-time",
        "events": [
            {"event_type": "SL_UPDATE_CONFIRMED", "event_time_utc": "2026-01-01T00:00:02Z",
             "timezone_mapping_evidenced": True, "source_event_ref": "synthetic:sl-confirmed-1"},
            {"event_type": "EXIT_FILL", "event_time_utc": "2026-01-01T00:00:03Z",
             "timezone_mapping_evidenced": True, "source_event_ref": "synthetic:exit-fill-1"},
        ],
        "expected_order": "FIRST_BEFORE_SECOND",
    },
    {
        "id": "LEDGER-05-same-time-without-sequence",
        "events": [
            {"event_type": "SL_UPDATE_CONFIRMED", "event_time_utc": "2026-01-01T00:00:03Z",
             "timezone_mapping_evidenced": True, "source_sequence_id": None,
             "source_event_ref": "synthetic:sl-confirmed-2"},
            {"event_type": "EXIT_FILL", "event_time_utc": "2026-01-01T00:00:03Z",
             "timezone_mapping_evidenced": True, "source_sequence_id": None,
             "source_event_ref": "synthetic:exit-fill-2"},
        ],
        "expected_order": "AMBIGUOUS",
    },
    {
        "id": "LEDGER-06-open-at-data-end",
        "events": [
            {"event_type": "ENTRY_FILL", "event_time_utc": "2026-01-01T00:00:01Z",
             "source_event_ref": "synthetic:entry-fill-1"},
            {"event_type": "DATA_END", "event_time_utc": "2026-01-01T00:05:00Z",
             "source_event_ref": "synthetic:data-end-1"},
        ],
        "expected_lifecycle": "OPEN_AT_END",
    },
    {
        "id": "LEDGER-07-strategy-profiles-remain-distinct",
        "strategy_b_profile": "strategy_b_live_market_deal",
        "rr2_profile": "strategy_a_rr2_trail4_research",
        "expected_distinct": True,
    },
    {
        "id": "LEDGER-08-touch-does-not-create-exit",
        "events": [
            {"event_type": "ENTRY_FILL", "event_time_utc": "2026-01-01T00:00:01Z",
             "source_event_ref": "synthetic:entry-fill-2"},
            {"event_type": "DATA_END", "event_time_utc": "2026-01-01T00:05:00Z",
             "source_event_ref": "synthetic:data-end-2"},
        ],
        "observed_ohlc_sl_touch": True,
        "observed_ohlc_tp_touch": False,
        "exit_fill_events": 0,
        "expected_lifecycle": "OPEN_AT_END",
    },
]


def entry_status(events):
    """Classify only explicit lifecycle evidence; absence is not negative proof."""
    fills = [e for e in events if e.get("event_type") == "ENTRY_FILL"
             and e.get("source_event_ref")]
    if fills:
        return "FILLED"
    terminal_rejections = [
        e for e in events
        if e.get("event_type") == "ORDER_REJECTED"
        and e.get("source_event_ref")
        and e.get("terminal_for_order") is True
        and e.get("partial_fill_possible") is False
    ]
    if terminal_rejections:
        return "NOT_FILLED"
    return "UNKNOWN"


def compare_event_order(first, second):
    """Order events only when source time basis is evidenced, or sequence IDs exist."""
    seq_a, seq_b = first.get("source_sequence_id"), second.get("source_sequence_id")
    if seq_a is not None and seq_b is not None:
        if seq_a < seq_b:
            return "FIRST_BEFORE_SECOND"
        if seq_a > seq_b:
            return "SECOND_BEFORE_FIRST"
        return "AMBIGUOUS"
    ta, tb = first.get("event_time_utc"), second.get("event_time_utc")
    if not (ta and tb and first.get("timezone_mapping_evidenced") is True
            and second.get("timezone_mapping_evidenced") is True):
        return "UNKNOWN"
    if ta < tb:
        return "FIRST_BEFORE_SECOND"
    if ta > tb:
        return "SECOND_BEFORE_FIRST"
    return "AMBIGUOUS"


def lifecycle_at_data_end(events):
    if not any(e.get("event_type") == "ENTRY_FILL" and e.get("source_event_ref")
               for e in events):
        return "UNKNOWN"
    if any(e.get("event_type") == "EXIT_FILL" and e.get("source_event_ref")
           for e in events):
        return "CLOSED"
    if any(e.get("event_type") == "DATA_END" and e.get("source_event_ref")
           for e in events):
        return "OPEN_AT_END"
    return "UNKNOWN"


class ReplayEventLedgerContractTests(unittest.TestCase):
    def test_fixture_ids_unique_and_types_valid(self):
        ids = [f["id"] for f in FIXTURES]
        self.assertEqual(len(ids), len(set(ids)))
        for fixture in FIXTURES:
            for event in fixture.get("events", []):
                self.assertIn(event["event_type"], EVENT_TYPES)
                self.assertTrue(event.get("source_event_ref"))
        self.assertEqual(len(PROFILES), 2)

    def test_candidate_is_not_fill_and_absence_is_unknown(self):
        fixture = FIXTURES[0]
        self.assertEqual(entry_status(fixture["events"]), fixture["expected_entry_status"])
        self.assertEqual(lifecycle_at_data_end(fixture["events"]), "UNKNOWN")

    def test_terminal_rejection_only_supports_not_filled_with_explicit_bounds(self):
        fixture = FIXTURES[1]
        self.assertEqual(entry_status(fixture["events"]), fixture["expected_entry_status"])
        weakened = [dict(fixture["events"][0], partial_fill_possible=True)]
        self.assertEqual(entry_status(weakened), "UNKNOWN")

    def test_repeated_candidates_do_not_imply_duplicate_fills_or_deduplication(self):
        fixture = FIXTURES[2]
        events = fixture["events"]
        self.assertEqual(sum(e["event_type"] == "SIGNAL_CANDIDATE" for e in events),
                         fixture["expected_candidate_count"])
        self.assertEqual(sum(e["event_type"] == "ENTRY_FILL" for e in events),
                         fixture["expected_fill_count"])
        self.assertFalse(fixture["deduplication_key_evidenced"])
        self.assertEqual(entry_status(events), "UNKNOWN")

    def test_sl_update_and_exit_order_requires_evidenced_time(self):
        fixture = FIXTURES[3]
        self.assertEqual(compare_event_order(*fixture["events"]), fixture["expected_order"])
        no_timezone_evidence = [
            dict(fixture["events"][0], timezone_mapping_evidenced=False),
            fixture["events"][1],
        ]
        self.assertEqual(compare_event_order(*no_timezone_evidence), "UNKNOWN")

    def test_equal_time_without_sequence_is_ambiguous(self):
        fixture = FIXTURES[4]
        self.assertEqual(compare_event_order(*fixture["events"]), fixture["expected_order"])

    def test_data_end_is_not_an_exit_and_evidenced_entry_stays_open(self):
        fixture = FIXTURES[5]
        self.assertEqual(lifecycle_at_data_end(fixture["events"]), fixture["expected_lifecycle"])
        self.assertFalse(any(e["event_type"] == "EXIT_FILL" for e in fixture["events"]))

    def test_strategy_b_and_rr2_profiles_do_not_share_order_mode(self):
        fixture = FIXTURES[6]
        strategy_b = PROFILES[fixture["strategy_b_profile"]]
        rr2 = PROFILES[fixture["rr2_profile"]]
        self.assertNotEqual(strategy_b["order_mode"], rr2["order_mode"])
        self.assertNotEqual(strategy_b["entry_path"], rr2["entry_path"])
        self.assertNotEqual(strategy_b["strategy_id"], rr2["strategy_id"])
        self.assertEqual(fixture["expected_distinct"], True)

    def test_ohlc_touch_does_not_create_exit_fill(self):
        fixture = FIXTURES[7]
        events = fixture["events"]
        self.assertTrue(fixture["observed_ohlc_sl_touch"])
        self.assertEqual(fixture["exit_fill_events"], 0)
        self.assertFalse(any(e["event_type"] == "EXIT_FILL" for e in events))
        self.assertEqual(lifecycle_at_data_end(events), fixture["expected_lifecycle"])


if __name__ == "__main__":
    unittest.main()
