from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sp2l_v31_performance_diagnostics as diagnostics


class PerformanceDiagnosticsTests(unittest.TestCase):
    def test_daily_grouping_direction_and_recorded_net(self):
        events = [
            {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 1, "position": 100,
             "entry": 0, "signal_id": "XAUUSD.ecn:1:BUY", "entry_price": 100.0,
             "net": -0.10, "ts_utc": "2026-11-04T08:00:00Z"},
            {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 2, "position": 100,
             "entry": 1, "signal_id": "XAUUSD.ecn:1:BUY", "net": 2.10,
             "ts_utc": "2026-11-04T09:00:00Z"},
            {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 3, "position": 200,
             "entry": 0, "signal_id": "XAUUSD.ecn:2:SELL", "entry_price": 101.0,
             "net": -0.10, "ts_utc": "2026-11-05T08:00:00Z"},
            {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 4, "position": 200,
             "entry": 1, "signal_id": "XAUUSD.ecn:2:SELL", "net": -1.40,
             "ts_utc": "2026-11-05T09:00:00Z"},
        ]
        result = diagnostics._build_diagnostics(events, "2026-11-04", "2026-11-05")
        self.assertEqual(result["daily"][0]["position_groups_with_exit_observed"], 1)
        self.assertEqual(result["daily"][0]["net_sum_runner_recorded"], 2.0)
        self.assertEqual(result["daily"][0]["buy"]["positions"], 1)
        self.assertEqual(result["daily"][0]["buy"]["positions_with_known_net"], 1)
        self.assertEqual(result["daily"][1]["sell"]["losses"], 1)
        self.assertEqual(result["overall"]["net_sum_runner_recorded"], 0.5)

    def test_trailing_deferred_same_bar_is_correlated_with_success(self):
        events = [
            {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 10, "position": 300,
             "entry": 0, "signal_id": "XAUUSD.ecn:3:BUY", "entry_price": 100,
             "net": -0.1, "ts_utc": "2026-11-05T08:00:00Z"},
            {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 11, "position": 300,
             "entry": 1, "signal_id": "XAUUSD.ecn:3:BUY", "net": -1.0,
             "ts_utc": "2026-11-05T09:00:00Z"},
            {"event": "TRAIL_DEFERRED", "position": 300, "completed_bar_time": 123,
             "ts_utc": "2026-11-05T08:30:00Z"},
            {"event": "TRAIL_UPDATE", "position": 300, "completed_bar_time": 123,
             "success": True, "favorable_move": 0.5,
             "ts_utc": "2026-11-05T08:31:00Z"},
        ]
        result = diagnostics._build_diagnostics(events, "2026-11-05", "2026-11-05")
        trade = result["trades"][0]
        self.assertEqual(trade["trail_deferred"], 1)
        self.assertEqual(trade["trail_deferred_unrecovered_same_bar"], 0)
        self.assertTrue(trade["trail_activation_observed"])
        self.assertEqual(result["overall"]["trailing"]["losses_with_unrecovered_deferred_same_bar"], 0)

    def test_price_excursions_are_marked_as_sampled_not_tick_complete(self):
        events = [
            {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 20, "position": 400,
             "entry": 0, "signal_id": "XAUUSD.ecn:4:BUY", "entry_price": 100,
             "net": 0, "ts_utc": "2026-11-04T08:00:00Z"},
            {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 21, "position": 400,
             "entry": 1, "signal_id": "XAUUSD.ecn:4:BUY", "net": 1,
             "ts_utc": "2026-11-04T10:00:00Z"},
            {"event": "POSITION_LIFECYCLE", "position": 400, "type": 0,
             "price_open": 100, "price_current": 120,
             "ts_utc": "2026-11-04T07:59:00Z"},
            {"event": "POSITION_LIFECYCLE", "position": 400, "type": 0,
             "price_open": 100, "price_current": 100.8,
             "ts_utc": "2026-11-04T08:30:00Z"},
            {"event": "POSITION_LIFECYCLE", "position": 400, "type": 0,
             "price_open": 100, "price_current": 99.6,
             "ts_utc": "2026-11-04T09:30:00Z"},
            {"event": "POSITION_LIFECYCLE", "position": 400, "type": 0,
             "price_open": 100, "price_current": 130,
             "ts_utc": "2026-11-04T10:01:00Z"},
        ]
        result = diagnostics._build_diagnostics(events, "2026-11-04", "2026-11-04")
        trade = result["trades"][0]
        self.assertEqual(trade["sampled_mfe_price"], 0.8)
        self.assertAlmostEqual(trade["sampled_mae_price"], 0.4)
        self.assertEqual(trade["price_sample_count"], 2)
        self.assertEqual(trade["net_status"], "COMPLETE_RECORDED_GROUP")
        self.assertIn("not tick-complete", result["data_limits"][3])

    def test_duplicate_deal_ids_are_deduplicated(self):
        entry = {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 30, "position": 500,
                 "entry": 0, "signal_id": "XAUUSD.ecn:5:SELL", "entry_price": 100.0,
                 "net": -0.10, "ts_utc": "2026-11-04T08:00:00Z"}
        exit_row = {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 31, "position": 500,
                    "entry": 1, "signal_id": "XAUUSD.ecn:5:SELL", "net": 1.35,
                    "ts_utc": "2026-11-04T09:00:00Z"}
        result = diagnostics._build_diagnostics(
            [entry, exit_row, dict(exit_row)], "2026-11-04", "2026-11-04"
        )
        self.assertEqual(result["overall"]["position_groups_with_exit_observed"], 1)
        self.assertEqual(result["overall"]["net_sum_runner_recorded"], 1.25)

    def test_invalid_date_range_is_rejected(self):
        with self.assertRaises(ValueError):
            diagnostics._build_diagnostics([], "2026-11-05", "2026-11-04")

    def test_tehran_local_day_boundary_is_used(self):
        events = [
            {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 40, "position": 600,
             "entry": 1, "signal_id": "XAUUSD.ecn:6:BUY", "net": 1.0,
             "ts_utc": "2026-11-04T21:00:00Z"},
        ]
        result = diagnostics._build_diagnostics(events, "2026-11-05", "2026-11-05")
        self.assertEqual(result["timezone"], "Asia/Tehran (UTC+03:30 fixed offset)")
        self.assertEqual(result["daily"][0]["date_local"], "2026-11-05")
        self.assertEqual(result["trades"][0]["last_exit_observation_day_local"], "2026-11-05")

    def test_tehran_local_day_keeps_pre_midnight_close_on_same_day(self):
        events = [
            {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 41, "position": 601,
             "entry": 1, "signal_id": "XAUUSD.ecn:7:SELL", "net": -1.0,
             "ts_utc": "2026-11-04T20:00:00Z"},
        ]
        result = diagnostics._build_diagnostics(events, "2026-11-04", "2026-11-05")
        self.assertEqual(result["daily"][0]["position_groups_with_exit_observed"], 1)
        self.assertEqual(result["daily"][1]["position_groups_with_exit_observed"], 0)


    def test_inout_is_an_exit_observation_but_missing_net_keeps_group_unknown(self):
        events = [
            {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 50, "position": 700,
             "entry": 0, "signal_id": "XAUUSD.ecn:8:BUY", "entry_price": 100,
             "net": -0.1, "ts_utc": "2026-11-05T08:00:00Z"},
            {"event": "TELEGRAM_DEAL_LIFECYCLE", "deal": 51, "position": 700,
             "entry": 2, "signal_id": "XAUUSD.ecn:8:BUY", "net": None,
             "ts_utc": "2026-11-05T09:00:00Z"},
        ]
        result = diagnostics._build_diagnostics(events, "2026-11-05", "2026-11-05")
        trade = result["trades"][0]
        self.assertEqual(trade["exit_deal_count"], 1)
        self.assertEqual(trade["position_group_status"], "EXIT_OBSERVED_NOT_BROKER_CONFIRMED_CLOSED")
        self.assertEqual(trade["net"], None)
        self.assertEqual(trade["net_status"], "INCOMPLETE_EVENT_WINDOW_OR_NET_FIELDS")
        self.assertEqual(result["overall"]["unknown_net"], 1)


if __name__ == "__main__":
    unittest.main()
