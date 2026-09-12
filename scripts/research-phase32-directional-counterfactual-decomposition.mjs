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

const ROOT = resolve(process.cwd());
const BASELINE_COMMIT = '3a96629838fb0a15e5b71f1927dc4f7fe63819e1';
const BASELINE_PATH = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-phase32-directional-counterfactual-decomposition');
const OUT = resolve(OUT_DIR, '5min.json');
const BREAKOUT_LOOKBACK = 5;
const FT_MAX_BARS = 2;
const SPIKE_MAX_CANDLES = 8;
const SPIKE_MIN_DIRECTIONAL_FRACTION = 0.5;
const SPIKE_MAX_OVERLAP_FRACTION = 0.8;
const CONTEXT = { emaPeriod: 60, roundStep: 50, roundDistance: 5, tradingSessions: [{ name: 'LONDON', startMinutes: 420, endMinutes: 960 }, { name: 'NEW_YORK', startMinutes: 780, endMinutes: 1320 }], avoidWindows: [] };
const EPS = 1e-9;

const baseline = JSON.parse(await readFile(BASELINE_PATH, 'utf8'));
const snapshot = JSON.parse(execFileSync('git', ['show', `${BASELINE_COMMIT}:data/historical/xauusd-5min.json`], { cwd: ROOT, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
const candles = snapshot.candles ?? [];
const storedTrades = baseline.trades ?? [];
if (candles.length !== Number(baseline.candles)) throw new Error(`Snapshot candle count mismatch: ${candles.length} !== ${baseline.candles}`);

function sameNumber(a, b) { return Number.isFinite(a) && Number.isFinite(b) && Math.abs(a - b) <= EPS; }
function stats(rows) {
  const resolved = rows.filter(r => Number.isFinite(r.rMultiple));
  const wins = resolved.filter(r => r.rMultiple > 0).length;
  const losses = resolved.filter(r => r.rMultiple <= 0).length;
  const grossWin = resolved.filter(r => r.rMultiple > 0).reduce((s, r) => s + r.rMultiple, 0);
  const grossLoss = Math.abs(resolved.filter(r => r.rMultiple <= 0).reduce((s, r) => s + r.rMultiple, 0));
  return { n: resolved.length, wins, losses, winRate: resolved.length ? wins / resolved.length : null, avgR: resolved.length ? resolved.reduce((s, r) => s + r.rMultiple, 0) / resolved.length : null, totalR: resolved.reduce((s, r) => s + r.rMultiple, 0), profitFactor: grossLoss ? grossWin / grossLoss : null };
}
function evaluate(candidate) {
  const risk = Math.abs(candidate.entry - candidate.stopLoss);
  for (let i = candidate.entryIndex + 1; i < candles.length; i++) {
    const c = candles[i];
    const sl = candidate.direction === 'BUY' ? c.low <= candidate.stopLoss : c.high >= candidate.stopLoss;
    const tp1 = candidate.direction === 'BUY' ? c.high >= candidate.tp1 : c.low <= candidate.tp1;
    if (sl && tp1) return { result: 'AMBIGUOUS', rMultiple: null, exitIndex: i };
    if (sl) return { result: 'SL', rMultiple: -1, exitIndex: i };
    if (tp1) return { result: 'TP1', rMultiple: Math.abs(candidate.tp1 - candidate.entry) / risk, exitIndex: i };
  }
  return { result: 'OPEN', rMultiple: null, exitIndex: null };
}
function mirror(t) {
  const risk = Math.abs(t.entry - t.stopLoss);
  const reward = Math.abs(t.tp1 - t.entry);
  return { ...t, direction: t.direction === 'BUY' ? 'SELL' : 'BUY', stopLoss: t.entry + (t.direction === 'BUY' ? risk : -risk), tp1: t.entry + (t.direction === 'BUY' ? -reward : reward) };
}
function add(map, key, row) { (map[key] ??= []).push(row); }

const generated = [];
for (let index = 0; index < candles.length; index++) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < Math.max(BREAKOUT_LOOKBACK + 2, CONTEXT.emaPeriod)) continue;
  const breakouts = detectBreakout(visible, BREAKOUT_LOOKBACK);
  if (!breakouts.length) continue;
  const ft = detectFollowThrough(visible, breakouts, { maxBarsAfterBreakout: FT_MAX_BARS, requireCloseBeyondBrokenLevel: true });
  if (!ft.length) continue;
  const spikes = detectSpikeCandidates(visible, breakouts, ft, { maxCandles: SPIKE_MAX_CANDLES, minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION, maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION });
  const eligible = spikes.candidates.filter(s => s.endIndex < index);
  const candidates = [];
  for (const spike of eligible) {
    const correction = detectFirstCorrection(visible, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(visible, correction);
    if (!trigger || trigger.index !== index) continue;
    const projection = projectLeg2(visible, correction);
    if (!projection) continue;
    const invalidation = getInvalidationRule(correction);
    const ema = buildEMAContext(visible.map(c => c.close), CONTEXT);
    if (!ema) continue;
    const location = buildLocationContext(trigger.entryPrice, CONTEXT);
    const session = buildSessionContext(trigger.timestamp, CONTEXT);
    const quality = scoreSetup(spike, { ema, location, session });
    if (!quality.tradeAllowed) continue;
    const risk = Math.abs(trigger.entryPrice - invalidation.invalidationLevel);
    const reward = Math.abs(projection.tp1 - trigger.entryPrice);
    const directional = trigger.direction === 'BUY' ? projection.tp1 > trigger.entryPrice : projection.tp1 < trigger.entryPrice;
    if (risk <= 0 || reward <= 0 || !directional) continue;
    candidates.push({ entryIndex: index, entryTime: trigger.timestamp, direction: trigger.direction, entry: trigger.entryPrice, stopLoss: invalidation.invalidationLevel, tp1: projection.tp1, session: session.session, qualityGrade: quality.grade, qualityScore: quality.score, structureScore: spike.structureScore, overlapScore: spike.overlapScore, hasPGAPEvidence: spike.hasPGAPEvidence, nearRoundLevel: location.nearRoundLevel, emaAligned: ema.aligned, spikeStartIndex: spike.startIndex, spikeEndIndex: spike.endIndex });
  }
  if (candidates.length) generated.push(candidates[0]);
}

const byTime = new Map(generated.map(t => [t.entryTime, t]));
const rows = storedTrades.map((stored, i) => {
  const g = byTime.get(stored.entryTime);
  const exact = !!g && g.entryIndex === stored.entryIndex && g.direction === stored.direction && sameNumber(g.entry, stored.entry) && sameNumber(g.stopLoss, stored.stopLoss) && sameNumber(g.tp1, stored.tp1);
  if (!exact) throw new Error(`Generation parity failed at ${stored.entryTime}`);
  const flipped = mirror(g);
  const result = evaluate(flipped);
  return { i, entryTime: stored.entryTime, originalDirection: stored.direction, flippedDirection: flipped.direction, entryIndex: stored.entryIndex, session: g.session, qualityGrade: g.qualityGrade, qualityScore: g.qualityScore, structureScore: g.structureScore, overlapScore: g.overlapScore, hasPGAPEvidence: g.hasPGAPEvidence, nearRoundLevel: g.nearRoundLevel, emaAligned: g.emaAligned, spikeBars: g.spikeEndIndex - g.spikeStartIndex + 1, originalR: stored.rMultiple, flippedR: result.rMultiple, flippedResult: result.result, flippedExitIndex: result.exitIndex };
});

const dimensions = [
  ['originalDirection', ['BUY', 'SELL']],
  ['session', [...new Set(rows.map(r => r.session).filter(Boolean))]],
  ['qualityGrade', [...new Set(rows.map(r => r.qualityGrade).filter(Boolean))]],
  ['emaAligned', [true, false]],
  ['nearRoundLevel', [true, false]],
  ['hasPGAPEvidence', [true, false]],
  ['spikeSize', ['HIGH', 'LOW']],
  ['overlap', ['HIGH', 'LOW']],
];
const groups = {};
for (const [dimension, values] of dimensions) {
  groups[dimension] = {};
  for (const value of values) {
    const selected = rows.filter(r => {
      if (dimension === 'spikeSize') return value === 'HIGH' ? r.structureScore >= 15.81569621847631 : r.structureScore < 15.81569621847631;
      if (dimension === 'overlap') return value === 'HIGH' ? r.overlapScore >= 0.8171813809520624 : r.overlapScore < 0.8171813809520624;
      return r[dimension] === value;
    });
    groups[dimension][String(value)] = { n: selected.length, flipped: stats(selected.map(r => ({ rMultiple: r.flippedR }))), flippedFromBUY: stats(selected.filter(r => r.originalDirection === 'BUY').map(r => ({ rMultiple: r.flippedR }))), flippedFromSELL: stats(selected.filter(r => r.originalDirection === 'SELL').map(r => ({ rMultiple: r.flippedR }))) };
  }
}

const half = candles.length / 2;
const temporal = {
  firstHalf: stats(rows.filter(r => r.entryIndex < half).map(r => ({ rMultiple: r.flippedR }))),
  secondHalf: stats(rows.filter(r => r.entryIndex >= half).map(r => ({ rMultiple: r.flippedR }))),
};
const report = { strategy: baseline.strategy, mode: 'PHASE32_DIRECTIONAL_COUNTERFACTUAL_DECOMPOSITION', timeframe: '5min', baselineCommit: BASELINE_COMMIT, canonicalN: rows.length, generationParity: { stored: storedTrades.length, generated: generated.length, exact: rows.length }, thresholds: { spikeSizeHigh: 15.81569621847631, overlapHigh: 0.8171813809520624 }, overallFlipped: stats(rows.map(r => ({ rMultiple: r.flippedR }))), byDimension: groups, temporal, methodology: 'Research-only decomposition. Uses exact baseline snapshot and requires candidate-generation parity. Direction is mirrored with preserved absolute risk/reward distances. Dimension thresholds are inherited from Phase27; no threshold optimization is performed. First/second half are descriptive stability checks, not DEV/VAL claims.', status: 'COUNTERFACTUAL_ONLY_DECOMPOSITION' };
await mkdir(OUT_DIR, { recursive: true });
await writeFile(OUT, JSON.stringify(report, null, 2));
console.log(`PHASE32_DIRECTIONAL_COUNTERFACTUAL_DECOMPOSITION GENERATION_STORED=${storedTrades.length} GENERATED=${generated.length} EXACT=${rows.length}`);
console.log(`FLIPPED N=${rows.length} WR=${(report.overallFlipped.winRate * 100).toFixed(2)}% avgR=${report.overallFlipped.avgR.toFixed(6)} PF=${report.overallFlipped.profitFactor?.toFixed(6) ?? 'undefined'} totalR=${report.overallFlipped.totalR.toFixed(6)}`);
for (const [k, v] of Object.entries(groups.originalDirection)) console.log(`DIRECTION ${k} N=${v.n} WR=${(v.flipped.winRate * 100).toFixed(2)}% avgR=${v.flipped.avgR.toFixed(6)} PF=${v.flipped.profitFactor?.toFixed(6) ?? 'undefined'} totalR=${v.flipped.totalR.toFixed(6)}`);
console.log(`TEMPORAL_FIRST_HALF N=${report.temporal.firstHalf.n} WR=${(report.temporal.firstHalf.winRate * 100).toFixed(2)}% avgR=${report.temporal.firstHalf.avgR.toFixed(6)} PF=${report.temporal.firstHalf.profitFactor?.toFixed(6) ?? 'undefined'}`);
console.log(`TEMPORAL_SECOND_HALF N=${report.temporal.secondHalf.n} WR=${(report.temporal.secondHalf.winRate * 100).toFixed(2)}% avgR=${report.temporal.secondHalf.avgR.toFixed(6)} PF=${report.temporal.secondHalf.profitFactor?.toFixed(6) ?? 'undefined'}`);
console.log(`REPORT=${OUT}`);
console.log('STATUS=COUNTERFACTUAL_ONLY_DECOMPOSITION');
