import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT = resolve(ROOT, 'data/reports/strategy-a-base-component-contribution-global-holdout');

function finite(v) { return Number.isFinite(Number(v)); }
function stats(rows) {
  const r = rows.map(x => Number(x.rMultiple)).filter(Number.isFinite);
  const wins = r.filter(x => x > 0);
  const losses = r.filter(x => x < 0);
  const grossWin = wins.reduce((a,b) => a+b, 0);
  const grossLoss = Math.abs(losses.reduce((a,b) => a+b, 0));
  let eq=0, peak=0, dd=0, cl=0, maxCl=0;
  for (const x of r) { eq += x; peak = Math.max(peak, eq); dd = Math.max(dd, peak-eq); cl = x<0 ? cl+1 : 0; maxCl=Math.max(maxCl,cl); }
  return { n:r.length, wins:wins.length, losses:losses.length, winRate:r.length?wins.length/r.length:0, avgR:r.length?r.reduce((a,b)=>a+b,0)/r.length:0, PF:grossLoss?grossWin/grossLoss:null, totalR:r.reduce((a,b)=>a+b,0), maxDrawdownR:dd, maxConsecutiveLosses:maxCl };
}
function split3(rows) {
  const n=rows.length, a=Math.floor(n/3), b=Math.floor((n-a)/2);
  return [rows.slice(0,a), rows.slice(a,a+b), rows.slice(a+b)];
}
function group(rows, key) {
  const out={};
  for(const r of rows){ const v=r[key] ?? 'UNKNOWN'; (out[v]??=[]).push(r); }
  return Object.fromEntries(Object.entries(out).map(([k,v])=>[k,stats(v)]));
}

async function run(tf){
  const raw=JSON.parse(await readFile(resolve(BASE,`${tf}.json`),'utf8'));
  const trades=(raw.trades??[]).filter(r=>finite(r.rMultiple));
  const [dev,val,holdout]=split3(trades);
  const components={
    structure:'market breakout + follow-through + spike structure',
    correction:'first correction / Leg-1 correction',
    trigger:'deterministic entry trigger',
    projection:'Leg-2 projection + directional TP1 validation',
    quality:'EMA/location/session quality gate',
  };
  const report={
    strategy:'Strategy A / SP2L',
    mode:'RESEARCH_BASE_COMPONENT_CONTRIBUTION_GLOBAL_HOLDOUT_V1',
    timeframe:tf,
    methodology:{ordering:'chronological',split:'first third DEV / middle third VAL / final third HOLDOUT',selection:'no optimization; baseline trades only',purpose:'attribute observed baseline outcomes to deterministic component/context dimensions; not a new trading rule',warning:'Conditional component statistics are diagnostic evidence and must not be interpreted as causal edge proof.'},
    components,
    overall:{DEV:stats(dev),VAL:stats(val),HOLDOUT:stats(holdout)},
    holdoutByDirection:group(holdout,'direction'),
    holdoutBySession:group(holdout,'session'),
    holdoutByDirectionSession:{
      BUY_LONDON:stats(holdout.filter(r=>r.direction==='BUY'&&r.session==='LONDON')),
      BUY_NEW_YORK:stats(holdout.filter(r=>r.direction==='BUY'&&r.session==='NEW_YORK')),
      SELL_LONDON:stats(holdout.filter(r=>r.direction==='SELL'&&r.session==='LONDON')),
      SELL_NEW_YORK:stats(holdout.filter(r=>r.direction==='SELL'&&r.session==='NEW_YORK')),
    },
  };
  await mkdir(OUT,{recursive:true});
  const out=resolve(OUT,`${tf}.json`);
  await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${tf}: trades=${trades.length} DEV/VAL/HOLDOUT=${dev.length}/${val.length}/${holdout.length}`);
  console.log(`  HOLDOUT PF=${report.overall.HOLDOUT.PF?.toFixed(4)??'n/a'} avgR=${report.overall.HOLDOUT.avgR.toFixed(4)} totalR=${report.overall.HOLDOUT.totalR.toFixed(4)} DD=${report.overall.HOLDOUT.maxDrawdownR.toFixed(4)} CL=${report.overall.HOLDOUT.maxConsecutiveLosses}`);
  for(const [k,v] of Object.entries(report.holdoutByDirectionSession)) console.log(`  ${k}: n=${v.n} PF=${v.PF?.toFixed(4)??'n/a'} avgR=${v.avgR.toFixed(4)} totalR=${v.totalR.toFixed(4)}`);
  console.log(`Report -> ${out}`);
}
await run('1min');
await run('5min');
