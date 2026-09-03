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
const BASE_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-candidate-competition-dev-val');
const TOTAL = 15000, PRE = 10000, DEV = 6000, MIN_N = 10;
const BREAKOUT_LOOKBACK = 5, FT_MAX_BARS = 2, SPIKE_MAX_CANDLES = 8, SPIKE_MIN_DIRECTIONAL_FRACTION = .5, SPIKE_MAX_OVERLAP_FRACTION = .8;
const CONTEXT = { emaPeriod:60, roundStep:50, roundDistance:5, tradingSessions:[{name:'LONDON',startMinutes:420,endMinutes:960},{name:'NEW_YORK',startMinutes:780,endMinutes:1320}], avoidWindows:[] };

function key(c){return `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;}
function metrics(rows){const rs=rows.map(x=>Number(x.r)).filter(Number.isFinite),wins=rs.filter(x=>x>0),losses=rs.filter(x=>x<0);const gp=wins.reduce((a,b)=>a+b,0),gl=-losses.reduce((a,b)=>a+b,0);return{n:rs.length,wins:wins.length,losses:losses.length,winRate:rs.length?wins.length/rs.length:0,avgR:rs.length?rs.reduce((a,b)=>a+b,0)/rs.length:0,totalR:rs.reduce((a,b)=>a+b,0),PF:gl?gp/gl:null};}
function pass(m){return m.n>=MIN_N&&m.avgR>0&&m.PF!==null&&m.PF>=1;}

function buildCandidates(candles,index){
 const visible=candles.slice(0,index+1); if(visible.length<Math.max(BREAKOUT_LOOKBACK+2,CONTEXT.emaPeriod))return[];
 const breakouts=detectBreakout(visible,BREAKOUT_LOOKBACK);
 const ft=detectFollowThrough(visible,breakouts,{maxBarsAfterBreakout:FT_MAX_BARS,requireCloseBeyondBrokenLevel:true});
 const spikes=detectSpikeCandidates(visible,breakouts,ft,{maxCandles:SPIKE_MAX_CANDLES,minDirectionalFraction:SPIKE_MIN_DIRECTIONAL_FRACTION,maxOverlapFraction:SPIKE_MAX_OVERLAP_FRACTION});
 const candidates=[];
 for(const spike of spikes.candidates){
  if(spike.endIndex>=index)continue;
  const correction=detectFirstCorrection(visible,spike); if(!correction||correction.correctionExtremeIndex>=index)continue;
  const trigger=detectEntryTrigger(visible,correction); if(!trigger||trigger.index!==index)continue;
  const projection=projectLeg2(visible,correction); if(!projection)continue;
  const invalidation=getInvalidationRule(correction);
  const ema=buildEMAContext(visible.map(c=>c.close),CONTEXT); if(!ema)continue;
  const location=buildLocationContext(trigger.entryPrice,CONTEXT),session=buildSessionContext(trigger.timestamp,CONTEXT);
  const quality=scoreSetup(spike,{ema,location,session}); if(!quality.tradeAllowed)continue;
  const risk=Math.abs(trigger.entryPrice-invalidation.invalidationLevel),reward=Math.abs(projection.tp1-trigger.entryPrice);
  const directional=trigger.direction==='BUY'?projection.tp1>trigger.entryPrice:projection.tp1<trigger.entryPrice;
  if(!(risk>0&&reward>0&&directional))continue;
  candidates.push({entryIndex:index,entryTime:trigger.timestamp,direction:trigger.direction,entry:trigger.entryPrice,stopLoss:invalidation.invalidationLevel,tp1:projection.tp1});
 }
 return candidates;
}

async function run(timeframe){
 const candles=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${timeframe}.json`),'utf8')).candles;
 if(candles.length<TOTAL) throw new Error(`${timeframe}: expected at least ${TOTAL} candles, got ${candles.length}`);
 const base=JSON.parse(await readFile(resolve(BASE_DIR,`${timeframe}.json`),'utf8'));
 const preCutoff=new Date(candles[PRE].timestamp);
 const canonical=new Map((base.trades??[]).filter(t=>t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&new Date(t.entryTime)<preCutoff).map(t=>[key(t),t]));
 const rows=[];
 for(let index=0;index<PRE;index++){
  const candidates=buildCandidates(candles,index); if(!candidates.length)continue;
  const selected=candidates[0],t=canonical.get(key(selected)); if(!t)continue;
  rows.push({index,candidateCount:candidates.length,r:Number(t.rMultiple)});
 }
 const devRows=rows.filter(r=>r.index<DEV),valRows=rows.filter(r=>r.index>=DEV&&r.index<PRE);
 const hypotheses=[
  {id:'SINGLE_CANDIDATE',label:'candidateCount == 1',test:r=>r.candidateCount===1},
  {id:'MULTI_CANDIDATE',label:'candidateCount > 1',test:r=>r.candidateCount>1},
 ];
 const tests=hypotheses.map(h=>{const dev=metrics(devRows.filter(h.test)),val=metrics(valRows.filter(h.test));return{id:h.id,label:h.label,DEV:dev,VAL:val,passDEV:pass(dev),passVAL:pass(val),pass:pass(dev)&&pass(val)};});
 const report={strategy:'Strategy A',mode:'CANDIDATE_COMPETITION_DEV_VAL_PREHOLDOUT',timeframe,scope:{totalCandles:TOTAL,preHoldoutCandles:PRE,devCandles:DEV,valCandles:PRE-DEV,freshHoldoutCandles:TOTAL-PRE,freshHoldoutExcluded:true,minNPerSplit:MIN_N},methodology:{hypothesis:'Frozen after pre-holdout candidate-selection forensic: selected trades with exactly one eligible same-candle candidate may outperform trades with multiple eligible candidates.',split:'Chronological candle split: first 6000 candles DEV; next 4000 candles VAL; last 5000 candles untouched.',gate:'n >= 10, AvgR > 0, PF >= 1 in both DEV and VAL.',purpose:'Validation only. Passing does not change production and only authorizes a separate one-time fresh holdout test.'},counts:{joined:rows.length,DEV:devRows.length,VAL:valRows.length},baseline:{DEV:metrics(devRows),VAL:metrics(valRows)},tests};
 await mkdir(OUT_DIR,{recursive:true}); const out=resolve(OUT_DIR,`${timeframe}.json`); await writeFile(out,JSON.stringify(report,null,2));
 console.log(`${timeframe}: joined=${rows.length} DEV=${devRows.length} VAL=${valRows.length} baselineDEV=${report.baseline.DEV.avgR.toFixed(4)} baselineVAL=${report.baseline.VAL.avgR.toFixed(4)}`);
 for(const t of tests) console.log(` ${t.label}: DEV n=${t.DEV.n} avgR=${t.DEV.avgR.toFixed(4)} PF=${t.DEV.PF?.toFixed(4)??'n/a'} | VAL n=${t.VAL.n} avgR=${t.VAL.avgR.toFixed(4)} PF=${t.VAL.PF?.toFixed(4)??'n/a'} | pass=${t.pass}`);
 console.log(`Report -> ${out}`);
}
await run('1min'); await run('5min');
