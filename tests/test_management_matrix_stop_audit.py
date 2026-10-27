import csv
import tempfile
import unittest
from pathlib import Path
from scripts.audit_sp2l_v3_management_matrix_stops import audit

class StopFloorAuditTests(unittest.TestCase):
    def test_minimum_stop_floor(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bars = root / "bars.csv"
            trades = root / "trades.csv"
            bars.write_text("timestamp,open,high,low,close\n100,100,101,99,100\n200,98.5,99,98,98.7\n", encoding="utf-8")
            trades.write_text("scenario,direction,trigger_time,entry_time,exit_time,entry,initial_sl,risk_price,final_sl,exit_price,reason,realized_R\nRUNNER,BUY,100,100,200,100,99.86,0.14,99,98.5,TRAIL_SL,-10.7142857\n", encoding="utf-8")
            report = audit(trades, bars)
            self.assertEqual(report["unit_assumption"]["minimum_risk_price"], 1.0)
            self.assertEqual(report["below_minimum_sl_rows"], 1)

if __name__ == "__main__":
    unittest.main()
