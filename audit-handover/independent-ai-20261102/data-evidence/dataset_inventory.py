import csv, json, hashlib, math
from pathlib import Path
from datetime import datetime, timezone
root=Path('/agent/workspace/sp2l-factory-audit')
results=[]
for p in sorted((root/'data/mt5-acquisition').glob('*.csv')):
    raw=p.read_bytes()
    rows=list(csv.DictReader(raw.decode('utf-8-sig').splitlines()))
    times=[]; invalid=0; nonfinite=0
    for r in rows:
        t=r.get('time_epoch_seconds') or r.get('time') or r.get('timestamp')
        try: times.append(int(float(t)))
        except (ValueError,TypeError):
            try: times.append(int(datetime.fromisoformat(t.replace('Z','+00:00')).timestamp()))
            except (ValueError,TypeError,AttributeError): pass
        try:
            o,h,l,c=[float(r[k]) for k in ('open','high','low','close')]
            if not all(math.isfinite(x) for x in (o,h,l,c)): nonfinite+=1
            if h<max(o,c,l) or l>min(o,c,h): invalid+=1
        except (KeyError,ValueError,TypeError): invalid+=1
    gaps=[b-a for a,b in zip(times,times[1:])]
    manifest=p.with_suffix('.manifest.json')
    metadata=json.loads(manifest.read_text()) if manifest.exists() else {}
    # No account/server/credential metadata is copied to audit outputs.
    results.append(dict(path=str(p.relative_to(root)),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),rows=len(rows),columns=list(rows[0]) if rows else [],first_raw_epoch=times[0] if times else None,last_raw_epoch=times[-1] if times else None,first_epoch_as_utc=datetime.fromtimestamp(times[0],timezone.utc).isoformat() if times else None,last_epoch_as_utc=datetime.fromtimestamp(times[-1],timezone.utc).isoformat() if times else None,duplicate_epochs=len(times)-len(set(times)),nonincreasing_pairs=sum(x<=0 for x in gaps),nonminute_aligned=sum(t%60!=0 for t in times),gap_pairs_over_60=sum(x>60 for x in gaps),max_gap_seconds=max(gaps,default=None),invalid_ohlc=invalid,nonfinite_ohlc=nonfinite,manifest_present=manifest.exists()))
Path('/agent/workspace/sp2l-audit-evidence/datasets.json').write_text(json.dumps(results,indent=2)+'\n')
for x in results: print(x['path'],x['rows'],x['first_epoch_as_utc'],x['last_epoch_as_utc'],x['sha256'], 'gaps',x['gap_pairs_over_60'],'invalid',x['invalid_ohlc'])
