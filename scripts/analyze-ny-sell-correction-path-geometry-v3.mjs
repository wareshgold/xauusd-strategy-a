import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';

const ROOT = resolve(process.cwd());
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-sell-correction-path-geometry-v3');
const DEV = 6000;
const PRE = 10000;
const p = (n) => Number.isFinite(n) ? Number(n.toFixed(5)) : null;
const utcMinutes = (ts) => { const d = new Date(ts); return d.getUTCHours() * 60 + d.getUTCMinutes(); };
const isNySell = (ts) => { const m = utcMinutes(ts); return m >= 960 && m < 1320; };

function replayAt(candles, index) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < 60) return null;
  const breakouts = detectBreakout(visible, 5);
  const ft = detectFollowThrough(visible, breakouts, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
  const spikes = detectSpikeCandidates(visible, breakouts, ft, { maxCandles: 8, minDirectionalFraction: .5, maxOverlapFraction: .8 });
  for (const spike of spikes.candidates) {
    if (spike.endIndex >= index) continue;
    const correction = detectFirstCorrection(visible, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(visible, correction);
    if (!trigger || trigger.index !== index || trigger.direction !== 'SELL' || !isNySell(trigger.timestamp)) continue;
    const breakout = breakouts.find((x) => x.index === spike.breakoutIndex && x.direction === spike.direction);
    const followThrough = ft.find((x) => x.breakoutIndex === spike.breakoutIndex && x.direction === spike.direction);
    if (!breakout || !followThrough) continue;
    return { visible, spike, breakout, followThrough, correction, trigger };
  }
  return null;
}

function quantiles(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return { n: 0 };
  const q = (f) => { const pos = (a.length - 1) * f; const lo = Math.floor(pos); const hi = Math.ceil(pos); return p(a[lo] + (a[hi] - a[lo]) * (pos - lo)); };
  return { n: a.length, p25: q(.25), median: q(.5), p75: q(.75), min: p(a[0]), max: p(a.at(-1)) };
}

function outcomeStats(rows) {
  const wins = rows.filter((x) => x.r > 0);
  const losses = rows.filter((x) => x.r <= 0);
  const grossWin = wins.reduce((s, x) => s + x.r, 0);
  const grossLoss = losses.reduce((s, x) => s + Math.abs(x.r), 0);
  return {
    n: rows.length,
    WR: rows.length ? wins.length / rows.length : null,
    avgR: rows.length ? rows.reduce((s, x) => s + x.r, 0) / rows.length : null,
    PF: grossLoss ? grossWin / grossLoss : null,
    totalR: rows.reduce((s, x) => s + x.r, 0),
  };
}

function quartileLabels(rows, feature) {
  const sorted = rows.slice().sort((a, b) => a[feature] - b[feature]);
  return sorted.map((x, i) => ({ time: x.time, label: `Q${Math.min(4, Math.floor(i * 4 / sorted.length) + 1)}` }));
}

function summarizeShape(rows, key) {
  const groups = [...new Set(rows.map((x) => x[key]))];
  return Object.fromEntries(groups.sort().map((g) => [g, outcomeStats(rows.filter((x) => x[key] === g))]));
}

async function main() {
  const base = JSON.parse(await readFile(BASE, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles ?? [];
  const targets = (base.trades ?? [])
    .map((t) => ({ entryIndex: Number(t.entryIndex), entryTime: t.entryTime, r: Number(t.rMultiple), direction: t.direction, result: t.result }))
    .filter((t) => Number.isInteger(t.entryIndex) && t.entryIndex < PRE && t.direction === 'SELL' && isNySell(t.entryTime) && t.result !== 'AMBIGUOUS' && Number.isFinite(t.r));

  const rows = targets.map((t) => {
    const x = replayAt(candles, t.entryIndex);
    if (!x || x.trigger.timestamp !== t.entryTime) throw new Error(`Lineage mismatch at ${t.entryIndex}`);
    const { visible, spike, correction, trigger } = x;
    const corr = visible.slice(correction.correctionStartIndex, correction.correctionExtremeIndex + 1);
    const triggerCandle = visible[t.entryIndex];
    const spikeSize = Math.abs(spike.size);
    const correctionSize = Math.max(0, correction.extremePrice - spike.endPrice);
    const ranges = corr.map((c) => Math.max(0, c.high - c.low));
    const bodyMoves = corr.map((c) => Math.abs(c.close - c.open));
    const closeMoves = corr.slice(1).map((c, i) => Math.abs(c.close - corr[i].close));
    const netCloseMove = Math.abs(corr.at(-1).close - corr[0].close);
    const pathLength = closeMoves.reduce((s, v) => s + v, 0);
    const upperWicks = corr.map((c) => Math.max(0, c.high - Math.max(c.open, c.close)));
    const lowerWicks = corr.map((c) => Math.max(0, Math.min(c.open, c.close) - c.low));
    const mid = Math.max(1, Math.floor(corr.length / 2));
    const firstHalf = corr.slice(0, mid);
    const secondHalf = corr.slice(mid);
    const firstHalfExcursion = firstHalf.length ? Math.max(...firstHalf.map((c) => c.high)) - spike.endPrice : 0;
    const secondHalfExcursion = secondHalf.length ? Math.max(...secondHalf.map((c) => c.high)) - spike.endPrice : 0;
    const triggerRange = triggerCandle.high - triggerCandle.low;
    const triggerBody = Math.abs(triggerCandle.close - triggerCandle.open);
    const reclaim = Math.max(0, correction.extremePrice - trigger.entryPrice);
    const correctionRange = Math.max(...corr.map((c) => c.high)) - Math.min(...corr.map((c) => c.low));
    const triggerCloseLocation = triggerRange > 0 ? (triggerCandle.close - triggerCandle.low) / triggerRange : null;

    return {
      split: t.entryIndex < DEV ? 'DEV' : 'VAL', time: t.entryTime, r: t.r,
      correctionBars: corr.length,
      correctionToSpike: spikeSize > 0 ? correctionSize / spikeSize : null,
      pathEfficiency: pathLength > 0 ? netCloseMove / pathLength : null,
      bodyParticipation: ranges.reduce((s, v, i) => s + v, 0) > 0 ? bodyMoves.reduce((s, v) => s + v, 0) / ranges.reduce((s, v) => s + v, 0) : null,
      upperWickShare: ranges.reduce((s, v) => s + v, 0) > 0 ? upperWicks.reduce((s, v) => s + v, 0) / ranges.reduce((s, v) => s + v, 0) : null,
      lowerWickShare: ranges.reduce((s, v) => s + v, 0) > 0 ? lowerWicks.reduce((s, v) => s + v, 0) / ranges.reduce((s, v) => s + v, 0) : null,
      secondHalfProgress: firstHalfExcursion > 0 ? secondHalfExcursion / Math.max(firstHalfExcursion, correctionSize) : null,
      triggerReclaimToRange: correctionRange > 0 ? reclaim / correctionRange : null,
      triggerBodyToRange: triggerRange > 0 ? triggerBody / triggerRange : null,
      triggerCloseLocation,
      triggerReclaimToCorrection: correctionSize > 0 ? reclaim / correctionSize : null,
    };
  });

  const FEATURES = ['correctionBars', 'correctionToSpike', 'pathEfficiency', 'bodyParticipation', 'upperWickShare', 'lowerWickShare', 'secondHalfProgress', 'triggerReclaimToRange', 'triggerBodyToRange', 'triggerCloseLocation', 'triggerReclaimToCorrection'];
  const shapeRows = rows.map((r) => ({ ...r,
    pathShape: r.pathEfficiency >= .65 ? 'DIRECTED' : r.pathEfficiency <= .35 ? 'CHOPPY' : 'MIXED',
    phaseShape: r.secondHalfProgress >= 1 ? 'LATE_EXPANSION' : r.secondHalfProgress <= .5 ? 'EARLY_EXPANSION' : 'BALANCED',
    triggerShape: r.triggerBodyToRange >= .65 ? 'IMPULSIVE' : r.triggerBodyToRange <= .25 ? 'SMALL_BODY' : 'MODERATE_BODY',
  }));

  const quartileAssignments = Object.fromEntries(FEATURES.map((f) => [f, quartileLabels(shapeRows, f)]));
  const result = {
    strategy: 'Strategy A / SP2L', mode: 'RESEARCH_NY_SELL_CORRECTION_PATH_GEOMETRY_V3', timeframe: '5m',
    scope: { total: shapeRows.length, dev: shapeRows.filter((x) => x.split === 'DEV').length, val: shapeRows.filter((x) => x.split === 'VAL').length, freshHoldoutExcluded: true, productionUntouched: true },
    methodology: {
      purpose: 'Descriptive path-shape analysis of canonical NY SELL correction and trigger mechanics.',
      noOptimization: true, noNewTradingRules: true, noThresholdSearch: true, holdoutLocked: true,
      note: 'Shape labels are coarse descriptive buckets chosen before outcome comparison; they are not proposed trading thresholds.'
    },
    featureDistributions: Object.fromEntries(FEATURES.map((f) => [f, { ALL: quantiles(shapeRows.map((x) => x[f])), DEV: quantiles(shapeRows.filter((x) => x.split === 'DEV').map((x) => x[f])), VAL: quantiles(shapeRows.filter((x) => x.split === 'VAL').map((x) => x[f])) }])),
    shapeOutcome: {
      pathShape: summarizeShape(shapeRows, 'pathShape'),
      phaseShape: summarizeShape(shapeRows, 'phaseShape'),
      triggerShape: summarizeShape(shapeRows, 'triggerShape'),
    },
    shapeOutcomeBySplit: {
      DEV: { pathShape: summarizeShape(shapeRows.filter((x) => x.split === 'DEV'), 'pathShape'), phaseShape: summarizeShape(shapeRows.filter((x) => x.split === 'DEV'), 'phaseShape'), triggerShape: summarizeShape(shapeRows.filter((x) => x.split === 'DEV'), 'triggerShape') },
      VAL: { pathShape: summarizeShape(shapeRows.filter((x) => x.split === 'VAL'), 'pathShape'), phaseShape: summarizeShape(shapeRows.filter((x) => x.split === 'VAL'), 'phaseShape'), triggerShape: summarizeShape(shapeRows.filter((x) => x.split === 'VAL'), 'triggerShape') },
    },
    quartileOutcome: Object.fromEntries(FEATURES.map((f) => [f, Object.fromEntries(['Q1','Q2','Q3','Q4'].map((q) => [q, outcomeStats(shapeRows.filter((x) => quartileAssignments[f].find((a) => a.time === x.time)?.label === q))]))])),
    cases: shapeRows,
  };

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(result, null, 2));

  const compact = (s) => `${s.n}/${s.WR == null ? '-' : p(s.WR * 100) + '%/' + p(s.avgR) + '/' + (s.PF == null ? '-' : p(s.PF))}`;
  console.log(`GEOM_V3_PATH_SHAPE N=${result.scope.total} DEV=${result.scope.dev} VAL=${result.scope.val} FRESH=LOCKED`);
  console.log(`DIRECTED: ${compact(result.shapeOutcome.pathShape.DIRECTED ?? { n:0 })} | MIXED: ${compact(result.shapeOutcome.pathShape.MIXED ?? { n:0 })} | CHOPPY: ${compact(result.shapeOutcome.pathShape.CHOPPY ?? { n:0 })}`);
  console.log(`PHASE EARLY: ${compact(result.shapeOutcome.phaseShape.EARLY_EXPANSION ?? { n:0 })} | BALANCED: ${compact(result.shapeOutcome.phaseShape.BALANCED ?? { n:0 })} | LATE: ${compact(result.shapeOutcome.phaseShape.LATE_EXPANSION ?? { n:0 })}`);
  console.log(`TRIGGER IMPULSIVE: ${compact(result.shapeOutcome.triggerShape.IMPULSIVE ?? { n:0 })} | MODERATE: ${compact(result.shapeOutcome.triggerShape.MODERATE_BODY ?? { n:0 })} | SMALL: ${compact(result.shapeOutcome.triggerShape.SMALL_BODY ?? { n:0 })}`);
  console.log('KEY FEATURES:', FEATURES.join(', '));
  console.log(`REPORT=${resolve(OUT, '5m.json')}`);
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
}

await main();
