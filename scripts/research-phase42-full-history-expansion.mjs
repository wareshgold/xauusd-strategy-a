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
const G50=resolve(ROOT,'data/acquired/g50');
const OUT=resolve(ROOT,'data/reports/strategy-a-phase42-full-history-expansion');
const CTX={emaPeriod:60,roundStep:50,roundDistance:5,tradingSessions:[{name:'LONDON',startMinutes:420,endMinutes:960},{name:'NEW_YORK',startMinutes:780,endMinutes:1320}],avoidWindows:[]};
const CFG={breakoutLookback:5,followThrough:{maxBarsAfterBreakout:2,requireCloseBeyondBrokenLevel:true},spike:{maxCandles:8,minDirectionalFraction:.5,maxOverlapFraction:.8}};

async function readSplit(split){const out=[];for(let i=0;i<100;i++){const p=resolve(G50,split,`chunk-${String(i).padStart(4,'0')}`,'normalized/candles.json');try{out.push(...JSON.parse(await readFile(p,'utf8')))}catch(e){if(e.code==='ENOENT')break;throw e}}return [...new Map(out.map(x=>[x.datetime,x])).values()].sort((a,b)=>Date.parse(a.datetime)-Date.parse(b.datetime));}
function aggregateM5(m1){const buckets=new Map();for(const c of m1){const t=Date.parse(c.datetime),k=Math.floor(t/300000)*300000;const b=buckets.get(k)||[];b.push(c);buckets.set(k,b)}const out=[];for(const [k,b] of [...buckets.entries()].sort((a,b)=>a[0]-b[0])){if(b.length!==5)continue;const ts=b.map(x=>Date.parse(x.datetime)).sort((a,b)=>a-b);if(ts.some((t,i)=>t!==k+i*60000))continue;const q=[...b].sort((a,b)=>Date.parse(a.datetime)-Date.parse(b.datetime));out.push({timestamp:new Date(k).toISOString(),open:q[0].open,high:Math.max(...q.map(x=>x.high)),low:Math.min(...q.map(x=>x.low)),close:q[4].close})}return out;}
function generate(candles){const out=[];for(let i=0;i<candles.length;i++){const visible=candles.slice(0,i+1);if(visible.length<60)continue;const bo=detectBreakout(visible,CFG.breakoutLookback);if(!bo.length)continue;const ft=detectFollowThrough(visible,bo,CFG.followThrough);if(!ft.length)continue;const sp=detectSpikeCandidates(visible,bo,ft,CFG.spike);for(const s of sp.candidates.filter(x=>x.endIndex<i)){const co=detectFirstCorrection(visible,s);if(!co||co.correctionExtremeIndex>=i)continue;const tr=detectEntryTrigger(visible,co);if(!tr||tr.index!==i)continue;const projection=projectLeg2(visible,co),invalidation=getInvalidationRule(co),ema=buildEMAContext(visible.map(x=>x.close),CTX);if(!projection||!ema)continue;const location=buildLocationContext(tr.entryPrice,CTX),session=buildSessionContext(tr.timestamp,CTX),quality=scoreSetup(s,{ema,location,session});if(!quality.tradeAllowed)continue;const risk=Math.abs(tr.entryPrice-invalidation.invalidationLevel);if(risk<=0)continue;const reward=Math.abs(projection.tp1-tr.entryPrice);if(reward<=0||!(tr.direction==='BUY'?projection.tp1>tr.entryPrice:projection.tp1<tr.entryPrice))continue;out.push({entryIndex:i,entryTime:tr.timestamp,direction:tr.direction,entry:tr.entryPrice,stopLoss:invalidation.invalidationLevel,tp1:projection.tp1,session:session.session});break}}return out;}
function scan(candles,i,entry,sl,tp,direction){const risk=Math.abs(entry-sl);if(!(risk>0))return null;for(let j=i+1;j<candles.length;j++){const c=candles[j],hitSL=direction==='BUY'?c.low<=sl:c.high>=sl,hitTP=direction==='BUY'?c.high>=tp:c.low<=tp;if(hitSL&&hitTP)return {reason:'AMBIGUOUS',index:j};if(hitSL)return {reason:'SL',index:j};if(hitTP)return {reason:'TP1',index:j}}return null;}
function preMFE(candles,i,exit,entry,risk,direction){let mfe=0;for(let j=i+1;j<=exit;j++){const c=candles[j],v=direction==='BUY'?(c.high-entry)/risk:(entry-c.low)/risk;mfe=Math.max(mfe,v)}return mfe;}
function archetype(mfe){if(mfe<.5)return'LOSS_A_NO_PRE_FAVORABLE';if(mfe<1)return'LOSS_B_PRE_0_5_TO_LT_1R';if(mfe<2)return'LOSS_C_PRE_1_TO_LT_2R';return'LOSS_D_PRE_GE_2R';}
function stats(v){const x=v.filter(Number.isFinite),w=x.filter(r=>r>0),l=x.filter(r=>r<=0),gw=w.reduce((s,r)=>s+r,0),gl=Math.abs(l.reduce((s,r)=>s+r,0)),z=[...x].sort((a,b)=>a-b);return{n:x.length,WR:x.length?w.length/x.length:null,avgR:x.length?x.reduce((s,r)=>s+r,0)/x.length:null,medianR:x.length?(z.length%2?z[(z.length-1)/2]:(z[z.length/2-1]+z[z.length/2])/2):null,PF:gl?gw/gl:null,totalR:x.reduce((s,r)=>s+r,0),positiveN:w.length,negativeN:l.length};}

const devM1=await readSplit('DEV_01'),valM1=await readSplit('VAL_01');
const allM1=[...devM1,...valM1].sort((a,b)=>Date.parse(a.datetime)-Date.parse(b.datetime));
const candles=[...new Map(allM1.map(x=>[x.datetime,x])).values()];
const m5=aggregateM5(candles);
const generated=generate(m5);
const rows=[];const mismatches=[];
for(const g of generated){
  if(g.direction!=='BUY'||g.session!=='NEW_YORK')continue;
  const ex=scan(m5,g.entryIndex,g.entry,g.stopLoss,g.tp1,g.direction);
  if(!ex||ex.reason!=='SL')continue;
  const risk=Math.abs(g.entry-g.stopLoss),mfe=preMFE(m5,g.entryIndex,ex.index,g.entry,risk,g.direction),arc=archetype(mfe);
  if(arc!=='LOSS_A_NO_PRE_FAVORABLE')continue;
  const flip={entryIndex:g.entryIndex,entry:g.entry,stopLoss:g.entry+risk,tp1:g.entry-(Math.abs(g.tp1-g.entry))};
  const fx=scan(m5,flip.entryIndex,flip.entry,flip.stopLoss,flip.tp1,'SELL');
  if(!fx||fx.reason==='AMBIGUOUS')continue;
  const r=fx.reason==='TP1'?Math.abs(flip.tp1-flip.entry)/risk:-1;
  rows.push({...g,originalExitIndex:ex.index,preEntryMFE:mfe,archetype:arc,counterfactualDirection:'SELL',counterfactualExitReason:fx.reason,r});
}
const bySplit={DEV:rows.filter(x=>x.entryTime<'2026-07-01T00:00:00.000Z'),VAL:rows.filter(x=>x.entryTime>='2026-07-01T00:00:00.000Z')};
const result={strategy:'Strategy A / SP2L',mode:'PHASE42_FULL_HISTORY_EXPANSION',timeframe:'5min',hypothesis:{archetype:'LOSS_A_NO_PRE_FAVORABLE',originalDirection:'BUY',session:'NEW_YORK',counterfactualDirection:'SELL',ruleChanged:false},data:{provider:'Twelve Data',source:'G50',DEV_01:{m1Rows:devM1.length,m5Rows:aggregateM5(devM1).length,first:devM1[0]?.datetime,last:devM1.at(-1)?.datetime},VAL_01:{m1Rows:valM1.length,m5Rows:aggregateM5(valM1).length,first:valM1[0]?.datetime,last:valM1.at(-1)?.datetime},combinedM1Rows:candles.length,combinedM5Rows:m5.length},selection:{generatedCandidates:generated.length,eligibleBuyNewYork:generated.filter(x=>x.direction==='BUY'&&x.session==='NEW_YORK').length,originalLossA:rows.length},results:{ALL:stats(rows.map(x=>x.r)),DEV:stats(bySplit.DEV.map(x=>x.r)),VAL:stats(bySplit.VAL.map(x=>x.r))},observations:rows,methodology:{researchOnly:true,noOptimization:true,noNewThresholds:true,noTradingRuleChange:true,exactSameGeneratorAsPhase40:true,archetypeDerivedFromOriginalTradePath:true,pendingLimitGeometryUnchanged:true,purpose:'Expand the fixed A/New York counterfactual hypothesis onto the full G50 history. The archetype is derived deterministically from each original BUY trade path; no Phase24 case list is reused as a selection filter.'},status:'COUNTERFACTUAL_ONLY_FULL_HISTORY_EXPANSION'};
await mkdir(OUT,{recursive:true});await writeFile(resolve(OUT,'5min.json'),JSON.stringify(result,null,2));
const s=result.results.ALL;console.log(`PHASE42_FULL_HISTORY_EXPANSION M1=${candles.length} M5=${m5.length} GENERATED=${generated.length} A_NY=${rows.length}`);console.log(`ALL N=${s.n} WR=${(s.WR*100).toFixed(2)}% avgR=${s.avgR?.toFixed(6)} medianR=${s.medianR?.toFixed(6)} PF=${s.PF?.toFixed(6)} totalR=${s.totalR.toFixed(6)}`);console.log(`DEV N=${result.results.DEV.n} VAL N=${result.results.VAL.n}`);console.log(`REPORT=${resolve(OUT,'5min.json')}`);console.log('STATUS=COUNTERFACTUAL_ONLY_FULL_HISTORY_EXPANSION');
