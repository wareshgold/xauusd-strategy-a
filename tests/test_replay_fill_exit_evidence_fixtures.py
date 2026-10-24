"""Deterministic synthetic evidence fixtures; no strategy or broker logic."""
from __future__ import annotations

import unittest


FIXTURES = [
    {
        "id": "FILL-00-explicit-no-fill-evidence",
        "entry_reference": 100.0,
        "fill_events": [],
        "authoritative_order_event": {
            "kind": "terminal_rejection_before_any_fill",
            "source_ref": "synthetic:order-event-1",
        },
        "expected_entry_status": "NOT_FILLED",
    },
    {
        "id": "FILL-01-entry-never-touched",
        "entry_reference": 100.0,
        "subsequent_candles": [{"low": 104.0, "high": 106.0}, {"low": 89.0, "high": 92.0}],
        "sl_reference": 90.0,
        "tp_reference": 110.0,
        "fill_events": [],
        "observed_entry_touch": False,
        "expected_entry_status": "UNKNOWN",
        "expected_exit_status": "UNKNOWN",
    },
    {
        "id": "FILL-02-entry-touched-semantics-unknown",
        "entry_reference": 100.0,
        "subsequent_candles": [{"low": 99.0, "high": 102.0}],
        "fill_events": [],
        "observed_entry_touch": True,
        "approved_fill_rule": None,
        "expected_entry_status": "UNKNOWN",
        "expected_exit_status": "UNKNOWN",
    },
    {
        "id": "EXIT-03-both-levels-same-bar",
        "entry_status": "FILLED",
        "fill_evidence_ref": "synthetic:fill-event-1",
        "sl_reference": 95.0,
        "tp_reference": 105.0,
        "exit_candle": {"index": 12, "low": 94.0, "high": 106.0},
        "finer_grained_exit_evidence": False,
        "expected_entry_status": "FILLED",
        "expected_exit_status": "AMBIGUOUS",
    },
    {
        "id": "OVERLAP-04-referenced-intervals",
        "trades": [
            {"id": "T1", "entry_index": 4, "exit_index": 9, "entry_evidenced": True, "exit_evidenced": True},
            {"id": "T2", "entry_index": 7, "exit_index": 11, "entry_evidenced": True, "exit_evidenced": True},
        ],
        "expected_overlap_status": "DETERMINABLE",
        "expected_overlap": True,
        "incomplete_control": {
            "id": "T3", "entry_index": 8, "exit_index": None,
            "entry_evidenced": True, "exit_evidenced": False,
            "expected_overlap_status": "NOT_DETERMINABLE",
        },
    },
    {
        "id": "R-05-conditional-tpR2-accounting",
        "tp_r": 2.0,
        "wins": 1,
        "losses": 1,
        "ambiguous": 0,
        "costs_assumption": "zero costs for arithmetic fixture only",
        "expected_conditional_total_r": 1.0,
        "expected_conditional_profit_factor": 2.0,
    },
]


class ReplayEvidenceSyntheticFixtureTests(unittest.TestCase):
    def test_fixture_ids_are_unique_and_required_cases_exist(self):
        ids = [fixture["id"] for fixture in FIXTURES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            set(ids),
            {
                "FILL-00-explicit-no-fill-evidence",
                "FILL-01-entry-never-touched",
                "FILL-02-entry-touched-semantics-unknown",
                "EXIT-03-both-levels-same-bar",
                "OVERLAP-04-referenced-intervals",
                "R-05-conditional-tpR2-accounting",
            },
        )

    def test_not_filled_requires_explicit_authoritative_negative_evidence(self):
        fixture = FIXTURES[0]
        event = fixture["authoritative_order_event"]
        self.assertEqual(event["kind"], "terminal_rejection_before_any_fill")
        self.assertTrue(event["source_ref"])
        self.assertEqual(fixture["fill_events"], [])
        self.assertEqual(fixture["expected_entry_status"], "NOT_FILLED")

    def test_later_stop_touch_does_not_create_fill_event(self):
        fixture = FIXTURES[1]
        self.assertFalse(fixture["observed_entry_touch"])
        self.assertEqual(fixture["fill_events"], [])
        self.assertEqual(fixture["expected_entry_status"], "UNKNOWN")
        self.assertTrue(any(
            candle["low"] <= fixture["sl_reference"] <= candle["high"]
            for candle in fixture["subsequent_candles"]
        ))

    def test_entry_touch_without_approved_rule_remains_unknown(self):
        fixture = FIXTURES[2]
        self.assertTrue(fixture["observed_entry_touch"])
        self.assertIsNone(fixture["approved_fill_rule"])
        self.assertEqual(fixture["expected_entry_status"], "UNKNOWN")
        self.assertNotEqual(fixture["expected_entry_status"], "NOT_FILLED")

    def test_same_bar_sl_tp_touch_is_ambiguous_without_finer_evidence(self):
        fixture = FIXTURES[3]
        candle = fixture["exit_candle"]
        self.assertLessEqual(candle["low"], fixture["sl_reference"])
        self.assertGreaterEqual(candle["high"], fixture["tp_reference"])
        self.assertFalse(fixture["finer_grained_exit_evidence"])
        self.assertEqual(fixture["expected_exit_status"], "AMBIGUOUS")

    def test_overlap_requires_both_interval_boundaries(self):
        fixture = FIXTURES[4]
        first, second = fixture["trades"]
        self.assertTrue(first["entry_evidenced"] and first["exit_evidenced"])
        self.assertTrue(second["entry_evidenced"] and second["exit_evidenced"])
        self.assertLess(max(first["entry_index"], second["entry_index"]),
                        min(first["exit_index"], second["exit_index"]))
        self.assertEqual(fixture["expected_overlap_status"], "DETERMINABLE")
        self.assertTrue(fixture["expected_overlap"])
        control = fixture["incomplete_control"]
        self.assertIsNone(control["exit_index"])
        self.assertFalse(control["exit_evidenced"])
        self.assertEqual(control["expected_overlap_status"], "NOT_DETERMINABLE")

    def test_tp_r2_conditional_accounting_is_explicit_and_deterministic(self):
        fixture = FIXTURES[5]
        total_r = fixture["wins"] * fixture["tp_r"] - fixture["losses"]
        profit_factor = fixture["wins"] * fixture["tp_r"] / fixture["losses"]
        self.assertEqual(total_r, fixture["expected_conditional_total_r"])
        self.assertEqual(profit_factor, fixture["expected_conditional_profit_factor"])
        self.assertIn("zero costs", fixture["costs_assumption"])


if __name__ == "__main__":
    unittest.main()
