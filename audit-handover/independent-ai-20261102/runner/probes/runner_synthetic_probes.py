"""Offline audit probes. Never import the runner or a real MT5 module."""
import ast, json, sys
from pathlib import Path
from types import SimpleNamespace
root=Path('/agent/workspace/sp2l-independent-audit')
sys.path.insert(0,str(root/'scripts'))
import sp2l_v3_1_rr4_act40_config as cfg
rows=[dict(time=60,open=100,high=101.1,low=99.9,close=101),dict(time=120,open=102,high=106.2,low=101.8,close=106),dict(time=180,open=107,high=108.2,low=106.9,close=108),dict(time=240,open=108.5,high=109,low=106.5,close=108.6)]
a=cfg.find_latest_candidate(rows,'SYNTHETIC')
rows[-1]['low']=104.0
b=cfg.find_latest_candidate(rows,'SYNTHETIC')
assert a['trigger_time']==b['trigger_time']==240
assert a['theoretical_entry'] != b['theoretical_entry']
source=(root/'scripts/run_sp2l_v3_1_xauusd_forward_test.py').read_text()
tree=ast.parse(source)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='trail_positions')
code=compile(ast.Module(body=[node],type_ignores=[]),'<extracted trailing function>','exec')
sends=[]
fake=SimpleNamespace(TIMEFRAME_M1=1,symbol_info=lambda s:SimpleNamespace(point=0.01,trade_stops_level=0,trade_freeze_level=0),symbol_info_tick=lambda s:SimpleNamespace(bid=101.2,ask=101.3),copy_rates_from_pos=lambda *args:[dict(time=120,high=101,low=100)],positions_get=lambda **kw:[SimpleNamespace(magic=7,ticket=1,price_open=100,sl=99,tp=104,time=60,time_msc=60000,type=0)],POSITION_TYPE_BUY=0,TRADE_ACTION_SLTP=6,TRADE_RETCODE_DONE=10009,account_info=lambda:SimpleNamespace(trade_mode=2))
def send(req):
    sends.append(req)
    return SimpleNamespace(retcode=10009,comment='SYNTHETIC ONLY')
fake.order_send=send
scope=dict(mt5=fake,cfg=cfg,_original_monitor=lambda *a:None,runner=SimpleNamespace(log_event=lambda e:None,LIVE_TRADING_ENABLE=False,ALLOW_REAL_EXECUTION=False),LIVE_TRADING_ENABLE=False,ALLOW_REAL_EXECUTION=False)
exec(code,scope)
scope['trail_positions'](dict(symbol='SYNTHETIC',magic=7),{})
assert len(sends)==1
result=dict(forming_bar_geometry_changes_for_same_key=dict(first=a,updated=b),trailing_fake_mutations_despite_disabled_flags=len(sends),missing_local_helpers=[name for name in ('sp2l_history_query_failure_log','sp2l_tracked_deal_history') if not (root/'scripts'/f'{name}.py').exists()],scope='Synthetic controls only; runner never imported; no MT5 installed or initialized; no network or broker')
Path('/agent/workspace/sp2l-audit-evidence/runner-synthetic-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
