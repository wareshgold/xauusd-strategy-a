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
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-stop-first-correction-geometry-fresh-holdout');
const TOTAL = 15000, PRE = 10000, MIN_N = 10;
const BREAKOUT_LOOKBACK = 5, FT_MAX_BARS = 2, SPIKE_MAX_CANDLES = 8, SPIKE_MIN_DIRECTIONAL_FRACTION = .5, SPIKE_MAX_OVERLAP_FRACTION = .8;
const CONTEXT = { emaPeriod:60, roundStep:50, roundDistance:5, tradingSessions:[{name:'LONDON',startMinutes:420,endMinutes:960},{name:'NEW_YORK',startMinutes:780,endMinutes:1320}], avoidWindows:[] };
function key(c){return `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;}
function stats(rs){const a=rs.map(Number).filter(Number.isFinite),w=a.filter(x=>x>0),l=a.filter(x=>x<0),gp=w.reduce((x,y)=>x+y,0),gl=-l.reduce((x,y)=>x+y,0);let eq=0,peak=0,dd=0,streak=0,maxCL=0;for(const r of a){eq+=r;peak=Math.max(peak,eq);dd=Math.max(dd,peak-eq);streak=r<0?streak+1:0;maxCL=Math.max(maxCL,streak);}return{n:a.length,wins:w.length,losses:l.length,winRate:a.length?w.length/a.length:0,avgR:a.length?a.reduce((x,y)=>x+y,0)/a.length:0,totalR:a.reduce((x,y)=>x+y,0),PF:gl?gp/gl:null,maxDD:dd,maxCL};}
function safeRatio(a,b){return Number.isFinite(a)&&Number.isFinite(b)&&b>0?a/b:null;}
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
  const impulse=Math.abs(spike.endPrice-spike.startPrice),correctionDepth=Math.abs(correction.extremePrice-spike.startPrice),correctionLeg=Math.abs(correction.extremePrice-spike.endPrice);
  candidates.push({entryIndex:index,entryTime:trigger.timestamp,direction:trigger.direction,entry:trigger.entryPrice,stopLoss:invalidation.invalidationLevel,tp1:projection.tp1,geometry:{riskToImpulse:safeRatio(risk,impulse),correctionDepthToImpulse:safeRatio(correctionDepth,impulse),entryExtensionToImpulse:safeRatio(risk,impulse),stopToCorrectionLeg:safeRatio(risk,correctionLeg),correctionLegToImpulse:safeRatio(correctionLeg,impulse),riskToCorrectionDepth:safeRatio(risk,correctionDepth)}});
 }
 return candidates;
}
async function run(timeframe){
 const candles=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${timeframe}.json`),'utf8')).candles??[];
 if(candles.length<TOTAL)throw new Error(`${timeframe}: expected at least ${TOTAL} candles, got ${candles.length}`);
 const base=JSON.parse(await readFile(resolve(BASE_DIR,`${timeframe}.json`),'utf8'));
 const freshCut=new Date(candles[PRE].timestamp);
 const freshTrades=(base.trades??[]).filter(t=>t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&new Date(t.entryTime)>=freshCut);
 const canonical=new Map(freshTrades.map(t=>[key(t),t]));
 const rows=[];
 for(let index=PRE;index<candles.length;index++){
  const candidates=buildCandidates(candles,index); if(!candidates.length)continue;
  const selected=candidates[0],t=canonical.get(key(selected)); if(!t)continue;
  rows.push({index,r:Number(t.rMultiple),geometry:selected.geometry});
 }
 const baseline=stats(rows.map(r=>r.r));
 const tests=[
  {name:'riskToImpulse 0.25-<0.50',pass:g=>g.riskToImpulse>=.25&&g.riskToImpulse<.5},
  {name:'stopToCorrectionLeg 0.25-<0.50',pass:g=>g.stopToCorrectionLeg>=.25&&g.stopToCorrectionLeg<.5},
  {name:'intersection: riskToImpulse 0.25-<0.50 AND stopToCorrectionLeg 0.25-<0.50',pass:g=>g.riskToImpulse>=.25&&g.riskToImpulse<.5&&g.stopToCorrectionLeg>=.25&&g.stopToCorrectionLeg<.5},
 ];
 const hypotheses=tests.map(h=>{const s=stats(rows.filter(r=>h.pass(r.geometry)).map(r=>r.r));return{name:h.name,...s,deltaAvgR:s.avgR-baseline.avgR,eligible:s.n>=MIN_N,pass:s.n>=MIN_N&&s.avgR>0&&s.PF!==null&&s.PF>=1};});
 const report={strategy:'Strategy A',mode:'STOP_FIRST_CORRECTION_GEOMETRY_FRESH_HOLDOUT',timeframe,scope:{totalCandles:candles.length,preHoldoutCandles:PRE,freshHoldoutCandles:candles.length-PRE},methodology:{outcomeSource:'canonical baseline backtest; no outcome recomputation',featureSource:'exact canonical candidate reconstruction from visible candles',selection:'three hypotheses frozen from DEV/VAL; no threshold optimization on fresh holdout',minN:MIN_N,productionUntouched:true},parity:{baselineFreshHoldout:freshTrades.length,joinedForensics:rows.length,baselineMissing:freshTrades.filter(t=>!canonical.has(key(t))).length},baseline,hypotheses,decision:'Fresh holdout confirmation only. No hypothesis is promoted automatically; any confirmed hypothesis requires separate robustness/stability validation before production consideration.'};
 await mkdir(OUT_DIR,{recursive:true});const out=resolve(OUT_DIR,`${timeframe}.json`);await writeFile(out,JSON.stringify(report,null,2));
 console.log(`${timeframe}: baseline n=${baseline.n} avgR=${baseline.avgR.toFixed(4)} PF=${baseline.PF?.toFixed(4)??'n/a'} joined=${rows.length}`);
 for(const h of hypotheses)console.log(`  ${h.name}: n=${h.n} avgR=${h.avgR.toFixed(4)} PF=${h.PF?.toFixed(3)??'n/a'} winRate=${(h.winRate*100).toFixed(2)}% totalR=${h.totalR.toFixed(4)} maxDD=${h.maxDD.toFixed(4)}R maxCL=${h.maxCL} deltaAvgR=${h.deltaAvgR.toFixed(4)} pass=${h.pass}`);
 console.log(`Report -> ${out}`);
}
for(const tf of ['1min','5min'])await run(tf);
