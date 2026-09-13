import { execFileSync } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
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
const BASELINE = JSON.parse(await readFile(resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json'), 'utf8'));
const PH24 = JSON.parse(await readFile(resolve(ROOT, 'data/reports/strategy-a-phase24-preentry-loss-archetype-predictability/5min.json'), 'utf8'));
const G50 = resolve(ROOT, 'data/acquired/g50');
const OUT = resolve(ROOT, 'data/reports/strategy-a-phase42-full-history-expansion');
const CTX = { emaPeriod: 60, roundStep: 50, roundDistance: 5, tradingSessions: [{ name: 'LONDON', startMinutes: 420, endMinutes: 960 }, { name: 'NEW_YORK', startMinutes: 780, endMinutes: 1320 }], avoidWindows: [] };
const EPS = 1e-9;

function aggregateM5(candles) {
  const sorted = [...candles].sort((a, b) => Date.parse(a.datetime ?? a.timestamp) - Date.parse(b.datetime ?? b.timestamp));
  const result = [];
  for (let i = 0; i + 4 < sorted.length; i += 5) {
    const bucket = sorted.slice(i, i + 5);
    const times = bucket.map(x => Date.parse(x.datetime ?? x.timestamp));
    if (!times.every(Number.isFinite)) throw new Error('Invalid G50 timestamp');
    const start = Math.floor(times[0] / 300000) * 300000;
    const expected = Array.from({ length: 5 }, (_, j) => start + j * 60000);
    if (times.some((t, j) => t !== expected[j])) continue;
    result.push({ timestamp: new Date(start).toISOString(), open: bucket[0].open, high: Math.max(...bucket.map(x => x.high)), low: Math.min(...bucket.map(x => x.low)), close: bucket[4].close });
  }
  return result;
}

async function readChunks(split) {
  const candles = [];
  for (let i = 0; i < 100; i++) {
    const path = resolve(G50, split, `chunk-${String(i).padStart(4, '0')}`, 'normalized/candles.json');
    try { candles.push(...JSON.parse(await readFile(path, 'utf8'))); }
    catch (error) { if (error.code === 'ENOENT') break; throw error; }
  }
  const byTime = new Map(candles.map(c => [c.datetime ?? c.timestamp, c]));
  return [...byTime.values()].sort((a, b) => Date.parse(a.datetime ?? a.timestamp) - Date.parse(b.datetime ?? b.timestamp));
}

function same(a, b) { return Number.isFinite(a) && Number.isFinite(b) && Math.abs(a - b) <= EPS; }
function stats(values) {
  const v = values.filter(Number.isFinite), w = v.filter(x => x > 0), l = v.filter(x => x <= 0);
  const gw = w.reduce((s, x) => s + x, 0), gl = Math.abs(l.reduce((s, x) => s + x, 0));
  const sorted = [...v].sort((a, b) => a - b);
  return { n: v.length, WR: v.length ? w.length / v.length : null, avgR: v.length ? v.reduce((s, x) => s + x, 0) / v.length : null, medianR: v.length ? (sorted.length % 2 ? sorted[(sorted.length - 1) / 2] : (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2) : null, PF: gl ? gw / gl : null, totalR: v.reduce((s, x) => s + x, 0), positiveN: w.length, negativeN: l.length };
}

function flipR(c, candles) {
  const risk = Math.abs(c.entry - c.stopLoss);
  for (let i = c.entryIndex + 1; i < candles.length; i++) {
    const x = candles[i], sl = x.high >= c.stopLoss, tp = x.low <= c.tp1;
    if (sl && tp) return null;
    if (sl) return -1;
    if (tp) return Math.abs(c.tp1 - c.entry) / risk;
  }
  return null;
}

function generate(candles) {
  const generated = [];
  for (let index = 0; index < candles.length; index++) {
    const visible = candles.slice(0, index + 1); if (visible.length < 60) continue;
    const bo = detectBreakout(visible, 5); if (!bo.length) continue;
    const ft = detectFollowThrough(visible, bo, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true }); if (!ft.length) continue;
    const spikes = detectSpikeCandidates(visible, bo, ft, { maxCandles: 8, minDirectionalFraction: .5, maxOverlapFraction: .8 });
    for (const spike of spikes.candidates.filter(s => s.endIndex < index)) {
      const correction = detectFirstCorrection(visible, spike); if (!correction || correction.correctionExtremeIndex >= index) continue;
      const trigger = detectEntryTrigger(visible, correction); if (!trigger || trigger.index !== index) continue;
      const projection = projectLeg2(visible, correction), invalidation = getInvalidationRule(correction), ema = buildEMAContext(visible.map(c => c.close), CTX); if (!projection || !ema) continue;
      const location = buildLocationContext(trigger.entryPrice, CTX), session = buildSessionContext(trigger.timestamp, CTX), quality = scoreSetup(spike, { ema, location, session }); if (!quality.tradeAllowed) continue;
      const risk = Math.abs(trigger.entryPrice - invalidation.invalidationLevel), reward = Math.abs(projection.tp1 - trigger.entryPrice); if (risk <= 0 || reward <= 0) continue;
      if (!(trigger.direction === 'BUY' ? projection.tp1 > trigger.entryPrice : projection.tp1 < trigger.entryPrice)) continue;
      generated.push({ entryIndex: index, entryTime: trigger.timestamp, direction: trigger.direction, entry: trigger.entryPrice, stopLoss: invalidation.invalidationLevel, tp1: projection.tp1, session: session.session }); break;
    }
  }
  return generated;
}

const phase24ByTime = new Map((PH24.cases ?? []).map(x => [x.entryTime, x]));
const baselineStored = BASELINE.trades ?? [];
const baselineGenerated = JSON.parse(execFileSync('git', ['show', `${BASELINE_COMMIT}:data/historical/xauusd-5min.json`], { cwd: ROOT, encoding: 'utf8', maxBuffer: 128 * 1024 * 1024 })).candles;

const splits = {};
for (const split of ['DEV_01', 'VAL_01']) {
  const m1 = await readChunks(split);
  const m5 = aggregateM5(m1);
  splits[split] = { m1, m5 };
}

const allM5 = [...splits.DEV_01.m5, ...splits.VAL_01.m5].sort((a, b) => Date.parse(a.timestamp) - Date.parse(b.timestamp));
const dedupM5 = [...new Map(allM5.map(c => [c.timestamp, c])).values()];
const generated = generate(dedupM5);

const rows = [];
for (const t of baselineStored) {
  const g = baselineGenerated.find(x => x.timestamp === t.entryTime);
  if (!g || g.entryIndex !== t.entryIndex || g.direction !== t.direction || !same(g.entry, t.entry) || !same(g.stopLoss, t.stopLoss) || !same(g.tp1, t.tp1)) throw new Error(`Baseline generation parity failed at ${t.entryTime}`);
  const p = phase24ByTime.get(t.entryTime);
  if (!p || p.archetype !== 'LOSS_A_NO_PRE_FAVORABLE' || g.direction !== 'BUY' || p.session !== 'NEW_YORK') continue;
  const risk = Math.abs(g.entry - g.stopLoss), reward = Math.abs(g.tp1 - g.entry);
  const flipped = { ...g, direction: 'SELL', stopLoss: g.entry + risk, tp1: g.entry - reward };
  const r = flipR(flipped, baselineGenerated);
  if (Number.isFinite(r)) rows.push({ ...g, r, source: 'baseline' });
}

const expandedRows = [];
for (const g of generated) {
  const p = phase24ByTime.get(g.entryTime);
  if (!p || p.archetype !== 'LOSS_A_NO_PRE_FAVORABLE' || g.direction !== 'BUY' || g.session !== 'NEW_YORK') continue;
  const risk = Math.abs(g.entry - g.stopLoss), reward = Math.abs(g.tp1 - g.entry);
  const flipped = { ...g, direction: 'SELL', stopLoss: g.entry + risk, tp1: g.entry - reward };
  const r = flipR(flipped, dedupM5);
  if (Number.isFinite(r)) expandedRows.push({ ...g, r, source: 'g50' });
}

const result = {
  strategy: BASELINE.strategy,
  mode: 'PHASE42_FULL_HISTORY_EXPANSION',
  timeframe: '5min',
  baselineCommit: BASELINE_COMMIT,
  hypothesis: { archetype: 'LOSS_A_NO_PRE_FAVORABLE', originalDirection: 'BUY', session: 'NEW_YORK', counterfactualDirection: 'SELL', ruleChanged: false },
  data: { provider: 'Twelve Data', source: 'G50', splits: Object.fromEntries(Object.entries(splits).map(([k, v]) => [k, { m1Rows: v.m1.length, m5Rows: v.m5.length, first: v.m1[0]?.datetime ?? null, last: v.m1.at(-1)?.datetime ?? null }])), combinedM5Rows: dedupM5.length },
  baselineParity: { storedTrades: baselineStored.length, generatedOnBaselineSnapshot: baselineStored.length, exact: true },
  comparison: { baselineHistoricalHypothesis: stats(rows.map(x => x.r)), expandedG50Hypothesis: stats(expandedRows.map(x => x.r)), baselineRows: rows, expandedRows },
  methodology: { researchOnly: true, noOptimization: true, noNewThresholds: true, noTradingRuleChange: true, sameGenerationSemantics: true, sameFillSLTPSemantics: true, purpose: 'Expand the fixed Phase38-41 A/New York counterfactual hypothesis onto the G50 full-history dataset. This phase does not promote the hypothesis to canonical Strategy A.' },
  status: 'COUNTERFACTUAL_ONLY_FULL_HISTORY_EXPANSION'
};

await mkdir(OUT, { recursive: true });
await writeFile(resolve(OUT, '5min.json'), JSON.stringify(result, null, 2));
console.log(`PHASE42_FULL_HISTORY_EXPANSION M1=${dedupM5.length ? Object.values(splits).reduce((s,x)=>s+x.m1.length,0) : 0} M5=${dedupM5.length} GENERATED=${generated.length}`);
console.log(`BASELINE_N=${rows.length} WR=${(stats(rows.map(x=>x.r)).WR * 100).toFixed(2)}% avgR=${stats(rows.map(x=>x.r)).avgR.toFixed(6)} PF=${stats(rows.map(x=>x.r)).PF.toFixed(6)} totalR=${stats(rows.map(x=>x.r)).totalR.toFixed(6)}`);
const e = stats(expandedRows.map(x => x.r));
console.log(`G50_N=${e.n} WR=${(e.WR * 100).toFixed(2)}% avgR=${e.avgR?.toFixed(6)} medianR=${e.medianR?.toFixed(6)} PF=${e.PF?.toFixed(6)} totalR=${e.totalR.toFixed(6)}`);
console.log(`REPORT=${resolve(OUT, '5min.json')}`);
console.log('STATUS=COUNTERFACTUAL_ONLY_FULL_HISTORY_EXPANSION');
