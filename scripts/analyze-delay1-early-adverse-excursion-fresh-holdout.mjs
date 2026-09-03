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
const CHECKPOINTS = [1, 2, 3, 5, 10];
const THRESHOLDS = [0.25, 0.5, 0.75, 1];
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-delay1-early-adverse-excursion-fresh-holdout');
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
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
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

    // DELAY1 means the entry candle is exactly the first candle after the
    // correction extreme. This is reconstructed directly from market data,
    // avoiding dependence on precomputed forensic reports.
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
      session: session.session,
      correction,
    };
  }

  return null;
}

function early(candles, candidate, trade) {
  const i = Number(candidate.entryIndex);
  const e = Number(candidate.entry);
  const s = Number(candidate.stopLoss);
  const d = String(candidate.direction).toUpperCase();
  const risk = Math.abs(e - s);
  if (!Number.isInteger(i) || !Number.isFinite(e) || !Number.isFinite(s) || !risk || !['BUY', 'SELL'].includes(d)) return null;

  const path = [];
  for (let j = i + 1; j <= Math.min(candles.length - 1, i + Math.max(...CHECKPOINTS)); j++) {
    const c = candles[j];
    const adverse = (d === 'BUY' ? e - c.low : c.high - e) / risk;
    const favorable = (d === 'BUY' ? c.high - e : e - c.low) / risk;
    path.push({ bar: j - i, adverse, favorable });
  }

  const checkpoints = {};
  for (const h of CHECKPOINTS) {
    const q = path.filter(x => x.bar <= h);
    checkpoints[h] = {
      mae: Math.max(0, ...q.map(x => x.adverse)),
      mfe: Math.max(0, ...q.map(x => x.favorable)),
    };
  }

  return {
    entryIndex: i,
    entryTime: candidate.entryTime,
    direction: d,
    entry: e,
    stopLoss: s,
    risk,
    rMultiple: Number(trade.rMultiple),
    checkpoints,
  };
}

function compare(rows, h, threshold) {
  const within = rows.filter(r => r.checkpoints[h].mae <= threshold);
  const beyond = rows.filter(r => r.checkpoints[h].mae > threshold);
  return {
    checkpoint: h,
    thresholdR: threshold,
    within: { ...stats(within), share: pct(within.length, rows.length) },
    beyond: { ...stats(beyond), share: pct(beyond.length, rows.length) },
    deltaAvgR: within.length && beyond.length
      ? mean(within.map(r => r.rMultiple)) - mean(beyond.map(r => r.rMultiple))
      : null,
  };
}

async function run(tf) {
  const raw = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8'));
  const candles = raw.candles ?? raw;
  if (candles.length < PRE + FRESH) throw new Error(`${tf}: expected at least ${PRE + FRESH} candles, found ${candles.length}`);

  const base = JSON.parse(await readFile(resolve(BASE_DIR, `${tf}.json`), 'utf8'));
  const freshCut = new Date(candles[PRE].timestamp);

  // Canonical outcomes are taken from the existing baseline backtest. We do
  // not rebuild outcome logic here; only the fresh-holdout entry geometry is
  // reconstructed so the join is based on the actual candle index and prices.
  const canonicalFresh = (base.trades ?? []).filter(t =>
    t.result !== 'AMBIGUOUS' &&
    Number.isFinite(Number(t.rMultiple)) &&
    new Date(t.entryTime) >= freshCut
  );
  const baseMap = new Map(canonicalFresh.map(t => [key(t), t]));

  const candidates = [];
  for (let i = PRE; i < candles.length; i++) {
    const candidate = buildCandidate(candles, i);
    if (!candidate) continue;
    const trade = baseMap.get(key(candidate));
    if (!trade) continue;
    candidates.push({ candidate, trade });
  }

  const rows = candidates.map(({ candidate, trade }) => early(candles, candidate, trade)).filter(Boolean);
  const unmatchedCanonical = canonicalFresh.length - rows.length;

  const report = {
    strategy: 'Strategy A',
    mode: 'DELAY1_EARLY_ADVERSE_EXCURSION_FRESH_HOLDOUT',
    timeframe: tf,
    scope: {
      totalCandles: candles.length,
      preHoldoutCandles: PRE,
      freshHoldoutCandles: FRESH,
      delayExactly: 1,
    },
    methodology: {
      outcomeSource: 'canonical baseline fresh-holdout trades',
      featureSource: 'post-entry OHLC excursion from reconstructed fresh-holdout entry',
      checkpoints: CHECKPOINTS,
      thresholdsR: THRESHOLDS,
      sameBarOHLC: 'No intrabar ordering inference.',
      frozenBeforeHoldout: true,
      noOptimization: true,
      productionUntouched: true,
      diagnosticOnly: true,
      joinMethod: 'reconstruct DELAY1 candidates on fresh candles, then exact key join to canonical outcomes',
    },
    parity: {
      canonicalFreshTrades: canonicalFresh.length,
      delay1FreshJoined: rows.length,
      unmatchedCanonicalFresh: unmatchedCanonical,
    },
    baselineDelay1: stats(rows),
    byCheckpoint: Object.fromEntries(
      CHECKPOINTS.map(h => [
        `MAE@${h}`,
        Object.fromEntries(THRESHOLDS.map(t => [`<=${t}R`, compare(rows, h, t)])),
      ])
    ),
    rows,
  };

  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${tf}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));

  console.log(`\n=== ${tf} DELAY1 EARLY ADVERSE EXCURSION — FRESH HOLDOUT ===`);
  console.log(`canonicalFresh=${canonicalFresh.length} delay1Joined=${rows.length} unmatchedCanonical=${unmatchedCanonical}`);
  console.log(`BASELINE DELAY1: n=${report.baselineDelay1.n} AvgR=${report.baselineDelay1.avgR?.toFixed(3)} PF=${report.baselineDelay1.PF?.toFixed(3) ?? 'n/a'} WR=${(100 * (report.baselineDelay1.winRate ?? 0)).toFixed(1)} TotalR=${report.baselineDelay1.totalR.toFixed(3)}`);

  for (const h of CHECKPOINTS) {
    for (const t of THRESHOLDS) {
      const s = compare(rows, h, t);
      console.log(
        `  MAE@${h} <=${t}R: n=${s.within.n} share=${(100 * (s.within.share ?? 0)).toFixed(1)} AvgR=${s.within.avgR?.toFixed(3)} PF=${s.within.PF?.toFixed(3) ?? 'n/a'} WR=${(100 * (s.within.winRate ?? 0)).toFixed(1)} | >${t}R: n=${s.beyond.n} AvgR=${s.beyond.avgR?.toFixed(3)} PF=${s.beyond.PF?.toFixed(3) ?? 'n/a'} WR=${(100 * (s.beyond.winRate ?? 0)).toFixed(1)} Δ=${s.deltaAvgR?.toFixed(3)}`
      );
    }
  }

  console.log(`Report -> ${out}`);
}

for (const tf of ['1min', '5min']) await run(tf);
