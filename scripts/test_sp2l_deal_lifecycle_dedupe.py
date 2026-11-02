"""Tests for idempotent V3.1 deal lifecycle event observation."""
from __future__ import annotations

import unittest

from sp2l_deal_lifecycle_dedupe import claim_deal_lifecycle_event


class DealLifecycleDedupeTests(unittest.TestCase):
    def test_first_observation_is_claimed(self):
        state = {"deal_events": set()}
        self.assertTrue(claim_deal_lifecycle_event(state, 64045947))
        self.assertEqual(state["deal_events"], {64045947})

    def test_same_deal_is_not_claimed_twice(self):
        state = {"deal_events": {64045947}}
        self.assertFalse(claim_deal_lifecycle_event(state, 64045947))
        self.assertEqual(state["deal_events"], {64045947})

    def test_json_loaded_list_is_normalized_to_set(self):
        state = {"deal_events": [64045947]}
        self.assertFalse(claim_deal_lifecycle_event(state, 64045947))
        self.assertIsInstance(state["deal_events"], set)

    def test_distinct_deals_are_independent(self):
        state = {"deal_events": set()}
        self.assertTrue(claim_deal_lifecycle_event(state, 64045947))
        self.assertTrue(claim_deal_lifecycle_event(state, 64045948))
        self.assertEqual(state["deal_events"], {64045947, 64045948})


if __name__ == "__main__":
    unittest.main()
