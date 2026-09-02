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

const ROOT=resolve(process.cwd()), OUTPUT=resolve(ROOT,'data/reports/strategy-a-entry-path-forensics');
const BREAKOUT_LOOKBACK=5, FT_MAX_BARS=2, SPIKE_MAX_CANDLES=8, SPIKE_MIN_DIRECTIONAL_FRACTION=.5, SPIKE_MAX_OVERLAP_FRACTION=.8;
const CONTEXT={emaPeriod:60,roundStep:50,roundDistance:5,tradingSessions:[{name:'LONDON',startMinutes:420,endMinutes:960},{name:'NEW_YORK',startMinutes:780,endMinutes:1320}],avoidWindows:[]};
function bump(m,k){m[k]=(m[k]??0)+1} function median(v){if(!v.length)return null;const a=[...v].sort((x,y)=>x-y),m=Math.floor(a.length/2);return a.length%2?a[m]:(a[m-1]+a[m])/2}
async function run(timeframe){
 const dataset=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${timeframe}.json`),'utf8')), candles=dataset.candles;
 const stages=Object.fromEntries(['visible','breakout','followThrough','spike','correction','trigger','projection','invalidation','context','quality','riskReward','accepted'].map(k=>[k,0]));
 const rejection={},baselineSelected=[],triggerCandidates=[],correctionCandidates=[];
 for(let index=0;index<candles.length;index++){
  const visible=candles.slice(0,index+1); if(visible.length<Math.max(BREAKOUT_LOOKBACK+2,CONTEXT.emaPeriod))continue; bump(stages,'visible');
  const breakouts=detectBreakout(visible,BREAKOUT_LOOKBACK); if(!breakouts.length){bump(rejection,'no_breakout');continue} bump(stages,'breakout');
  const ft=detectFollowThrough(visible,breakouts,{maxBarsAfterBreakout:FT_MAX_BARS,requireCloseBeyondBrokenLevel:true}); if(!ft.length){bump(rejection,'no_follow_through');continue} bump(stages,'followThrough');
  const spikes=detectSpikeCandidates(visible,breakouts,ft,{maxCandles:SPIKE_MAX_CANDLES,minDirectionalFraction:SPIKE_MIN_DIRECTIONAL_FRACTION,maxOverlapFraction:SPIKE_MAX_OVERLAP_FRACTION});
  const eligible=spikes.candidates.filter(s=>s.endIndex<index); if(!eligible.length){bump(rejection,'no_eligible_spike');continue} bump(stages,'spike');
  let sawCorrection=false,sawTrigger=false,sawProjection=false,sawInvalidation=false,sawContext=false,sawQuality=false,sawRR=false;
  const candidates=[];
  for(const spike of eligible){
   const correction=detectFirstCorrection(visible,spike); if(!correction||correction.correctionExtremeIndex>=index)continue; sawCorrection=true;
   const impulseSize=Math.abs(spike.endPrice-spike.startPrice);
   correctionCandidates.push({index,spikeEndIndex:spike.endIndex,correctionExtremeIndex:correction.correctionExtremeIndex,direction:correction.direction,depth:Math.abs(correction.extremePrice-spike.startPrice)/Math.max(impulseSize,1e-9)});
   const trigger=detectEntryTrigger(visible,correction); if(!trigger||trigger.index!==index)continue; sawTrigger=true; triggerCandidates.push({index,timestamp:trigger.timestamp,direction:trigger.direction,entryPrice:trigger.entryPrice,triggerLevel:trigger.triggerLevel,delay:index-correction.correctionExtremeIndex});
   const projection=projectLeg2(visible,correction); if(!projection)continue; sawProjection=true; const invalidation=getInvalidationRule(correction); sawInvalidation=true;
   const ema=buildEMAContext(visible.map(c=>c.close),CONTEXT); if(!ema)continue; const location=buildLocationContext(trigger.entryPrice,CONTEXT),session=buildSessionContext(trigger.timestamp,CONTEXT); sawContext=true;
   const quality=scoreSetup(spike,{ema,location,session}); if(!quality.tradeAllowed)continue; sawQuality=true;
   const risk=Math.abs(trigger.entryPrice-invalidation.invalidationLevel),reward=Math.abs(projection.tp1-trigger.entryPrice),directional=trigger.direction==='BUY'?projection.tp1>trigger.entryPrice:projection.tp1<trigger.entryPrice; if(risk<=0||reward<=0||!directional)continue; sawRR=true;
   const triggerExtension=Math.abs(trigger.entryPrice-trigger.triggerLevel)/Math.max(impulseSize,1e-9);
   const stopToImpulse=risk/Math.max(impulseSize,1e-9);
   candidates.push({index,timestamp:trigger.timestamp,direction:trigger.direction,entry:trigger.entryPrice,stopLoss:invalidation.invalidationLevel,tp1:projection.tp1,risk,reward,rr:reward/risk,session:session.session,qualityGrade:quality.grade,qualityScore:quality.score,structureScore:spike.structureScore,overlapScore:spike.overlapScore,hasPGAPEvidence:spike.hasPGAPEvidence,nearRoundLevel:location.nearRoundLevel,emaAligned:ema.aligned,spikeStartIndex:spike.startIndex,spikeEndIndex:spike.endIndex,spikeSize:impulseSize,correctionExtremeIndex:correction.correctionExtremeIndex,triggerLevel:trigger.triggerLevel,triggerDelay:index-correction.correctionExtremeIndex,correctionDepth:Math.abs(correction.extremePrice-spike.startPrice)/Math.max(impulseSize,1e-9),triggerExtension,stopToImpulse});
  }
  // Exact baseline parity: decide() returns candidates.slice(0, 1).
  const selected=candidates.slice(0,1);
  if(selected.length){baselineSelected.push(selected[0]);bump(stages,'riskReward');bump(stages,'accepted');}
  if(sawCorrection)bump(stages,'correction');else bump(rejection,'no_eligible_correction'); if(sawTrigger)bump(stages,'trigger');else bump(rejection,'no_trigger_at_current_index'); if(sawProjection)bump(stages,'projection');else if(sawTrigger)bump(rejection,'no_projection'); if(sawInvalidation)bump(stages,'invalidation'); if(sawContext)bump(stages,'context'); if(sawQuality)bump(stages,'quality');else if(sawContext)bump(rejection,'quality_rejected'); if(sawRR)bump(stages,'riskReward_candidate');else if(sawQuality)bump(rejection,'invalid_risk_reward');
 }
 const report={strategy:'Strategy A',mode:'DIRECT_BASELINE_PATH_FORENSICS',timeframe,candles:candles.length,methodology:'Research-only replay of the baseline decision path candle-by-candle with no future candles. Candidate selection mirrors baseline decide() semantics by taking only candidates.slice(0,1) per candle. All trigger opportunities remain diagnostic. Feature enrichment is descriptive only; no production rules or thresholds changed.',parameters:{BREAKOUT_LOOKBACK,FT_MAX_BARS,SPIKE_MAX_CANDLES,SPIKE_MIN_DIRECTIONAL_FRACTION,SPIKE_MAX_OVERLAP_FRACTION,emaPeriod:CONTEXT.emaPeriod,roundStep:CONTEXT.roundStep,roundDistance:CONTEXT.roundDistance},stages,rejectionReasons:rejection,counts:{triggerCandidates:triggerCandidates.length,baselineSelected:baselineSelected.length,accepted:baselineSelected.length,correctionCandidates:correctionCandidates.length},triggerStats:{medianDelay:median(triggerCandidates.map(x=>x.delay)),delays:triggerCandidates.map(x=>x.delay)},acceptedStats:{medianRR:median(baselineSelected.map(x=>x.rr)),medianDelay:median(baselineSelected.map(x=>x.triggerDelay)),medianCorrectionDepth:median(baselineSelected.map(x=>x.correctionDepth)),medianTriggerExtension:median(baselineSelected.map(x=>x.triggerExtension)),medianStopToImpulse:median(baselineSelected.map(x=>x.stopToImpulse))},baselineSelected};
 await mkdir(OUTPUT,{recursive:true}); const out=resolve(OUTPUT,`${timeframe}.json`); await writeFile(out,JSON.stringify(report,null,2)); console.log(`${timeframe}: visible=${stages.visible} breakout=${stages.breakout} FT=${stages.followThrough} spike=${stages.spike} correction=${stages.correction} trigger=${stages.trigger} projection=${stages.projection} quality=${stages.quality} RRcandidate=${stages.riskReward_candidate} baselineSelected=${stages.accepted}`); console.log(`  triggerCandidates=${triggerCandidates.length} medianDelay=${report.triggerStats.medianDelay??'n/a'} baselineSelectedMedianRR=${report.acceptedStats.medianRR??'n/a'} medianTriggerExtension=${report.acceptedStats.medianTriggerExtension??'n/a'} medianStopToImpulse=${report.acceptedStats.medianStopToImpulse??'n/a'}`); console.log(`Report -> ${out}`);
}
await run('1min'); await run('5min');
