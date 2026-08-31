import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT = resolve(ROOT, 'data/reports/strategy-a-base-component-contribution-global-holdout');

function stats(rows) {
  const r = rows.map((x) => Number(x.rMultiple)).filter(Number.isFinite);
  const w = r.filter((x) => x > 0);
  const l = r.filter((x) => x < 0);
  const gw = w.reduce((a, b) => a + b, 0);
  const gl = Math.abs(l.reduce((a, b) => a + b, 0));
  let eq = 0, pk = 0, dd = 0, cl = 0, mcl = 0;
  for (const x of r) {
    eq += x; pk = Math.max(pk, eq); dd = Math.max(dd, pk - eq);
    cl = x < 0 ? cl + 1 : 0; mcl = Math.max(mcl, cl);
  }
  return { n:r.length, wins:w.length, losses:l.length, winRate:r.length ? w.length/r.length : 0,
    avgR:r.length ? r.reduce((a,b)=>a+b,0)/r.length : 0, PF:gl ? gw/gl : null,
    totalR:r.reduce((a,b)=>a+b,0), maxDrawdownR:dd, maxConsecutiveLosses:mcl };
}

function sessionFromTimestamp(timestamp) {
  const d = new Date(timestamp);
  if (Number.isNaN(d.getTime())) return 'UNKNOWN';
  const m = d.getUTCHours() * 60 + d.getUTCMinutes();
  if (m >= 13 * 60 && m < 22 * 60) return 'NEW_YORK';
  if (m >= 7 * 60 && m < 16 * 60) return 'LONDON';
  return 'OUTSIDE';
}

function normalize(row) {
  return { ...row, direction: row.direction ?? 'UNKNOWN', session: row.session ?? sessionFromTimestamp(row.entryTime) };
}
function split3(rows) { const n=rows.length, a=Math.floor(n/3), b=Math.floor((n-a)/2); return [rows.slice(0,a), rows.slice(a,a+b), rows.slice(a+b)]; }
function groups(rows,pred) { return stats(rows.filter(pred)); }
function by(rows,key) { const out={}; for(const r of rows){const k=r[key]??'UNKNOWN';(out[k]??=[]).push(r);} return Object.fromEntries(Object.entries(out).map(([k,v])=>[k,stats(v)])); }
function factorTests(rows) {
  const tests={};
  const add=(name,pred)=>{const s=stats(rows.filter(pred)); tests[name]={...s,share:rows.length?s.n/rows.length:0};};
  add('structure_high',r=>Number(r.structureScore)>=0.7); add('structure_low',r=>Number(r.structureScore)<0.7);
  add('overlap_clean',r=>Number(r.overlapScore)>=0.7); add('overlap_dirty',r=>Number(r.overlapScore)<0.7);
  add('p_gap',r=>r.hasPGAPEvidence===true); add('no_p_gap',r=>r.hasPGAPEvidence!==true);
  add('near_round',r=>r.nearRoundLevel===true); add('not_near_round',r=>r.nearRoundLevel!==true);
  add('ema_aligned',r=>r.emaAligned===true); add('ema_not_aligned',r=>r.emaAligned!==true);
  add('grade_A',r=>r.qualityGrade==='A'); add('grade_B',r=>r.qualityGrade==='B');
  return tests;
}

async function run(tf) {
  const raw=JSON.parse(await readFile(resolve(BASE,`${tf}.json`),'utf8'));
  const trades=(raw.trades??[]).filter(r=>Number.isFinite(Number(r.rMultiple))).map(normalize);
  const [dev,val,holdout]=split3(trades);
  const report={
    strategy:'Strategy A / SP2L', mode:'RESEARCH_BASE_COMPONENT_CONTRIBUTION_GLOBAL_HOLDOUT_V3', timeframe:tf,
    methodology:{ordering:'chronological',split:'first third DEV / middle third VAL / final third HOLDOUT',
      purpose:'diagnostic conditional contribution of deterministic base components; no rule optimization or causal claim',
      sessionFallback:'derive from entryTime in UTC when baseline trade metadata is absent',
      components:['breakout/follow-through/spike structure','first correction / Leg-1','entry trigger','Leg-2 projection / TP1','quality context: EMA/location/session']},
    overall:{DEV:stats(dev),VAL:stats(val),HOLDOUT:stats(holdout)},
    holdout:{byDirection:by(holdout,'direction'),bySession:by(holdout,'session'),
      byDirectionSession:{
        BUY_LONDON:groups(holdout,r=>r.direction==='BUY'&&r.session==='LONDON'),
        BUY_NEW_YORK:groups(holdout,r=>r.direction==='BUY'&&r.session==='NEW_YORK'),
        SELL_LONDON:groups(holdout,r=>r.direction==='SELL'&&r.session==='LONDON'),
        SELL_NEW_YORK:groups(holdout,r=>r.direction==='SELL'&&r.session==='NEW_YORK')},
      componentFactors:factorTests(holdout)}
  };
  await mkdir(OUT,{recursive:true}); const out=resolve(OUT,`${tf}.json`); await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${tf}: trades=${trades.length} DEV/VAL/HOLDOUT=${dev.length}/${val.length}/${holdout.length}`);
  console.log(`  HOLDOUT PF=${report.overall.HOLDOUT.PF?.toFixed(4)??'n/a'} avgR=${report.overall.HOLDOUT.avgR.toFixed(4)} totalR=${report.overall.HOLDOUT.totalR.toFixed(4)} DD=${report.overall.HOLDOUT.maxDrawdownR.toFixed(4)} CL=${report.overall.HOLDOUT.maxConsecutiveLosses}`);
  for(const[k,v]of Object.entries(report.holdout.byDirectionSession)) console.log(`  ${k}: n=${v.n} PF=${v.PF?.toFixed(4)??'n/a'} avgR=${v.avgR.toFixed(4)} totalR=${v.totalR.toFixed(4)}`);
  console.log(`Report -> ${out}`);
}
await run('1min'); await run('5min');
