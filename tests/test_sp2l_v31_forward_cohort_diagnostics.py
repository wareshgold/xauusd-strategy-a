import unittest
from scripts.sp2l_v31_forward_cohort_diagnostics import analyze, duration_bucket, trail_bucket

class CohortDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"position_id":"1","status":"CLOSED","side":"BUY","net_account_currency":"2.0",
             "entry_time_utc":"2026-11-08T08:00:00+00:00","exit_time_utc":"2026-11-08T08:04:00+00:00",
             "volume_in":"0.01","volume_out":"0.01","entry_price_volume_weighted":"2000",
             "exit_price_volume_weighted":"2002","trail_update_count":"1"},
            {"position_id":"2","status":"CLOSED","side":"SELL","net_account_currency":"-3.0",
             "entry_time_utc":"2026-11-08T08:00:00+00:00","exit_time_utc":"2026-11-08T08:20:00+00:00",
             "volume_in":"0.02","volume_out":"0.01","entry_price_volume_weighted":"2000",
             "exit_price_volume_weighted":"2003","trail_update_count":"0"},
        ]

    def test_reconciles_and_groups(self):
        r = analyze(self.rows)
        self.assertEqual(r["closed_rows"], 2)
        self.assertEqual(r["closed_net_reconciled"], -1.0)
        self.assertEqual(r["by_side"]["BUY"]["wins"], 1)
        self.assertEqual(r["by_trailing_bucket"]["0"]["losses"], 1)
        self.assertEqual(r["anomalies"]["volume_mismatch_count"], 1)
        self.assertEqual(r["hold_duration_minutes"]["median"], 12.0)

    def test_bucket_edges(self):
        self.assertEqual(duration_bucket(4.99), "<5m")
        self.assertEqual(duration_bucket(5), "5-15m")
        self.assertEqual(duration_bucket(15), "15-30m")
        self.assertEqual(duration_bucket(30), "30-60m")
        self.assertEqual(duration_bucket(60), ">=60m")
        self.assertEqual(trail_bucket("3"), "2+")

if __name__ == "__main__":
    unittest.main()
