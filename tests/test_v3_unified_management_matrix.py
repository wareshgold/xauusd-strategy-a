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
