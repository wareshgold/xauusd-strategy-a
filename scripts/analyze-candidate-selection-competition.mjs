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
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-candidate-selection-competition');
const BREAKOUT_LOOKBACK = 5, FT_MAX_BARS = 2, SPIKE_MAX_CANDLES = 8, SPIKE_MIN_DIRECTIONAL_FRACTION = .5, SPIKE_MAX_OVERLAP_FRACTION = .8;
const CONTEXT = { emaPeriod: 60, roundStep: 50, roundDistance: 5, tradingSessions: [
  { name: 'LONDON', startMinutes: 420, endMinutes: 960 },
  { name: 'NEW_YORK', startMinutes: 780, endMinutes: 1320 },
], avoidWindows: [] };
const PRE = 10000;

function key(c) { return `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`; }
function metrics(rows) {
  const rs = rows.map(x => Number(x.r)).filter(Number.isFinite); const wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  const gp = wins.reduce((a,b)=>a+b,0), gl = -losses.reduce((a,b)=>a+b,0);
  return { n: rs.length, wins: wins.length, losses: losses.length, winRate: rs.length ? wins.length/rs.length : 0, avgR: rs.length ? rs.reduce((a,b)=>a+b,0)/rs.length : 0, totalR: rs.reduce((a,b)=>a+b,0), PF: gl ? gp/gl : null };
}
function evaluate(c, candles) {
  const risk = Math.abs(c.entry - c.stopLoss); if (!(risk > 0)) return { result:'INVALID', r:null, exitIndex:null };
  for (let i = c.entryIndex + 1; i < candles.length; i++) {
    const x = candles[i], sl = c.direction === 'BUY' ? x.low <= c.stopLoss : x.high >= c.stopLoss;
    const tp = c.direction === 'BUY' ? x.high >= c.tp1 : x.low <= c.tp1;
    if (sl && tp) return { result:'AMBIGUOUS', r:null, exitIndex:i };
    if (sl) return { result:'SL', r:-1, exitIndex:i };
    if (tp) return { result:'TP1', r:Math.abs(c.tp1-c.entry)/risk, exitIndex:i };
  }
  return { result:'OPEN', r:null, exitIndex:null };
}
function buildCandidates(candles, index) {
  const visible = candles.slice(0, index + 1); if (visible.length < Math.max(BREAKOUT_LOOKBACK + 2, CONTEXT.emaPeriod)) return [];
  const breakouts = detectBreakout(visible, BREAKOUT_LOOKBACK);
  const ft = detectFollowThrough(visible, breakouts, { maxBarsAfterBreakout: FT_MAX_BARS, requireCloseBeyondBrokenLevel: true });
  const spikes = detectSpikeCandidates(visible, breakouts, ft, { maxCandles: SPIKE_MAX_CANDLES, minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION, maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION });
  const candidates = [];
  for (const spike of spikes.candidates) {
    if (spike.endIndex >= index) continue;
    const correction = detectFirstCorrection(visible, spike); if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(visible, correction); if (!trigger || trigger.index !== index) continue;
    const projection = projectLeg2(visible, correction); if (!projection) continue;
    const invalidation = getInvalidationRule(correction);
    const ema = buildEMAContext(visible.map(c => c.close), CONTEXT); if (!ema) continue;
    const location = buildLocationContext(trigger.entryPrice, CONTEXT), session = buildSessionContext(trigger.timestamp, CONTEXT);
    const quality = scoreSetup(spike, { ema, location, session }); if (!quality.tradeAllowed) continue;
    const risk = Math.abs(trigger.entryPrice-invalidation.invalidationLevel), reward = Math.abs(projection.tp1-trigger.entryPrice);
    const directional = trigger.direction === 'BUY' ? projection.tp1 > trigger.entryPrice : projection.tp1 < trigger.entryPrice;
    if (!(risk > 0 && reward > 0 && directional)) continue;
    candidates.push({ entryIndex:index, entryTime:trigger.timestamp, direction:trigger.direction, entry:trigger.entryPrice, stopLoss:invalidation.invalidationLevel, tp1:projection.tp1,
      session:session.session, qualityGrade:quality.grade, qualityScore:quality.score, structureScore:spike.structureScore, overlapScore:spike.overlapScore,
      hasPGAPEvidence:spike.hasPGAPEvidence, nearRoundLevel:location.nearRoundLevel, emaAligned:ema.aligned, spikeStartIndex:spike.startIndex, spikeEndIndex:spike.endIndex,
      spikeSize:Math.abs(spike.endPrice-spike.startPrice), correctionExtremeIndex:correction.correctionExtremeIndex, triggerLevel:trigger.triggerLevel,
      triggerDelay:index-correction.correctionExtremeIndex, correctionDepth:Math.abs(correction.extremePrice-spike.startPrice)/Math.max(Math.abs(spike.endPrice-spike.startPrice),1e-9),
      rr:reward/risk });
  }
  return candidates;
}

async function run(timeframe) {
  const candles = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8')).candles;
  const base = JSON.parse(await readFile(resolve(BASE_DIR, `${timeframe}.json`), 'utf8'));
  const canonical = new Map((base.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && new Date(t.entryTime) < new Date(candles[PRE].timestamp)).map(t => [key(t), t]));
  const byIndex = new Map();
  for (let index = 0; index < Math.min(PRE, candles.length); index++) {
    const candidates = buildCandidates(candles, index); if (!candidates.length) continue;
    const enriched = candidates.map((c, position) => ({ ...c, selectionPosition: position + 1, selectionCount: candidates.length, outcome: evaluate(c, candles) }));
    byIndex.set(index, enriched);
  }

  const groups = [];
  for (const [index, candidates] of byIndex) {
    const selected = candidates[0];
    if (!selected) continue;
    const canonicalTrade = canonical.get(key(selected));
    if (!canonicalTrade) continue;
    const alternatives = candidates.slice(1).filter(c => Number.isFinite(c.outcome.r));
    const selectedR = Number(canonicalTrade.rMultiple);
    const bestAlt = alternatives.length ? alternatives.reduce((a,b) => b.outcome.r > a.outcome.r ? b : a) : null;
    const worstAlt = alternatives.length ? alternatives.reduce((a,b) => b.outcome.r < a.outcome.r ? b : a) : null;
    const sortedQuality = [...candidates].sort((a,b) => Number(b.qualityScore ?? -Infinity)-Number(a.qualityScore ?? -Infinity));
    const sortedRR = [...candidates].sort((a,b) => b.rr-a.rr);
    groups.push({ index, candidateCount:candidates.length, selectedR, selectedResult:canonicalTrade.result, bestAlternativeR:bestAlt?.outcome.r ?? null, worstAlternativeR:worstAlt?.outcome.r ?? null,
      realizedOpportunityCost:bestAlt ? bestAlt.outcome.r-selectedR : null, selectedQualityRank:sortedQuality.findIndex(c=>key(c)===key(selected))+1,
      selectedRRRank:sortedRR.findIndex(c=>key(c)===key(selected))+1, selectedQualityScore:selected.qualityScore, selectedRR:selected.rr,
      alternatives:candidates.slice(1).map(c=>({ selectionPosition:c.selectionPosition, direction:c.direction, entry:c.entry, stopLoss:c.stopLoss, tp1:c.tp1, rr:c.rr, qualityScore:c.qualityScore,
        structureScore:c.structureScore, overlapScore:c.overlapScore, triggerDelay:c.triggerDelay, outcome:c.outcome })) });
  }

  const multi = groups.filter(g=>g.candidateCount>1);
  const selectedVsBest = multi.filter(g=>Number.isFinite(g.bestAlternativeR));
  const report = { strategy:'Strategy A', mode:'CANDIDATE_SELECTION_COMPETITION_PREHOLDOUT', timeframe, scope:{preHoldoutCandles:PRE,freshHoldoutExcluded:true},
    methodology:{candidateReplay:'Exact baseline decision-path reconstruction; candidates are kept in the same order produced by the baseline loop and selected[0] mirrors decide() candidates.slice(0,1).',
      outcome:'Diagnostic TP1/SL replay matching BacktestEngine semantics: first candle with both is AMBIGUOUS; SL before TP1 is -1R; TP1 is actual reward/risk.',
      bestAlternative:'Realized future outcome among non-selected same-candle candidates; post-hoc only and never a predictive feature.',
      purpose:'Determine whether candidate selection materially harms outcomes; no optimization and no production change.'},
    counts:{decisionIndexes:groups.length,multiCandidateIndexes:multi.length,singleCandidateIndexes:groups.length-multi.length,alternativeEvaluated:selectedVsBest.length},
    selectionCompetition:metrics(selectedVsBest.map(g=>({r:g.selectedR}))),
    opportunityCost:metrics(selectedVsBest.map(g=>({r:g.realizedOpportunityCost}))),
    multiCandidateSelected:metrics(multi.map(g=>({r:g.selectedR}))),
    singleCandidateSelected:metrics(groups.filter(g=>g.candidateCount===1).map(g=>({r:g.selectedR}))),
    ranks:{selectedQualityBestN:selectedVsBest.filter(g=>g.selectedQualityRank===1).length,selectedRRBestN:selectedVsBest.filter(g=>g.selectedRRRank===1).length,
      selectedQualityNotBestN:selectedVsBest.filter(g=>g.selectedQualityRank>1).length,selectedRRNotBestN:selectedVsBest.filter(g=>g.selectedRRRank>1).length},
    selectedVsBestAlternative:{n:selectedVsBest.length,selectedAvgR:selectedVsBest.length?selectedVsBest.reduce((a,g)=>a+g.selectedR,0)/selectedVsBest.length:null,bestAlternativeAvgR:selectedVsBest.length?selectedVsBest.reduce((a,g)=>a+g.bestAlternativeR,0)/selectedVsBest.length:null,
      positiveOpportunityCostN:selectedVsBest.filter(g=>g.realizedOpportunityCost>0).length,selectedWorseByAtLeast1RN:selectedVsBest.filter(g=>g.realizedOpportunityCost>=1).length},
    groups:groups.map(g=>({index:g.index,candidateCount:g.candidateCount,selectedR:g.selectedR,selectedResult:g.selectedResult,bestAlternativeR:g.bestAlternativeR,worstAlternativeR:g.worstAlternativeR,realizedOpportunityCost:g.realizedOpportunityCost,
      selectedQualityRank:g.selectedQualityRank,selectedRRRank:g.selectedRRRank,selectedQualityScore:g.selectedQualityScore,selectedRR:g.selectedRR,alternatives:g.alternatives})) };
  await mkdir(OUT_DIR,{recursive:true}); const out=resolve(OUT_DIR,`${timeframe}.json`); await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${timeframe}: decisionIndexes=${groups.length} multi=${multi.length} single=${groups.length-multi.length}`);
  console.log(` selected multi ${JSON.stringify(report.multiCandidateSelected)} | selected single ${JSON.stringify(report.singleCandidateSelected)}`);
  console.log(` selected-vs-best n=${selectedVsBest.length} selectedAvgR=${report.selectedVsBestAlternative.selectedAvgR?.toFixed(4)??'n/a'} bestAltAvgR=${report.selectedVsBestAlternative.bestAlternativeAvgR?.toFixed(4)??'n/a'} positiveCost=${report.selectedVsBestAlternative.positiveOpportunityCostN} >=1R=${report.selectedVsBestAlternative.selectedWorseByAtLeast1RN}`);
  console.log(` ranks qualityBest=${report.ranks.selectedQualityBestN} qualityNotBest=${report.ranks.selectedQualityNotBestN} rrBest=${report.ranks.selectedRRBestN} rrNotBest=${report.ranks.selectedRRNotBestN}`);
  console.log(`Report -> ${out}`);
}
await run('1min'); await run('5min');
