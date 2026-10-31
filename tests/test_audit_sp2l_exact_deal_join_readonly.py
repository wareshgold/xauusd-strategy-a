"""Synthetic deterministic tests for exact broker-deal join auditing."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_sp2l_exact_deal_join_readonly import audit_join


def write_jsonl(path: Path, rows, malformed=()):
    with path.open("wb") as stream:
        for row in rows:
            stream.write((json.dumps(row, sort_keys=True) + "\n").encode())
        for raw in malformed:
            stream.write(raw + b"\n")


def event(**overrides):
    row = {
        "event_id": "event-1",
        "deal_id": "deal-1",
        "order_id": "order-1",
        "position_id": "position-1",
        "observation_time": "2026-01-01T00:00:01Z",
    }
    row.update(overrides)
    return row


def deal(**overrides):
    row = {
        "deal_id": "deal-1",
        "order_id": "order-1",
        "position_id": "position-1",
        "execution_time_original": "2026-01-01T00:00:00Z",
        "execution_price": 2000.25,
        "executed_volume": 0.01,
    }
    row.update(overrides)
    return row


class ExactDealJoinAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.events = self.root / "events.jsonl"
        self.deals = self.root / "deals.jsonl"

    def audit(self, events, deals, malformed_events=(), malformed_deals=()):
        write_jsonl(self.events, events, malformed_events)
        write_jsonl(self.deals, deals, malformed_deals)
        return audit_join(self.events, self.deals)

    def test_exact_unique_id_and_required_fields_matches(self):
        result = self.audit([event()], [deal()])
        self.assertEqual(result["join_summary"]["confirmed_identity_and_execution_fields_complete"], 1)
        self.assertEqual(result["source_event_results"][0]["status"], "CONFIRMED_IDENTITY_FIELDS_COMPLETE")
        self.assertEqual(result["broker_deal_results"][0]["status"], "MATCHED_CONFIRMED")

    def test_event_without_deal_is_not_filled(self):
        result = self.audit([event()], [])
        self.assertEqual(result["source_event_results"][0]["status"], "UNMATCHED")
        self.assertIn("NO_DEAL_WITH_EXACT_ID", result["source_event_results"][0]["reason_codes"])

    def test_deal_without_event_is_retained(self):
        result = self.audit([], [deal()])
        self.assertEqual(result["broker_deal_results"][0]["status"], "UNMATCHED")
        self.assertIn("NO_EVENT_WITH_EXACT_ID", result["broker_deal_results"][0]["reason_codes"])

    def test_duplicate_broker_deal_id_is_ambiguous(self):
        result = self.audit([event()], [deal(), deal(execution_price=2001.0)])
        self.assertEqual(result["source_event_results"][0]["status"], "AMBIGUOUS")
        self.assertIn("deal-1", result["integrity_and_duplicates"]["duplicate_broker_deal_ids"])

    def test_two_events_claiming_same_deal_are_ambiguous(self):
        result = self.audit([event(), event(event_id="event-2")], [deal()])
        self.assertTrue(all(x["status"] == "AMBIGUOUS" for x in result["source_event_results"]))
        self.assertEqual(result["integrity_and_duplicates"]["deal_ids_claimed_by_multiple_events"], ["deal-1"])

    def test_conflicting_order_link_is_ambiguous(self):
        result = self.audit([event(order_id="order-A")], [deal(order_id="order-B")])
        self.assertEqual(result["source_event_results"][0]["status"], "AMBIGUOUS")
        self.assertTrue(any(x.startswith("CONFLICTING_LINK_FIELDS") for x in result["source_event_results"][0]["reason_codes"]))

    def test_same_timestamp_does_not_join_different_deal_ids(self):
        result = self.audit(
            [event(deal_id="deal-A", observation_time="2026-01-01T00:00:00Z")],
            [deal(deal_id="deal-B", execution_time_original="2026-01-01T00:00:00Z")],
        )
        self.assertEqual(result["source_event_results"][0]["status"], "UNMATCHED")
        self.assertEqual(result["join_summary"]["time_proximity_used_for_join"], False)

    def test_missing_execution_time_blocks_confirmation(self):
        result = self.audit([event()], [deal(execution_time_original=None)])
        self.assertEqual(result["source_event_results"][0]["status"], "IDENTITY_MATCH_INCOMPLETE")
        self.assertIn("EXECUTION_TIME", result["source_event_results"][0]["reason_codes"][0])

    def test_missing_price_blocks_confirmation(self):
        result = self.audit([event()], [deal(execution_price=None)])
        self.assertEqual(result["source_event_results"][0]["status"], "IDENTITY_MATCH_INCOMPLETE")

    def test_missing_executed_volume_does_not_use_requested_volume(self):
        result = self.audit([event(requested_volume=0.01)], [deal(executed_volume=None)])
        self.assertEqual(result["source_event_results"][0]["status"], "IDENTITY_MATCH_INCOMPLETE")
        self.assertIn("EXECUTED_VOLUME", result["source_event_results"][0]["reason_codes"][0])

    def test_runner_observation_time_is_not_used_as_deal_time(self):
        result = self.audit([event(observation_time="2026-01-01T00:01:00Z")], [deal()])
        self.assertEqual(result["source_event_results"][0]["status"], "CONFIRMED_IDENTITY_FIELDS_COMPLETE")
        self.assertEqual(result["join_summary"]["time_proximity_used_for_join"], False)

    def test_malformed_row_is_reported_not_silently_discarded(self):
        result = self.audit([event()], [deal()], malformed_events=(b"{broken",))
        self.assertEqual(result["row_counts"]["source_event_rejected_rows"], 1)
        self.assertEqual(result["rejected_rows"]["source_events"][0]["reason"], "INVALID_JSON")

    def test_input_hashes_are_deterministic(self):
        first = self.audit([event()], [deal()])
        second = self.audit([event()], [deal()])
        self.assertEqual(first["inputs"], second["inputs"])
        self.assertEqual(
            json.dumps(first, sort_keys=True),
            json.dumps(second, sort_keys=True),
        )

    def test_missing_event_id_cannot_be_confirmed(self):
        result = self.audit([event(event_id=None)], [deal()])
        self.assertNotEqual(result["source_event_results"][0]["status"], "CONFIRMED_IDENTITY_FIELDS_COMPLETE")
        self.assertIn("MISSING_EVENT_ID", result["source_event_results"][0]["reason_codes"])


    def test_conflicting_position_link_is_ambiguous(self):
        result = self.audit([event(position_id="position-A")], [deal(position_id="position-B")])
        self.assertEqual(result["source_event_results"][0]["status"], "AMBIGUOUS")
        self.assertIn("CONFLICTING_LINK_FIELDS:POSITION_ID", result["source_event_results"][0]["reason_codes"])

    def test_duplicate_event_ids_block_both_claims(self):
        result = self.audit([event(event_id="duplicate"), event(event_id="duplicate", deal_id="deal-2")],
                            [deal(), deal(deal_id="deal-2", order_id="order-2", position_id="position-2")])
        self.assertTrue(all(row["status"] == "AMBIGUOUS" for row in result["source_event_results"]))
        self.assertEqual(result["integrity_and_duplicates"]["duplicate_event_ids"], ["duplicate"])

    def test_non_object_json_row_is_reported(self):
        result = self.audit([event()], [deal()], malformed_events=(b'["not", "an", "object"]',))
        self.assertEqual(result["row_counts"]["source_event_rejected_rows"], 1)
        self.assertEqual(result["rejected_rows"]["source_events"][0]["reason"], "ROW_NOT_OBJECT")

    def test_malformed_broker_deal_row_is_reported(self):
        result = self.audit([event()], [deal()], malformed_deals=(b"not-json",))
        self.assertEqual(result["row_counts"]["broker_deal_rejected_rows"], 1)
        self.assertEqual(result["rejected_rows"]["broker_deals"][0]["reason"], "INVALID_JSON")



if __name__ == "__main__":
    unittest.main()
