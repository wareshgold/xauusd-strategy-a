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
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-phase31-counterfactual-direction-flip-snapshot');
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
function bump(map, key) { map[key] = (map[key] ?? 0) + 1; }
function stats(rs) {
  const resolved = rs.filter(r => r.rMultiple !== null && Number.isFinite(r.rMultiple));
  const wins = resolved.filter(r => r.rMultiple > 0).length;
  const losses = resolved.filter(r => r.rMultiple <= 0).length;
  const grossWin = resolved.filter(r => r.rMultiple > 0).reduce((s, r) => s + r.rMultiple, 0);
  const grossLoss = Math.abs(resolved.filter(r => r.rMultiple <= 0).reduce((s, r) => s + r.rMultiple, 0));
  let equity = 0, peak = 0, maxDD = 0, consec = 0, maxConsec = 0;
  for (const r of resolved) { equity += r.rMultiple; peak = Math.max(peak, equity); maxDD = Math.max(maxDD, peak - equity); consec = r.rMultiple <= 0 ? consec + 1 : 0; maxConsec = Math.max(maxConsec, consec); }
  return { n: resolved.length, wins, losses, winRate: resolved.length ? wins / resolved.length : null, avgR: resolved.length ? equity / resolved.length : null, totalR: equity, profitFactor: grossLoss > 0 ? grossWin / grossLoss : null, maxDrawdownR: maxDD, maxConsecutiveLosses: maxConsec };
}

function evaluate(candidate) {
  const risk = Math.abs(candidate.entry - candidate.stopLoss);
  let exitIndex = null, result = 'OPEN', rMultiple = null;
  for (let i = candidate.entryIndex + 1; i < candles.length; i++) {
    const c = candles[i];
    const sl = candidate.direction === 'BUY' ? c.low <= candidate.stopLoss : c.high >= candidate.stopLoss;
    const tp1 = candidate.direction === 'BUY' ? c.high >= candidate.tp1 : c.low <= candidate.tp1;
    const tp2 = candidate.tp2 == null ? false : candidate.direction === 'BUY' ? c.high >= candidate.tp2 : c.low <= candidate.tp2;
    if (sl && (tp1 || tp2)) { exitIndex = i; result = 'AMBIGUOUS'; break; }
    if (sl) { exitIndex = i; result = 'SL'; rMultiple = -1; break; }
    if (tp2) { exitIndex = i; result = 'TP2'; rMultiple = Math.abs(candidate.tp2 - candidate.entry) / risk; break; }
    if (tp1) { exitIndex = i; result = 'TP1'; rMultiple = Math.abs(candidate.tp1 - candidate.entry) / risk; break; }
  }
  return { result, rMultiple, exitIndex, exitTime: exitIndex == null ? null : candles[exitIndex].timestamp };
}

function mirror(trade) {
  const risk = Math.abs(trade.entry - trade.stopLoss);
  const reward1 = Math.abs(trade.tp1 - trade.entry);
  const reward2 = trade.tp2 == null ? null : Math.abs(trade.tp2 - trade.entry);
  return {
    ...trade,
    direction: trade.direction === 'BUY' ? 'SELL' : 'BUY',
    stopLoss: trade.entry + (trade.direction === 'BUY' ? risk : -risk),
    tp1: trade.entry + (trade.direction === 'BUY' ? -reward1 : reward1),
    tp2: reward2 == null ? null : trade.entry + (trade.direction === 'BUY' ? -reward2 : reward2),
  };
}

const generated = [];
const mismatchReasons = {};
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
    candidates.push({ entryIndex: index, entryTime: trigger.timestamp, direction: trigger.direction, entry: trigger.entryPrice, stopLoss: invalidation.invalidationLevel, tp1: projection.tp1, tp2: null, session: session.session, qualityGrade: quality.grade, qualityScore: quality.score, structureScore: spike.structureScore, overlapScore: spike.overlapScore, hasPGAPEvidence: spike.hasPGAPEvidence, nearRoundLevel: location.nearRoundLevel, emaAligned: ema.aligned, spikeStartIndex: spike.startIndex, spikeEndIndex: spike.endIndex });
  }
  if (candidates.length) generated.push(candidates[0]);
}

const generatedByTime = new Map(generated.map(t => [t.entryTime, t]));
const parityRows = storedTrades.map((stored, i) => {
  const generatedTrade = generatedByTime.get(stored.entryTime);
  const checks = generatedTrade ? [
    generatedTrade.entryIndex === stored.entryIndex,
    generatedTrade.direction === stored.direction,
    sameNumber(generatedTrade.entry, stored.entry),
    sameNumber(generatedTrade.stopLoss, stored.stopLoss),
    sameNumber(generatedTrade.tp1, stored.tp1),
  ] : [];
  const exact = checks.length === 5 && checks.every(Boolean);
  if (!exact) bump(mismatchReasons, generatedTrade ? 'geometry_or_index_mismatch' : 'missing_generated_candidate');
  return { i, entryTime: stored.entryTime, exact, stored: { entryIndex: stored.entryIndex, direction: stored.direction, entry: stored.entry, stopLoss: stored.stopLoss, tp1: stored.tp1 }, generated: generatedTrade ? { entryIndex: generatedTrade.entryIndex, direction: generatedTrade.direction, entry: generatedTrade.entry, stopLoss: generatedTrade.stopLoss, tp1: generatedTrade.tp1 } : null };
});
const exactCount = parityRows.filter(r => r.exact).length;
const generatedExtra = generated.filter(t => !storedTrades.some(s => s.entryTime === t.entryTime)).length;
const generationParity = { stored: storedTrades.length, generated: generated.length, exact: exactCount, missing: storedTrades.length - exactCount, extraGenerated: generatedExtra, matchRate: storedTrades.length ? exactCount / storedTrades.length : null, mismatchReasons };

if (generationParity.missing > 0 || generationParity.extraGenerated > 0) {
  const report = { strategy: baseline.strategy, mode: 'PHASE31_COUNTERFACTUAL_DIRECTION_FLIP_SNAPSHOT', baselineCommit: BASELINE_COMMIT, generationParity, status: 'COUNTERFACTUAL_BLOCKED_GENERATION_PARITY_FAILED', samples: parityRows.filter(r => !r.exact).slice(0, 20) };
  await mkdir(OUT_DIR, { recursive: true }); await writeFile(OUT, JSON.stringify(report, null, 2));
  console.log(`PHASE31_COUNTERFACTUAL_DIRECTION_FLIP_SNAPSHOT GENERATION_STORED=${storedTrades.length} GENERATED=${generated.length} EXACT=${exactCount} MISSING=${generationParity.missing} EXTRA=${generatedExtra}`);
  console.log(`STATUS=${report.status}`);
  console.log(`REPORT=${OUT}`);
  process.exit(0);
}

const original = storedTrades.map(t => ({ ...t, ...evaluate(t) }));
const flipped = storedTrades.map(t => ({ ...mirror(t), ...evaluate(mirror(t)) }));
const report = {
  strategy: baseline.strategy,
  mode: 'PHASE31_COUNTERFACTUAL_DIRECTION_FLIP_SNAPSHOT',
  timeframe: '5min',
  baselineCommit: BASELINE_COMMIT,
  snapshot: { candles: candles.length, from: candles[0]?.timestamp, to: candles.at(-1)?.timestamp },
  generationParity,
  original: stats(original),
  flipped: stats(flipped),
  byOriginalDirection: {
    BUY: stats(flipped.filter((_, i) => storedTrades[i].direction === 'BUY')),
    SELL: stats(flipped.filter((_, i) => storedTrades[i].direction === 'SELL')),
  },
  methodology: 'Research-only counterfactual. Original candidate generation must exactly reproduce the baseline snapshot before mirrored direction/geometry is evaluated. Mirroring preserves entry and absolute risk/reward distances while reversing direction and price-side geometry. No production rules changed.',
  status: 'COUNTERFACTUAL_ONLY_VALIDATED_GENERATION_PARITY',
};
await mkdir(OUT_DIR, { recursive: true }); await writeFile(OUT, JSON.stringify(report, null, 2));
console.log(`PHASE31_COUNTERFACTUAL_DIRECTION_FLIP_SNAPSHOT GENERATION_STORED=${storedTrades.length} GENERATED=${generated.length} EXACT=${exactCount}`);
console.log(`ORIGINAL N=${original.length} WR=${(report.original.winRate * 100).toFixed(2)}% avgR=${report.original.avgR.toFixed(6)} PF=${report.original.profitFactor?.toFixed(6) ?? 'undefined'} totalR=${report.original.totalR.toFixed(6)}`);
console.log(`FLIPPED N=${flipped.length} WR=${(report.flipped.winRate * 100).toFixed(2)}% avgR=${report.flipped.avgR.toFixed(6)} PF=${report.flipped.profitFactor?.toFixed(6) ?? 'undefined'} totalR=${report.flipped.totalR.toFixed(6)}`);
console.log(`FLIPPED_FROM_BUY N=${report.byOriginalDirection.BUY.n} WR=${(report.byOriginalDirection.BUY.winRate * 100).toFixed(2)}% avgR=${report.byOriginalDirection.BUY.avgR.toFixed(6)}`);
console.log(`FLIPPED_FROM_SELL N=${report.byOriginalDirection.SELL.n} WR=${(report.byOriginalDirection.SELL.winRate * 100).toFixed(2)}% avgR=${report.byOriginalDirection.SELL.avgR.toFixed(6)}`);
console.log(`REPORT=${OUT}`);
console.log(`STATUS=${report.status}`);
