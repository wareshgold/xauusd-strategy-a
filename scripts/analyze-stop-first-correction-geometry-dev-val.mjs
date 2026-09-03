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
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-stop-first-correction-geometry-dev-val');
const TOTAL = 15000, PRE = 10000, DEV = 6000, MIN_N = 10;
const BREAKOUT_LOOKBACK = 5, FT_MAX_BARS = 2, SPIKE_MAX_CANDLES = 8, SPIKE_MIN_DIRECTIONAL_FRACTION = .5, SPIKE_MAX_OVERLAP_FRACTION = .8;
const CONTEXT = { emaPeriod:60, roundStep:50, roundDistance:5, tradingSessions:[{name:'LONDON',startMinutes:420,endMinutes:960},{name:'NEW_YORK',startMinutes:780,endMinutes:1320}], avoidWindows:[] };

function key(c){return `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;}
function metrics(rows){const rs=rows.map(x=>Number(x.r)).filter(Number.isFinite),wins=rs.filter(x=>x>0),losses=rs.filter(x=>x<0);const gp=wins.reduce((a,b)=>a+b,0),gl=-losses.reduce((a,b)=>a+b,0);return{n:rs.length,wins:wins.length,losses:losses.length,winRate:rs.length?wins.length/rs.length:0,avgR:rs.length?rs.reduce((a,b)=>a+b,0)/rs.length:0,totalR:rs.reduce((a,b)=>a+b,0),PF:gl?gp/gl:null};}
function pass(m){return m.n>=MIN_N&&m.avgR>0&&m.PF!==null&&m.PF>=1;}
function safeRatio(a,b){return Number.isFinite(a)&&Number.isFinite(b)&&b>0?a/b:null;}
function bin(v,bins){if(v===null||!Number.isFinite(v))return null;for(const b of bins)if(b.test(v))return b.id;return null;}

const BINS_4=[
 {id:'LT_025',label:'< 0.25',test:v=>v<.25},
 {id:'025_050',label:'0.25-<0.50',test:v=>v>=.25&&v<.5},
 {id:'050_100',label:'0.50-<1.00',test:v=>v>=.5&&v<1},
 {id:'GE_100',label:'>= 1.00',test:v=>v>=1},
];
const DEPTH_BINS=[
 {id:'LT_025',label:'< 0.25',test:v=>v<.25},
 {id:'025_050',label:'0.25-<0.50',test:v=>v>=.25&&v<.5},
 {id:'050_075',label:'0.50-<0.75',test:v=>v>=.5&&v<.75},
 {id:'075_100',label:'0.75-<1.00',test:v=>v>=.75&&v<1},
 {id:'GE_100',label:'>= 1.00',test:v=>v>=1},
];

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
  const impulse=Math.abs(spike.endPrice-spike.startPrice);
  const correctionDepth=Math.abs(correction.extremePrice-spike.startPrice);
  const correctionLeg=Math.abs(correction.extremePrice-spike.endPrice);
  const entryExtension=risk;
  candidates.push({
   entryIndex:index,entryTime:trigger.timestamp,direction:trigger.direction,entry:trigger.entryPrice,stopLoss:invalidation.invalidationLevel,tp1:projection.tp1,
   geometry:{
    riskToImpulse:safeRatio(risk,impulse),
    correctionDepthToImpulse:safeRatio(correctionDepth,impulse),
    entryExtensionToImpulse:safeRatio(entryExtension,impulse),
    stopToCorrectionLeg:safeRatio(risk,correctionLeg),
    correctionLegToImpulse:safeRatio(correctionLeg,impulse),
    riskToCorrectionDepth:safeRatio(risk,correctionDepth),
   },
  });
 }
 return candidates;
}

const hypotheses=[
 {id:'RISK_TO_IMPULSE',label:'riskToImpulse',get:r=>r.geometry.riskToImpulse,bins:BINS_4},
 {id:'CORRECTION_DEPTH_TO_IMPULSE',label:'correctionDepthToImpulse',get:r=>r.geometry.correctionDepthToImpulse,bins:DEPTH_BINS},
 {id:'ENTRY_EXTENSION_TO_IMPULSE',label:'entryExtensionToImpulse',get:r=>r.geometry.entryExtensionToImpulse,bins:BINS_4},
 {id:'STOP_TO_CORRECTION_LEG',label:'stopToCorrectionLeg',get:r=>r.geometry.stopToCorrectionLeg,bins:BINS_4},
 {id:'CORRECTION_LEG_TO_IMPULSE',label:'correctionLegToImpulse',get:r=>r.geometry.correctionLegToImpulse,bins:DEPTH_BINS},
 {id:'RISK_TO_CORRECTION_DEPTH',label:'riskToCorrectionDepth',get:r=>r.geometry.riskToCorrectionDepth,bins:BINS_4},
];

async function run(timeframe){
 const candles=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${timeframe}.json`),'utf8')).candles;
 if(candles.length<TOTAL)throw new Error(`${timeframe}: expected at least ${TOTAL} candles, got ${candles.length}`);
 const base=JSON.parse(await readFile(resolve(BASE_DIR,`${timeframe}.json`),'utf8'));
 const preCutoff=new Date(candles[PRE].timestamp);
 const canonical=new Map((base.trades??[]).filter(t=>t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&new Date(t.entryTime)<preCutoff).map(t=>[key(t),t]));
 const rows=[];
 for(let index=0;index<PRE;index++){
  const candidates=buildCandidates(candles,index); if(!candidates.length)continue;
  const selected=candidates[0],t=canonical.get(key(selected)); if(!t)continue;
  rows.push({index,candidateCount:candidates.length,r:Number(t.rMultiple),...selected.geometry});
 }
 const devRows=rows.filter(r=>r.index<DEV),valRows=rows.filter(r=>r.index>=DEV&&r.index<PRE);
 const tests=[];
 for(const h of hypotheses){
  for(const b of h.bins){
   const dev=metrics(devRows.filter(r=>bin(h.get(r),[b])===b.id)),val=metrics(valRows.filter(r=>bin(h.get(r),[b])===b.id));
   tests.push({id:`${h.id}__${b.id}`,feature:h.id,label:h.label,bin:b.id,range:b.label,DEV:dev,VAL:val,passDEV:pass(dev),passVAL:pass(val),pass:pass(dev)&&pass(val)});
  }
 }
 const report={strategy:'Strategy A',mode:'STOP_FIRST_CORRECTION_GEOMETRY_DEV_VAL_PREHOLDOUT',timeframe,scope:{totalCandles:TOTAL,preHoldoutCandles:PRE,devCandles:DEV,valCandles:PRE-DEV,freshHoldoutCandles:TOTAL-PRE,freshHoldoutExcluded:true,minNPerSplit:MIN_N},methodology:{hypothesis:'Frozen descriptive forensic focused on stop placement and first-correction geometry. Each feature is tested independently using fixed bins; no thresholds are learned from VAL or fresh holdout.',features:['riskToImpulse','correctionDepthToImpulse','entryExtensionToImpulse','stopToCorrectionLeg','correctionLegToImpulse','riskToCorrectionDepth'],gate:'n >= 10, AvgR > 0, PF >= 1 in both DEV and VAL.',purpose:'Validation only. Passing does not change production and only authorizes a separate one-time fresh holdout test of the exact frozen bin.'},counts:{joined:rows.length,DEV:devRows.length,VAL:valRows.length},baseline:{DEV:metrics(devRows),VAL:metrics(valRows)},tests};
 await mkdir(OUT_DIR,{recursive:true});const out=resolve(OUT_DIR,`${timeframe}.json`);await writeFile(out,JSON.stringify(report,null,2));
 console.log(`${timeframe}: joined=${rows.length} DEV=${devRows.length} VAL=${valRows.length} baselineDEV=${report.baseline.DEV.avgR.toFixed(4)} baselineVAL=${report.baseline.VAL.avgR.toFixed(4)}`);
 for(const h of hypotheses){console.log(` ${h.label}:`);for(const t of tests.filter(x=>x.feature===h.id))console.log(`  ${t.range}: DEV n=${t.DEV.n} avgR=${t.DEV.avgR.toFixed(4)} PF=${t.DEV.PF?.toFixed(4)??'n/a'} | VAL n=${t.VAL.n} avgR=${t.VAL.avgR.toFixed(4)} PF=${t.VAL.PF?.toFixed(4)??'n/a'} | pass=${t.pass}`);}
 console.log(`Report -> ${out}`);
}

await run('1min');
await run('5min');
