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
const OUT = resolve(ROOT, 'data/reports/strategy-a-delay1-entry-edge-post-entry-path');
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline');

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

const key = t => `${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`;
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const pct = (n, d) => d ? n / d : null;
const pf = rs => {
  const grossWin = rs.filter(x => x > 0).reduce((a, b) => a + b, 0);
  const grossLoss = -rs.filter(x => x < 0).reduce((a, b) => a + b, 0);
  return grossLoss > 0 ? grossWin / grossLoss : null;
};

function stats(rows) {
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  return { n: rs.length, avgR: mean(rs), totalR: rs.reduce((a, b) => a + b, 0), PF: pf(rs), WR: pct(rs.filter(x => x > 0).length, rs.length) };
}

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
    return { entryIndex: index, entryTime: trigger.timestamp, direction: trigger.direction, entry: trigger.entryPrice, stopLoss: inv.invalidationLevel, tp1: projection.tp1 };
  }
  return null;
}

function path(candles, c) {
  const i = Number(c.entryIndex), e = Number(c.entry), s = Number(c.stopLoss), d = c.direction;
  const risk = Math.abs(e - s);
  if (!Number.isInteger(i) || !Number.isFinite(e) || !Number.isFinite(s) || risk <= 0) return null;
  const out = [];
  for (let j = i + 1; j <= Math.min(candles.length - 1, i + 20); j++) {
    const x = candles[j];
    out.push({ bar: j - i, adverse: Math.max(0, (d === 'BUY' ? e - x.low : x.high - e) / risk), favorable: Math.max(0, (d === 'BUY' ? x.high - e : e - x.low) / risk) });
  }
  return out;
}

function maeAt(p, h) { return Math.max(0, ...p.filter(x => x.bar <= h).map(x => x.adverse)); }
function maeState(mae) {
  if (mae <= .25) return '<=.25R';
  if (mae <= .5) return '>.25-.50R';
  if (mae <= .75) return '>.50-.75R';
  if (mae <= 1) return '>.75-1.00R';
  return '>1R';
}

function firstEvent(p, start, end) {
  let plus1 = null, stop = null;
  for (const x of p) {
    if (x.bar <= start || x.bar > end) continue;
    if (plus1 === null && x.favorable >= 1) plus1 = x.bar;
    if (stop === null && x.adverse >= 1) stop = x.bar;
  }
  if (plus1 === null && stop === null) return 'NONE';
  if (plus1 !== null && stop !== null && plus1 === stop) return 'SAME_BAR_AMBIGUOUS';
  if (plus1 === null) return 'STOP';
  if (stop === null) return 'PLUS1';
  return plus1 < stop ? 'PLUS1' : 'STOP';
}

function transition(bucket, checkpoint, horizon, eligibleN) {
  const future = bucket.filter(r => r.p.some(x => x.bar > checkpoint && x.bar <= horizon));
  const first = future.map(r => firstEvent(r.p, checkpoint, horizon));
  const rs = future.map(r => r.rMultiple);
  return {
    n: future.length,
    shareOfEligible: pct(future.length, eligibleN),
    avgR: mean(rs),
    totalR: rs.reduce((a, b) => a + b, 0),
    PF: pf(rs),
    WR: pct(rs.filter(x => x > 0).length, rs.length),
    plus1Rate: pct(future.filter(r => r.p.some(x => x.bar > checkpoint && x.bar <= horizon && x.favorable >= 1)).length, future.length),
    plus2Rate: pct(future.filter(r => r.p.some(x => x.bar > checkpoint && x.bar <= horizon && x.favorable >= 2)).length, future.length),
    stopRate: pct(future.filter(r => r.p.some(x => x.bar > checkpoint && x.bar <= horizon && x.adverse >= 1)).length, future.length),
    plus1BeforeStopRate: pct(first.filter(x => x === 'PLUS1').length, future.length),
    stopBeforePlus1Rate: pct(first.filter(x => x === 'STOP').length, future.length),
    sameBarRate: pct(first.filter(x => x === 'SAME_BAR_AMBIGUOUS').length, future.length),
    noneRate: pct(first.filter(x => x === 'NONE').length, future.length),
  };
}

function stateRows(rows, checkpoint, survivorsOnly) {
  const eligible = rows.filter(r => !survivorsOnly || r.p.filter(x => x.bar <= checkpoint).every(x => x.adverse < 1));
  const grouped = {};
  for (const r of eligible) (grouped[maeState(maeAt(r.p, checkpoint))] ??= []).push(r);
  return { eligibleN: eligible.length, grouped };
}

async function loadBase(tf, candles, fresh) {
  const report = JSON.parse(await readFile(resolve(BASE, `${tf}.json`), 'utf8'));
  const cutoff = new Date(candles[PRE].timestamp);
  return (report.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && (fresh ? new Date(t.entryTime) >= cutoff : new Date(t.entryTime) < cutoff));
}

async function run(tf) {
  const raw = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8'));
  const candles = raw.candles ?? raw;
  if (candles.length < PRE + FRESH) throw new Error(`${tf}: expected ${PRE + FRESH} candles, found ${candles.length}`);
  const pre = await loadBase(tf, candles, false), fresh = await loadBase(tf, candles, true);
  const preMap = new Map(pre.map(t => [key(t), t])), freshMap = new Map(fresh.map(t => [key(t), t]));
  const makeRows = (start, end, map) => {
    const rows = [];
    for (let i = start; i < end; i++) {
      const c = buildCandidate(candles, i);
      if (!c) continue;
      const t = map.get(key(c));
      if (!t) continue;
      const p = path(candles, c);
      if (p) rows.push({ entryIndex: i, entryTime: c.entryTime, direction: c.direction, rMultiple: Number(t.rMultiple), p });
    }
    return rows;
  };
  const datasets = { DEV: makeRows(0, DEV, preMap), VAL: makeRows(DEV, PRE, preMap), FRESH: makeRows(PRE, PRE + FRESH, freshMap) };
  const report = {
    strategy: 'Strategy A',
    mode: 'DELAY1_ENTRY_EDGE_VS_POST_ENTRY_PATH',
    timeframe: tf,
    scope: { preHoldoutCandles: PRE, devCandles: DEV, valCandles: PRE - DEV, freshHoldoutCandles: FRESH, delayExactly: 1, checkpoints: CHECKPOINTS, horizons: HORIZONS, maeBinsR: MAE_BINS },
    methodology: {
      purpose: 'Separate the frozen entry outcome from the conditional post-entry path outcome.',
      entryEdge: 'Canonical baseline rMultiple of exact-joined DELAY1 entries; no alternate entry or management.',
      pathState: 'At T1/T2/T3 classify by maximum MAE accumulated from entry through T.',
      conditionalOutcome: 'State-wise canonical AvgR/PF/WR plus future +1R/+2R/-1R event probabilities.',
      survivorView: 'SURVIVORS_ONLY excludes trades that touched canonical 1R stop by the checkpoint; descriptive only.',
      sameBarOHLC: 'Same-candle +1R and -1R first events are SAME_BAR_AMBIGUOUS; no intrabar ordering inferred.',
      fresh: 'Fresh holdout is evaluation-only; no state or threshold is selected from it.',
      noOptimization: true, diagnosticOnly: true, productionUntouched: true,
    },
    parity: {}, datasets: {},
  };
  for (const [name, rows] of Object.entries(datasets)) {
    report.parity[name] = { joined: rows.length, baseline: stats(rows) };
    report.datasets[name] = { summary: stats(rows), states: { ALL: {}, SURVIVORS_ONLY: {} } };
    for (const checkpoint of CHECKPOINTS) for (const horizon of HORIZONS.filter(h => h > checkpoint)) {
      const label = `T${checkpoint}_H${horizon}`;
      for (const survivor of [false, true]) {
        const view = stateRows(rows, checkpoint, survivor), out = {};
        for (const [state, bucket] of Object.entries(view.grouped)) out[state] = transition(bucket, checkpoint, horizon, view.eligibleN);
        report.datasets[name].states[survivor ? 'SURVIVORS_ONLY' : 'ALL'][label] = { eligibleN: view.eligibleN, states: out };
      }
    }
  }
  await mkdir(OUT, { recursive: true });
  const outFile = resolve(OUT, `${tf}.json`);
  await writeFile(outFile, JSON.stringify(report, null, 2));
  console.log(`\n=== ${tf} DELAY1 ENTRY EDGE vs POST-ENTRY PATH ===`);
  for (const [name, rows] of Object.entries(datasets)) {
    const s = stats(rows);
    console.log(`${name}: n=${s.n} AvgR=${s.avgR?.toFixed(3)} PF=${s.PF?.toFixed(3) ?? 'n/a'} WR=${(100 * (s.WR ?? 0)).toFixed(1)} TotalR=${s.totalR.toFixed(3)}`);
    for (const checkpoint of CHECKPOINTS) {
      const horizon = HORIZONS.find(h => h > checkpoint), view = stateRows(rows, checkpoint, true);
      console.log(`  T${checkpoint}->H${horizon} survivors=${view.eligibleN}`);
      for (const [state, bucket] of Object.entries(view.grouped)) {
        const x = transition(bucket, checkpoint, horizon, view.eligibleN);
        console.log(`    ${state}: n=${x.n} AvgR=${x.avgR?.toFixed(3) ?? 'n/a'} PF=${x.PF?.toFixed(3) ?? 'n/a'} +1beforeSTOP=${(100 * (x.plus1BeforeStopRate ?? 0)).toFixed(1)}% STOPbefore+1=${(100 * (x.stopBeforePlus1Rate ?? 0)).toFixed(1)}% +1R=${(100 * (x.plus1Rate ?? 0)).toFixed(1)}% STOP=${(100 * (x.stopRate ?? 0)).toFixed(1)}%`);
      }
    }
  }
  console.log(`Report -> ${outFile}`);
}

for (const tf of ['1min', '5min']) await run(tf);
