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
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-sell-expanded-anatomy');
const DEV = 6000;
const PRE = 10000;

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

const p = (n) => Number.isFinite(n) ? Number(n.toFixed(4)) : null;

function utcMinutes(ts) {
  const d = new Date(ts);
  return d.getUTCHours() * 60 + d.getUTCMinutes();
}

function isNySell(ts) {
  const m = utcMinutes(ts);
  return m >= 16 * 60 && m < 22 * 60;
}

function median(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const i = Math.floor(a.length / 2);
  return a.length % 2 ? a[i] : (a[i - 1] + a[i]) / 2;
}

function quantiles(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return { n: 0 };
  const q = (f) => {
    const pos = (a.length - 1) * f;
    const lo = Math.floor(pos);
    const hi = Math.ceil(pos);
    return p(a[lo] + (a[hi] - a[lo]) * (pos - lo));
  };
  return { n: a.length, min: p(a[0]), p25: q(.25), median: q(.5), p75: q(.75), max: p(a[a.length - 1]), mean: p(a.reduce((s, x) => s + x, 0) / a.length) };
}

function stats(rows) {
  const r = rows.map((x) => Number(x.r)).filter(Number.isFinite);
  const wins = r.filter((x) => x > 0);
  const losses = r.filter((x) => x < 0);
  const gp = wins.reduce((a, b) => a + b, 0);
  const gl = -losses.reduce((a, b) => a + b, 0);
  return { n: r.length, wins: wins.length, losses: losses.length, winRate: r.length ? p(100 * wins.length / r.length) : 0, avgR: r.length ? p(r.reduce((a, b) => a + b, 0) / r.length) : 0, totalR: p(r.reduce((a, b) => a + b, 0)), PF: gl ? p(gp / gl) : (gp ? null : 0) };
}

function classify(r) {
  if (r >= 5) return 'EXCEPTIONAL_WIN';
  if (r > 0) return 'NORMAL_WIN';
  return 'LOSS';
}

function range(candles) {
  if (!candles.length) return null;
  return Math.max(...candles.map((c) => c.high)) - Math.min(...candles.map((c) => c.low));
}

function buildGeometry(candles, index) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < 60) return null;
  const breakouts = detectBreakout(visible, 5);
  const followThrough = detectFollowThrough(visible, breakouts, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
  const spikes = detectSpikeCandidates(visible, breakouts, followThrough, { maxCandles: 8, minDirectionalFraction: .5, maxOverlapFraction: .8 });

  for (const spike of spikes.candidates) {
    if (spike.endIndex >= index) continue;
    const breakout = breakouts.find((x) => x.index === spike.breakoutIndex && x.direction === spike.direction);
    const ft = followThrough.find((x) => x.breakoutIndex === spike.breakoutIndex && x.direction === spike.direction);
    if (!breakout || !ft || ft.followThroughIndex >= index) continue;
    const correction = detectFirstCorrection(visible, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(visible, correction);
    if (!trigger || trigger.index !== index || trigger.direction !== 'SELL' || !isNySell(trigger.timestamp)) continue;
    const projection = projectLeg2(visible, correction);
    if (!projection) continue;
    const inv = getInvalidationRule(correction);
    const ema = buildEMAContext(visible.map((c) => c.close), CONTEXT);
    if (!ema) continue;
    const location = buildLocationContext(trigger.entryPrice, CONTEXT);
    const session = buildSessionContext(trigger.timestamp, CONTEXT);
    const quality = scoreSetup(spike, { ema, location, session });
    if (!quality.tradeAllowed) continue;

    const risk = Math.abs(trigger.entryPrice - inv.invalidationLevel);
    const reward = Math.abs(projection.tp1 - trigger.entryPrice);
    if (!(risk > 0 && reward > 0)) continue;

    const spikeCandles = visible.slice(spike.startIndex, spike.endIndex + 1);
    const preCandles = visible.slice(Math.max(0, spike.startIndex - 5), spike.startIndex);
    const preRange = range(preCandles);
    const spikeSize = Math.abs(spike.endPrice - spike.startPrice);
    const breakoutExtension = spike.direction === 'BEARISH' ? breakout.brokenLevel - breakout.close : breakout.close - breakout.brokenLevel;
    const ftCandle = visible[ft.followThroughIndex];
    const followThroughDistance = ftCandle ? (spike.direction === 'BEARISH' ? breakout.close - ftCandle.close : ftCandle.close - breakout.close) : null;
    const followThroughFromLevel = ftCandle ? (spike.direction === 'BEARISH' ? breakout.brokenLevel - ftCandle.close : ftCandle.close - breakout.brokenLevel) : null;
    const medianSpikeRange = median(spikeCandles.map((c) => c.high - c.low));
    const correctionDepth = Math.abs(correction.extremePrice - spike.startPrice) / Math.max(spikeSize, 1e-9);
    const entryDistanceFromStructuralHigh = Math.abs(trigger.entryPrice - correction.extremePrice);

    return {
      entryIndex: index,
      entryTime: trigger.timestamp,
      r: null,
      classification: null,
      geometry: {
        breakoutExtension,
        breakoutExtensionToPreRange: preRange ? breakoutExtension / preRange : null,
        breakoutToFollowThroughBars: ft.followThroughIndex - breakout.index,
        followThroughDistance,
        followThroughFromLevel,
        followThroughDistanceToPreRange: preRange && followThroughDistance != null ? followThroughDistance / preRange : null,
        spikeSize,
        spikeSizeToMedianRange: medianSpikeRange ? spikeSize / medianSpikeRange : null,
        spikeSizeToPreRange: preRange ? spikeSize / preRange : null,
        spikeDurationBars: spike.endIndex - spike.startIndex + 1,
        correctionBars: correction.correctionExtremeIndex - correction.correctionStartIndex + 1,
        correctionDepth,
        entryDelayFromCorrection: index - correction.correctionExtremeIndex,
        entryDistanceFromStructuralHigh,
        entryDistanceFromStructuralHighPct: entryDistanceFromStructuralHigh / Math.max(spikeSize, 1e-9),
        entryDistanceFromSpikeEnd: Math.abs(trigger.entryPrice - spike.endPrice),
        entryDistanceFromSpikeEndPct: Math.abs(trigger.entryPrice - spike.endPrice) / Math.max(spikeSize, 1e-9),
        stopDistance: risk,
        rewardDistance: reward,
        plannedRR: reward / risk,
        leg1Size: projection.leg1Size,
        structureScore: spike.structureScore,
        overlapScore: spike.overlapScore,
        hasPGAPEvidence: spike.hasPGAPEvidence,
        nearRoundLevel: location.nearRoundLevel,
        emaAligned: ema.aligned,
        qualityScore: quality.score,
        qualityGrade: quality.grade,
      },
    };
  }
  return null;
}

const FEATURE_NAMES = [
  'breakoutExtension','breakoutExtensionToPreRange','followThroughDistance','followThroughFromLevel','followThroughDistanceToPreRange',
  'spikeSize','spikeSizeToMedianRange','spikeSizeToPreRange','spikeDurationBars','correctionBars','correctionDepth','entryDelayFromCorrection',
  'entryDistanceFromStructuralHigh','entryDistanceFromStructuralHighPct','entryDistanceFromSpikeEnd','entryDistanceFromSpikeEndPct',
  'stopDistance','rewardDistance','plannedRR','leg1Size','structureScore','overlapScore',
];

const DISPLAY_FEATURES = [
  ['breakoutExtension', 'BO extension'],
  ['breakoutExtensionToPreRange', 'BO / pre-range'],
  ['followThroughDistanceToPreRange', 'FT / pre-range'],
  ['spikeSizeToPreRange', 'Spike / pre-range'],
  ['spikeSizeToMedianRange', 'Spike / median range'],
  ['correctionBars', 'Correction bars'],
  ['correctionDepth', 'Correction depth'],
  ['entryDelayFromCorrection', 'Entry delay'],
  ['entryDistanceFromStructuralHighPct', 'Entry / structural'],
  ['entryDistanceFromSpikeEndPct', 'Entry / spike-end'],
  ['plannedRR', 'Planned RR'],
  ['structureScore', 'Structure score'],
  ['overlapScore', 'Overlap score'],
];

function featureTable(rows) {
  const groups = { ALL: rows, EXCEPTIONAL_WIN: rows.filter((x) => x.classification === 'EXCEPTIONAL_WIN'), NORMAL_WIN: rows.filter((x) => x.classification === 'NORMAL_WIN'), LOSS: rows.filter((x) => x.classification === 'LOSS') };
  return Object.fromEntries(FEATURE_NAMES.map((f) => [f, Object.fromEntries(Object.entries(groups).map(([g, rs]) => [g, quantiles(rs.map((x) => Number(x.geometry[f])))]))]));
}

function anomalyRows(rows) {
  return rows.filter((x) => x.geometry.correctionBars > 200 || x.geometry.entryDelayFromCorrection > 50);
}

function printStats(statsByName) {
  console.log('');
  console.log('STATS');
  console.table(statsByName);
}

function printClassCounts(rows) {
  const groups = ['EXCEPTIONAL_WIN', 'NORMAL_WIN', 'LOSS'];
  console.log('CLASS COUNTS');
  console.table(Object.fromEntries(groups.map((g) => {
    const rs = rows.filter((x) => x.classification === g);
    return [g, { n: rs.length, DEV: rs.filter((x) => x.split === 'DEV').length, VAL: rs.filter((x) => x.split === 'VAL').length }];
  })));
}

function printFeatureMedians(rows) {
  const groups = ['EXCEPTIONAL_WIN', 'NORMAL_WIN', 'LOSS'];
  console.log('PRE-ENTRY FEATURE MEDIANS');
  console.table(Object.fromEntries(DISPLAY_FEATURES.map(([f, label]) => {
    const out = {};
    for (const g of groups) {
      out[g] = p(median(rows.filter((x) => x.classification === g).map((x) => Number(x.geometry[f]))));
    }
    return [label, out];
  })));
}

function printCompactCases(rows) {
  console.log('CASES (compact)');
  console.table(rows.map((x) => ({
    split: x.split,
    time: x.entryTime,
    R: p(x.r),
    class: x.classification,
    spikePre: p(x.geometry.spikeSizeToPreRange),
    corr: p(x.geometry.correctionDepth),
    corrBars: x.geometry.correctionBars,
    delay: x.geometry.entryDelayFromCorrection,
    entryStruct: p(x.geometry.entryDistanceFromStructuralHighPct),
    RR: p(x.geometry.plannedRR),
  })));
}

async function main() {
  const base = JSON.parse(await readFile(BASE, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles ?? [];
  const byIndex = new Map();

  for (const t of base.trades ?? []) {
    const entryIndex = Number(t.entryIndex);
    const r = Number(t.rMultiple);
    if (!Number.isInteger(entryIndex) || entryIndex < 0 || entryIndex >= PRE) continue;
    if (t.result === 'AMBIGUOUS' || !Number.isFinite(r)) continue;
    if (t.direction !== 'SELL') continue;
    if (!isNySell(t.entryTime)) continue;
    byIndex.set(entryIndex, { r, result: t.result, entryTime: t.entryTime });
  }

  const rows = [];
  for (const [entryIndex, outcome] of byIndex) {
    const row = buildGeometry(candles, entryIndex);
    if (!row) continue;
    if (row.entryTime !== outcome.entryTime) throw new Error(`Lineage mismatch at ${entryIndex}: baseline=${outcome.entryTime} rebuilt=${row.entryTime}`);
    row.r = outcome.r;
    row.classification = classify(row.r);
    row.split = entryIndex < DEV ? 'DEV' : 'VAL';
    rows.push(row);
  }
  rows.sort((a, b) => a.entryIndex - b.entryIndex);

  const dev = rows.filter((x) => x.split === 'DEV');
  const val = rows.filter((x) => x.split === 'VAL');
  const allGroups = { ALL: rows, DEV: dev, VAL: val, EXCEPTIONAL_WIN: rows.filter((x) => x.classification === 'EXCEPTIONAL_WIN'), NORMAL_WIN: rows.filter((x) => x.classification === 'NORMAL_WIN'), LOSS: rows.filter((x) => x.classification === 'LOSS') };
  const anomalies = anomalyRows(rows);

  const output = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_NY_SELL_EXPANDED_ANATOMY',
    timeframe: '5m',
    scope: { source: 'canonical baseline trades + deterministic geometry reconstruction', n: rows.length, dev: dev.length, val: val.length, freshHoldoutExcluded: true, productionUntouched: true },
    session: { definition: 'UTC 16:00 inclusive through 22:00 exclusive', allowedStrategySegments: ['LONDON BUY','LONDON SELL','NEW_YORK BUY','NEW_YORK SELL'], target: 'NEW_YORK SELL' },
    methodology: {
      purpose: 'Expand the prior 15-case NY SELL anatomy to the complete pre-holdout canonical NY SELL sample.',
      outcomeSource: 'Existing canonical baseline outcome; no outcome redefinition.',
      geometrySource: 'Existing deterministic Strategy A detectors replayed candle-by-candle at each canonical NY SELL entry.',
      classification: 'EXCEPTIONAL_WIN r>=5R; NORMAL_WIN 0<r<5R; LOSS r<=0. Descriptive only.',
      noOptimization: true,
      noNewTradingRules: true,
      noThresholdSearch: true,
      freshHoldout: 'locked and excluded',
      lineageCheck: 'rebuilt entry timestamp must equal baseline entry timestamp',
    },
    stats: Object.fromEntries(['ALL','DEV','VAL'].map((k) => [k, stats(allGroups[k])])),
    featureMedians: Object.fromEntries(FEATURE_NAMES.map((f) => [f, Object.fromEntries(['DEV','VAL','EXCEPTIONAL_WIN','NORMAL_WIN','LOSS'].map((g) => [g, quantiles((allGroups[g] ?? []).map((x) => Number(x.geometry[f]))).median]))])),
    featureDistributions: featureTable(rows),
    anomalies: anomalies.map((x) => ({ split: x.split, entryTime: x.entryTime, entryIndex: x.entryIndex, r: x.r, correctionBars: x.geometry.correctionBars, entryDelayFromCorrection: x.geometry.entryDelayFromCorrection })),
    cases: rows.map((x) => ({ split: x.split, entryTime: x.entryTime, entryIndex: x.entryIndex, r: x.r, classification: x.classification, ...x.geometry })),
  };

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(output, null, 2));

  console.log('');
  console.log('════════════════════════════════════════════════════════════');
  console.log('NY SELL — EXPANDED PRE-ENTRY ANATOMY');
  console.log('════════════════════════════════════════════════════════════');
  console.log(`Universe: ${rows.length} canonical NY SELL | DEV=${dev.length} | VAL=${val.length} | Fresh=LOCKED`);
  printStats(output.stats);
  printClassCounts(rows);
  printFeatureMedians(rows);

  if (anomalies.length) {
    console.log('ANOMALIES — DIAGNOSTIC ONLY');
    console.table(anomalies.map((x) => ({ split: x.split, time: x.entryTime, R: p(x.r), correctionBars: x.geometry.correctionBars, entryDelay: x.geometry.entryDelayFromCorrection })));
    console.log('These are detector-lineage diagnostics, not proposed filters.');
  } else {
    console.log('ANOMALIES: none');
  }

  printCompactCases(rows);
  console.log('');
  console.log(`Full machine-readable report -> ${resolve(OUT, '5m.json')}`);
  console.log('No optimization, no new rules, no Fresh Holdout access.');
}

await main();
