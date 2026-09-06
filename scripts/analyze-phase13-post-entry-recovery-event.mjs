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
const PRE = 10000;
const DEV = 6000;
const BLOCK = 2000;
const H20 = 20;
const MAE_BOUNDARY = 0.5;
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT = resolve(ROOT, 'data/reports/strategy-a-phase13-post-entry-recovery-event');
const CONTEXT = {
  emaPeriod: 60, roundStep: 50, roundDistance: 5,
  tradingSessions: [{ name: 'LONDON', startMinutes: 420, endMinutes: 960 }, { name: 'NEW_YORK', startMinutes: 780, endMinutes: 1320 }],
  avoidWindows: [],
};

const key = t => `${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`;
const stats = rows => {
  const rs = rows.map(r => r.r).filter(Number.isFinite);
  const wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  const grossWin = wins.reduce((s,x)=>s+x,0), grossLoss = -losses.reduce((s,x)=>s+x,0);
  return { n: rs.length, avgR: rs.length ? rs.reduce((s,x)=>s+x,0)/rs.length : null, PF: grossLoss ? grossWin/grossLoss : null, WR: rs.length ? wins.length/rs.length : null, totalR: rs.reduce((s,x)=>s+x,0) };
};
const fmt = x => Number.isFinite(x) ? x.toFixed(4) : '-';

function buildCandidate(candles, index) {
  const v = candles.slice(0, index + 1);
  if (v.length < Math.max(CONTEXT.emaPeriod, 7)) return null;
  const bo = detectBreakout(v, 5);
  const ft = detectFollowThrough(v, bo, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
  const sp = detectSpikeCandidates(v, bo, ft, { maxCandles: 8, minDirectionalFraction: 0.5, maxOverlapFraction: 0.8 });
  for (const spike of sp.candidates) {
    if (spike.endIndex >= index) continue;
    const correction = detectFirstCorrection(v, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(v, correction);
    if (!trigger || trigger.index !== index || index - correction.correctionExtremeIndex !== 1) continue;
    const projection = projectLeg2(v, correction);
    if (!projection) continue;
    const inv = getInvalidationRule(correction);
    const ema = buildEMAContext(v.map(c=>c.close), CONTEXT);
    if (!ema) continue;
    const location = buildLocationContext(trigger.entryPrice, CONTEXT);
    const session = buildSessionContext(trigger.timestamp, CONTEXT);
    const quality = scoreSetup(spike, { ema, location, session });
    if (!quality.tradeAllowed) continue;
    const risk = Math.abs(trigger.entryPrice - inv.invalidationLevel);
    const reward = Math.abs(projection.tp1 - trigger.entryPrice);
    if (!(risk > 0 && reward > 0)) continue;
    if (!(trigger.direction === 'BUY' ? projection.tp1 > trigger.entryPrice : projection.tp1 < trigger.entryPrice)) continue;
    return { entryIndex:index, entryTime:trigger.timestamp, direction:trigger.direction, entry:trigger.entryPrice, stopLoss:inv.invalidationLevel, tp1:projection.tp1 };
  }
  return null;
}

function path(candles, c) {
  const risk = Math.abs(c.entry - c.stopLoss);
  if (!(risk > 0)) return [];
  const out=[];
  for(let j=c.entryIndex+1;j<=Math.min(candles.length-1,c.entryIndex+H20);j++){
    const x=candles[j];
    out.push({ bar:j-c.entryIndex, adverse:Math.max(0,(c.direction==='BUY'?c.entry-x.low:x.high-c.entry)/risk), close:x.close });
  }
  return out;
}

function classify(c,p){
  let mae=0;
  let adverseBar=null;
  for(const x of p){
    mae=Math.max(mae,x.adverse);
    if(adverseBar===null && mae>=MAE_BOUNDARY) adverseBar=x.bar;
  }
  if(adverseBar===null) return { state:'NO_ADVERSE_0_5R', adverseBar:null, recoveryBar:null };
  for(const x of p){
    if(x.bar<=adverseBar) continue;
    const recovered=c.direction==='BUY' ? x.close>=c.entry : x.close<=c.entry;
    if(recovered) return { state:'RECOVERY_AFTER_0_5R', adverseBar, recoveryBar:x.bar, recoveryDelay:x.bar-adverseBar };
  }
  return { state:'NO_RECOVERY_H20', adverseBar, recoveryBar:null };
}

async function run(tf){
  const raw=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${tf}.json`),'utf8'));
  const candles=raw.candles??raw;
  const baselineReport=JSON.parse(await readFile(resolve(BASE,`${tf}.json`),'utf8'));
  const cutoff=new Date(candles[PRE].timestamp);
  const baseline=(baselineReport.trades??[]).filter(t=>t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&new Date(t.entryTime)<cutoff);
  const canonical=new Map(baseline.map(t=>[key(t),t]));
  const rows=[];
  for(let i=0;i<PRE;i++){
    const c=buildCandidate(candles,i); if(!c) continue;
    const t=canonical.get(key(c)); if(!t) continue;
    const p=path(candles,c); if(!p.length) continue;
    rows.push({entryIndex:i,time:c.entryTime,direction:c.direction,session:buildSessionContext(c.entryTime,CONTEXT)?.sessionName??'OUT_OF_SESSION',r:Number(t.rMultiple),exceptional:Number(t.rMultiple)>=5,event:classify(c,p)});
  }
  if(rows.length!==baseline.length) throw new Error(`INTEGRITY mismatch baseline=${baseline.length} joined=${rows.length}`);
  const counts={};
  for(const r of rows) counts[r.event.state]=(counts[r.event.state]??0)+1;
  const eventGroups={};
  for(const state of ['NO_ADVERSE_0_5R','RECOVERY_AFTER_0_5R','NO_RECOVERY_H20']){
    const g=rows.filter(r=>r.event.state===state);
    eventGroups[state]={stats:stats(g),noExceptional:stats(g.filter(r=>!r.exceptional)),recoveryTiming:state==='RECOVERY_AFTER_0_5R'?{mean:g.length?g.reduce((s,r)=>s+r.event.recoveryDelay,0)/g.length:null}:null};
  }
  const windows=[];
  for(let start=0;start<PRE;start+=BLOCK){
    const end=Math.min(PRE,start+BLOCK), g=rows.filter(r=>r.entryIndex>=start&&r.entryIndex<end);
    windows.push({label:start<DEV?`DEV_${start/BLOCK+1}`:`VAL_${(start-DEV)/BLOCK+1}`,start,endExclusive:end,n:g.length,stats:stats(g),groups:Object.fromEntries(Object.keys(counts).map(s=>[s,stats(g.filter(r=>r.event.state===s))]))});
  }
  const segments=[];
  for(const direction of ['BUY','SELL']) for(const session of ['LONDON','NEW_YORK','OUT_OF_SESSION']){
    const g=rows.filter(r=>r.direction===direction&&r.session===session); if(g.length<5) continue;
    segments.push({segment:`${direction}+${session}`,n:g.length,all:Object.fromEntries(Object.keys(counts).map(s=>[s,stats(g.filter(r=>r.event.state===s))])),dev:Object.fromEntries(Object.keys(counts).map(s=>[s,stats(g.filter(r=>r.entryIndex<DEV&&r.event.state===s))])),val:Object.fromEntries(Object.keys(counts).map(s=>[s,stats(g.filter(r=>r.entryIndex>=DEV&&r.event.state===s))]))});
  }
  const report={mode:'PHASE_13_POST_ENTRY_RECOVERY_EVENT',timeframe:tf,scope:{baselinePre:baseline.length,joined:rows.length,dev:rows.filter(r=>r.entryIndex<DEV).length,val:rows.filter(r=>r.entryIndex>=DEV).length,freshLocked:true},eventDefinition:{boundaryR:MAE_BOUNDARY,horizon:H20,recovery:'first later candle close through entry after first cumulative MAE >= 0.50R',noIntrabarInference:true},overall:stats(rows),eventGroups,windows,segments,cases:rows,methodology:{fixedChronologicalWindows:true,noThresholdSearch:true,noHorizonSelection:true,noNewRule:true,noFresh:true,productionUnchanged:true,diagnosticOnly:true}};
  await mkdir(OUT,{recursive:true}); const file=resolve(OUT,`${tf}.json`); await writeFile(file,JSON.stringify(report,null,2));
  console.log(`PHASE_13_RECOVERY_EVENT ${tf} N=${rows.length} DEV=${report.scope.dev} VAL=${report.scope.val} FRESH=LOCKED`);
  console.log(`INTEGRITY baselinePre=${baseline.length} joined=${rows.length} mismatch=${baseline.length-rows.length}`);
  console.log(`BASELINE avgR=${fmt(report.overall.avgR)} PF=${fmt(report.overall.PF)} WR=${fmt(report.overall.WR*100)}%`);
  for(const [s,x] of Object.entries(eventGroups)) console.log(`${s}: N=${x.stats.n} avgR=${fmt(x.stats.avgR)} PF=${fmt(x.stats.PF)} WR=${fmt(x.stats.WR*100)}% | NO_EX avgR=${fmt(x.noExceptional.avgR)} PF=${fmt(x.noExceptional.PF)} | recoveryDelayMean=${fmt(x.recoveryTiming?.mean)}`);
  console.log('=== WINDOWS ==='); for(const w of windows) console.log(`${w.label} idx=${w.start}-${w.endExclusive-1} N=${w.n} avgR=${fmt(w.stats.avgR)} | ${Object.entries(w.groups).map(([s,x])=>`${s}=${x.n}/${fmt(x.avgR)}`).join(' | ')}`);
  console.log('=== SEGMENTS ==='); for(const s of segments) console.log(`${s.segment} N=${s.n} | ALL ${Object.entries(s.all).map(([k,x])=>`${k}:${x.n}/${fmt(x.avgR)}`).join(' ')} | DEV ${Object.entries(s.dev).map(([k,x])=>`${k}:${x.n}/${fmt(x.avgR)}`).join(' ')} | VAL ${Object.entries(s.val).map(([k,x])=>`${k}:${x.n}/${fmt(x.avgR)}`).join(' ')}`);
  console.log(`REPORT=${file}`); console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_HORIZON_SELECTION NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
}
for(const tf of ['1min','5min']) await run(tf);
