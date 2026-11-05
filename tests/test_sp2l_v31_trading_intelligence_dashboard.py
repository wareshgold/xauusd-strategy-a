from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sp2l_v31_trading_intelligence_dashboard as dashboard


class TradingIntelligenceDashboardTests(unittest.TestCase):
    def test_deals_are_deduplicated_and_entry_codes_are_labeled(self):
        events = [
            {
                "event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 101, "position": 9001,
                "entry": 0, "net": -0.20, "signal_id": "XAUUSD.ecn:123:BUY",
                "ts_utc": "2026-11-04T08:00:00Z",
            },
            {
                "event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 101, "position": 9001,
                "entry": 0, "net": -0.20, "signal_id": "XAUUSD.ecn:123:BUY",
                "ts_utc": "2026-11-04T08:00:00Z",
            },
            {
                "event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 102, "position": 9001,
                "entry": 1, "net": 2.50, "signal_id": "XAUUSD.ecn:123:BUY",
                "ts_utc": "2026-11-04T08:10:00Z",
            },
        ]
        rows = dashboard._deal_rows(events)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["entry_label"], "IN")
        self.assertEqual(rows[1]["entry_label"], "OUT")
        self.assertEqual(rows[0]["side"], "BUY")

    def test_position_journal_groups_deals_without_claiming_full_close(self):
        deals = [
            {"position_id": "9001", "entry_code": 0, "side": "BUY",
             "signal_id": "sig", "time_local": "t1", "time_utc": "2026-11-04T08:00:00Z", "net": -0.2},
            {"position_id": "9001", "entry_code": 1, "side": "BUY",
             "signal_id": "sig", "time_local": "t2", "time_utc": "2026-11-04T08:10:00Z", "net": 2.5},
        ]
        rows = dashboard._position_journal(deals)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "EXIT_OBSERVED")
        self.assertEqual(rows[0]["observed_net"], 2.3)
        self.assertEqual(rows[0]["deal_count"], 2)

    def test_position_without_exit_remains_entry_only(self):
        rows = dashboard._position_journal([
            {"position_id": "9002", "entry_code": 0, "side": "SELL",
             "time_local": "t1", "time_utc": "2026-11-04T08:00:00Z", "net": -0.1}
        ])
        self.assertEqual(rows[0]["status"], "ENTRY_ONLY")

    def test_performance_is_labeled_as_deal_net_not_equity(self):
        result = dashboard._performance([
            {"time_local": "t1", "time_utc": "2026-11-04T08:00:00Z", "net": -0.2},
            {"time_local": "t2", "time_utc": "2026-11-04T08:10:00Z", "net": 2.5},
        ])
        self.assertEqual(result["net_sum"], 2.3)
        self.assertEqual(result["positive_deals"], 1)
        self.assertEqual(result["negative_deals"], 1)
        self.assertIn("not account equity", result["metric_label"])

    def test_api_explicitly_disclaims_mt5_and_broker_verification(self):
        snapshot = {
            "runner": {"alive": True, "pids": [1]},
            "state_age_seconds": 1.0,
            "event_meta": {"bytes": 10},
            "health": {"total_lines": 1, "malformed_lines": 0, "path": "events.jsonl"},
            "diagnostics": [],
            "latest": None,
            "metrics": {},
            "events": [],
            "state": {},
        }
        with patch.object(dashboard.ops, "_snapshot", return_value=snapshot):
            response = dashboard.APP.test_client().get("/api/dashboard")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertFalse(body["mt5_queried"])
        self.assertFalse(body["broker_state_verified"])
        self.assertEqual(body["journal"], [])
        self.assertEqual(body["performance"]["net_sum"], 0.0)

    def test_performance_diagnostics_is_embedded_in_existing_dashboard(self):
        snapshot = {
            "runner": {"alive": True, "pids": [1]},
            "state_age_seconds": 1.0,
            "event_meta": {"bytes": 10},
            "health": {"total_lines": 1, "malformed_lines": 0, "path": "events.jsonl"},
            "diagnostics": [],
            "latest": None,
            "metrics": {},
            "events": [
                {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 501, "position": 9501,
                 "entry": 1, "signal_id": "XAUUSD.ecn:123:BUY", "net": 1.25,
                 "ts_utc": "2026-11-04T21:00:00Z"}
            ],
            "state": {},
        }
        with patch.object(dashboard.ops, "_snapshot", return_value=snapshot):
            response = dashboard.APP.test_client().get(
                "/api/performance-diagnostics?start=2026-11-05&end=2026-11-05"
            )
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertFalse(body["mt5_queried"])
        self.assertFalse(body["broker_state_verified"])
        self.assertEqual(body["daily"][0]["date_local"], "2026-11-05")
        page = dashboard.APP.test_client().get("/")
        self.assertIn(b"Performance Diagnostics", page.data)
        self.assertIn(b"page-diagnostics", page.data)

    def test_dashboard_page_renders(self):
        response = dashboard.APP.test_client().get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Deal Journal", response.data)
        self.assertIn(b"not account equity", response.data)


if __name__ == "__main__":
    unittest.main()
