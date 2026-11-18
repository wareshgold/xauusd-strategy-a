import unittest
from scripts.research_replay_36_path_bounds import simulate_path, summarize

def trade(direction="BUY",entry=100.0,sl=99.0,entry_time=60):
    return {"position_id":1,"direction":direction,"entry":entry,"sl":sl,
            "risk":abs(entry-sl),"entry_time":entry_time}
def bar(ts,o,h,l,c):
    return {"time":ts,"open":o,"high":h,"low":l,"close":c}

class ReplayTests(unittest.TestCase):
    def test_entry_minute_excluded(self):
        r=simulate_path(trade(entry_time=90),[bar(60,100,102,98,100),bar(120,100,100.5,99.5,100)],2,10,10,"ADVERSE_FIRST")
        self.assertEqual(r["status"],"END_OF_DATA")
    def test_initial_stop(self):
        r=simulate_path(trade(),[bar(120,100,100.2,98.8,99.2)],2,10,10,"ADVERSE_FIRST")
        self.assertEqual(r["reason"],"SL"); self.assertAlmostEqual(r["realized_R"],-1)
    def test_tp(self):
        r=simulate_path(trade(),[bar(120,100,102.2,99.8,101.5)],2,10,10,"FAVORABLE_FIRST")
        self.assertEqual(r["reason"],"TP"); self.assertAlmostEqual(r["realized_R"],2)
    def test_same_bar_ordering_diverges(self):
        bars=[bar(120,100,102.5,98.5,100)]
        a=simulate_path(trade(),bars,2,10,10,"ADVERSE_FIRST")
        f=simulate_path(trade(),bars,2,10,10,"FAVORABLE_FIRST")
        self.assertEqual(a["reason"],"SL"); self.assertEqual(f["reason"],"TP")
    def test_gap_trigger_has_no_fill(self):
        r=simulate_path(trade(),[bar(120,98.5,99.5,98,99)],2,10,10,"ADVERSE_FIRST")
        self.assertEqual(r["status"],"GAP_TRIGGER_UNRESOLVED"); self.assertIsNone(r["realized_R"])
    def test_data_gap_censors(self):
        r=simulate_path(trade(),[bar(120,100,100.2,99.8,100),bar(300,100,100.2,99.8,100)],2,10,10,"ADVERSE_FIRST")
        self.assertEqual(r["status"],"DATA_GAP_CENSOR"); self.assertIsNone(r["realized_R"])
    def test_unresolved_remains_in_counts(self):
        rows=[{"status":"RESOLVED","realized_R":1.0,"gross_usd_proxy":1.0},
              {"status":"RESOLVED","realized_R":-1.0,"gross_usd_proxy":-1.0},
              {"status":"END_OF_DATA","realized_R":None,"gross_usd_proxy":None}]
        s=summarize(rows); self.assertEqual(s["positions"],3); self.assertEqual(s["resolved"],2)
        self.assertEqual(s["non_resolved"],1); self.assertEqual(s["wins"],1); self.assertEqual(s["losses"],1)

if __name__=="__main__": unittest.main()
