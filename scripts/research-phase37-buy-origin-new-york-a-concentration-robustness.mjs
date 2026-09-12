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
const OUT=resolve(ROOT,'data/reports/strategy-a-phase37-buy-origin-new-york-a-concentration-robustness');
const EPS=1e-9,D='LOSS_D_PRE_GE_2R';
const CTX={emaPeriod:60,roundStep:50,roundDistance:5,tradingSessions:[{name:'LONDON',startMinutes:420,endMinutes:960},{name:'NEW_YORK',startMinutes:780,endMinutes:1320}],avoidWindows:[]};
const byTime=new Map((PH24.cases??[]).map(x=>[x.entryTime,x]));
function same(a,b){return Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=EPS;}
function flipR(c){const risk=Math.abs(c.entry-c.stopLoss);for(let i=c.entryIndex+1;i<candles.length;i++){const x=candles[i],sl=x.high>=c.stopLoss,tp=x.low<=c.tp1;if(sl&&tp)return null;if(sl)return-1;if(tp)return Math.abs(c.tp1-c.entry)/risk;}return null;}
function session(ts){const d=new Date(ts),m=d.getUTCHours()*60+d.getUTCMinutes();if(m>=420&&m<960)return'LONDON';if(m>=780&&m<1320)return'NEW_YORK';return'OUT_OF_SESSION';}
function stats(a){const v=a.filter(Number.isFinite),w=v.filter(x=>x>0),l=v.filter(x=>x<=0),gw=w.reduce((s,x)=>s+x,0),gl=Math.abs(l.reduce((s,x)=>s+x,0));return{n:v.length,WR:v.length?w.length/v.length:null,avgR:v.length?v.reduce((s,x)=>s+x,0)/v.length:null,PF:gl?gw/gl:null,totalR:v.reduce((s,x)=>s+x,0)};}
function median(a){const v=[...a].sort((x,y)=>x-y);if(!v.length)return null;const m=Math.floor(v.length/2);return v.length%2?v[m]:(v[m-1]+v[m])/2;}
function concentration(r){const v=r.map(x=>x.r).filter(Number.isFinite).sort((a,b)=>b-a),total=v.reduce((s,x)=>s+x,0);const positive=v.filter(x=>x>0),positiveTotal=positive.reduce((s,x)=>s+x,0);const top=k=>v.slice(0,k).reduce((s,x)=>s+x,0);const trimHigh=k=>stats(v.slice(k));return{n:v.length,totalR:total,medianR:median(v),maxR:v[0]??null,minR:v.at(-1)??null,positiveCount:positive.length,positiveTotalR:positiveTotal,top1R:top(1),top2R:top(2),top3R:top(3),top5R:top(5),top1ShareOfTotal:total?top(1)/total:null,top3ShareOfTotal:total?top(3)/total:null,trimTop1:trimHigh(1),trimTop3:trimHigh(3),trimTop5:trimHigh(5)};}

const generated=[];
for(let index=0;index<candles.length;index++){
  const visible=candles.slice(0,index+1); if(visible.length<60)continue;
  const bo=detectBreakout(visible,5); if(!bo.length)continue;
  const ft=detectFollowThrough(visible,bo,{maxBarsAfterBreakout:2,requireCloseBeyondBrokenLevel:true}); if(!ft.length)continue;
  const spikes=detectSpikeCandidates(visible,bo,ft,{maxCandles:8,minDirectionalFraction:.5,maxOverlapFraction:.8});
  for(const spike of spikes.candidates.filter(s=>s.endIndex<index)){
    const correction=detectFirstCorrection(visible,spike); if(!correction||correction.correctionExtremeIndex>=index)continue;
    const trigger=detectEntryTrigger(visible,correction); if(!trigger||trigger.index!==index)continue;
    const projection=projectLeg2(visible,correction),invalidation=getInvalidationRule(correction),ema=buildEMAContext(visible.map(c=>c.close),CTX); if(!projection||!ema)continue;
    const location=buildLocationContext(trigger.entryPrice,CTX),sess=buildSessionContext(trigger.timestamp,CTX),quality=scoreSetup(spike,{ema,location,session:sess}); if(!quality.tradeAllowed)continue;
    const risk=Math.abs(trigger.entryPrice-invalidation.invalidationLevel),reward=Math.abs(projection.tp1-trigger.entryPrice); if(risk<=0||reward<=0)continue;
    if(!(trigger.direction==='BUY'?projection.tp1>trigger.entryPrice:projection.tp1<trigger.entryPrice))continue;
    generated.push({entryIndex:index,entryTime:trigger.timestamp,direction:trigger.direction,entry:trigger.entryPrice,stopLoss:invalidation.invalidationLevel,tp1:projection.tp1,session:sess.session}); break;
  }
}

const stored=BASELINE.trades??[]; const rows=[]; let exact=0;
for(const t of stored){
  const g=generated.find(x=>x.entryTime===t.entryTime); if(!g||g.entryIndex!==t.entryIndex||g.direction!==t.direction||!same(g.entry,t.entry)||!same(g.stopLoss,t.stopLoss)||!same(g.tp1,t.tp1))throw new Error(`Generation parity failed at ${t.entryTime}`); exact++;
  const p=byTime.get(t.entryTime); if(!p||p.archetype===D||g.direction!=='BUY'||g.session!=='NEW_YORK'||p.archetype!=='LOSS_A_NO_PRE_FAVORABLE')continue;
  const risk=Math.abs(g.entry-g.stopLoss),reward=Math.abs(g.tp1-g.entry),flipped={...g,direction:'SELL',stopLoss:g.entry+risk,tp1:g.entry-reward};
  const r=flipR(flipped); if(Number.isFinite(r))rows.push({r,entryTime:g.entryTime});
}

const report={
  strategy:BASELINE.strategy,
  mode:'PHASE37_BUY_ORIGIN_NEW_YORK_A_CONCENTRATION_ROBUSTNESS',
  timeframe:'5min',baselineCommit:BASELINE_COMMIT,
  generationParity:{stored:stored.length,generated:generated.length,exact},
  scope:{archetype:'LOSS_A_NO_PRE_FAVORABLE',direction:'Original BUY flipped to SELL',session:'NEW_YORK',phase24Source:true},
  stats:stats(rows.map(x=>x.r)),
  concentration:concentration(rows),
  robustness:{
    withoutTop1:stats(rows.slice().sort((a,b)=>b.r-a.r).slice(1).map(x=>x.r)),
    withoutTop3:stats(rows.slice().sort((a,b)=>b.r-a.r).slice(3).map(x=>x.r)),
    withoutTop5:stats(rows.slice().sort((a,b)=>b.r-a.r).slice(5).map(x=>x.r)),
    negativeCount:rows.filter(x=>x.r<=0).length,
    positiveCount:rows.filter(x=>x.r>0).length
  },
  methodology:{researchOnly:true,noOptimization:true,noTradingRules:true,purpose:'Test whether the observed counterfactual A/New York edge is broad or concentrated in a few extreme outcomes.',counterfactualOnly:true,topKPolicy:'Fixed descriptive top-1/top-3/top-5 and trimmed-result audit; no threshold search.'},
  status:'COUNTERFACTUAL_ONLY_ROBUSTNESS_AUDIT'
};
await mkdir(OUT,{recursive:true});await writeFile(resolve(OUT,'5min.json'),JSON.stringify(report,null,2));
console.log(`PHASE37_BUY_ORIGIN_NEW_YORK_A_CONCENTRATION_ROBUSTNESS GENERATION_STORED=${stored.length} GENERATED=${generated.length} EXACT=${exact}`);
console.log(`A_NY N=${report.stats.n} WR=${(report.stats.WR*100).toFixed(2)}% avgR=${report.stats.avgR.toFixed(6)} PF=${report.stats.PF.toFixed(6)} totalR=${report.stats.totalR.toFixed(6)}`);
console.log(`MEDIAN_R=${report.concentration.medianR.toFixed(6)} MAX_R=${report.concentration.maxR.toFixed(6)} MIN_R=${report.concentration.minR.toFixed(6)} POSITIVE_N=${report.concentration.positiveCount}`);
console.log(`TOP1_R=${report.concentration.top1R.toFixed(6)} TOP3_R=${report.concentration.top3R.toFixed(6)} TOP5_R=${report.concentration.top5R.toFixed(6)}`);
console.log(`WITHOUT_TOP1 N=${report.robustness.withoutTop1.n} avgR=${report.robustness.withoutTop1.avgR?.toFixed(6)} PF=${report.robustness.withoutTop1.PF?.toFixed(6)} totalR=${report.robustness.withoutTop1.totalR.toFixed(6)}`);
console.log(`WITHOUT_TOP3 N=${report.robustness.withoutTop3.n} avgR=${report.robustness.withoutTop3.avgR?.toFixed(6)} PF=${report.robustness.withoutTop3.PF?.toFixed(6)} totalR=${report.robustness.withoutTop3.totalR.toFixed(6)}`);
console.log(`WITHOUT_TOP5 N=${report.robustness.withoutTop5.n} avgR=${report.robustness.withoutTop5.avgR?.toFixed(6)} PF=${report.robustness.withoutTop5.PF?.toFixed(6)} totalR=${report.robustness.withoutTop5.totalR.toFixed(6)}`);
console.log(`REPORT=${resolve(OUT,'5min.json')}`); console.log('STATUS=COUNTERFACTUAL_ONLY_ROBUSTNESS_AUDIT');
