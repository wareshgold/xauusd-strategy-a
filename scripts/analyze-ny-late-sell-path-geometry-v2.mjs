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
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-late-sell-path-geometry-v2');
const PRE = 10000;
const DEV = 6000;
const TZ_L = 'Europe/London';
const TZ_N = 'America/New_York';
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

function p(n) { return Number.isFinite(n) ? Number(n.toFixed(6)) : null; }
function stats(rows) {
  const r = rows.map((x) => Number(x.r)).filter(Number.isFinite);
  const wins = r.filter((x) => x > 0);
  const losses = r.filter((x) => x < 0);
  const gp = wins.reduce((a, b) => a + b, 0);
  const gl = -losses.reduce((a, b) => a + b, 0);
  return {
    n: r.length,
    winRate: r.length ? wins.length / r.length : 0,
    avgR: r.length ? r.reduce((a, b) => a + b, 0) / r.length : 0,
    totalR: r.reduce((a, b) => a + b, 0),
    PF: gl ? gp / gl : (gp ? null : 0),
  };
}
function localParts(ts, tz) {
  const parts = new Intl.DateTimeFormat('en-GB', { timeZone: tz, hour12: false, hour: '2-digit', minute: '2-digit' }).formatToParts(new Date(ts));
  return { hour: Number(parts.find((x) => x.type === 'hour')?.value), minute: Number(parts.find((x) => x.type === 'minute')?.value) };
}
function inNyLate(ts) {
  const l = localParts(ts, TZ_L);
  const n = localParts(ts, TZ_N);
  return l.hour * 60 + l.minute >= 480 && n.hour * 60 + n.minute >= 840 && n.hour * 60 + n.minute < 1020;
}
function key(c) {
  return `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;
}
function median(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
}
function range(candles) {
  if (!candles.length) return null;
  return Math.max(...candles.map((c) => c.high)) - Math.min(...candles.map((c) => c.low));
}
function build(candles, index) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < 60) return null;
  const breakouts = detectBreakout(visible, 5);
  const followThrough = detectFollowThrough(visible, breakouts, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
  const spikes = detectSpikeCandidates(visible, breakouts, followThrough, { maxCandles: 8, minDirectionalFraction: 0.5, maxOverlapFraction: 0.8 });

  for (const spike of spikes.candidates) {
    if (spike.endIndex >= index) continue;
    const breakout = breakouts.find((x) => x.index === spike.breakoutIndex && x.direction === spike.direction);
    const ft = followThrough.find((x) => x.breakoutIndex === spike.breakoutIndex && x.direction === spike.direction);
    if (!breakout || !ft || ft.followThroughIndex >= index) continue;
    const correction = detectFirstCorrection(visible, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(visible, correction);
    if (!trigger || trigger.index !== index || trigger.direction !== 'SELL' || !inNyLate(trigger.timestamp)) continue;
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
    const breakoutExtension = spike.direction === 'BEARISH'
      ? breakout.brokenLevel - breakout.close
      : breakout.close - breakout.brokenLevel;
    const followThroughCandle = visible[ft.followThroughIndex];
    const followThroughDistance = followThroughCandle
      ? (spike.direction === 'BEARISH' ? breakout.close - followThroughCandle.close : followThroughCandle.close - breakout.close)
      : null;
    const followThroughFromLevel = followThroughCandle
      ? (spike.direction === 'BEARISH' ? breakout.brokenLevel - followThroughCandle.close : followThroughCandle.close - breakout.brokenLevel)
      : null;
    const medianSpikeRange = median(spikeCandles.map((c) => c.high - c.low));
    const correctionDepth = Math.abs(correction.extremePrice - spike.startPrice) / Math.max(spikeSize, 1e-9);
    const entryDistanceFromStructuralHigh = Math.abs(trigger.entryPrice - correction.extremePrice);

    return {
      entryIndex: index,
      direction: 'SELL',
      entry: trigger.entryPrice,
      stopLoss: inv.invalidationLevel,
      tp1: projection.tp1,
      entryTime: trigger.timestamp,
      r: null,
      features: {
        breakoutIndex: breakout.index,
        breakoutLevel: breakout.brokenLevel,
        breakoutClose: breakout.close,
        breakoutExtension,
        breakoutExtensionToPreRange: preRange ? breakoutExtension / preRange : null,
        followThroughIndex: ft.followThroughIndex,
        breakoutToFollowThroughBars: ft.followThroughIndex - breakout.index,
        followThroughDistance,
        followThroughFromLevel,
        followThroughDistanceToPreRange: preRange && followThroughDistance != null ? followThroughDistance / preRange : null,
        spikeStartIndex: spike.startIndex,
        spikeEndIndex: spike.endIndex,
        spikeBars: spike.endIndex - spike.startIndex + 1,
        spikeSize,
        spikeSizeToMedianRange: medianSpikeRange ? spikeSize / medianSpikeRange : null,
        spikeSizeToPreRange: preRange ? spikeSize / preRange : null,
        spikeDurationBars: spike.endIndex - spike.startIndex + 1,
        structuralHigh: correction.extremePrice,
        correctionStartIndex: correction.correctionStartIndex,
        correctionExtremeIndex: correction.correctionExtremeIndex,
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
function summarize(rows, name) {
  const values = rows.map((x) => x.features[name]).filter(Number.isFinite);
  if (!values.length) return { n: 0 };
  return { n: values.length, min: p(Math.min(...values)), median: p(median(values)), max: p(Math.max(...values)), mean: p(values.reduce((a, b) => a + b, 0) / values.length) };
}
function archetypes(rows) {
  const defs = [
    ['fastCorrection', (x) => x.features.correctionBars <= 2],
    ['slowCorrection', (x) => x.features.correctionBars >= 3],
    ['shallowCorrection', (x) => x.features.correctionDepth <= 0.5],
    ['deepCorrection', (x) => x.features.correctionDepth > 0.5],
    ['fastEntry', (x) => x.features.entryDelayFromCorrection <= 1],
    ['delayedEntry', (x) => x.features.entryDelayFromCorrection >= 2],
    ['cleanStructure', (x) => x.features.structureScore >= 0.7],
    ['lessCleanStructure', (x) => x.features.structureScore < 0.7],
    ['fastShallow', (x) => x.features.entryDelayFromCorrection <= 1 && x.features.correctionDepth <= 0.5],
  ];
  return Object.fromEntries(defs.map(([name, fn]) => [name, stats(rows.filter(fn))]));
}
async function run(tf) {
  const candles = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8')).candles ?? [];
  const base = JSON.parse(await readFile(resolve(BASE, `${tf}.json`), 'utf8'));
  const cutoff = new Date(candles[PRE].timestamp);
  const devCut = new Date(candles[DEV].timestamp);
  const outcomes = new Map((base.trades ?? [])
    .filter((t) => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && new Date(t.entryTime) < cutoff)
    .map((t) => [key(t), Number(t.rMultiple)]));
  const rows = [];
  for (let i = 59; i < PRE; i += 1) {
    const row = build(candles, i);
    if (!row) continue;
    const r = outcomes.get(key(row));
    if (r == null) continue;
    row.r = r;
    row.features.r = r;
    rows.push(row);
  }
  rows.sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));
  const dev = rows.filter((x) => new Date(x.entryTime) < devCut);
  const val = rows.filter((x) => new Date(x.entryTime) >= devCut && new Date(x.entryTime) < cutoff);
  const featureNames = [
    'breakoutExtension', 'breakoutExtensionToPreRange', 'breakoutToFollowThroughBars', 'followThroughDistance',
    'followThroughFromLevel', 'followThroughDistanceToPreRange', 'spikeBars', 'spikeSize', 'spikeSizeToMedianRange',
    'spikeSizeToPreRange', 'spikeDurationBars', 'correctionBars', 'correctionDepth', 'entryDelayFromCorrection',
    'entryDistanceFromStructuralHigh', 'entryDistanceFromStructuralHighPct', 'entryDistanceFromSpikeEnd',
    'entryDistanceFromSpikeEndPct', 'stopDistance', 'rewardDistance', 'plannedRR', 'leg1Size', 'structureScore', 'overlapScore',
  ];
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_NY_LATE_SELL_PATH_GEOMETRY_V2',
    timeframe: tf,
    window: { londonStart: '08:00 Europe/London', nyLateStart: '14:00 America/New_York', nyEnd: '17:00 America/New_York', dstAware: true },
    scope: { preHoldoutCandles: PRE, devCandles: DEV, valCandles: PRE - DEV, freshHoldoutExcluded: true, productionUntouched: true },
    universe: { n: rows.length, dev: dev.length, val: val.length, all: stats(rows), DEV: stats(dev), VAL: stats(val) },
    featureDistributions: Object.fromEntries(featureNames.map((name) => [name, { all: summarize(rows, name), DEV: summarize(dev, name), VAL: summarize(val, name) }])),
    fixedArchetypes: { DEV: archetypes(dev), VAL: archetypes(val) },
    cases: rows.map((x) => ({ entryTime: x.entryTime, entryIndex: x.entryIndex, r: x.r, ...x.features })),
    methodology: {
      canonicalReconstruction: true,
      outcomeJoin: 'exact entryIndex + direction + entry + stopLoss + tp1 key',
      geometry: 'descriptive only; breakout level, breakout extension, follow-through distance/timing, spike geometry, correction geometry, structural high and entry geometry are measured without changing detectors',
      precedingRange: '5 completed candles immediately before spike start; descriptive normalization only',
      thresholds: 'no new thresholds introduced; existing detector/archetype definitions retained',
      valRole: 'chronological OOS stability check only',
      freshHoldout: 'locked and excluded',
      productionRule: 'unchanged',
    },
    interpretation: 'Path Geometry V2 completes the missing breakout-to-spike-to-correction-to-entry measurements. It is intended to inspect the 5m NY-Late SELL cases row-by-row and compare DEV versus VAL before any hypothesis is frozen.',
  };
  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, `${tf}.json`), JSON.stringify(report, null, 2));
  console.log(`${tf}: rows=${rows.length} DEV=${dev.length} VAL=${val.length} | DEV avgR=${p(stats(dev).avgR)} PF=${p(stats(dev).PF)} | VAL avgR=${p(stats(val).avgR)} PF=${p(stats(val).PF)}`);
  console.table(rows.map((x) => ({ time: x.entryTime, r: x.r, boExt: p(x.features.breakoutExtension), ftDist: p(x.features.followThroughDistance), spike: p(x.features.spikeSize), preRatio: p(x.features.spikeSizeToPreRange), corr: p(x.features.correctionDepth), delay: x.features.entryDelayFromCorrection, entryStruct: p(x.features.entryDistanceFromStructuralHigh), rr: p(x.features.plannedRR) })));
}

await run(process.argv[2] ?? '5m');
