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
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT = resolve(ROOT, 'data/reports/strategy-a-delay1-post-entry-path-stability');
const PRE = 10000;
const DEV = 6000;
const BLOCK = 2000;
const CHECKPOINTS = [1, 2, 3];
const HORIZONS = [5, 10, 20];
const STATES = ['<=.25R', '>.25-.50R', '>.50-.75R', '>.75-1.00R'];

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
  const wins = rs.filter(x => x > 0).reduce((a, b) => a + b, 0);
  const losses = -rs.filter(x => x < 0).reduce((a, b) => a + b, 0);
  return losses > 0 ? wins / losses : null;
};
const stats = rows => {
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  return { n: rs.length, avgR: mean(rs), PF: pf(rs), WR: pct(rs.filter(x => x > 0).length, rs.length), totalR: rs.reduce((a, b) => a + b, 0) };
};

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
  const risk = Math.abs(c.entry - c.stopLoss);
  if (!(risk > 0)) return [];
  const out = [];
  for (let j = c.entryIndex + 1; j <= Math.min(candles.length - 1, c.entryIndex + 20); j++) {
    const x = candles[j];
    out.push({
      bar: j - c.entryIndex,
      adverse: Math.max(0, (c.direction === 'BUY' ? c.entry - x.low : x.high - c.entry) / risk),
      favorable: Math.max(0, (c.direction === 'BUY' ? x.high - c.entry : c.entry - x.low) / risk),
    });
  }
  return out;
}

function maeAt(p, checkpoint) {
  return Math.max(0, ...p.filter(x => x.bar <= checkpoint).map(x => x.adverse));
}
function state(mae) {
  if (mae <= 0.25) return '<=.25R';
  if (mae <= 0.5) return '>.25-.50R';
  if (mae <= 0.75) return '>.50-.75R';
  if (mae <= 1) return '>.75-1.00R';
  return '>1R';
}

function firstEvent(p, start, end) {
  let plus = null, stop = null;
  for (const x of p) {
    if (x.bar <= start || x.bar > end) continue;
    if (plus === null && x.favorable >= 1) plus = x.bar;
    if (stop === null && x.adverse >= 1) stop = x.bar;
  }
  if (plus === null && stop === null) return 'NONE';
  if (plus !== null && stop !== null && plus === stop) return 'SAME_BAR_AMBIGUOUS';
  if (plus === null) return 'STOP';
  if (stop === null) return 'PLUS1';
  return plus < stop ? 'PLUS1' : 'STOP';
}

function evaluate(rows, checkpoint, horizon) {
  const eligible = rows.filter(r => r.p.some(x => x.bar > checkpoint && x.bar <= horizon));
  const grouped = Object.fromEntries(STATES.map(s => [s, []]));
  for (const r of eligible) {
    const mae = maeAt(r.p, checkpoint);
    const s = state(mae);
    if (grouped[s]) grouped[s].push(r);
  }
  const out = {};
  for (const s of STATES) {
    const bucket = grouped[s];
    const events = bucket.map(r => firstEvent(r.p, checkpoint, horizon));
    const st = stats(bucket);
    out[s] = {
      n: bucket.length,
      share: pct(bucket.length, eligible.length),
      avgR: st.avgR,
      PF: st.PF,
      WR: st.WR,
      plus1BeforeStop: pct(events.filter(x => x === 'PLUS1').length, events.length),
      stopBeforePlus1: pct(events.filter(x => x === 'STOP').length, events.length),
      sameBarAmbiguous: pct(events.filter(x => x === 'SAME_BAR_AMBIGUOUS').length, events.length),
      none: pct(events.filter(x => x === 'NONE').length, events.length),
    };
  }
  return { eligibleN: eligible.length, states: out };
}

async function loadBaseline(tf, candles) {
  const report = JSON.parse(await readFile(resolve(BASE, `${tf}.json`), 'utf8'));
  const cutoff = new Date(candles[PRE].timestamp);
  return (report.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && new Date(t.entryTime) < cutoff);
}

async function run(tf) {
  const raw = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8'));
  const candles = raw.candles ?? raw;
  if (candles.length < PRE) throw new Error(`${tf}: expected at least ${PRE} candles, found ${candles.length}`);
  const baseline = await loadBaseline(tf, candles);
  const canonical = new Map(baseline.map(t => [key(t), t]));
  const rows = [];
  for (let i = 0; i < PRE; i++) {
    const c = buildCandidate(candles, i);
    if (!c) continue;
    const t = canonical.get(key(c));
    if (!t) continue;
    const p = path(candles, c);
    if (p.length) rows.push({ entryIndex: i, entryTime: c.entryTime, direction: c.direction, rMultiple: Number(t.rMultiple), p });
  }

  const windows = [];
  for (let start = 0; start < PRE; start += BLOCK) {
    const end = Math.min(PRE, start + BLOCK);
    const label = start < DEV ? `DEV_${String(start / BLOCK + 1).padStart(2, '0')}` : `VAL_${String((start - DEV) / BLOCK + 1).padStart(2, '0')}`;
    const windowRows = rows.filter(r => r.entryIndex >= start && r.entryIndex < end);
    const stateStability = {};
    for (const checkpoint of CHECKPOINTS) {
      stateStability[`T${checkpoint}`] = {};
      for (const horizon of HORIZONS.filter(h => h > checkpoint)) {
        stateStability[`T${checkpoint}`][`H${horizon}`] = evaluate(windowRows, checkpoint, horizon);
      }
    }
    windows.push({
      label,
      candleStart: start,
      candleEndExclusive: end,
      startTime: candles[start]?.timestamp ?? null,
      endTime: candles[end - 1]?.timestamp ?? null,
      baseline: stats(windowRows),
      stateStability,
    });
  }

  const report = {
    strategy: 'Strategy A',
    mode: 'DELAY1_POST_ENTRY_PATH_STABILITY',
    timeframe: tf,
    scope: { preHoldoutCandles: PRE, devCandles: DEV, valCandles: PRE - DEV, blockCandles: BLOCK, delayExactly: 1, checkpoints: CHECKPOINTS, horizons: HORIZONS },
    methodology: {
      purpose: 'Test whether early post-entry MAE states remain directionally stable across chronological windows.',
      windows: 'Five fixed 2,000-candle windows: DEV_01..03 and VAL_01..02.',
      stateDefinition: 'Maximum adverse excursion from entry through checkpoint: <=.25R, >.25-.50R, >.50-.75R, >.75-1.00R.',
      outcome: 'Canonical baseline AvgR/PF/WR plus future first-event probabilities for +1R before -1R and -1R before +1R.',
      ambiguity: 'If +1R and -1R are first touched on the same candle, classify SAME_BAR_AMBIGUOUS; no intrabar order inferred.',
      noOptimization: true,
      freshHoldoutExcluded: true,
      diagnosticOnly: true,
      productionUntouched: true,
    },
    joined: rows.length,
    overall: stats(rows),
    windows,
    interpretationRule: 'Diagnostic support requires the same qualitative state ordering (low-MAE healthier, high-MAE more hostile) across multiple chronological windows, not merely a pooled average. This report authorizes no production threshold or management rule.',
  };

  await mkdir(OUT, { recursive: true });
  const file = resolve(OUT, `${tf}.json`);
  await writeFile(file, JSON.stringify(report, null, 2));

  console.log(`\n=== ${tf} DELAY1 POST-ENTRY PATH STABILITY ===`);
  console.log(`joined=${rows.length} AvgR=${report.overall.avgR?.toFixed(3) ?? 'n/a'} PF=${report.overall.PF?.toFixed(3) ?? 'n/a'}`);
  for (const w of windows) {
    console.log(`${w.label}: n=${w.baseline.n} AvgR=${w.baseline.avgR?.toFixed(3) ?? 'n/a'} PF=${w.baseline.PF?.toFixed(3) ?? 'n/a'}`);
    for (const checkpoint of CHECKPOINTS) {
      const horizon = HORIZONS.find(h => h > checkpoint);
      const view = w.stateStability[`T${checkpoint}`][`H${horizon}`];
      console.log(`  T${checkpoint}->H${horizon} eligible=${view.eligibleN}`);
      for (const s of STATES) {
        const x = view.states[s];
        console.log(`    ${s}: n=${x.n} AvgR=${x.avgR?.toFixed(3) ?? 'n/a'} PF=${x.PF?.toFixed(3) ?? 'n/a'} +1beforeSTOP=${(100 * (x.plus1BeforeStop ?? 0)).toFixed(1)}% STOPbefore+1=${(100 * (x.stopBeforePlus1 ?? 0)).toFixed(1)}% SAME=${(100 * (x.sameBarAmbiguous ?? 0)).toFixed(1)}%`);
      }
    }
  }
  console.log(`Report -> ${file}`);
}

for (const tf of ['1min', '5min']) await run(tf);
