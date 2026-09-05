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
import { runStrategyABacktest } from '../src/backtest/StrategyAAdapter.js';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-t1-extreme-state-fresh-holdout');
const FRESH_HOLDOUT_CANDLES = Number(process.env.FRESH_HOLDOUT_CANDLES ?? '5000');
const PRE = 10000;
const DEV = 6000;
const BINS = [3, 4, 5];
const PERMUTATIONS = 499;
const SEED = 20260905;
const CTX = {
  emaPeriod: 60,
  roundStep: 50,
  roundDistance: 5,
  tradingSessions: [
    { name: 'LONDON', startMinutes: 420, endMinutes: 960 },
    { name: 'NEW_YORK', startMinutes: 780, endMinutes: 1320 },
  ],
  avoidWindows: [],
};
const finite = Number.isFinite;
const mean = (a) => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const median = (a) => { const v = [...a].sort((x, y) => x - y); return v.length ? v[Math.floor(v.length / 2)] : null; };
function quantileEdges(values, bins) {
  const a = values.filter(finite).sort((x, y) => x - y);
  if (!a.length) return [];
  return [...new Set(Array.from({ length: bins - 1 }, (_, i) => {
    const p = (a.length - 1) * (i + 1) / bins;
    const lo = Math.floor(p), hi = Math.ceil(p);
    return a[lo] + (a[hi] - a[lo]) * (p - lo);
  }).filter(finite))];
}
const bucket = (value, edges) => finite(value) ? edges.reduce((k, edge) => k + (value > edge ? 1 : 0), 0) : null;

function candidate(candles, index) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < 60) return null;
  const breakout = detectBreakout(visible, 5);
  const followThrough = detectFollowThrough(visible, breakout, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
  const spikes = detectSpikeCandidates(visible, breakout, followThrough, { maxCandles: 8, minDirectionalFraction: 0.5, maxOverlapFraction: 0.8 });
  for (const spike of spikes.candidates) {
    if (spike.endIndex >= index) continue;
    const correction = detectFirstCorrection(visible, spike);
    if (!correction || correction.correctionExtremeIndex >= index || index - correction.correctionExtremeIndex !== 1) continue;
    const trigger = detectEntryTrigger(visible, correction);
    if (!trigger || trigger.index !== index) continue;
    const projection = projectLeg2(visible, correction);
    if (!projection) continue;
    const invalidation = getInvalidationRule(correction);
    const ema = buildEMAContext(visible.map((c) => c.close), CTX);
    if (!ema) continue;
    const location = buildLocationContext(trigger.entryPrice, CTX);
    const session = buildSessionContext(trigger.timestamp, CTX);
    if (!scoreSetup(spike, { ema, location, session }).tradeAllowed) continue;
    const risk = Math.abs(trigger.entryPrice - invalidation.invalidationLevel);
    if (!(risk > 0)) continue;
    return {
      entryIndex: index,
      direction: trigger.direction,
      entry: trigger.entryPrice,
      stopLoss: invalidation.invalidationLevel,
      tp1: projection.tp1,
      risk,
    };
  }
  return null;
}

function t1Mae(trade, candles) {
  const next = candles[trade.entryIndex + 1];
  if (!next) return null;
  const adverse = trade.direction === 'BUY'
    ? (trade.entry - next.low) / Math.abs(trade.entry - trade.stopLoss)
    : (next.high - trade.entry) / Math.abs(trade.entry - trade.stopLoss);
  return Math.max(0, adverse);
}

function rowsFromTrades(trades, candles) {
  return trades
    .filter((t) => t.result !== 'AMBIGUOUS' && finite(t.rMultiple))
    .map((t) => ({
      entryIndex: t.entryIndex,
      direction: t.direction,
      entry: t.entry,
      stopLoss: t.stopLoss,
      tp1: t.tp1,
      y: Number(t.rMultiple),
      T1_MAE: t1Mae(t, candles),
    }))
    .filter((r) => finite(r.T1_MAE));
}

function stats(rows) {
  const ys = rows.map((r) => r.y).filter(finite);
  const wins = ys.filter((x) => x > 0);
  const losses = ys.filter((x) => x < 0);
  const grossWin = wins.reduce((a, x) => a + x, 0);
  const grossLoss = Math.abs(losses.reduce((a, x) => a + x, 0));
  return {
    n: ys.length,
    meanR: mean(ys),
    medianR: median(ys),
    winRate: ys.length ? wins.length / ys.length : null,
    profitFactor: grossLoss > 0 ? grossWin / grossLoss : null,
  };
}

function lcg(seed) {
  let s = seed >>> 0;
  return () => { s = (1664525 * s + 1013904223) >>> 0; return s / 4294967296; };
}

function permutationP(rows, isExtreme) {
  const extreme = rows.filter(isExtreme);
  const control = rows.filter((r) => !isExtreme(r));
  if (!extreme.length || !control.length) return null;
  const observed = mean(extreme.map((r) => r.y)) - mean(control.map((r) => r.y));
  const values = rows.map((r) => r.y);
  const labels = rows.map(isExtreme);
  const rng = lcg(SEED);
  let ge = 0;
  for (let k = 0; k < PERMUTATIONS; k += 1) {
    const shuffled = [...values];
    for (let i = shuffled.length - 1; i > 0; i -= 1) {
      const j = Math.floor(rng() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    const a = [], b = [];
    for (let i = 0; i < shuffled.length; i += 1) (labels[i] ? a : b).push(shuffled[i]);
    const d = mean(a) - mean(b);
    if (Math.abs(d) >= Math.abs(observed)) ge += 1;
  }
  return { observedDifferenceR: observed, p: (ge + 1) / (PERMUTATIONS + 1) };
}

function bootstrapCI(rows, isExtreme) {
  const extremeN = rows.filter(isExtreme).length;
  const controlN = rows.length - extremeN;
  if (!extremeN || !controlN) return null;
  const rng = lcg(SEED + 17);
  const diffs = [];
  for (let k = 0; k < 1000; k += 1) {
    const extreme = [], control = [];
    for (let i = 0; i < extremeN; i += 1) {
      const candidates = rows.filter(isExtreme);
      extreme.push(candidates[Math.floor(rng() * candidates.length)].y);
    }
    for (let i = 0; i < controlN; i += 1) {
      const candidates = rows.filter((r) => !isExtreme(r));
      control.push(candidates[Math.floor(rng() * candidates.length)].y);
    }
    diffs.push(mean(extreme) - mean(control));
  }
  diffs.sort((a, b) => a - b);
  return { low95: diffs[Math.floor(diffs.length * 0.025)], high95: diffs[Math.floor(diffs.length * 0.975)] };
}

async function run(timeframe) {
  const dataset = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8'));
  const candles = dataset.candles ?? dataset;
  if (candles.length < PRE + FRESH_HOLDOUT_CANDLES) {
    throw new Error(`${timeframe}: need at least ${PRE + FRESH_HOLDOUT_CANDLES} candles, got ${candles.length}`);
  }

  // Canonical Strategy A backtest is run over the complete dataset; the fresh holdout is
  // identified chronologically only after the result exists. No holdout information is used
  // to fit the T1 quantile edges.
  const result = runStrategyABacktest(candles, (event) => {
    const c = candidate(candles, event.index);
    return c ? [c] : [];
  }).result;
  const allRows = rowsFromTrades(result.trades, candles);
  const freshStart = candles.length - FRESH_HOLDOUT_CANDLES;
  const preHoldout = allRows.filter((r) => r.entryIndex < freshStart && r.entryIndex < PRE);
  const holdout = allRows.filter((r) => r.entryIndex >= freshStart);
  if (preHoldout.length === 0 || holdout.length === 0) throw new Error(`${timeframe}: insufficient matched rows preHoldout=${preHoldout.length} holdout=${holdout.length}`);

  const report = {
    strategy: 'Strategy A',
    mode: 'DELAY1_T1_EXTREME_STATE_FRESH_HOLDOUT',
    timeframe,
    symbol: dataset.symbol ?? null,
    source: dataset.source ?? null,
    candles: candles.length,
    scope: {
      preHoldoutCandles: PRE,
      devCandles: DEV,
      valCandles: PRE - DEV,
      freshHoldoutCandles: FRESH_HOLDOUT_CANDLES,
      freshHoldoutStartIndex: freshStart,
      freshHoldoutFrom: candles[freshStart]?.timestamp ?? null,
      freshHoldoutTo: candles.at(-1)?.timestamp ?? null,
      freshHoldoutExcludedFromAllFitting: true,
      delayExactly: 1,
    },
    methodology: {
      hypothesis: 'The highest T1_MAE quantile is economically worse than all lower T1_MAE states.',
      stateDefinition: 'Edges are fitted only on the original DEV window (first 6000 candles of the original 10000-candle pre-holdout sample). The highest quantile is extreme; all lower quantiles form control.',
      bins: BINS,
      permutations: PERMUTATIONS,
      seed: SEED,
      bootstrapReplicates: 1000,
      noThresholdOptimization: true,
      diagnosticOnly: true,
      productionUntouched: true,
    },
    preHoldoutMatchedRows: preHoldout.length,
    freshHoldoutMatchedRows: holdout.length,
    results: {},
  };

  for (const b of BINS) {
    const edges = quantileEdges(preHoldout.filter((r) => r.entryIndex < DEV).map((r) => r.T1_MAE), b);
    const extreme = (r) => bucket(r.T1_MAE, edges) === b - 1;
    report.results[b] = {
      frozenDevEdges: edges,
      freshHoldout: {
        extreme: stats(holdout.filter(extreme)),
        control: stats(holdout.filter((r) => !extreme(r))),
        test: permutationP(holdout, extreme),
        bootstrapCI: bootstrapCI(holdout, extreme),
      },
    };
  }

  await mkdir(OUT, { recursive: true });
  const out = resolve(OUT, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`\n${timeframe}: candles=${candles.length} freshHoldout=${holdout.length} from=${report.scope.freshHoldoutFrom}`);
  for (const b of BINS) {
    const x = report.results[b].freshHoldout;
    console.log(`bins=${b} EXTREME n=${x.extreme.n} meanR=${x.extreme.meanR?.toFixed(4)} win=${(x.extreme.winRate * 100).toFixed(1)}% PF=${x.extreme.profitFactor?.toFixed(4) ?? 'n/a'} | CONTROL n=${x.control.n} meanR=${x.control.meanR?.toFixed(4)} win=${(x.control.winRate * 100).toFixed(1)}% PF=${x.control.profitFactor?.toFixed(4) ?? 'n/a'} | diff=${x.test?.observedDifferenceR?.toFixed(4)} p=${x.test?.p?.toFixed(4)} | CI95=[${x.bootstrapCI?.low95?.toFixed(4)}, ${x.bootstrapCI?.high95?.toFixed(4)}]`);
  }
  console.log(`Report -> ${out}`);
}

for (const timeframe of ['1min', '5min']) await run(timeframe);
