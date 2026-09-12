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
const PH27=JSON.parse(await readFile(resolve(ROOT,'data/reports/strategy-a-phase27-d-archetype-conditional-residual-decomposition/5min.json'),'utf8'));
const candles=JSON.parse(execFileSync('git',['show',`${BASELINE_COMMIT}:data/historical/xauusd-5min.json`],{cwd:ROOT,encoding:'utf8',maxBuffer:64*1024*1024})).candles;
const OUT=resolve(ROOT,'data/reports/strategy-a-phase33-counterfactual-phase27-archetype-decomposition');
const EPS=1e-9;
const CTX={emaPeriod:60,roundStep:50,roundDistance:5,tradingSessions:[{name:'LONDON',startMinutes:420,endMinutes:960},{name:'NEW_YORK',startMinutes:780,endMinutes:1320}],avoidWindows:[]};
const D='LOSS_D_PRE_GE_2R';
const phase24Cases=[...(PH24.cases??[])];
const byTime=new Map(phase24Cases.map(x=>[x.entryTime,x]));
const phase27Scope=PH27.scope??{};
function same(a,b){return Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=EPS;}
function evalFlip(c){const risk=Math.abs(c.entry-c.stopLoss);for(let i=c.entryIndex+1;i<candles.length;i++){const x=candles[i];const sl=c.direction==='BUY'?x.low<=c.stopLoss:x.high>=c.stopLoss;const tp=c.direction==='BUY'?x.high>=c.tp1:x.low<=c.tp1;if(sl&&tp)return null;if(sl)return -1;if(tp)return Math.abs(c.tp1-c.entry)/risk;}return null;}
function stats(rows){const v=rows.filter(x=>Number.isFinite(x.r));const w=v.filter(x=>x.r>0),l=v.filter(x=>x.r<=0);const gw=w.reduce((s,x)=>s+x.r,0),gl=Math.abs(l.reduce((s,x)=>s+x.r,0));return {n:v.length,winRate:v.length?w.length/v.length:null,avgR:v.length?v.reduce((s,x)=>s+x.r,0)/v.length:null,totalR:v.reduce((s,x)=>s+x.r,0),profitFactor:gl?gw/gl:null};}
const generated=[];
for(let index=0;index<candles.length;index++){
 const visible=candles.slice(0,index+1); if(visible.length<60)continue;
 const bo=detectBreakout(visible,5); if(!bo.length)continue;
 const ft=detectFollowThrough(visible,bo,{maxBarsAfterBreakout:2,requireCloseBeyondBrokenLevel:true}); if(!ft.length)continue;
 const spikes=detectSpikeCandidates(visible,bo,ft,{maxCandles:8,minDirectionalFraction:.5,maxOverlapFraction:.8});
 for(const spike of spikes.candidates.filter(s=>s.endIndex<index)){
  const correction=detectFirstCorrection(visible,spike); if(!correction||correction.correctionExtremeIndex>=index)continue;
  const trigger=detectEntryTrigger(visible,correction); if(!trigger||trigger.index!==index)continue;
  const projection=projectLeg2(visible,correction); if(!projection)continue;
  const invalidation=getInvalidationRule(correction),ema=buildEMAContext(visible.map(c=>c.close),CTX); if(!ema)continue;
  const location=buildLocationContext(trigger.entryPrice,CTX),session=buildSessionContext(trigger.timestamp,CTX),quality=scoreSetup(spike,{ema,location,session}); if(!quality.tradeAllowed)continue;
  const risk=Math.abs(trigger.entryPrice-invalidation.invalidationLevel),reward=Math.abs(projection.tp1-trigger.entryPrice); if(risk<=0||reward<=0)continue;
  const directional=trigger.direction==='BUY'?projection.tp1>trigger.entryPrice:projection.tp1<trigger.entryPrice;if(!directional)continue;
  generated.push({entryIndex:index,entryTime:trigger.timestamp,direction:trigger.direction,entry:trigger.entryPrice,stopLoss:invalidation.invalidationLevel,tp1:projection.tp1,session:session.session,qualityGrade:quality.grade}); break;
 }
}
const stored=BASELINE.trades??[];const rows=[];let exact=0;let mapped=0;
for(const t of stored){const g=generated.find(x=>x.entryTime===t.entryTime);if(!g||g.entryIndex!==t.entryIndex||g.direction!==t.direction||!same(g.entry,t.entry)||!same(g.stopLoss,t.stopLoss)||!same(g.tp1,t.tp1))throw new Error(`Generation parity failed at ${t.entryTime}`);exact++;const p=byTime.get(t.entryTime);if(!p)continue;mapped++;const spikeSizeR=p.features?.spikeSizeR,correctionEfficiency=p.features?.correctionEfficiency;if(!Number.isFinite(spikeSizeR)||!Number.isFinite(correctionEfficiency))throw new Error(`Phase24 feature missing at ${t.entryTime}`);const risk=Math.abs(g.entry-g.stopLoss),reward=Math.abs(g.tp1-g.entry);const flipped={...g,direction:g.direction==='BUY'?'SELL':'BUY',stopLoss:g.entry+(g.direction==='BUY'?risk:-risk),tp1:g.entry+(g.direction==='BUY'?-reward:reward)};rows.push({r:evalFlip(flipped),originalDirection:g.direction,archetype:p.archetype,spikeSizeR,correctionEfficiency,spikeHigh:spikeSizeR>=PH27.interactionConditioning[0].thresholds.spikeSizeR,correctionEffHigh:correctionEfficiency>=PH27.interactionConditioning[1].thresholds.correctionEfficiency,entryTime:g.entryTime});}
function group(name,fn){const a=rows.filter(fn);return {name,...stats(a),buyOrigin:stats(a.filter(x=>x.originalDirection==='BUY')),sellOrigin:stats(a.filter(x=>x.originalDirection==='SELL'))};}
const qSpike=PH27.interactionConditioning[0].thresholds.spikeSizeR,qCorr=PH27.interactionConditioning[1].thresholds.correctionEfficiency;
const report={strategy:BASELINE.strategy,mode:'PHASE33_COUNTERFACTUAL_PHASE27_ARCHETYPE_DECOMPOSITION',timeframe:'5min',baselineCommit:BASELINE_COMMIT,generationParity:{stored:stored.length,generated:generated.length,exact},phase27Mapping:{mapped,unmapped:stored.length-mapped,sourceCases:phase24Cases.length,dCases:Number(phase27Scope.dCases),nonDCases:Number(phase27Scope.nonDCases),spikeQ66:qSpike,correctionEfficiencyQ66:qCorr},overall:stats(rows),byArchetype:[group('D',x=>x.archetype===D),group('NON_D',x=>x.archetype!==D)],byOriginAndArchetype:[group('BUY_ORIGIN_D',x=>x.originalDirection==='BUY'&&x.archetype===D),group('BUY_ORIGIN_NON_D',x=>x.originalDirection==='BUY'&&x.archetype!==D),group('SELL_ORIGIN_D',x=>x.originalDirection==='SELL'&&x.archetype===D),group('SELL_ORIGIN_NON_D',x=>x.originalDirection==='SELL'&&x.archetype!==D)],geometry:[group('D_SPIKE_HIGH',x=>x.archetype===D&&x.spikeHigh),group('D_CORR_EFF_HIGH',x=>x.archetype===D&&x.correctionEffHigh),group('D_SPIKE_HIGH_CORR_EFF_HIGH',x=>x.archetype===D&&x.spikeHigh&&x.correctionEffHigh),group('NON_D_SPIKE_HIGH_CORR_EFF_HIGH',x=>x.archetype!==D&&x.spikeHigh&&x.correctionEffHigh)],methodology:{researchOnly:true,noOptimization:true,noTradingRules:true,archetypeSource:'Phase24 case population used by Phase27; Phase27 publishes aggregate scope/thresholds but not raw cases. Archetype and pre-entry geometry features are taken from the same Phase24 case keyed by canonical entryTime.',directionSource:'Baseline candidate generation; direction is counterfactually mirrored with preserved absolute risk/reward.',note:'Only baseline trades present in the Phase24/Phase27 canonical case population can be mapped; unmapped baseline trades remain excluded from archetype-conditioned groups.'},status:'COUNTERFACTUAL_ONLY_DECOMPOSITION'};
await mkdir(OUT,{recursive:true});await writeFile(resolve(OUT,'5min.json'),JSON.stringify(report,null,2));
console.log(`PHASE33_COUNTERFACTUAL_PHASE27_ARCHETYPE_DECOMPOSITION GENERATION_STORED=${stored.length} GENERATED=${generated.length} EXACT=${exact} MAPPED=${mapped} UNMAPPED=${stored.length-mapped}`);
for(const x of report.byArchetype)console.log(`${x.name} N=${x.n} WR=${x.winRate==null?'undefined':(x.winRate*100).toFixed(2)+'%'} avgR=${x.avgR?.toFixed(6)} PF=${x.profitFactor?.toFixed(6)} totalR=${x.totalR.toFixed(6)}`);
for(const x of report.byOriginAndArchetype)console.log(`${x.name} N=${x.n} WR=${x.winRate==null?'undefined':(x.winRate*100).toFixed(2)+'%'} avgR=${x.avgR?.toFixed(6)} PF=${x.profitFactor?.toFixed(6)} totalR=${x.totalR.toFixed(6)}`);
for(const x of report.geometry)console.log(`${x.name} N=${x.n} WR=${x.winRate==null?'undefined':(x.winRate*100).toFixed(2)+'%'} avgR=${x.avgR?.toFixed(6)} PF=${x.profitFactor?.toFixed(6)} totalR=${x.totalR.toFixed(6)}`);
console.log(`REPORT=${resolve(OUT,'5min.json')}`);console.log('STATUS=COUNTERFACTUAL_ONLY_DECOMPOSITION');
