from __future__ import annotations
import argparse, csv, importlib.util, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / 'scripts' / 'run_sp2l_v3_candidate_backtest_matrix_causal.py'
OUT = ROOT / 'artifacts' / 'v3' / 'profit_optimizer'

def load_matrix():
    s = importlib.util.spec_from_file_location('sp2l_matrix', MATRIX)
    if s is None or s.loader is None: raise RuntimeError('cannot load matrix')
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def ek(e):
    return (e.get('symbol'), int(e.get('trigger_index', -1)), int(e.get('trigger_time', -1)), e.get('side'))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mt5-path',required=True); p.add_argument('--symbol',default='XAUUSD.ecn')
    p.add_argument('--start',default='2026-07-03T00:00:00+00:00'); p.add_argument('--end')
    p.add_argument('--contract-size',type=float,default=100.0); p.add_argument('--volume',type=float,default=0.01)
    p.add_argument('--pip-size-price',type=float,default=0.01)
    p.add_argument('--rr',nargs='+',type=float,default=[1,1.5,2,2.5,3,4,5])
    p.add_argument('--activation',nargs='+',type=float,default=[0,2,5,10,15,20])
    p.add_argument('--trail',nargs='+',type=float,default=[1,2,3,4,5,8,10])
    a=p.parse_args(); m=load_matrix()
    start=datetime.fromisoformat(a.start); end=datetime.fromisoformat(a.end) if a.end else datetime.now(timezone.utc)
    m.cfg.XAU_PIP_SIZE_PRICE=a.pip_size_price
    if not m.mt5.initialize(path=a.mt5_path): raise RuntimeError(str(m.mt5.last_error()))
    try:
        info=m.mt5.symbol_info(a.symbol); rows=m.load_m1(a.symbol,start,end)
    finally: m.mt5.shutdown()
    if info is None or not rows: raise RuntimeError('missing symbol or M1 data')
    m.cfg.TP_R=a.rr[0]; _,base=m.detect_entries(rows,a.symbol); base_keys=[ek(x) for x in base]
    if not base_keys: raise RuntimeError('no valid entries')
    checks=[]; results=[]
    print('SP2L V3 PROFIT OPTIMIZER - RESEARCH ONLY')
    print('Data:',start.isoformat(),'->',end.isoformat(),'bars=',len(rows),'entries=',len(base))
    print('point=',info.point,'research_pip=',a.pip_size_price)
    for rr in a.rr:
        m.cfg.TP_R=rr; _,entries=m.detect_entries(rows,a.symbol); same=[ek(x) for x in entries]==base_keys
        checks.append((rr,len(entries),same))
        if not same: raise RuntimeError('RR changed signal population: '+str(rr))
        for act in a.activation:
            for trail in a.trail:
                for two in (False,True):
                    v={'id':f'RR{rr:g}_ACT{act:g}_TRAIL{trail:g}_2X'+('ON' if two else 'OFF'),'activation_pips':act,'trail_pips':trail,'use_2x':two}
                    r=m.run_variant(rows=rows,entries=entries,variant=v,contract_size=a.contract_size,volume=a.volume)
                    results.append(dict(candidate=v['id'],rr=rr,activation_pips=act,trail_pips=trail,two_x=two,trades=r['trades'],decisive=r['decisive'],wins=r['wins'],losses=r['losses'],ambiguous=r['ambiguous'],win_rate_pct=r['win_rate_pct'],net_R=r['net_R'],net_USD=r['net_USD'],profit_factor=r['profit_factor'],max_drawdown_R=r['max_drawdown_R'],entry2_touched=r['entry2_touched'],trail_updates=r['total_trail_updates']))
    results.sort(key=lambda x:(x['net_R'],x['profit_factor'],-x['max_drawdown_R']),reverse=True)
    OUT.mkdir(parents=True,exist_ok=True); stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'); basep=OUT/('SP2L_V3_PROFIT_OPTIMIZER_'+stamp)
    payload={'version':'SP2L_V3_PROFIT_OPTIMIZER_20261006','research_only':True,'canonical':False,'symbol':a.symbol,'start_utc':start.isoformat(),'end_utc':end.isoformat(),'m1_bars':len(rows),'mt5_point':info.point,'pip_size_price':a.pip_size_price,'frozen_entries':len(base),'population_checks':[{'rr':x,'entries':n,'same_population':s} for x,n,s in checks],'results':results}
    basep.with_suffix('.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    with basep.with_suffix('.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0])); w.writeheader(); w.writerows(results)
    lines=['# SP2L V3 Profit Optimizer Snapshot','','RESEARCH ONLY','No canonical rule changed.','Fresh holdout required.','','## Population gate','', '| RR | Entries | Same |','|---:|---:|:---:|']
    lines += [f'| {x:g} | {n} | {"PASS" if s else "FAIL"} |' for x,n,s in checks]
    lines += ['', '## Top 20 by Net R','', '| Rank | Candidate | Net R | PF | DD R | WR |','|---:|---|---:|---:|---:|---:|']
    lines += [f"| {i} | {r['candidate']} | {r['net_R']:.3f} | {r['profit_factor']:.3f} | {r['max_drawdown_R']:.3f} | {r['win_rate_pct']:.2f}% |" for i,r in enumerate(results[:20],1)]
    basep.with_name(basep.name+'_SNAPSHOT.md').write_text('\n'.join(lines),encoding='utf-8')
    print('COMPLETE'); print('JSON:',basep.with_suffix('.json')); print('CSV:',basep.with_suffix('.csv')); print('SNAPSHOT:',basep.with_name(basep.name+'_SNAPSHOT.md'))
    for i,r in enumerate(results[:20],1): print(i,r['candidate'],'R=',round(r['net_R'],3),'PF=',round(r['profit_factor'],3),'DD=',round(r['max_drawdown_R'],3),'WR=',round(r['win_rate_pct'],2))

if __name__=='__main__': main()