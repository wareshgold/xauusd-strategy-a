import json
import zipfile
from scripts.sp2l_v31_forward_forensic import analyze_zip, compact_text


def _zip(path):
    metadata={"captured_at":"2026-11-07T06:00:39Z","expected_version":"V3.1","symbol":"XAUUSD.ecn","magic":26092301}
    deals=[
        {"ticket":1,"position_id":900,"order":100,"entry":0,"type":0,"time":1000,"price":2000,"volume":0.01,"commission":-0.1},
        {"ticket":2,"position_id":900,"order":101,"entry":1,"type":1,"time":1100,"price":2001,"volume":0.01,"profit":1,"commission":-0.1,"reason":5},
        {"ticket":3,"position_id":901,"order":102,"entry":0,"type":1,"time":1200,"price":2002,"volume":0.01,"commission":-0.1},
        {"ticket":4,"position_id":901,"order":103,"entry":1,"type":0,"time":1300,"price":2001,"volume":0.01,"profit":-1,"commission":-0.1,"reason":4},
    ]
    orders=[{"ticket":100},{"ticket":101},{"ticket":102},{"ticket":103}]
    events=[
        {"event":"TRAIL_UPDATE","position":900,"success":True,"new_sl":2000.5},
        {"event":"TRAIL_UPDATE","position":901,"success":False,"new_sl":2001.5},
        {"event":"MT5_DEAL_HISTORY_QUERY_FAILED","target":100},
    ]
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("raw/capture_metadata.json",json.dumps(metadata))
        z.writestr("raw/mt5_history_deals.json",json.dumps(deals))
        z.writestr("raw/mt5_history_orders.json",json.dumps(orders))
        z.writestr("raw/runner_files/forward_events.jsonl","\n".join(map(json.dumps,events))+"\n")


def test_realized_net_and_trailing_join_by_position(tmp_path):
    archive=tmp_path/"capture.zip"; _zip(archive)
    s,rows,_=analyze_zip(archive)
    assert s["realized_closed_positions"]["count"]==2
    assert s["realized_closed_positions"]["wins"]==1
    assert s["realized_closed_positions"]["losses"]==1
    assert s["realized_closed_positions"]["net_account_currency"]==-0.4
    assert s["exit_reasons"]=={"SL":1,"TP":1}
    assert s["trailing"]["updates"]==2
    assert s["trailing"]["success"]==1 and s["trailing"]["failed"]==1
    assert rows[0]["position_id"]==900 and rows[0]["trail_success_count"]==1


def test_compact_output_contains_core_facts(tmp_path):
    archive=tmp_path/"capture.zip"; _zip(archive)
    s,_,_=analyze_zip(archive); out=compact_text(s)
    assert "CLOSED_POSITIONS=2" in out
    assert "HISTORY_QUERY_FAILURES=1" in out
    assert "MFE/MAE" in out
