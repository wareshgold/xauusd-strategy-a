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
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-late-sell-path-geometry-v1');
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
  const lm = l.hour * 60 + l.minute;
  const nm = n.hour * 60 + n.minute;
  return lm >= 480 && nm >= 840 && nm < 1020;
}
function key(c) {
  return `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;
}
function medianRange(candles) {
  const ranges = candles.map((c) => c.high - c.low).filter((x) => x > 0).sort((a, b) => a - b);
  if (!ranges.length) return null;
  const m = Math.floor(ranges.length / 2);
  return ranges.length % 2 ? ranges[m] : (ranges[m - 1] + ranges[m]) / 2;
}
function build(candles, index) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < 60) return null;
  const bo = detectBreakout(visible, 5);
  const ft = detectFollowThrough(visible, bo, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
  const sp = detectSpikeCandidates(visible, bo, ft, { maxCandles: 8, minDirectionalFraction: 0.5, maxOverlapFraction: 0.8 });
  for (const spike of sp.candidates) {
    if (spike.endIndex >= index) continue;
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
    const medianBodyRange = medianRange(spikeCandles);
    const spikeSize = Math.abs(spike.endPrice - spike.startPrice);
    const correctionDepth = Math.abs(correction.extremePrice - spike.startPrice) / Math.max(spikeSize, 1e-9);
    const leg1Size = projection.leg1Size;

    return {
      entryIndex: index,
      direction: 'SELL',
      entry: trigger.entryPrice,
      stopLoss: inv.invalidationLevel,
      tp1: projection.tp1,
      entryTime: trigger.timestamp,
      features: {
        r: null,
        spikeStartIndex: spike.startIndex,
        breakoutIndex: spike.breakoutIndex ?? null,
        followThroughIndex: spike.followThroughIndex ?? null,
        spikeEndIndex: spike.endIndex,
        spikeBars: spike.endIndex - spike.startIndex + 1,
        breakoutToFollowThroughBars: (spike.followThroughIndex ?? spike.endIndex) - (spike.breakoutIndex ?? spike.startIndex),
        breakoutExtension: null,
        spikeSize,
        spikeSizeToMedianRange: medianBodyRange ? spikeSize / medianBodyRange : null,
        correctionBars: correction.correctionExtremeIndex - spike.endIndex,
        correctionDepth,
        entryDelayFromCorrection: index - correction.correctionExtremeIndex,
        entryDistanceFromSpikeEnd: Math.abs(trigger.entryPrice - spike.endPrice),
        entryDistanceFromSpikeEndPct: Math.abs(trigger.entryPrice - spike.endPrice) / Math.max(spikeSize, 1e-9),
        entryDistanceFromCorrectionExtreme: Math.abs(trigger.entryPrice - correction.extremePrice),
        entryDistanceFromCorrectionExtremePct: Math.abs(trigger.entryPrice - correction.extremePrice) / Math.max(spikeSize, 1e-9),
        stopDistance: risk,
        rewardDistance: reward,
        plannedRR: reward / risk,
        leg1Size,
        correctionExtreme: correction.extremePrice,
        spikeStartPrice: spike.startPrice,
        spikeEndPrice: spike.endPrice,
        structureScore: spike.structureScore,
        overlapScore: spike.overlapScore,
        hasPGAPEvidence: spike.hasPGAPEvidence,
        nearRoundLevel: location.nearRoundLevel,
        emaAligned: ema.aligned,
        qualityScore: quality.score,
        qualityGrade: quality.grade,
      },
      meta: { brokenLevel: null, breakoutClose: null },
    };
  }
  return null;
}
function addBreakoutGeometry(row, candles) {
  if (row.meta.breakoutIndex == null) return row;
  const b = candles[row.meta.breakoutIndex];
  return row;
}
function summarizeFeature(rows, name) {
  const values = rows.map((x) => x.features[name]).filter(Number.isFinite);
  if (!values.length) return { n: 0 };
  const sorted = [...values].sort((a, b) => a - b);
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const m = Math.floor(sorted.length / 2);
  return { n: values.length, min: p(sorted[0]), median: p(sorted.length % 2 ? sorted[m] : (sorted[m - 1] + sorted[m]) / 2), max: p(sorted.at(-1)), mean: p(mean) };
}
function booleanAttribution(rows, name) {
  const yes = rows.filter((x) => x.features[name] === true);
  const no = rows.filter((x) => x.features[name] === false);
  return { yes: stats(yes), no: stats(no) };
}
function fixedArchetypes(rows) {
  const defs = [
    ['fastCorrection', (x) => x.features.correctionBars <= 2],
    ['slowCorrection', (x) => x.features.correctionBars >= 3],
    ['shallowCorrection', (x) => x.features.correctionDepth <= 0.5],
    ['deepCorrection', (x) => x.features.correctionDepth > 0.5],
    ['fastEntry', (x) => x.features.entryDelayFromCorrection <= 1],
    ['delayedEntry', (x) => x.features.entryDelayFromCorrection >= 2],
    ['shortSpike', (x) => x.features.spikeBars <= 4],
    ['longSpike', (x) => x.features.spikeBars >= 5],
    ['cleanStructure', (x) => x.features.structureScore >= 0.7],
    ['lessCleanStructure', (x) => x.features.structureScore < 0.7],
    ['cleanOverlap', (x) => x.features.overlapScore >= 0.7],
    ['lessCleanOverlap', (x) => x.features.overlapScore < 0.7],
    ['roundLevel', (x) => x.features.nearRoundLevel],
    ['emaAligned', (x) => x.features.emaAligned],
    ['fastShallow', (x) => x.features.entryDelayFromCorrection <= 1 && x.features.correctionDepth <= 0.5],
    ['cleanFastShallow', (x) => x.features.structureScore >= 0.7 && x.features.entryDelayFromCorrection <= 1 && x.features.correctionDepth <= 0.5],
  ];
  return Object.fromEntries(defs.map(([name, filter]) => [name, stats(rows.filter(filter))]));
}
async function run(tf) {
  const candles = (JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8')).candles ?? []);
  const base = JSON.parse(await readFile(resolve(BASE, `${tf}.json`), 'utf8'));
  const cutoff = new Date(candles[PRE].timestamp);
  const devCut = new Date(candles[DEV].timestamp);
  const outcomes = new Map((base.trades ?? [])
    .filter((t) => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && new Date(t.entryTime) < cutoff)
    .map((t) => [key(t), Number(t.rMultiple)]));
  const rows = [];
  for (let i = 59; i < PRE; i += 1) {
    const c = build(candles, i);
    if (!c) continue;
    const r = outcomes.get(key(c));
    if (r == null) continue;
    c.features.r = r;
    rows.push({ ...c, r });
  }
  rows.sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));
  const dev = rows.filter((x) => new Date(x.entryTime) < devCut);
  const val = rows.filter((x) => new Date(x.entryTime) >= devCut && new Date(x.entryTime) < cutoff);
  const featureNames = [
    'spikeBars', 'breakoutToFollowThroughBars', 'spikeSize', 'spikeSizeToMedianRange',
    'correctionBars', 'correctionDepth', 'entryDelayFromCorrection',
    'entryDistanceFromSpikeEnd', 'entryDistanceFromSpikeEndPct',
    'entryDistanceFromCorrectionExtreme', 'entryDistanceFromCorrectionExtremePct',
    'stopDistance', 'rewardDistance', 'plannedRR', 'leg1Size', 'structureScore', 'overlapScore',
  ];
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_NY_LATE_SELL_PATH_GEOMETRY_V1',
    timeframe: tf,
    window: { londonStart: '08:00 Europe/London', nyLateStart: '14:00 America/New_York', nyEnd: '17:00 America/New_York', dstAware: true },
    scope: { preHoldoutCandles: PRE, devCandles: DEV, valCandles: PRE - DEV, freshHoldoutExcluded: true, productionUntouched: true },
    universe: { n: rows.length, dev: dev.length, val: val.length, baseline: stats(rows), DEV: stats(dev), VAL: stats(val) },
    featureDistributions: Object.fromEntries(featureNames.map((name) => [name, { all: summarizeFeature(rows, name), DEV: summarizeFeature(dev, name), VAL: summarizeFeature(val, name) }])),
    booleanAttribution: {
      nearRoundLevel: { DEV: booleanAttribution(dev, 'nearRoundLevel'), VAL: booleanAttribution(val, 'nearRoundLevel') },
      emaAligned: { DEV: booleanAttribution(dev, 'emaAligned'), VAL: booleanAttribution(val, 'emaAligned') },
      hasPGAPEvidence: { DEV: booleanAttribution(dev, 'hasPGAPEvidence'), VAL: booleanAttribution(val, 'hasPGAPEvidence') },
    },
    fixedArchetypes: { DEV: fixedArchetypes(dev), VAL: fixedArchetypes(val) },
    cases: rows.map((x) => ({ entryTime: x.entryTime, entryIndex: x.entryIndex, r: x.features.r, spikeBars: x.features.spikeBars, spikeSize: p(x.features.spikeSize), spikeSizeToMedianRange: p(x.features.spikeSizeToMedianRange), correctionBars: x.features.correctionBars, correctionDepth: p(x.features.correctionDepth), entryDelayFromCorrection: x.features.entryDelayFromCorrection, entryDistanceFromSpikeEndPct: p(x.features.entryDistanceFromSpikeEndPct), entryDistanceFromCorrectionExtremePct: p(x.features.entryDistanceFromCorrectionExtremePct), stopDistance: p(x.features.stopDistance), plannedRR: p(x.features.plannedRR), structureScore: p(x.features.structureScore), overlapScore: p(x.features.overlapScore), nearRoundLevel: x.features.nearRoundLevel, emaAligned: x.features.emaAligned, qualityScore: x.features.qualityScore, qualityGrade: x.features.qualityGrade })),
    methodology: {
      canonicalReconstruction: true,
      outcomeJoin: 'exact entryIndex + direction + entry + stopLoss + tp1 key',
      discovery: 'descriptive path geometry only; no threshold optimization',
      thresholds: 'all archetype cutoffs were predeclared before observing this report',
      valRole: 'OOS stability check only; VAL was not used to select thresholds',
      freshHoldout: 'locked and excluded',
      productionRule: 'unchanged',
    },
    interpretation: 'This report is a geometry/path map of the 5m NY-Late SELL research cell. It may identify a small number of source-consistent hypotheses, but it does not promote a timing, structure, or geometry rule. Any hypothesis that survives DEV/VAL must be frozen and tested once on the fresh holdout.',
  };
  await mkdir(OUT, { recursive: true });
  const output = resolve(OUT, `${tf}.json`);
  await writeFile(output, JSON.stringify(report, null, 2));
  console.log(`${tf}: NY_LATE_SELL path rows=${rows.length} DEV=${dev.length} VAL=${val.length} | DEV avgR=${p(stats(dev).avgR)} PF=${p(stats(dev).PF)} | VAL avgR=${p(stats(val).avgR)} PF=${p(stats(val).PF)}`);
  for (const [name, value] of Object.entries(report.fixedArchetypes.DEV)) {
    const v = report.fixedArchetypes.VAL[name];
    console.log(`  ${name}: DEV n=${value.n} avgR=${p(value.avgR)} PF=${p(value.PF)} | VAL n=${v.n} avgR=${p(v.avgR)} PF=${p(v.PF)}`);
  }
  console.log(`Report -> ${output}`);
}
await run('1min');
await run('5min');
