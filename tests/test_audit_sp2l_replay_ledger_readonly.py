import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_sp2l_replay_ledger_readonly import audit


class ReplayLedgerAuditTests(unittest.TestCase):
    def write_fixture(self, root: Path, payload: dict) -> Path:
        path = root / "replay.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_detects_tp_weighted_accounting_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fixture(Path(directory), {
                "config": {"tpR": 2.0},
                "signals_detected": 3,
                "trades_closed_or_ambiguous": 3,
                "wins": 2,
                "losses": 1,
                "ambiguous": 0,
                "open_or_unresolved": 0,
                "totalR": 1,
                "profit_factor": 2.0,
                "signals": [
                    {"index": 4, "time": 100, "direction": "BUY"},
                    {"index": 7, "time": 160, "direction": "SELL"},
                    {"index": 9, "time": 280, "direction": "BUY"},
                ],
                "trades": [
                    {"index": 4, "time": 100, "direction": "BUY", "outcome": "WIN"},
                    {"index": 7, "time": 160, "direction": "SELL", "outcome": "WIN"},
                    {"index": 9, "time": 280, "direction": "BUY", "outcome": "LOSS"},
                ],
            })
            report = audit(path)
            self.assertEqual(report["conditional_fixed_R_accounting"]["totalR"], 3.0)
            self.assertEqual(report["conditional_fixed_R_accounting"]["profit_factor"], 4.0)
            self.assertTrue(any("totalR differs" in item for item in report["warnings"]))
            self.assertTrue(any("profit_factor differs" in item for item in report["warnings"]))
            self.assertEqual(
                report["overlap_assessment"]["status"],
                "NOT_DETERMINABLE_FROM_ARTIFACT",
            )

    def test_tp_one_matches_counting_metrics_but_overlap_stays_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fixture(Path(directory), {
                "config": {"tpR": 1.0},
                "signals_detected": 2,
                "trades_closed_or_ambiguous": 2,
                "wins": 1,
                "losses": 1,
                "ambiguous": 0,
                "open_or_unresolved": 0,
                "totalR": 0,
                "profit_factor": 1.0,
                "signals": [
                    {"index": 4, "time": 100, "direction": "BUY"},
                    {"index": 5, "time": 160, "direction": "SELL"},
                ],
                "trades": [
                    {"index": 4, "time": 100, "direction": "BUY", "outcome": "WIN"},
                    {"index": 5, "time": 160, "direction": "SELL", "outcome": "LOSS"},
                ],
            })
            report = audit(path)
            self.assertEqual(report["conditional_fixed_R_accounting"]["totalR"], 0.0)
            self.assertEqual(report["conditional_fixed_R_accounting"]["profit_factor"], 1.0)
            self.assertFalse(any("totalR differs" in item for item in report["warnings"]))
            self.assertTrue(any("overlap cannot be validated" in item for item in report["warnings"]))


if __name__ == "__main__":
    unittest.main()
