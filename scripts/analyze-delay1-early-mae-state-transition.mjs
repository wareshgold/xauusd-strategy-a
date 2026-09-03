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
const FRESH = 5000;
const CHECKPOINTS = [1, 2, 3];
const HORIZONS = [5, 10, 20];
const MAE_BINS = [0.25, 0.5, 0.75, 1];
const OUT = resolve(ROOT, 'data/reports/strategy-a-delay1-early-mae-state-transition');
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

function buildCandidate(candles, index) {
  const v = candles.slice(0, index + 1);
  if (v.length < Math.max(BREAKOUT_LOOKBACK + 2, CONTEXT.emaPeriod)) return null;
  const bo = detectBreakout(v, BREAKOUT_LOOKBACK);
  const ft = detectFollowThrough(v, bo, { maxBarsAfterBreakout: FT_MAX_BARS, requireCloseBeyondBrokenLevel: true });
  const sp = detectSpikeCandidates(v, bo, ft, {
    maxCandles: SPIKE_MAX_CANDLES,
    minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION,
    maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION,
  });

  for (const spike of sp.candidates) {
    if (spike.endIndex >= index) continue;
    const correction = detectFirstCorrection(v, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(v, correction);
    if (!trigger || trigger.index !== index) continue;
    if (index - correction.correctionExtremeIndex !== 1) continue;
    const projection = projectLeg2(v, correction);
    if (!projection) continue;
    const inv = getInvalidationRule(correction);
    const ema = buildEMAContext(v.map(c => c.close), CONTEXT);
    if (!ema) continue;
    const location = buildLocationContext(trigger.entryPrice, CONTEXT);
    const session = buildSessionContext(trigger.timestamp, CONTEXT);
    const quality = scoreSetup(spike, { ema, location, session });
    if (!quality.tradeAllowed) continue;
    const risk = Math.abs(trigger.entryPrice - inv.invalidationLevel);
    const reward = Math.abs(projection.tp1 - trigger.entryPrice);
    if (!(risk > 0 && reward > 0)) continue;
    if (!(trigger.direction === 'BUY' ? projection.tp1 > trigger.entryPrice : projection.tp1 < trigger.entryPrice)) continue;

    return {
      entryIndex: index,
      entryTime: trigger.timestamp,
      direction: trigger.direction,
      entry: trigger.entryPrice,
      stopLoss: inv.invalidationLevel,
      tp1: projection.tp1,
    };
  }
  return null;
}

function pathFor(candles, candidate) {
  const i = Number(candidate.entryIndex);
  const e = Number(candidate.entry);
  const s = Number(candidate.stopLoss);
  const d = String(candidate.direction).toUpperCase();
  const risk = Math.abs(e - s);
  if (!Number.isInteger(i) || !Number.isFinite(e) || !Number.isFinite(s) || !(risk > 0) || !['BUY', 'SELL'].includes(d)) return null;

  const path = [];
  for (let j = i + 1; j <= Math.min(candles.length - 1, i + Math.max(...HORIZONS)); j++) {
    const c = candles[j];
    path.push({
      bar: j - i,
      adverse: Math.max(0, (d === 'BUY' ? e - c.low : c.high - e) / risk),
      favorable: Math.max(0, (d === 'BUY' ? c.high - e : e - c.low) / risk),
    });
  }
  return { risk, direction: d, path };
}

function maeThrough(path, h) {
  return Math.max(0, ...path.filter(x => x.bar <= h).map(x => x.adverse));
}

function stateForMae(mae) {
  if (mae <= MAE_BINS[0]) return `<=${MAE_BINS[0]}R`;
  if (mae <= MAE_BINS[1]) return `>${MAE_BINS[0]}-${MAE_BINS[1]}R`;
  if (mae <= MAE_BINS[2]) return `>${MAE_BINS[1]}-${MAE_BINS[2]}R`;
  if (mae <= MAE_BINS[3]) return `>${MAE_BINS[2]}-${MAE_BINS[3]}R`;
  return `>${MAE_BINS[3]}R`;
}

function firstEvent(path, horizon) {
  let plus1 = null;
  let plus2 = null;
  let stop = null;
  for (const x of path.filter(p => p.bar <= horizon)) {
    if (plus1 === null && x.favorable >= 1) plus1 = x.bar;
    if (plus2 === null && x.favorable >= 2) plus2 = x.bar;
    if (stop === null && x.adverse >= 1) stop = x.bar;
  }
  const events = [];
  if (plus1 !== null) events.push(['PLUS1', plus1]);
  if (stop !== null) events.push(['STOP', stop]);
  if (!events.length) return { event: 'NONE', bar: null };
  const minBar = Math.min(...events.map(x => x[1]));
  const at = events.filter(x => x[1] === minBar).map(x => x[0]);
  if (at.length > 1) return { event: 'SAME_BAR_AMBIGUOUS', bar: minBar };
  return { event: at[0], bar: minBar, plus2Bar: plus2 };
}

function futureOutcome(path, checkpoint, horizon) {
  const future = path.filter(x => x.bar > checkpoint && x.bar <= horizon);
  const maxF = Math.max(0, ...future.map(x => x.favorable));
  const maxA = Math.max(0, ...future.map(x => x.adverse));
  const hit1 = maxF >= 1;
  const hit2 = maxF >= 2;
  const hitStop = maxA >= 1;
  const first = firstEvent(future, horizon);
  return {
    hitPlus1: hit1,
    hitPlus2: hit2,
    hitStop: hitStop,
    firstEvent: first.event,
    firstEventBarFromEntry: first.bar,
  };
}

function transitionSummary(rows, checkpoint, horizon, survivorsOnly) {
  const eligible = rows.filter(r => {
    if (survivorsOnly && r.checkpoints[checkpoint].stopTouched) return false;
    return r.path.some(x => x.bar > checkpoint && x.bar <= horizon);
  });

  const states = {};
  for (const row of eligible) {
    const state = row.checkpoints[checkpoint].state;
    if (!states[state]) states[state] = [];
    states[state].push(row);
  }

  const out = {};
  for (const [state, bucket] of Object.entries(states)) {
    const outcomes = bucket.map(r => r.future[checkpoint][horizon]);
    const first = outcomes.map(x => x.firstEvent);
    out[state] = {
      n: bucket.length,
      share: pct(bucket.length, eligible.length),
      hitPlus1Rate: pct(outcomes.filter(x => x.hitPlus1).length, bucket.length),
      hitPlus2Rate: pct(outcomes.filter(x => x.hitPlus2).length, bucket.length),
      hitStopRate: pct(outcomes.filter(x => x.hitStop).length, bucket.length),
      plus1BeforeStopRate: pct(first.filter(x => x === 'PLUS1').length, bucket.length),
      stopBeforePlus1Rate: pct(first.filter(x => x === 'STOP').length, bucket.length),
      sameBarAmbiguousRate: pct(first.filter(x => x === 'SAME_BAR_AMBIGUOUS').length, bucket.length),
      noEventRate: pct(first.filter(x => x === 'NONE').length, bucket.length),
    };
  }
  return { eligibleN: eligible.length, states: out };
}

function datasetRows(candles, canonicalTrades, start, end) {
  const canonical = new Map(canonicalTrades.map(t => [key(t), t]));
  const rows = [];
  for (let i = start; i < end; i++) {
    const candidate = buildCandidate(candles, i);
    if (!candidate) continue;
    const trade = canonical.get(key(candidate));
    if (!trade) continue;
    const p = pathFor(candles, candidate);
    if (!p) continue;

    const checkpoints = {};
    const future = {};
    for (const h of CHECKPOINTS) {
      const mae = maeThrough(p.path, h);
      checkpoints[h] = {
        mae,
        state: stateForMae(mae),
        stopTouched: mae >= 1,
      };
      future[h] = {};
      for (const horizon of HORIZONS) future[h][horizon] = futureOutcome(p.path, h, horizon);
    }

    rows.push({
      entryIndex: i,
      entryTime: candidate.entryTime,
      direction: candidate.direction,
      rMultiple: Number(trade.rMultiple),
      path: p.path,
      checkpoints,
      future,
    });
  }
  return rows;
}

function summary(rows) {
  const rs = rows.map(r => r.rMultiple).filter(Number.isFinite);
  return { n: rs.length, avgR: mean(rs), totalR: rs.reduce((a, b) => a + b, 0) };
}

async function loadCanonical(tf, candles, fresh) {
  const base = JSON.parse(await readFile(resolve(BASE_DIR, `${tf}.json`), 'utf8'));
  if (!fresh) {
    return (base.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && new Date(t.entryTime) < new Date(candles[PRE].timestamp));
  }
  const cutoff = new Date(candles[PRE].timestamp);
  return (base.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && new Date(t.entryTime) >= cutoff);
}

async function run(tf) {
  const raw = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8'));
  const candles = raw.candles ?? raw;
  if (candles.length < PRE + FRESH) throw new Error(`${tf}: expected at least ${PRE + FRESH} candles, found ${candles.length}`);

  const preCanonical = await loadCanonical(tf, candles, false);
  const freshCanonical = await loadCanonical(tf, candles, true);
  const dev = datasetRows(candles, preCanonical, 0, DEV);
  const val = datasetRows(candles, preCanonical, DEV, PRE);
  const fresh = datasetRows(candles, freshCanonical, PRE, PRE + FRESH);

  const datasets = { DEV: dev, VAL: val, FRESH: fresh };
  const report = {
    strategy: 'Strategy A',
    mode: 'DELAY1_EARLY_MAE_STATE_TRANSITION',
    timeframe: tf,
    scope: {
      preHoldoutCandles: PRE,
      devCandles: DEV,
      valCandles: PRE - DEV,
      freshHoldoutCandles: FRESH,
      delayExactly: 1,
      checkpoints: CHECKPOINTS,
      horizons: HORIZONS,
      maeBinsR: MAE_BINS,
    },
    methodology: {
      state: 'At checkpoint T, classify the trade by maximum adverse excursion from entry through T completed candles.',
      actionableSurvivor: 'A survivor has not touched canonical 1R stop through checkpoint T.',
      futureEvents: 'After checkpoint T, measure whether +1R, +2R, or -1R is reached by the horizon; first-event ordering is candle-level only.',
      sameBarOHLC: 'If +1R and -1R are both first reached on the same candle, classify SAME_BAR_AMBIGUOUS; no intrabar ordering is inferred.',
      outcomeSource: 'canonical baseline trade rMultiple',
      freshFeatureSource: 'DELAY1 entries reconstructed directly on fresh candles and exact-joined to canonical fresh outcomes',
      noOptimization: true,
      noProductionChange: true,
      diagnosticOnly: true,
    },
    parity: Object.fromEntries(Object.entries(datasets).map(([name, rows]) => [name, { joined: rows.length, canonical: name === 'DEV' || name === 'VAL' ? preCanonical.length : freshCanonical.length }])),
    datasets: {},
  };

  for (const [name, rows] of Object.entries(datasets)) {
    report.datasets[name] = {
      summary: summary(rows),
      transitions: {
        ALL: {},
        SURVIVORS_ONLY: {},
      },
    };
    for (const h of CHECKPOINTS) {
      for (const horizon of HORIZONS.filter(x => x > h)) {
        report.datasets[name].transitions.ALL[`T${h}_H${horizon}`] = transitionSummary(rows, h, horizon, false);
        report.datasets[name].transitions.SURVIVORS_ONLY[`T${h}_H${horizon}`] = transitionSummary(rows, h, horizon, true);
      }
    }
  }

  await mkdir(OUT, { recursive: true });
  const out = resolve(OUT, `${tf}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));

  console.log(`\n=== ${tf} DELAY1 EARLY MAE STATE TRANSITION ===`);
  for (const [name, rows] of Object.entries(datasets)) {
    const s = summary(rows);
    console.log(`${name}: n=${s.n} AvgR=${s.avgR?.toFixed(3)} TotalR=${s.totalR.toFixed(3)}`);
    for (const h of CHECKPOINTS) {
      for (const horizon of HORIZONS.filter(x => x > h)) {
        const t = report.datasets[name].transitions.SURVIVORS_ONLY[`T${h}_H${horizon}`];
        console.log(`  T${h}->H${horizon} survivors=${t.eligibleN}`);
        for (const [state, x] of Object.entries(t.states)) {
          console.log(`    ${state}: n=${x.n} +1R=${(100 * x.hitPlus1Rate).toFixed(1)}% +2R=${(100 * x.hitPlus2Rate).toFixed(1)}% STOP=${(100 * x.hitStopRate).toFixed(1)}% +1beforeSTOP=${(100 * x.plus1BeforeStopRate).toFixed(1)}% STOPbefore+1=${(100 * x.stopBeforePlus1Rate).toFixed(1)}% SAME=${(100 * x.sameBarAmbiguousRate).toFixed(1)}% NONE=${(100 * x.noEventRate).toFixed(1)}%`);
        }
      }
    }
  }
  console.log(`Report -> ${out}`);
}

for (const tf of ['1min', '5min']) await run(tf);
