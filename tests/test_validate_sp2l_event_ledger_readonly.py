"""Deterministic synthetic tests for event-ledger envelope validation."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_sp2l_event_ledger_readonly import audit, validate_rows


def valid_event(**overrides):
    row = {
        "schema_version": "1.0-proposal",
        "run_id": "run-synthetic-01",
        "event_id": "event-01",
        "candidate_id": None,
        "trade_id": None,
        "strategy_id": "strategy_b",
        "profile_id": "strategy_b_live_market_deal",
        "source_commit": None,
        "config_sha256": None,
        "dataset_sha256": None,
        "event_type": "SIGNAL_CANDIDATE",
        "source_event_ref": "synthetic:test-event-01",
        "source_artifact_sha256": None,
        "source_row_ref": "fixture:row-1",
        "event_time_original": "2026-01-01T00:00:00Z",
        "event_timezone_basis": "synthetic fixture explicitly UTC",
        "event_time_utc": "2026-01-01T00:00:00Z",
        "source_sequence_id": None,
        "price": None,
        "volume": None,
        "side": None,
        "order_id": None,
        "position_id": None,
        "deal_id": None,
        "evidence_class": "synthetic_fixture",
        "notes": None,
        "warnings": [],
    }
    row.update(overrides)
    return row


class EventLedgerSchemaValidationTests(unittest.TestCase):
    def test_complete_envelope_with_nullable_trade_fields_passes(self):
        result = validate_rows([valid_event()])
        self.assertTrue(result["valid"], result["issues"])
        self.assertEqual(result["rows_seen"], 1)
        self.assertEqual(result["issue_count"], 0)

    def test_missing_envelope_keys_fail(self):
        row = valid_event()
        del row["source_row_ref"]
        del row["event_timezone_basis"]
        result = validate_rows([row])
        self.assertFalse(result["valid"])
        self.assertTrue(any(i["code"] == "MISSING_KEYS" for i in result["issues"]))

    def test_invalid_hash_fails(self):
        result = validate_rows([valid_event(config_sha256="not-a-sha256")])
        self.assertTrue(any(i["code"] == "INVALID_HASH" for i in result["issues"]))

    def test_utc_timestamp_without_timezone_basis_fails(self):
        result = validate_rows([valid_event(event_timezone_basis=None)])
        self.assertTrue(any(i["code"] == "UTC_WITHOUT_BASIS" for i in result["issues"]))

    def test_naive_timestamp_is_not_accepted_as_utc(self):
        result = validate_rows([valid_event(event_time_utc="2026-01-01T00:00:00")])
        self.assertTrue(any(i["code"] == "NAIVE_UTC_TIME" for i in result["issues"]))

    def test_non_utc_offset_is_not_accepted_in_utc_field(self):
        result = validate_rows([valid_event(event_time_utc="2026-01-01T03:30:00+03:30")])
        self.assertTrue(any(i["code"] == "NON_UTC_TIME" for i in result["issues"]))

    def test_unresolved_time_is_allowed_when_utc_is_null(self):
        row = valid_event(event_time_original="2026-01-01 03:30:00", event_timezone_basis=None,
                          event_time_utc=None)
        result = validate_rows([row])
        self.assertTrue(result["valid"], result["issues"])

    def test_duplicate_event_id_within_run_fails(self):
        first = valid_event()
        second = valid_event(event_id="event-01")
        result = validate_rows([first, second])
        self.assertTrue(any(i["code"] == "DUPLICATE_EVENT_ID" for i in result["issues"]))

    def test_unknown_event_label_fails(self):
        result = validate_rows([valid_event(event_type="FILLED_BECAUSE_CANDLE_TOUCHED")])
        self.assertTrue(any(i["code"] == "INVALID_EVENT_TYPE" for i in result["issues"]))

    def test_malformed_jsonl_is_reported_and_hash_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic-ledger.jsonl"
            path.write_text(json.dumps(valid_event()) + "\n{broken json\n", encoding="utf-8")
            result = audit(path)
            self.assertFalse(result["valid"])
            self.assertTrue(any(i["code"] == "INVALID_JSONL" for i in result["issues"]))
            self.assertEqual(len(result["input_sha256"]), 64)

    def test_json_array_row_is_rejected_as_not_an_object(self):
        result = validate_rows([["not", "an", "event"]])
        self.assertTrue(any(i["code"] == "ROW_NOT_OBJECT" for i in result["issues"]))


if __name__ == "__main__":
    unittest.main()
