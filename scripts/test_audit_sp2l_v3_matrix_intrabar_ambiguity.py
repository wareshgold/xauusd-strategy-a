import unittest
from audit_sp2l_v3_matrix_intrabar_ambiguity import Bar, Trade, inspect_variant, EXPECTED_IDS

class SyntheticAuditTests(unittest.TestCase):
    def setUp(self):
        self.trade=Trade(62458477,"BUY",100.0,99.0,120,240,99.5)

    def test_same_bar_tp_sl_flagged(self):
        bars=[Bar(180,100.0,102.1,98.9,100.5),Bar(240,100.5,100.8,100.2,100.4)]
        row=inspect_variant(self.trade,bars,2,0,0,False)
        self.assertEqual(row["classification"],"AMBIGUOUS")
        self.assertTrue(row["has_same_bar_tp_sl"])

    def test_trail_update_and_touch_same_bar_flagged(self):
        bars=[Bar(180,100.0,101.0,100.4,100.6),Bar(240,100.6,101.0,100.3,100.5)]
        row=inspect_variant(self.trade,bars,4,50,50,False)
        self.assertEqual(row["classification"],"AMBIGUOUS")
        self.assertTrue(row["has_trail_update_and_touch_same_bar"])

    def test_2x_is_touch_not_fill(self):
        bars=[Bar(180,100.0,100.2,99.4,99.8),Bar(240,99.8,100.0,99.7,99.9)]
        row=inspect_variant(self.trade,bars,4,0,0,True)
        self.assertTrue(row["has_2x_touch_before_first_candidate"])
        self.assertEqual(row["classification"],"NO_LEVEL_TOUCH_OBSERVED")

    def test_gap_is_reported(self):
        bars=[Bar(180,100.0,100.2,99.8,100.0),Bar(300,100.0,100.2,99.8,100.0)]
        row=inspect_variant(self.trade,bars,4,0,0,False)
        self.assertIn("M1_GAP_IN_REPLAY_WINDOW",row["ambiguity_flags"])
        self.assertEqual(row["classification"],"DATA_GAP_OR_COVERAGE_LIMIT")

    def test_whitelist_count(self):
        self.assertEqual(len(EXPECTED_IDS),36)

if __name__=="__main__": unittest.main()
