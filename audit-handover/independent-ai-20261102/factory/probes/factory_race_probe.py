"""Synthetic provenance race probe: writes only to a fresh temporary directory."""
import csv, hashlib, json, sys, tempfile
from pathlib import Path
sys.path.insert(0,'/agent/workspace/sp2l-factory-audit/src')
from strategy_factory import v3_research_session as mod
with tempfile.TemporaryDirectory(prefix='sp2l-offline-race-') as temp:
    root=Path(temp); m1=root/'m1.json'; entries=root/'entries.csv'
    start='2027-01-15T08:00:00+00:00'; end='2027-01-15T08:01:00+00:00'
    from datetime import datetime
    ts=int(datetime.fromisoformat(start).timestamp())
    payload=dict(schema_version=1,research_only=True,symbol='SYNTHETIC',timeframe='M1',window_utc=dict(start=start,end=end),bars=[dict(time=ts,open=100,high=100,low=100,close=100,tick_volume=1,spread=0,real_volume=0),dict(time=ts+60,open=100,high=101,low=99,close=100,tick_volume=1,spread=0,real_volume=0)])
    m1.write_text(json.dumps(payload)); original_hash=hashlib.sha256(m1.read_bytes()).hexdigest()
    fields='strategy variant direction setup_time_utc entry_time_utc entry_proxy sl_initial target risk_price exit_time_utc exit_price exit_reason status r_multiple'.split()
    row=dict.fromkeys(fields,''); row.update(strategy='A',variant='V3_FROZEN',direction='BUY',setup_time_utc=start,entry_time_utc=start,entry_proxy='100',sl_initial='95',target='105',risk_price='5',status='OPEN')
    with entries.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerow(row)
    original_validator=mod.validate_m1_artifact
    def change_after_validation(*a,**kw):
        result=original_validator(*a,**kw)
        payload['bars'][1].update(high=106,close=105)
        m1.write_text(json.dumps(payload))
        return result
    mod.validate_m1_artifact=change_after_validation
    lab=mod.V3ResearchSession(m1_artifact=m1,entry_artifact=entries,expected_dataset_sha256=original_hash,expected_entry_sha256=hashlib.sha256(entries.read_bytes()).hexdigest(),expected_symbol='SYNTHETIC',expected_start_utc=start,expected_end_utc=end,mt5_point=.01,contract_size=100,volume=.01,engine_revision='SYNTHETIC-UNVERIFIED-LABEL')
    variant=lab.evaluate(rr=1,activation_points=None,distance_points=None)
    assert lab.dataset_report['content_sha256']==original_hash
    assert hashlib.sha256(m1.read_bytes()).hexdigest()!=original_hash
    assert variant.trades[0]['reason']=='TP'
    result=dict(accepted=True,manifest_hash_is_old=True,loaded_bars_are_changed=True,result='TP on changed bytes; original bytes would remain OPEN_OR_UNRESOLVED',scope='Synthetic engineering reproduction only, not market research')
    Path('/agent/workspace/sp2l-audit-evidence/factory-race-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
