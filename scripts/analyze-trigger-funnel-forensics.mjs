import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const OUT=resolve(ROOT,'data/reports/strategy-a-trigger-funnel-forensics');
const CFG={breakoutLookback:5,ftMaxBars:2,spikeMaxCandles:8,minDirectionalFraction:0.5,maxOverlapFraction:0.8,emaPeriod:60,roundStep:50,roundDistance:5,tradingSessions:[{name:'LONDON',startMinutes:420,endMinutes:960},{name:'NEW_YORK',startMinutes:780,endMinutes:1320}],avoidWindows:[]};

const [Breakout,FT,Spike,Correction,Trigger,Invalidation,Projection,Context,Quality]=await Promise.all([
  import('../src/domain/market/BreakoutDetector.ts'),import('../src/domain/market/FollowThroughDetector.ts'),import('../src/domain/strategy-a/SpikeDetector.ts'),import('../src/domain/strategy-a/CorrectionDetector.ts'),import('../src/domain/strategy-a/EntryTrigger.ts'),import('../src/domain/strategy-a/Invalidation.ts'),import('../src/domain/strategy-a/LegProjection.ts'),import('../src/domain/strategy-a/Context.ts'),import('../src/domain/strategy-a/QualityScore.ts')
]);

function counter(){return {seen:0,passed:0,rejected:0};}
function inc(x,pass){x.seen++;if(pass)x.passed++;else x.rejected++;}
function add(map,key){map[key]=(map[key]??0)+1;}

async function run(tf){
 const raw=JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-'+tf+'.json'),'utf8'));
 const candles=raw.candles;
 const stages={events:counter(),breakout:counter(),followThrough:counter(),spike:counter(),correction:counter(),trigger:counter(),projection:counter(),invalidation:counter(),quality:counter(),riskReward:counter()};
 const triggerRows=[]; const seenTriggerKeys=new Set();
 for(let index=0;index<candles.length;index++){
   inc(stages.events,true);
   if(index+1<CFG.emaPeriod) continue;
   const visible=candles.slice(0,index+1);
   const breakouts=Breakout.detectBreakout(visible,CFG.breakoutLookback).filter(b=>b.index<index);
   for(const b of breakouts){
     inc(stages.breakout,true);
     const ft=FT.detectFollowThrough(visible,[b],{maxBarsAfterBreakout:CFG.ftMaxBars,requireCloseBeyondBrokenLevel:true})[0];
     inc(stages.followThrough,!!ft); if(!ft)continue;
     const spike=Spike.detectSpikeCandidates(visible,[b],[ft],{maxCandles:CFG.spikeMaxCandles,minDirectionalFraction:CFG.minDirectionalFraction,maxOverlapFraction:CFG.maxOverlapFraction}).candidates.find(s=>s.breakoutIndex===b.index&&s.endIndex<index);
     inc(stages.spike,!!spike); if(!spike)continue;
     const correction=Correction.detectFirstCorrection(visible,spike);
     const correctionOk=!!correction&&correction.correctionExtremeIndex<index;
     inc(stages.correction,correctionOk); if(!correctionOk)continue;
     const trigger=Trigger.detectEntryTrigger(visible,correction);
     const triggerOk=!!trigger&&trigger.index===index;
     inc(stages.trigger,triggerOk); if(!triggerOk)continue;
     const key=trigger.index+':'+trigger.direction+':'+trigger.entryPrice;
     if(seenTriggerKeys.has(key)) continue;
     seenTriggerKeys.add(key);
     const projection=Projection.projectLeg2(visible,correction); inc(stages.projection,!!projection); if(!projection)continue;
     const invalidation=Invalidation.getInvalidationRule(correction); inc(stages.invalidation,!!invalidation); if(!invalidation)continue;
     const ema=Context.buildEMAContext(visible.map(c=>c.close),CFG);
     const location=Context.buildLocationContext(trigger.entryPrice,CFG);
     const session=Context.buildSessionContext(trigger.timestamp,CFG);
     const quality=Quality.scoreSetup(spike,{ema,location,session}); inc(stages.quality,!!quality.tradeAllowed); if(!quality.tradeAllowed)continue;
     const risk=Math.abs(trigger.entryPrice-invalidation.invalidationLevel), reward=Math.abs(projection.tp1-trigger.entryPrice);
     const rr=risk>0&&reward>0&&(trigger.direction==='BUY'?projection.tp1>trigger.entryPrice:projection.tp1<trigger.entryPrice);
     inc(stages.riskReward,rr);
     triggerRows.push({entryIndex:trigger.index,entryTime:trigger.timestamp,direction:trigger.direction,session:session.session,qualityGrade:quality.grade,qualityScore:quality.score,tradeAllowed:quality.tradeAllowed,riskRewardOk:rr,structureScore:spike.structureScore,overlapScore:spike.overlapScore,hasPGAPEvidence:spike.hasPGAPEvidence});
   }
 }
 const byDirection={},bySession={},byQuality={};
 for(const r of triggerRows){add(byDirection,r.direction);add(bySession,r.session);add(byQuality,r.qualityGrade);}
 const report={strategy:'Strategy A / SP2L',mode:'RESEARCH_TRIGGER_FUNNEL_FORENSICS_V1',timeframe:tf,methodology:'Diagnostic replay from breakout to trigger. Raw persistent historical paths are counted, while emitted trigger rows are deduplicated by entry index/direction/price.',stages,uniqueTriggerRows:triggerRows.length,byDirection,bySession,byQuality,rows:triggerRows};
 await mkdir(OUT,{recursive:true}); const out=resolve(OUT,tf+'.json'); await writeFile(out,JSON.stringify(report,null,2));
 console.log(tf+': uniqueTriggers='+triggerRows.length+' qualityAllowed='+triggerRows.filter(x=>x.tradeAllowed).length+' rrOk='+triggerRows.filter(x=>x.riskRewardOk).length);
 console.log('Report -> '+out);
}
await run('1min');await run('5min');
