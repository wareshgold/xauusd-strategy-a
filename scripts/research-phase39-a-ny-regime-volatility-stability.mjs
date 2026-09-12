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
const OUT=resolve(ROOT,'data/reports/strategy-a-phase39-a-ny-regime-volatility-stability');
const EPS=1e-9;
const CTX={emaPeriod:60,roundStep:50,roundDistance:5,tradingSessions:[{name:'LONDON',startMinutes:420,endMinutes:960},{name:'NEW_YORK',startMinutes:780,endMinutes:1320}],avoidWindows:[]};
const byTime=new Map((PH24.cases??[]).map(x=>[x.entryTime,x]));
function same(a,b){return Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=EPS;}
function flipR(c){const risk=Math.abs(c.entry-c.stopLoss);for(let i=c.entryIndex+1;i<candles.length;i++){const x=candles[i],sl=x.high>=c.stopLoss,tp=x.low<=c.tp1;if(sl&&tp)return null;if(sl)return-1;if(tp)return Math.abs(c.tp1-c.entry)/risk;}return null;}
function stats(values){const v=values.filter(Number.isFinite),w=v.filter(x=>x>0),l=v.filter(x=>x<=0),gw=w.reduce((s,x)=>s+x,0),gl=Math.abs(l.reduce((s,x)=>s+x,0));return{n:v.length,WR:v.length?w.length/v.length:null,avgR:v.length?v.reduce((s,x)=>s+x,0)/v.length:null,PF:gl?gw/gl:null,totalR:v.reduce((s,x)=>s+x,0),positiveN:w.length,negativeN:l.length};}
function mean(v){return v.length?v.reduce((s,x)=>s+x,0)/v.length:null;}
function percentile(v,p){const a=[...v].sort((x,y)=>x-y);if(!a.length)return null;const i=(a.length-1)*p,k=Math.floor(i),f=i-k;return a[k+1]===undefined?a[k]:a[k]+(a[k+1]-a[k])*f;}
function atrAt(index,period=20){if(index<period)return null;let tr=0;for(let i=index-period+1;i<=index;i++){const c=candles[i],prev=candles[i-1];tr+=Math.max(c.high-c.low,Math.abs(c.high-prev.close),Math.abs(c.low-prev.close));}return tr/period;}
function realizedRange(index,period=20){if(index<period)return null;let hi=-Infinity,lo=Infinity;for(let i=index-period+1;i<=index;i++){hi=Math.max(hi,candles[i].high);lo=Math.min(lo,candles[i].low);}return hi-lo;}
function candleBody(index){const c=candles[index];return Math.abs(c.close-c.open);}
function regime(row){return {atr20:row.atr20,range20:row.range20,body20:row.body20};}
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
    generated.push({entryIndex:index,entryTime:trigger.timestamp,direction:trigger.direction,entry:trigger.entryPrice,stopLoss:invalidation.invalidationLevel,tp1:projection.tp1,session:sess.session,atr20:atrAt(index),range20:realizedRange(index),body20:mean(Array.from({length:20},(_,k)=>candleBody(index-k)))});break;
  }
}
const stored=BASELINE.trades??[],rows=[];let exact=0;
for(const t of stored){
  const g=generated.find(x=>x.entryTime===t.entryTime);if(!g||g.entryIndex!==t.entryIndex||g.direction!==t.direction||!same(g.entry,t.entry)||!same(g.stopLoss,t.stopLoss)||!same(g.tp1,t.tp1))throw new Error(`Generation parity failed at ${t.entryTime}`);exact++;
  const p=byTime.get(t.entryTime);if(!p||p.archetype!=='LOSS_A_NO_PRE_FAVORABLE'||g.direction!=='BUY'||g.session!=='NEW_YORK')continue;
  const risk=Math.abs(g.entry-g.stopLoss),reward=Math.abs(g.tp1-g.entry);const flipped={...g,direction:'SELL',stopLoss:g.entry+risk,tp1:g.entry-reward};const r=flipR(flipped);if(Number.isFinite(r))rows.push({...g,r});
}
const finite=v=>v.filter(Number.isFinite);
const overall=stats(rows.map(x=>x.r));
const metrics=['atr20','range20','body20'];
const cuts={};
for(const m of metrics){const values=finite(rows.map(x=>x[m]));cuts[m]={q33:percentile(values,1/3),q50:percentile(values,.5),q67:percentile(values,2/3),mean:mean(values)};}
function bucketStats(name,subset){return{name,...stats(subset.map(x=>x.r)),regime:{n:subset.length,atr20Mean:mean(finite(subset.map(x=>x.atr20))),range20Mean:mean(finite(subset.map(x=>x.range20))),body20Mean:mean(finite(subset.map(x=>x.body20)))}};}
const regimes=[];
for(const m of metrics){for(const [label,q] of [['LOW',cuts[m].q33],['MID',cuts[m].q67]]){const subset=m==='atr20'?(label==='LOW'?rows.filter(x=>x.atr20<cuts[m].q33):rows.filter(x=>x.atr20>=cuts[m].q33&&x.atr20<cuts[m].q67)):(m==='range20'?(label==='LOW'?rows.filter(x=>x.range20<cuts[m].q33):rows.filter(x=>x.range20>=cuts[m].q33&&x.range20<cuts[m].q67)):(label==='LOW'?rows.filter(x=>x.body20<cuts[m].q33):rows.filter(x=>x.body20>=cuts[m].q33&&x.body20<cuts[m].q67)));regimes.push(bucketStats(`${m}_${label}`,subset));}regimes.push(bucketStats(`${m}_HIGH`,m==='atr20'?rows.filter(x=>x.atr20>=cuts[m].q67):m==='range20'?rows.filter(x=>x.range20>=cuts[m].q67):rows.filter(x=>x.body20>=cuts[m].q67)));}
const quartileTimes=[];const sorted=[...rows].sort((a,b)=>a.entryIndex-b.entryIndex);const span=Math.max(1,sorted.at(-1).entryIndex-sorted[0].entryIndex+1);for(let q=0;q<4;q++){const lo=sorted[0].entryIndex+Math.floor(span*q/4),hi=q===3?sorted.at(-1).entryIndex+1:sorted[0].entryIndex+Math.floor(span*(q+1)/4);quartileTimes.push(bucketStats(`TIME_Q${q+1}`,rows.filter(x=>x.entryIndex>=lo&&x.entryIndex<hi)));}
const report={strategy:BASELINE.strategy,mode:'PHASE39_A_NY_REGIME_VOLATILITY_STABILITY',timeframe:'5min',baselineCommit:BASELINE_COMMIT,generationParity:{stored:stored.length,generated:generated.length,exact},scope:{archetype:'LOSS_A_NO_PRE_FAVORABLE',direction:'Original BUY flipped to SELL',session:'NEW_YORK',counterfactual:true},overall,regimeDefinitions:{atr20:'20-candle average true range at entry',range20:'20-candle high-low realized range at entry',body20:'20-candle mean absolute candle body at entry',cutPolicy:'Fixed descriptive tertiles computed within the A/NY sample; no outcome-based threshold optimization.'},cuts,regimes,timeQuartiles:quartileTimes,methodology:{researchOnly:true,noOptimization:true,noTradingRules:true,purpose:'Audit whether the Phase38 temporal concentration is associated with contemporaneous volatility/range/body regime rather than arbitrary calendar timing.'},status:'COUNTERFACTUAL_ONLY_REGIME_VOLATILITY_AUDIT'};
await mkdir(OUT,{recursive:true});await writeFile(resolve(OUT,'5min.json'),JSON.stringify(report,null,2));
console.log(`PHASE39_A_NY_REGIME_VOLATILITY_STABILITY GENERATION_STORED=${stored.length} GENERATED=${generated.length} EXACT=${exact}`);
console.log(`A_NY N=${overall.n} WR=${(overall.WR*100).toFixed(2)}% avgR=${overall.avgR.toFixed(6)} PF=${overall.PF.toFixed(6)} totalR=${overall.totalR.toFixed(6)}`);
for(const x of regimes)console.log(`${x.name} N=${x.n} WR=${x.WR==null?'undefined':(x.WR*100).toFixed(2)+'%'} avgR=${x.avgR==null?'undefined':x.avgR.toFixed(6)} PF=${x.PF==null?'undefined':x.PF.toFixed(6)} totalR=${x.totalR.toFixed(6)}`);
for(const x of quartileTimes)console.log(`${x.name} N=${x.n} WR=${x.WR==null?'undefined':(x.WR*100).toFixed(2)+'%'} avgR=${x.avgR==null?'undefined':x.avgR.toFixed(6)} PF=${x.PF==null?'undefined':x.PF.toFixed(6)} totalR=${x.totalR.toFixed(6)}`);
console.log(`REPORT=${resolve(OUT,'5min.json')}`);console.log('STATUS=COUNTERFACTUAL_ONLY_REGIME_VOLATILITY_AUDIT');
