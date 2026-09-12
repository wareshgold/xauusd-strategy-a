import { execFileSync } from 'node:child_process';
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

const ROOT=resolve(process.cwd());
const BASELINE_COMMIT='3a96629838fb0a15e5b71f1927dc4f7fe63819e1';
const BASELINE=JSON.parse(await readFile(resolve(ROOT,'data/reports/strategy-a-baseline/5min.json'),'utf8'));
const PH24=JSON.parse(await readFile(resolve(ROOT,'data/reports/strategy-a-phase24-preentry-loss-archetype-predictability/5min.json'),'utf8'));
const candles=JSON.parse(execFileSync('git',['show',`${BASELINE_COMMIT}:data/historical/xauusd-5min.json`],{cwd:ROOT,encoding:'utf8',maxBuffer:64*1024*1024})).candles;
const OUT=resolve(ROOT,'data/reports/strategy-a-phase38-a-ny-temporal-stability');
const D='LOSS_D_PRE_GE_2R',EPS=1e-9;
const CTX={emaPeriod:60,roundStep:50,roundDistance:5,tradingSessions:[{name:'LONDON',startMinutes:420,endMinutes:960},{name:'NEW_YORK',startMinutes:780,endMinutes:1320}],avoidWindows:[]};
const byTime=new Map((PH24.cases??[]).map(x=>[x.entryTime,x]));
function same(a,b){return Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=EPS;}
function session(ts){const d=new Date(ts),m=d.getUTCHours()*60+d.getUTCMinutes();if(m>=420&&m<960)return'LONDON';if(m>=780&&m<1320)return'NEW_YORK';return'OUT_OF_SESSION';}
function flipR(c){const risk=Math.abs(c.entry-c.stopLoss);for(let i=c.entryIndex+1;i<candles.length;i++){const x=candles[i],sl=x.high>=c.stopLoss,tp=x.low<=c.tp1;if(sl&&tp)return null;if(sl)return-1;if(tp)return Math.abs(c.tp1-c.entry)/risk;}return null;}
function stats(values){const v=values.filter(Number.isFinite),w=v.filter(x=>x>0),l=v.filter(x=>x<=0),gw=w.reduce((s,x)=>s+x,0),gl=Math.abs(l.reduce((s,x)=>s+x,0));return{n:v.length,WR:v.length?w.length/v.length:null,avgR:v.length?v.reduce((s,x)=>s+x,0)/v.length:null,PF:gl?gw/gl:null,totalR:v.reduce((s,x)=>s+x,0),positiveN:w.length,negativeN:l.length};}
const generated=[];
for(let index=0;index<candles.length;index++){
  const visible=candles.slice(0,index+1);if(visible.length<60)continue;
  const bo=detectBreakout(visible,5);if(!bo.length)continue;
  const ft=detectFollowThrough(visible,bo,{maxBarsAfterBreakout:2,requireCloseBeyondBrokenLevel:true});if(!ft.length)continue;
  const spikes=detectSpikeCandidates(visible,bo,ft,{maxCandles:8,minDirectionalFraction:.5,maxOverlapFraction:.8});
  for(const spike of spikes.candidates.filter(s=>s.endIndex<index)){
    const correction=detectFirstCorrection(visible,spike);if(!correction||correction.correctionExtremeIndex>=index)continue;
    const trigger=detectEntryTrigger(visible,correction);if(!trigger||trigger.index!==index)continue;
    const projection=projectLeg2(visible,correction),invalidation=getInvalidationRule(correction),ema=buildEMAContext(visible.map(c=>c.close),CTX);if(!projection||!ema)continue;
    const location=buildLocationContext(trigger.entryPrice,CTX),sess=buildSessionContext(trigger.timestamp,CTX),quality=scoreSetup(spike,{ema,location,session:sess});if(!quality.tradeAllowed)continue;
    const risk=Math.abs(trigger.entryPrice-invalidation.invalidationLevel),reward=Math.abs(projection.tp1-trigger.entryPrice);if(risk<=0||reward<=0)continue;
    if(!(trigger.direction==='BUY'?projection.tp1>trigger.entryPrice:projection.tp1<trigger.entryPrice))continue;
    generated.push({entryIndex:index,entryTime:trigger.timestamp,direction:trigger.direction,entry:trigger.entryPrice,stopLoss:invalidation.invalidationLevel,tp1:projection.tp1,session:sess.session});break;
  }
}
const stored=BASELINE.trades??[],rows=[];let exact=0;
for(const t of stored){
  const g=generated.find(x=>x.entryTime===t.entryTime);if(!g||g.entryIndex!==t.entryIndex||g.direction!==t.direction||!same(g.entry,t.entry)||!same(g.stopLoss,t.stopLoss)||!same(g.tp1,t.tp1))throw new Error(`Generation parity failed at ${t.entryTime}`);exact++;
  const p=byTime.get(t.entryTime);if(!p||p.archetype===D||p.archetype!=='LOSS_A_NO_PRE_FAVORABLE'||g.direction!=='BUY'||g.session!=='NEW_YORK')continue;
  const risk=Math.abs(g.entry-g.stopLoss),reward=Math.abs(g.tp1-g.entry),flipped={...g,direction:'SELL',stopLoss:g.entry+risk,tp1:g.entry-reward};
  const r=flipR(flipped);if(Number.isFinite(r))rows.push({r,entryIndex:g.entryIndex,entryTime:g.entryTime});
}
const minIndex=Math.min(...rows.map(x=>x.entryIndex)),maxIndex=Math.max(...rows.map(x=>x.entryIndex)),span=Math.max(1,maxIndex-minIndex+1);
function bucketStats(name,lo,hi){const subset=rows.filter(x=>x.entryIndex>=lo&&x.entryIndex<hi);return{name,startIndex:lo,endIndexExclusive:hi,...stats(subset.map(x=>x.r)),entryTimes:subset.map(x=>x.entryTime)};}
const halves=[bucketStats('FIRST_HALF',minIndex,minIndex+Math.ceil(span/2)),bucketStats('SECOND_HALF',minIndex+Math.ceil(span/2),maxIndex+1)];
const quarters=[0,1,2,3].map(q=>bucketStats(`Q${q+1}`,minIndex+Math.floor(span*q/4),q===3?maxIndex+1:minIndex+Math.floor(span*(q+1)/4)));
const positives=quarters.filter(x=>x.positiveN>0).length;
const report={strategy:BASELINE.strategy,mode:'PHASE38_A_NY_TEMPORAL_STABILITY',timeframe:'5min',baselineCommit:BASELINE_COMMIT,generationParity:{stored:stored.length,generated:generated.length,exact},scope:{archetype:'LOSS_A_NO_PRE_FAVORABLE',direction:'Original BUY flipped to SELL',session:'NEW_YORK',counterfactual:true},overall:stats(rows.map(x=>x.r)),coverage:{minEntryIndex:minIndex,maxEntryIndex:maxIndex,rowN:rows.length,positiveQuarterCount:positives},halves,quarters,methodology:{researchOnly:true,noOptimization:true,noTradingRules:true,temporalPolicy:'Fixed chronological halves and quarters over the full canonical entry-index span; bins are defined before inspecting outcomes.',purpose:'Audit whether the Phase37 A/New York counterfactual edge persists across time rather than being concentrated in one temporal segment.'},status:'COUNTERFACTUAL_ONLY_TEMPORAL_STABILITY_AUDIT'};
await mkdir(OUT,{recursive:true});await writeFile(resolve(OUT,'5min.json'),JSON.stringify(report,null,2));
console.log(`PHASE38_A_NY_TEMPORAL_STABILITY GENERATION_STORED=${stored.length} GENERATED=${generated.length} EXACT=${exact}`);
console.log(`A_NY N=${report.overall.n} WR=${(report.overall.WR*100).toFixed(2)}% avgR=${report.overall.avgR.toFixed(6)} PF=${report.overall.PF.toFixed(6)} totalR=${report.overall.totalR.toFixed(6)}`);
for(const x of [...halves,...quarters])console.log(`${x.name} N=${x.n} WR=${x.WR==null?'undefined':(x.WR*100).toFixed(2)+'%'} avgR=${x.avgR==null?'undefined':x.avgR.toFixed(6)} PF=${x.PF==null?'undefined':x.PF.toFixed(6)} totalR=${x.totalR.toFixed(6)} POS=${x.positiveN} NEG=${x.negativeN}`);
console.log(`REPORT=${resolve(OUT,'5min.json')}`);console.log('STATUS=COUNTERFACTUAL_ONLY_TEMPORAL_STABILITY_AUDIT');