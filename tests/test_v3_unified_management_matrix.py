import pytest
from strategy_factory.v3_management_engine import normalize_management_spec
from strategy_factory.v3_exit_engine import V3ExitEngineError
from scripts.run_sp2l_v3_unified_management_matrix import variants,summary
def test_variant_inventory():
 v=variants();c={}
 for x in v:c[x["family"]]=c.get(x["family"],0)+1
 assert len(v)==603
 assert c=={"FIXED_RR":4,"NO_TARGET":1,"BREAK_EVEN":3,"FIXED_DISTANCE_TRAIL":110,"STEP_LOCK":1,"STEP_LOCK_TP":4,"BE_PLUS_TRAIL":36,"FIXED_TP_PLUS_TRAIL":440,"TIME_EXIT":4}
 assert next(x for x in v if x["name"]=="FDT_A0_D0.2")["spec"]["activation_r"]==0
def test_summary_counts_breakeven_and_unresolved():
 rows=[{"ambiguous":False,"realized_R":1.,"realized_usd":10.,"reason":"TP"},{"ambiguous":False,"realized_R":0.,"realized_usd":0.,"reason":"BE"},{"ambiguous":False,"realized_R":-1.,"realized_usd":-10.,"reason":"SL"},{"ambiguous":True,"realized_R":None,"realized_usd":None,"reason":"M1_GAP_WHILE_OPEN"},{"ambiguous":False,"realized_R":None,"realized_usd":None,"reason":"OPEN_OR_UNRESOLVED"}]
 s=summary(rows);assert(s["decisive"],s["wins"],s["losses"],s["breakeven"])==(3,1,1,1);assert(s["ambiguous"],s["open_unresolved"],s["gap_exposed"])==(1,1,1)

def test_no_final_tp_and_zero_trailing_activation_are_explicit():
 assert normalize_management_spec({"mode":"BREAK_EVEN","rr":None,"activation_r":1})["rr"] is None
 assert normalize_management_spec({"mode":"BREAK_EVEN_TRAILING","rr":None,"be_activation_r":1,"be_offset_r":0,"trail_activation_r":1,"trail_distance_r":0.5})["rr"] is None
 assert normalize_management_spec({"mode":"TRAILING_R","rr":None,"activation_r":0,"distance_r":0.2})["activation_r"]==0
 with pytest.raises(V3ExitEngineError):
  normalize_management_spec({"mode":"BREAK_EVEN","rr":None,"activation_r":0})

def test_zero_activation_trailing_is_eligible_even_if_first_bar_never_reaches_entry():
 from strategy_factory.v3_management_engine import replay_management_trade
 c={"entry_idx":0,"theoretical_entry":100.0,"risk":5.0,"sl":95.0,
    "direction":"BUY","trigger_time":1800000000,"signal_time_utc":"t0"}
 b=[{"time":1800000000,"open":100.0,"high":100.0,"low":100.0,"close":100.0},
    {"time":1800000060,"open":99.8,"high":99.9,"low":99.7,"close":99.8}]
 r=replay_management_trade(c,b,normalize_management_spec(
    {"mode":"TRAILING_R","rr":None,"activation_r":0,"distance_r":0.1}),
    mt5_point=.01,contract_size=100,volume=.01)
 assert r["trailing_activated"] is True
 assert r["trailing_updates"] == 1
 assert r["final_sl"] == 99.4

def test_drawdown_uses_exit_time_cohorts_and_is_row_order_invariant():
 rows=[
  {"ambiguous":False,"realized_R":-0.5,"realized_usd":-5.,"reason":"SL","exit_time_utc":"2026-01-02T00:00:00+00:00"},
  {"ambiguous":False,"realized_R":1.,"realized_usd":10.,"reason":"TP","exit_time_utc":"2026-01-01T00:00:00+00:00"},
  {"ambiguous":False,"realized_R":-0.5,"realized_usd":-5.,"reason":"SL","exit_time_utc":"2026-01-03T00:00:00+00:00"},
 ]
 assert summary(rows)["max_drawdown_usd"]==10
 assert summary(list(reversed(rows)))["max_drawdown_usd"]==10


def test_same_minute_exits_are_aggregated_without_inventing_intraminute_order():
 rows=[
  {"ambiguous":False,"realized_R":1.,"realized_usd":10.,"reason":"TP","exit_time_utc":"2026-01-01T00:00:00+00:00"},
  {"ambiguous":False,"realized_R":-0.5,"realized_usd":-5.,"reason":"SL","exit_time_utc":"2026-01-01T00:00:00+00:00"},
  {"ambiguous":False,"realized_R":-0.5,"realized_usd":-5.,"reason":"SL","exit_time_utc":"2026-01-02T00:00:00+00:00"},
 ]
 assert summary(rows)["max_drawdown_usd"]==5
 assert summary(list(reversed(rows)))["max_drawdown_usd"]==5
