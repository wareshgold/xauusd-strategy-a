from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sp2l_v31_local_monitoring_dashboard_v3 as dashboard


class DashboardOperationalInspectorTests(unittest.TestCase):
    def setUp(self):
        self.client = dashboard.APP.test_client()

    def test_order_lifecycle_is_runner_evidence_not_broker_inventory(self):
        events = [
            {"event": "ORDER_ATTEMPT", "order": 71001, "ts_utc": "2026-11-04T08:00:00Z"},
            {"event": "ORDER_RESULT", "result": {"order": 71001, "ok": True},
             "ts_utc": "2026-11-04T08:00:01Z"},
            {"event": "PENDING_ORDER_LIFECYCLE", "order": 71001, "state": "FILLED",
             "ts_utc": "2026-11-04T08:01:00Z"},
        ]
        rows = dashboard._order_lifecycle(events, {"orders": []})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["order_id"], "71001")
        self.assertEqual(rows[0]["lifecycle_status"], "FILLED")
        self.assertFalse(rows[0]["broker_reconciled"])

    def test_trailing_retry_and_success_are_distinguished(self):
        retry = [{
            "event": "TRAIL_UPDATE", "position": 80001,
            "completed_bar_time": "2026-11-04T08:00:00Z",
            "success": False, "retry_scheduled": True,
            "ts_utc": "2026-11-04T08:00:02Z",
        }]
        rows = dashboard._trailing_diagnostics(retry)
        self.assertEqual(rows[0]["status"], "RETRY_PENDING")

        recovered = retry + [{
            "event": "TRAIL_UPDATE", "position": 80001,
            "completed_bar_time": "2026-11-04T08:00:00Z",
            "success": True, "old_sl": 2300.0, "new_sl": 2300.4,
            "ts_utc": "2026-11-04T08:00:05Z",
        }]
        rows = dashboard._trailing_diagnostics(recovered)
        self.assertEqual(rows[0]["status"], "SUCCEEDED")
        self.assertEqual(rows[0]["attempts"], 2)

    def test_history_failure_is_not_converted_to_empty_history(self):
        event = {
            "event": "MT5_DEAL_HISTORY_QUERY_FAILED",
            "ticket": 65006182,
            "last_error": [-2, "Terminal: Invalid params"],
            "ts_utc": "2026-11-04T08:00:00Z",
        }
        rows = dashboard._history_failures([event])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["ticket"], 65006182)
        self.assertEqual(rows[0]["last_error"], [-2, "Terminal: Invalid params"])

    def test_api_orders_endpoint_explicitly_disclaims_broker_reconciliation(self):
        snapshot = {
            "events": [{"event": "ORDER_ATTEMPT", "order": 71002,
                        "ts_utc": "2026-11-04T08:00:00Z"}],
            "state": {"orders": []},
        }
        with patch.object(dashboard, "_snapshot", return_value=snapshot):
            response = self.client.get("/api/orders")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertFalse(body["broker_reconciled"])
        self.assertEqual(body["orders"][0]["order_id"], "71002")

    def test_events_api_filters_and_paginates(self):
        snapshot = {
            "events": [
                {"event": "ORDER_ATTEMPT", "order": 1, "ts_utc": "2026-11-04T08:00:00Z"},
                {"event": "TRAIL_UPDATE", "position": 2, "ts_utc": "2026-11-04T08:01:00Z"},
            ],
            "state": {},
        }
        with patch.object(dashboard, "_snapshot", return_value=snapshot):
            response = self.client.get("/api/events?event=TRAIL_UPDATE&limit=1&offset=0")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["total"], 1)
        self.assertEqual(body["events"][0]["event"], "TRAIL_UPDATE")

    def test_fingerprint_reports_file_stability(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "evidence.jsonl"
            path.write_text('{"event":"TEST"}\\n', encoding="utf-8")
            result = dashboard._file_fingerprint(path)
        self.assertTrue(result["exists"])
        self.assertTrue(result["stable_during_hash"])
        self.assertEqual(len(result["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
