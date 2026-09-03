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
const FRESH = 5000;
const CHECKPOINTS = [1, 2, 3];
const THRESHOLDS = [0.5, 0.75];
const EXECUTION_MODELS = ['CHECKPOINT_CLOSE', 'NEXT_OPEN'];
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-delay1-early-adverse-excursion-management');
const BASE_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');

const BREAKOUT_LOOKBACK = 5;
const FT_MAX_BARS = 2;
const SPIKE_MAX_CANDLES = 8;
const SPIKE_MIN_DIRECTIONAL_FRACTION = 0.5;
const SPIKE_MAX_OVERLAP_FRACTION = 0.8;
const CONTEXT = {
  emaPeriod: 60,
  roundStep: 50,
  roundDistance: 5,
  tradingSessions: [
    { name: 'LONDON', startMinutes: 420, endMinutes: 960 },
    { name: 'NEW_YORK', startMinutes: 780, endMinutes: 1320 },
  ],
  avoidWindows: [],
};

const key = c => `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const pct = (n, d) => d ? n / d : null;
const pf = rs => {
  const gp = rs.filter(x => x > 0).reduce((a, b) => a + b, 0);
  const gl = -rs.filter(x => x < 0).reduce((a, b) => a + b, 0);
  return gl ? gp / gl : null;
};

function stats(rows) {
  const rs = rows.map(r => Number(r.finalR)).filter(Number.isFinite);
  return {
    n: rs.length,
    avgR: mean(rs),
    PF: pf(rs),
    winRate: pct(rs.filter(r => r > 0).length, rs.length),
    totalR: rs.reduce((a, b) => a + b, 0),
  };
}

function buildCandidate(candles, index) {
  const v = candles.slice(0, index + 1);
  if (v.length < Math.max(BREAKOUT_LOOKBACK + 2, CONTEXT.emaPeriod)) return null;

  const breakout = detectBreakout(v, BREAKOUT_LOOKBACK);
  const followThrough = detectFollowThrough(v, breakout, {
    maxBarsAfterBreakout: FT_MAX_BARS,
    requireCloseBeyondBrokenLevel: true,
  });
  const spikes = detectSpikeCandidates(v, breakout, followThrough, {
    maxCandles: SPIKE_MAX_CANDLES,
    minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION,
    maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION,
  });

  for (const spike of spikes.candidates) {
    if (spike.endIndex >= index) continue;

    const correction = detectFirstCorrection(v, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;

    const trigger = detectEntryTrigger(v, correction);
    if (!trigger || trigger.index !== index) continue;
    if (index - correction.correctionExtremeIndex !== 1) continue;

    const projection = projectLeg2(v, correction);
    if (!projection) continue;

    const invalidation = getInvalidationRule(correction);
    const ema = buildEMAContext(v.map(c => c.close), CONTEXT);
    if (!ema) continue;

    const location = buildLocationContext(trigger.entryPrice, CONTEXT);
    const session = buildSessionContext(trigger.timestamp, CONTEXT);
    const quality = scoreSetup(spike, { ema, location, session });
    if (!quality.tradeAllowed) continue;

    const risk = Math.abs(trigger.entryPrice - invalidation.invalidationLevel);
    const reward = Math.abs(projection.tp1 - trigger.entryPrice);
    if (!(risk > 0 && reward > 0)) continue;
    if (!(trigger.direction === 'BUY' ? projection.tp1 > trigger.entryPrice : projection.tp1 < trigger.entryPrice)) continue;

    return {
      entryIndex: index,
      entryTime: trigger.timestamp,
      direction: trigger.direction,
      entry: trigger.entryPrice,
      stopLoss: invalidation.invalidationLevel,
      tp1: projection.tp1,
    };
  }

  return null;
}

function excursionAt(candles, candidate, h) {
  const i = candidate.entryIndex;
  const e = Number(candidate.entry);
  const s = Number(candidate.stopLoss);
  const d = candidate.direction;
  const risk = Math.abs(e - s);
  if (!Number.isFinite(risk) || risk <= 0) return null;
  const end = i + h;
  if (end >= candles.length) return null;

  let mae = 0;
  for (let j = i + 1; j <= end; j++) {
    const c = candles[j];
    const adverse = d === 'BUY' ? e - c.low : c.high - e;
    mae = Math.max(mae, adverse / risk);
  }
  return mae;
}

function exitR(candidate, price) {
  const e = Number(candidate.entry);
  const s = Number(candidate.stopLoss);
  const risk = Math.abs(e - s);
  const d = candidate.direction;
  return (d === 'BUY' ? price - e : e - price) / risk;
}

function simulate(candles, row, threshold, checkpoint, executionModel) {
  const { candidate, trade } = row;
  const mae = excursionAt(candles, candidate, checkpoint);
  if (mae == null) return null;

  if (mae <= threshold) {
    return {
      ...row,
      finalR: Number(trade.rMultiple),
      management: 'HOLD_CANONICAL',
      checkpoint,
      thresholdR: threshold,
      executionModel,
      maeAtCheckpoint: mae,
      exitIndex: null,
      exitTime: null,
      exitPrice: null,
      exitR: null,
    };
  }

  const exitIndex = executionModel === 'CHECKPOINT_CLOSE'
    ? candidate.entryIndex + checkpoint
    : candidate.entryIndex + checkpoint + 1;
  if (exitIndex >= candles.length) return null;

  const exitCandle = candles[exitIndex];
  const exitPrice = Number(executionModel === 'CHECKPOINT_CLOSE' ? exitCandle.close : exitCandle.open);
  const r = exitR(candidate, exitPrice);

  return {
    ...row,
    finalR: r,
    management: 'EARLY_EXIT',
    checkpoint,
    thresholdR: threshold,
    executionModel,
    maeAtCheckpoint: mae,
    exitIndex,
    exitTime: exitCandle.timestamp,
    exitPrice,
    exitR: r,
  };
}

async function run(tf) {
  const raw = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8'));
  const candles = raw.candles ?? raw;
  if (candles.length < PRE + FRESH) throw new Error(`${tf}: expected at least ${PRE + FRESH} candles, found ${candles.length}`);

  const base = JSON.parse(await readFile(resolve(BASE_DIR, `${tf}.json`), 'utf8'));
  const freshCut = new Date(candles[PRE].timestamp);
  const canonicalFresh = (base.trades ?? []).filter(t =>
    t.result !== 'AMBIGUOUS' &&
    Number.isFinite(Number(t.rMultiple)) &&
    new Date(t.entryTime) >= freshCut
  );
  const baseMap = new Map(canonicalFresh.map(t => [key(t), t]));

  const rows = [];
  for (let i = PRE; i < candles.length; i++) {
    const candidate = buildCandidate(candles, i);
    if (!candidate) continue;
    const trade = baseMap.get(key(candidate));
    if (!trade) continue;
    rows.push({ candidate, trade });
  }

  const results = {};
  for (const executionModel of EXECUTION_MODELS) {
    results[executionModel] = {};
    for (const h of CHECKPOINTS) {
      results[executionModel][`h${h}`] = {};
      for (const threshold of THRESHOLDS) {
        const simulated = rows.map(r => simulate(candles, r, threshold, h, executionModel)).filter(Boolean);
        const early = simulated.filter(r => r.management === 'EARLY_EXIT');
        const canonical = simulated.map(r => ({ ...r, finalR: Number(r.trade.rMultiple) }));
        const s = stats(simulated);
        const baseline = stats(canonical);
        results[executionModel][`h${h}`][`>${threshold}R`] = {
          ...s,
          baselineAvgR: baseline.avgR,
          deltaAvgR: s.avgR != null && baseline.avgR != null ? s.avgR - baseline.avgR : null,
          earlyExitCount: early.length,
          earlyExitShare: pct(early.length, simulated.length),
          earlyExitAvgR: stats(early).avgR,
          earlyExitPF: stats(early).PF,
        };
      }
    }
  }

  const report = {
    strategy: 'Strategy A',
    mode: 'DELAY1_EARLY_ADVERSE_EXCURSION_MANAGEMENT',
    timeframe: tf,
    scope: {
      totalCandles: candles.length,
      preHoldoutCandles: PRE,
      freshHoldoutCandles: FRESH,
      delayExactly: 1,
    },
    frozenPolicies: {
      checkpoints: CHECKPOINTS,
      thresholdsR: THRESHOLDS,
      executionModels: EXECUTION_MODELS,
      rule: 'At checkpoint h, if MAE through candle h exceeds threshold, exit at the specified executable price; otherwise retain canonical outcome.',
      checkpointClose: 'exit at close of candle entryIndex+h',
      nextOpen: 'exit at open of candle entryIndex+h+1',
    },
    methodology: {
      outcomeSource: 'canonical baseline fresh-holdout trades',
      entrySource: 'reconstructed DELAY1 fresh-holdout candidates',
      noIntrabarInference: true,
      canonicalAmbiguousExcluded: true,
      noOptimization: true,
      productionUntouched: true,
      diagnosticOnly: true,
      exactJoin: true,
    },
    parity: {
      canonicalFreshTrades: canonicalFresh.length,
      delay1FreshJoined: rows.length,
      unmatchedCanonicalFresh: canonicalFresh.length - rows.length,
    },
    baselineDelay1: stats(rows.map(r => ({ finalR: Number(r.trade.rMultiple) }))),
    policies: results,
  };

  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${tf}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));

  console.log(`\n=== ${tf} DELAY1 EARLY ADVERSE EXCURSION — MANAGEMENT SIMULATION ===`);
  console.log(`canonicalFresh=${canonicalFresh.length} delay1Joined=${rows.length} unmatchedCanonical=${canonicalFresh.length - rows.length}`);
  console.log(`BASELINE DELAY1: n=${report.baselineDelay1.n} AvgR=${report.baselineDelay1.avgR?.toFixed(3)} PF=${report.baselineDelay1.PF?.toFixed(3) ?? 'n/a'} WR=${(100 * (report.baselineDelay1.winRate ?? 0)).toFixed(1)} TotalR=${report.baselineDelay1.totalR.toFixed(3)}`);

  for (const executionModel of EXECUTION_MODELS) {
    console.log(`\n${executionModel}`);
    for (const h of CHECKPOINTS) {
      for (const threshold of THRESHOLDS) {
        const s = results[executionModel][`h${h}`][`>${threshold}R`];
        console.log(`  h${h} MAE>${threshold}R: n=${s.n} AvgR=${s.avgR?.toFixed(3)} PF=${s.PF?.toFixed(3) ?? 'n/a'} WR=${(100 * (s.winRate ?? 0)).toFixed(1)} ΔvsBase=${s.deltaAvgR?.toFixed(3)} earlyExits=${s.earlyExitCount} share=${(100 * (s.earlyExitShare ?? 0)).toFixed(1)} earlyExitAvgR=${s.earlyExitAvgR?.toFixed(3) ?? 'n/a'} earlyExitPF=${s.earlyExitPF?.toFixed(3) ?? 'n/a'}`);
      }
    }
  }

  console.log(`Report -> ${out}`);
}

for (const tf of ['1min', '5min']) await run(tf);
