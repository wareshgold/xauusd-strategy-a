import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const PATH_DIR=resolve(ROOT,'data/reports/strategy-a-first-correction-path-forensics');
const BASE_DIR=resolve(ROOT,'data/reports/strategy-a-baseline');
const OUT_DIR=resolve(ROOT,'data/reports/strategy-a-entry-quality-combinations-dev-val');
const TOTAL=15000, PRE=10000, DEV=6000, MIN_N=10;

function stats(rows){const rs=rows.map(r=>Number(r.r)).filter(Number.isFinite),w=rs.filter(x=>x>0),l=rs.filter(x=>x<0),gp=w.reduce((a,b)=>a+b,0),gl=-l.reduce((a,b)=>a+b,0);return{n:rs.length,wins:w.length,losses:l.length,winRate:rs.length?w.length/rs.length:0,avgR:rs.length?rs.reduce((a,b)=>a+b,0)/rs.length:0,totalR:rs.reduce((a,b)=>a+b,0),PF:gl?gp/gl:null};}
function key(c){return `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;}
function evaluate(name,p,dev,val,bD,bV){const d=stats(dev.filter(p)),v=stats(val.filter(p));return{name,DEV:d,VAL:v,devDeltaAvgR:d.avgR-bD.avgR,valDeltaAvgR:v.avgR-bV.avgR,eligible:d.n>=MIN_N&&v.n>=MIN_N,pass:d.n>=MIN_N&&v.n>=MIN_N&&d.avgR>0&&v.avgR>0&&d.PF!==null&&v.PF!==null&&d.PF>=1&&v.PF>=1};}
async function run(timeframe){
 const candles=(JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${timeframe}.json`),'utf8')).candles??[]);
 const path=JSON.parse(await readFile(resolve(PATH_DIR,`${timeframe}.json`),'utf8'));
 const base=JSON.parse(await readFile(resolve(BASE_DIR,`${timeframe}.json`),'utf8'));
 const cutoff=new Date(candles[PRE].timestamp),devCut=new Date(candles[DEV].timestamp);
 const canonical=new Map((base.trades??[]).filter(t=>t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&new Date(t.entryTime)<cutoff).map(t=>[key(t),t]));
 const selected=(path.baselineSelected??[]).filter(c=>c.index<PRE),rows=[];
 for(const c of selected){const t=canonical.get(key(c));if(t)rows.push({...c,r:Number(t.rMultiple),entryTime:t.entryTime});}
 const dev=rows.filter(r=>r.index<DEV),val=rows.filter(r=>r.index>=DEV&&r.index<PRE),bD=stats(dev),bV=stats(val);
 const predicates={
  'delay<=1':r=>r.triggerDelay<=1,
  'triggerBody>=50%':r=>r.triggerBody>=0.50,
  'triggerClose>=75%':r=>r.triggerCloseLocation>=0.75,
  'triggerOppWick<=25%':r=>r.triggerOppositeWick<=0.25,
  'delay<=1 AND body>=50%':r=>r.triggerDelay<=1&&r.triggerBody>=0.50,
  'delay<=1 AND close>=75%':r=>r.triggerDelay<=1&&r.triggerCloseLocation>=0.75,
  'delay<=1 AND oppWick<=25%':r=>r.triggerDelay<=1&&r.triggerOppositeWick<=0.25,
  'body>=50% AND close>=75%':r=>r.triggerBody>=0.50&&r.triggerCloseLocation>=0.75,
  'body>=50% AND oppWick<=25%':r=>r.triggerBody>=0.50&&r.triggerOppositeWick<=0.25,
  'close>=75% AND oppWick<=25%':r=>r.triggerCloseLocation>=0.75&&r.triggerOppositeWick<=0.25,
  'delay<=1 AND body>=50% AND close>=75%':r=>r.triggerDelay<=1&&r.triggerBody>=0.50&&r.triggerCloseLocation>=0.75,
  'delay<=1 AND body>=50% AND oppWick<=25%':r=>r.triggerDelay<=1&&r.triggerBody>=0.50&&r.triggerOppositeWick<=0.25,
  'delay<=1 AND close>=75% AND oppWick<=25%':r=>r.triggerDelay<=1&&r.triggerCloseLocation>=0.75&&r.triggerOppositeWick<=0.25,
  'body>=50% AND close>=75% AND oppWick<=25%':r=>r.triggerBody>=0.50&&r.triggerCloseLocation>=0.75&&r.triggerOppositeWick<=0.25,
  'ALL FOUR':r=>r.triggerDelay<=1&&r.triggerBody>=0.50&&r.triggerCloseLocation>=0.75&&r.triggerOppositeWick<=0.25
 };
 const results=Object.entries(predicates).map(([n,p])=>evaluate(n,p,dev,val,bD,bV));
 const report={strategy:'Strategy A',mode:'ENTRY_QUALITY_COMBINATIONS_DEV_VAL',timeframe,scope:{totalCandles:TOTAL,preHoldoutCandles:PRE,devCandles:DEV,valCandles:PRE-DEV,freshHoldoutCandles:TOTAL-PRE,freshHoldoutExcluded:true},methodology:{purpose:'Frozen diagnostic matrix for reclaim/entry quality; not a production optimization.',outcomeSource:'canonical baseline outcome joined by exact entry/direction/SL/TP1 key',featureSource:'first-correction path forensics',thresholdsFrozen:{triggerDelay:'<=1',triggerBody:0.50,triggerCloseLocation:0.75,triggerOppositeWick:0.25},split:'chronological 6000 DEV / 4000 VAL',minN:MIN_N,valNotUsedForThresholdSelection:true,noFreshHoldout:true,productionUntouched:true},baseline:{DEV:bD,VAL:bV},results,decision:'Attribution only. A passing combination does not authorize production change; any candidate must be separately pre-registered for one fresh-holdout confirmation.'};
 await mkdir(OUT_DIR,{recursive:true});const out=resolve(OUT_DIR,`${timeframe}.json`);await writeFile(out,JSON.stringify(report,null,2));
 console.log(`${timeframe}: joined=${rows.length} DEV=${dev.length} VAL=${val.length} baselineDEV=${bD.avgR.toFixed(4)} baselineVAL=${bV.avgR.toFixed(4)}`);
 for(const x of results)console.log(`  ${x.name}: DEV n=${x.DEV.n} avgR=${x.DEV.avgR.toFixed(4)} PF=${x.DEV.PF?.toFixed(3)??'n/a'} | VAL n=${x.VAL.n} avgR=${x.VAL.avgR.toFixed(4)} PF=${x.VAL.PF?.toFixed(3)??'n/a'} | pass=${x.pass}`);
 console.log(`Report -> ${out}`);
}
await run('1min');await run('5min');
