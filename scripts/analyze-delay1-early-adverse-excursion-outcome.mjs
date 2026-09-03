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
const CHECKPOINTS = [1, 2, 3, 5, 10];
const THRESHOLDS = [0.25, 0.5, 0.75, 1];
const OUT = resolve(ROOT, 'data/reports/strategy-a-delay1-early-adverse-excursion-outcome');
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

const key = (c) => `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;
const mean = (a) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : null);
const median = (a) => {
  if (!a.length) return null;
  const s = [...a].sort((x, y) => x - y);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
};
const pct = (n, d) => (d ? n / d : null);
const pf = (rs) => {
  const grossProfit = rs.filter((x) => x > 0).reduce((a, b) => a + b, 0);
  const grossLoss = -rs.filter((x) => x < 0).reduce((a, b) => a + b, 0);
  return grossLoss ? grossProfit / grossLoss : null;
};

function build(candles, index) {
  const v = candles.slice(0, index + 1);
  if (v.length < Math.max(BREAKOUT_LOOKBACK + 2, CONTEXT.emaPeriod)) return [];
  const bo = detectBreakout(v, BREAKOUT_LOOKBACK);
  const ft = detectFollowThrough(v, bo, { maxBarsAfterBreakout: FT_MAX_BARS, requireCloseBeyondBrokenLevel: true });
  const sp = detectSpikeCandidates(v, bo, ft, {
    maxCandles: SPIKE_MAX_CANDLES,
    minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION,
    maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION,
  });
  const out = [];
  for (const spike of sp.candidates) {
    if (spike.endIndex >= index) continue;
    const correction = detectFirstCorrection(v, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(v, correction);
    if (!trigger || trigger.index !== index) continue;
    const projection = projectLeg2(v, correction);
    if (!projection) continue;
    const inv = getInvalidationRule(correction);
    const ema = buildEMAContext(v.map((c) => c.close), CONTEXT);
    if (!ema) continue;
    const location = buildLocationContext(trigger.entryPrice, CONTEXT);
    const session = buildSessionContext(trigger.timestamp, CONTEXT);
    const quality = scoreSetup(spike, { ema, location, session });
    if (!quality.tradeAllowed) continue;
    const risk = Math.abs(trigger.entryPrice - inv.invalidationLevel);
    const reward = Math.abs(projection.tp1 - trigger.entryPrice);
    if (!(risk > 0 && reward > 0 && (trigger.direction === 'BUY' ? projection.tp1 > trigger.entryPrice : projection.tp1 < trigger.entryPrice))) continue;
    out.push({
      entryIndex: index,
      entryTime: trigger.timestamp,
      direction: trigger.direction,
      entry: trigger.entryPrice,
      stopLoss: inv.invalidationLevel,
      tp1: projection.tp1,
      session: session.session,
      correction,
    });
  }
  return out;
}

function analyze(candles, candidate, trade) {
  const i = Number(candidate.entryIndex);
  const entry = Number(candidate.entry);
  const stop = Number(candidate.stopLoss);
  const direction = String(candidate.direction).toUpperCase();
  const risk = Math.abs(entry - stop);
  if (!Number.isInteger(i) || !Number.isFinite(entry) || !Number.isFinite(stop) || !risk || !['BUY', 'SELL'].includes(direction)) return null;

  const path = [];
  for (let j = i + 1; j <= Math.min(candles.length - 1, i + Math.max(...CHECKPOINTS)); j++) {
    const candle = candles[j];
    const favorable = (direction === 'BUY' ? candle.high - entry : entry - candle.low) / risk;
    const adverse = (direction === 'BUY' ? entry - candle.low : candle.high - entry) / risk;
    path.push({ bar: j - i, favorable, adverse });
  }

  const checkpoints = {};
  for (const h of CHECKPOINTS) {
    const q = path.filter((x) => x.bar <= h);
    checkpoints[h] = {
      mfe: Math.max(0, ...q.map((x) => x.favorable)),
      mae: Math.max(0, ...q.map((x) => x.adverse)),
    };
  }

  return {
    entryIndex: i,
    entryTime: candidate.entryTime,
    direction,
    entry,
    stopLoss: stop,
    risk,
    rMultiple: Number(trade.rMultiple),
    checkpoints,
  };
}

function outcomeSummary(rows) {
  const x = rows.filter((r) => Number.isFinite(r.rMultiple));
  return {
    n: x.length,
    avgR: mean(x.map((r) => r.rMultiple)),
    pf: pf(x.map((r) => r.rMultiple)),
    winRate: pct(x.filter((r) => r.rMultiple > 0).length, x.length),
    medianMAE: Object.fromEntries(CHECKPOINTS.map((h) => [h, median(x.map((r) => r.checkpoints[h].mae))])),
    medianMFE: Object.fromEntries(CHECKPOINTS.map((h) => [h, median(x.map((r) => r.checkpoints[h].mfe))])),
  };
}

function bucketSummary(rows, checkpoint, threshold) {
  const x = rows.filter((r) => r.checkpoints[checkpoint].mae <= threshold);
  const y = rows.filter((r) => r.checkpoints[checkpoint].mae > threshold);
  return {
    checkpoint,
    thresholdR: threshold,
    within: { ...outcomeSummary(x), shareOfAll: pct(x.length, rows.length) },
    beyond: { ...outcomeSummary(y), shareOfAll: pct(y.length, rows.length) },
    contrast: {
      avgRDeltaWithinMinusBeyond: x.length && y.length ? mean(x.map((r) => r.rMultiple)) - mean(y.map((r) => r.rMultiple)) : null,
    },
  };
}

async function run(tf) {
  const raw = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8'));
  const candles = raw.candles ?? raw;
  const base = JSON.parse(await readFile(resolve(BASE_DIR, `${tf}.json`), 'utf8'));
  const cutoff = new Date(candles[PRE].timestamp);
  const canonical = new Map(
    (base.trades ?? [])
      .filter((t) => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && new Date(t.entryTime) < cutoff)
      .map((t) => [key(t), t]),
  );

  const rows = [];
  for (let i = 0; i < PRE; i++) {
    const candidates = build(candles, i);
    if (!candidates.length) continue;
    const candidate = candidates[0];
    const trade = canonical.get(key(candidate));
    if (!trade || candidate.entryIndex - candidate.correction.correctionExtremeIndex !== 1) continue;
    const row = analyze(candles, candidate, trade);
    if (row) rows.push(row);
  }

  const dev = rows.filter((r) => r.entryIndex < DEV);
  const val = rows.filter((r) => r.entryIndex >= DEV && r.entryIndex < PRE);
  const makeGrid = (subset) => Object.fromEntries(
    CHECKPOINTS.map((h) => [
      `MAE@${h}`,
      Object.fromEntries(THRESHOLDS.map((t) => [`<=${t}R`, bucketSummary(subset, h, t)])),
    ]),
  );

  const report = {
    strategy: 'Strategy A',
    mode: 'DELAY1_EARLY_ADVERSE_EXCURSION_OUTCOME',
    scope: {
      preHoldoutCandles: PRE,
      devCandles: DEV,
      valCandles: PRE - DEV,
      delayExactly: 1,
      freshHoldoutExcluded: true,
    },
    methodology: {
      checkpoints: CHECKPOINTS,
      thresholdsR: THRESHOLDS,
      definition: 'At each fixed post-entry checkpoint T, MAE@T is the maximum adverse excursion observed from entry through T candles. Eventual outcome is the canonical pre-holdout trade rMultiple.',
      comparison: 'For each checkpoint and threshold, compare eventual outcomes of trades whose MAE@T stayed within the threshold versus trades whose MAE@T exceeded it.',
      sameBarOHLC: 'Intrabar ordering is not inferred; this diagnostic only uses excursion magnitudes through completed candle ranges.',
      noOptimization: true,
      noFreshHoldout: true,
      productionUntouched: true,
      diagnosticOnly: true,
    },
    DEV: { ...outcomeSummary(dev), byCheckpoint: makeGrid(dev) },
    VAL: { ...outcomeSummary(val), byCheckpoint: makeGrid(val) },
    allPreHoldout: { ...outcomeSummary(rows), byCheckpoint: makeGrid(rows) },
    rows,
  };

  await mkdir(OUT, { recursive: true });
  const out = resolve(OUT, `${tf}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));

  const print = (label, subset, summary) => {
    console.log(`${label}: n=${summary.n} AvgR=${summary.avgR?.toFixed(3)} PF=${summary.pf?.toFixed(3)} WR=${summary.winRate === null ? 'null' : (100 * summary.winRate).toFixed(1)}`);
    for (const h of CHECKPOINTS) {
      console.log(`  MAE@${h}: median=${summary.medianMAE[h]?.toFixed(3)} MFE=${summary.medianMFE[h]?.toFixed(3)}`);
      for (const t of THRESHOLDS) {
        const s = bucketSummary(subset, h, t);
        console.log(`    <=${t}R: n=${s.within.n} share=${(100 * (s.within.shareOfAll ?? 0)).toFixed(1)} AvgR=${s.within.avgR?.toFixed(3)} PF=${s.within.pf?.toFixed(3)} WR=${s.within.winRate === null ? 'null' : (100 * s.within.winRate).toFixed(1)} | >${t}R: n=${s.beyond.n} AvgR=${s.beyond.avgR?.toFixed(3)} PF=${s.beyond.pf?.toFixed(3)} WR=${s.beyond.winRate === null ? 'null' : (100 * s.beyond.winRate).toFixed(1)} ΔAvgR=${s.contrast.avgRDeltaWithinMinusBeyond?.toFixed(3)}`);
      }
    }
  };

  console.log(`\n=== ${tf} DELAY1 EARLY ADVERSE EXCURSION → FINAL OUTCOME ===`);
  print('DEV', dev, report.DEV);
  print('VAL', val, report.VAL);
  console.log(`Report -> ${out}`);
}

for (const tf of ['1min', '5min']) await run(tf);
