import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';
import { getInvalidationRule } from '../src/domain/strategy-a/Invalidation.js';
import { projectLeg2 } from '../src/domain/strategy-a/LegProjection.js';
import { buildEMAContext, buildLocationContext, buildSessionContext } from '../src/domain/strategy-a/Context.js';
import { scoreSetup } from '../src/domain/strategy-a/QualityScore.js';

const ROOT = resolve(process.cwd());
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT = resolve(ROOT, 'data/reports/strategy-a-delay1-early-mae-transition-economics');
const PRE = 10000;
const DEV = 6000;
const END = 20;
const H = [3, 5, 10];
const STATES = ['<0.25R', '0.25-0.50R', '0.50-0.75R', '0.75-1.00R', '>=1.00R'];
const finite = Number.isFinite;
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const pct = (n, d) => d ? n / d : null;
const pf = rs => { const w = rs.filter(x => x > 0).reduce((a,b)=>a+b,0); const l = -rs.filter(x => x < 0).reduce((a,b)=>a+b,0); return l > 0 ? w/l : null; };
const stats = rows => { const rs=rows.map(r=>r.rMultiple).filter(finite); return {n:rs.length,avgR:mean(rs),PF:pf(rs),WR:pct(rs.filter(x=>x>0).length,rs.length),exceptional:rs.filter(x=>x>=5).length}; };
const key = t => `${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`;
const state = x => x < .25 ? '<0.25R' : x < .5 ? '0.25-0.50R' : x < .75 ? '0.50-0.75R' : x < 1 ? '0.75-1.00R' : '>=1.00R';

const CTX = { emaPeriod:60, roundStep:50, roundDistance:5, tradingSessions:[{name:'LONDON',startMinutes:420,endMinutes:960},{name:'NEW_YORK',startMinutes:960,endMinutes:1320}], avoidWindows:[] };

function candidate(candles,index){
  const v=candles.slice(0,index+1); if(v.length<60)return null;
  const bo=detectBreakout(v,5); const ft=detectFollowThrough(v,bo,{maxBarsAfterBreakout:2,requireCloseBeyondBrokenLevel:true});
  const sp=detectSpikeCandidates(v,bo,ft,{maxCandles:8,minDirectionalFraction:.5,maxOverlapFraction:.8});
  for(const spike of sp.candidates){
    if(spike.endIndex>=index)continue; const cor=detectFirstCorrection(v,spike);
    if(!cor||cor.correctionExtremeIndex>=index||index-cor.correctionExtremeIndex!==1)continue;
    const tr=detectEntryTrigger(v,cor); if(!tr||tr.index!==index)continue; const pr=projectLeg2(v,cor); if(!pr)continue;
    const inv=getInvalidationRule(cor); const ema=buildEMAContext(v.map(c=>c.close),CTX); if(!ema)continue;
    const loc=buildLocationContext(tr.entryPrice,CTX); const ses=buildSessionContext(tr.timestamp,CTX);
    if(!scoreSetup(spike,{ema,location:loc,session:ses}).tradeAllowed)continue;
    const risk=Math.abs(tr.entryPrice-inv.invalidationLevel); if(!(risk>0))continue;
    if(!(tr.direction==='BUY'?pr.tp1>tr.entryPrice:pr.tp1<tr.entryPrice))continue;
    return {entryIndex:index,direction:tr.direction,entry:tr.entryPrice,stopLoss:inv.invalidationLevel,tp1:pr.tp1,risk};
  } return null;
}

function path(c,cand,a,b){
  let maxMae=0,maxMfe=0,maeBar=null,mfeBar=null; const s=cand.entryIndex+a,e=Math.min(cand.entryIndex+b,c.length-1); if(s>e)return null;
  for(let i=s;i<=e;i++){const x=c[i];const adverse=(cand.direction==='BUY'?cand.entry-x.low:x.high-cand.entry)/cand.risk;const favorable=(cand.direction==='BUY'?x.high-cand.entry:cand.entry-x.low)/cand.risk;
    if(finite(adverse)&&Math.max(0,adverse)>maxMae){maxMae=Math.max(0,adverse);maeBar=i-cand.entryIndex;}
    if(finite(favorable)&&Math.max(0,favorable)>maxMfe){maxMfe=Math.max(0,favorable);mfeBar=i-cand.entryIndex;}
  } return {mae:maxMae,mfe:maxMfe,maeBar,mfeBar};
}

async function load(){
  const raw=JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8')); const candles=raw.candles??raw;
  const baseline=JSON.parse(await readFile(resolve(BASE,'5min.json'),'utf8')).trades??[];
  const usable=baseline.filter(t=>t.result!=='AMBIGUOUS'&&finite(Number(t.rMultiple))&&Number(t.entryIndex)<PRE); const counts=new Map();
  for(const t of usable)counts.set(key(t),(counts.get(key(t))??0)+1); const dup=[...counts.values()].filter(n=>n>1).length; if(dup)throw new Error(`duplicateKeys=${dup}`);
  const map=new Map(usable.map(t=>[key(t),t])); const rows=[]; let candidates=0,matched=0;
  for(let i=0;i<PRE;i++){const c=candidate(candles,i);if(!c)continue;candidates++;const t=map.get(key(c));if(!t)continue;matched++;
    const ps={}; for(const h of H)ps[h]=path(candles,c,1,h); if(Object.values(ps).some(x=>!x))continue;
    rows.push({entryIndex:Number(t.entryIndex),rMultiple:Number(t.rMultiple),sameBarSL:c.direction==='BUY'?candles[i+1].low<=c.stopLoss:candles[i+1].high>=c.stopLoss,...Object.fromEntries(H.map(h=>[`mae${h}`,ps[h].mae])),...Object.fromEntries(H.map(h=>[`mae${h}Bar`,ps[h].maeBar])),...Object.fromEntries(H.map(h=>[`mfe${h}`,ps[h].mfe])),...Object.fromEntries(H.map(h=>[`mfe${h}Bar`,ps[h].mfeBar]))});
  }
  return {rows,candidates,matched,baselinePre:usable.length,duplicateKeys:dup};
}

function transition(rows,from,to){const out={};for(const s of STATES){const q=rows.filter(r=>state(r[`mae${from}`])===s);const counts=Object.fromEntries(STATES.map(x=>[x,0]));for(const r of q)counts[state(r[`mae${to}`])]++;out[s]={n:q.length,to:Object.fromEntries(STATES.map(x=>[x,pct(counts[x],q.length)]))};}return out;}
function transitionEconomics(rows,from,to){
  const out={}; for(const s of STATES){const q=rows.filter(r=>state(r[`mae${from}`])===s);const buckets={IMPROVED:[],UNCHANGED:[],WORSENED:[]};
    for(const r of q){const a=STATES.indexOf(state(r[`mae${from}`])),b=STATES.indexOf(state(r[`mae${to}`]));buckets[b<a?'IMPROVED':b>a?'WORSENED':'UNCHANGED'].push(r);}
    out[s]={n:q.length,improved:stats(buckets.IMPROVED),unchanged:stats(buckets.UNCHANGED),worsened:stats(buckets.WORSENED)};
  } return out;
}
function recovery(rows,h){
  const q=rows.filter(r=>r[`mae${h}`]>=1); const rec=q.filter(r=>r[`mfe${h}`]>=1); const rec2=q.filter(r=>r[`mfe${h}`]>=2);
  return {n:q.length,ge1R:rec.length,pctGE1R:pct(rec.length,q.length),ge2R:rec2.length,pctGE2R:pct(rec2.length,q.length)};
}
function timing(rows,h){
  const q=rows.filter(r=>r[`mae${h}`]>=1&&finite(r[`mfe${h}`Bar])); const before=q.filter(r=>r[`mfe${h}Bar`]>r[`mae${h}Bar`]);
  return {n:q.length,mfeAfterMae:pct(before.length,q.length),maeBarMedian:mean(q.map(r=>r[`mae${h}Bar`]).filter(finite)),mfeBarMedian:mean(q.map(r=>r[`mfe${h}Bar`]).filter(finite))};
}

async function run(){
  const l=await load(),rows=l.rows,dev=rows.filter(r=>r.entryIndex<DEV),val=rows.filter(r=>r.entryIndex>=DEV&&r.entryIndex<PRE),post=rows.filter(r=>!r.sameBarSL),postDev=post.filter(r=>r.entryIndex<DEV),postVal=post.filter(r=>r.entryIndex>=DEV&&r.entryIndex<PRE);
  if(rows.length!==144||dev.length!==91||val.length!==53)throw new Error(`Integrity gate failed rows=${rows.length} dev=${dev.length} val=${val.length}`);
  const make=h=>({transitionToT5:h===3?{all:transition(rows,3,5),dev:transition(dev,3,5),val:transition(val,3,5),economics:transitionEconomics(rows,3,5)}:null,transitionToT10:h===3?{all:transition(rows,3,10),dev:transition(dev,3,10),val:transition(val,3,10),economics:transitionEconomics(rows,3,10)}:h===5?{all:transition(rows,5,10),dev:transition(dev,5,10),val:transition(val,5,10),economics:transitionEconomics(rows,5,10)}:null,recovery:{all:recovery(rows,h),dev:recovery(dev,h),val:recovery(val,h),postEntry:recovery(post,h),postEntryDev:recovery(postDev,h),postEntryVal:recovery(postVal,h)},timing:{all:timing(rows,h),dev:timing(dev,h),val:timing(val,h)}});
  const report={strategy:'Strategy A',mode:'DELAY1_EARLY_MAE_TRANSITION_ECONOMICS',timeframe:'5min',scope:{preHoldoutCandles:PRE,devCutoff:DEV,horizons:H,pathEnd:END,fixedStates:STATES,freshHoldoutAccessed:false},integrity:{baselinePre:l.baselinePre,candidates:l.candidates,matched:l.matched,rows:rows.length,devN:dev.length,valN:val.length,duplicateKeys:l.duplicateKeys,deterministic:true},methodology:{purpose:'Descriptive MAE state-transition economics; determine whether improvement/worsening states separate subsequent outcomes.',outcome:'Canonical baseline rMultiple.',transition:'Earlier fixed MAE state mapped to later fixed MAE state; no optimized thresholds.',timing:'Uses first maximum-MAE/MFE bar locations within the fixed diagnostic path; not an execution model.',sameBarSL:'Reported separately; OHLC cannot establish intrabar event order.',noThresholdOptimization:true,noExitRuleCreation:true,noBrokerExecutionModel:true,diagnosticOnly:true,freshHoldoutExcluded:true,productionUntouched:true},baseline:{all:stats(rows),dev:stats(dev),val:stats(val),postEntry:stats(post),postEntryDev:stats(postDev),postEntryVal:stats(postVal)},horizons:Object.fromEntries(H.map(h=>[`T${h}`,make(h)]))};
  await mkdir(OUT,{recursive:true}); await writeFile(resolve(OUT,'5m.json'),JSON.stringify(report,null,2));
  console.log(`PHASE_10D_EARLY_MAE_TRANSITION N=${rows.length} DEV=${dev.length} VAL=${val.length} FRESH=LOCKED`);
  console.log(`INTEGRITY baselinePre=${l.baselinePre} candidates=${l.candidates} matched=${l.matched} duplicateKeys=${l.duplicateKeys} deterministic=true`);
  console.log(`BASELINE ALL avgR=${report.baseline.all.avgR.toFixed(4)} PF=${report.baseline.all.PF?.toFixed(4)} WR=${(report.baseline.all.WR*100).toFixed(2)}% | POST_ENTRY avgR=${report.baseline.postEntry.avgR.toFixed(4)} PF=${report.baseline.postEntry.PF?.toFixed(4)} WR=${(report.baseline.postEntry.WR*100).toFixed(2)}%`);
  for(const h of H){const x=report.horizons[`T${h}`];const r=x.recovery.all;console.log(`T${h} >=1R: N=${r.n} recovery>=1R=${(r.pctGE1R*100).toFixed(2)}% >=2R=${(r.pctGE2R*100).toFixed(2)}% | DEV=${(x.recovery.dev.pctGE1R*100).toFixed(2)}% VAL=${(x.recovery.val.pctGE1R*100).toFixed(2)}%`);console.log(`T${h} TIMING: N=${x.timing.all.n} MFE_AFTER_MAE=${(x.timing.all.mfeAfterMae*100).toFixed(2)}% meanMAEbar=${x.timing.all.maeBarMedian?.toFixed(2)} meanMFEbar=${x.timing.all.mfeBarMedian?.toFixed(2)}`);}
  console.log('=== TRANSITION ECONOMICS ==='); console.log('T3->T5',JSON.stringify(report.horizons.T3.transitionToT5)); console.log('T3->T10',JSON.stringify(report.horizons.T3.transitionToT10)); console.log('T5->T10',JSON.stringify(report.horizons.T5.transitionToT10));
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
}
run().catch(err=>{console.error(err);process.exitCode=1;});
