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
const OUT=resolve(ROOT,'data/reports/strategy-a-phase36-buy-origin-new-york-archetype-decomposition');
const EPS=1e-9,D='LOSS_D_PRE_GE_2R';
const CTX={emaPeriod:60,roundStep:50,roundDistance:5,tradingSessions:[{name:'LONDON',startMinutes:420,endMinutes:960},{name:'NEW_YORK',startMinutes:780,endMinutes:1320}],avoidWindows:[]};
const phase24Cases=[...(PH24.cases??[])],byTime=new Map(phase24Cases.map(x=>[x.entryTime,x]));
function same(a,b){return Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=EPS;}
function flipR(c){const risk=Math.abs(c.entry-c.stopLoss);for(let i=c.entryIndex+1;i<candles.length;i++){const x=candles[i],sl=x.high>=c.stopLoss,tp=x.low<=c.tp1;if(sl&&tp)return null;if(sl)return-1;if(tp)return Math.abs(c.tp1-c.entry)/risk;}return null;}
function stats(a){const v=a.filter(x=>Number.isFinite(x.r)),w=v.filter(x=>x.r>0),l=v.filter(x=>x.r<=0),gw=w.reduce((s,x)=>s+x.r,0),gl=Math.abs(l.reduce((s,x)=>s+x.r,0));return{n:v.length,WR:v.length?w.length/v.length:null,avgR:v.length?v.reduce((s,x)=>s+x.r,0)/v.length:null,PF:gl?gw/gl:null,totalR:v.reduce((s,x)=>s+x.r,0)};}
function session(ts){const d=new Date(ts),m=d.getUTCHours()*60+d.getUTCMinutes();if(m>=420&&m<960)return'LONDON';if(m>=780&&m<1320)return'NEW_YORK';return'OUT_OF_SESSION';}
const generated=[];
for(let index=0;index<candles.length;index++){const visible=candles.slice(0,index+1);if(visible.length<60)continue;const bo=detectBreakout(visible,5);if(!bo.length)continue;const ft=detectFollowThrough(visible,bo,{maxBarsAfterBreakout:2,requireCloseBeyondBrokenLevel:true});if(!ft.length)continue;const spikes=detectSpikeCandidates(visible,bo,ft,{maxCandles:8,minDirectionalFraction:.5,maxOverlapFraction:.8});for(const spike of spikes.candidates.filter(s=>s.endIndex<index)){const correction=detectFirstCorrection(visible,spike);if(!correction||correction.correctionExtremeIndex>=index)continue;const trigger=detectEntryTrigger(visible,correction);if(!trigger||trigger.index!==index)continue;const projection=projectLeg2(visible,correction),invalidation=getInvalidationRule(correction),ema=buildEMAContext(visible.map(c=>c.close),CTX);if(!projection||!ema)continue;const location=buildLocationContext(trigger.entryPrice,CTX),sess=buildSessionContext(trigger.timestamp,CTX),quality=scoreSetup(spike,{ema,location,session:sess});if(!quality.tradeAllowed)continue;const risk=Math.abs(trigger.entryPrice-invalidation.invalidationLevel),reward=Math.abs(projection.tp1-trigger.entryPrice);if(risk<=0||reward<=0)continue;if(!(trigger.direction==='BUY'?projection.tp1>trigger.entryPrice:projection.tp1<trigger.entryPrice))continue;generated.push({entryIndex:index,entryTime:trigger.timestamp,direction:trigger.direction,entry:trigger.entryPrice,stopLoss:invalidation.invalidationLevel,tp1:projection.tp1,session:sess.session});break;}}
const stored=BASELINE.trades??[],rows=[];let exact=0,mapped=0;
for(const t of stored){const g=generated.find(x=>x.entryTime===t.entryTime);if(!g||g.entryIndex!==t.entryIndex||g.direction!==t.direction||!same(g.entry,t.entry)||!same(g.stopLoss,t.stopLoss)||!same(g.tp1,t.tp1))throw new Error(`Generation parity failed at ${t.entryTime}`);exact++;const p=byTime.get(t.entryTime);if(!p||p.archetype===D||g.direction!=='BUY'||g.session!=='NEW_YORK')continue;mapped++;const risk=Math.abs(g.entry-g.stopLoss),reward=Math.abs(g.tp1-g.entry),flipped={...g,direction:'SELL',stopLoss:g.entry+risk,tp1:g.entry-reward};rows.push({r:flipR(flipped),archetype:p.archetype,spikeSizeR:p.features?.spikeSizeR,correctionEfficiency:p.features?.correctionEfficiency,entryTime:g.entryTime});}
function group(name,fn){return{name,...stats(rows.filter(fn))};}
const archetypes=['LOSS_A_NO_PRE_FAVORABLE','LOSS_B_PRE_0_5_TO_LT_1R','LOSS_C_PRE_1_TO_LT_2R'];
const spikeThreshold=PH27.interactionConditioning?.[0]?.thresholds?.spikeSizeR ?? 16.304685569162483;
const corrEffThreshold=PH27.interactionConditioning?.[1]?.thresholds?.correctionEfficiency ?? 0.8320235324313076;
const report={strategy:BASELINE.strategy,mode:'PHASE36_BUY_ORIGIN_NEW_YORK_ARCHETYPE_DECOMPOSITION',timeframe:'5min',baselineCommit:BASELINE_COMMIT,generationParity:{stored:stored.length,generated:generated.length,exact},mapping:{mappedBuyNonDNewYork:mapped,sourcePhase24Cases:phase24Cases.length},overall:stats(rows),archetypes:archetypes.map(a=>group(a,x=>x.archetype===a)),cross:[...archetypes.map(a=>group(`${a}_SPIKE_HIGH`,x=>x.archetype===a&&x.spikeSizeR>=spikeThreshold)),...archetypes.map(a=>group(`${a}_CORR_EFF_HIGH`,x=>x.archetype===a&&x.correctionEfficiency>=corrEffThreshold))],methodology:{researchOnly:true,noOptimization:true,noTradingRules:true,archetypeSource:'Phase24 post-entry loss archetype attribution; used descriptively only.',scope:'Original BUY, NON-D, NEW_YORK; counterfactual direction flip with preserved absolute risk/reward.',thresholdPolicy:'Only fixed Phase27 q66 thresholds; no threshold search.',fixedThresholds:{spikeSizeR:spikeThreshold,correctionEfficiency:corrEffThreshold}},status:'COUNTERFACTUAL_ONLY_DECOMPOSITION'};
await mkdir(OUT,{recursive:true});await writeFile(resolve(OUT,'5min.json'),JSON.stringify(report,null,2));
console.log(`PHASE36_BUY_ORIGIN_NEW_YORK_ARCHETYPE_DECOMPOSITION GENERATION_STORED=${stored.length} GENERATED=${generated.length} EXACT=${exact} MAPPED=${mapped}`);
console.log(`ALL N=${report.overall.n} WR=${(report.overall.WR*100).toFixed(2)}% avgR=${report.overall.avgR.toFixed(6)} PF=${report.overall.PF.toFixed(6)} totalR=${report.overall.totalR.toFixed(6)}`);
for(const x of [...report.archetypes,...report.cross])console.log(`${x.name} N=${x.n} WR=${x.WR==null?'undefined':(x.WR*100).toFixed(2)+'%'} avgR=${x.avgR?.toFixed(6)} PF=${x.PF?.toFixed(6)} totalR=${x.totalR.toFixed(6)}`);
console.log(`REPORT=${resolve(OUT,'5min.json')}`);console.log('STATUS=COUNTERFACTUAL_ONLY_DECOMPOSITION');