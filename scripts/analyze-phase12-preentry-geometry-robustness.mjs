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
const OUT = resolve(ROOT, 'data/reports/strategy-a-phase12-preentry-geometry-robustness');
const PRE = 10000;
const DEV = 6000;

const p = (n) => Number.isFinite(n) ? Number(n.toFixed(6)) : null;
const utcMinutes = (ts) => { const d = new Date(ts); return d.getUTCHours() * 60 + d.getUTCMinutes(); };
const sessionOf = (ts) => {
  const m = utcMinutes(ts);
  if (m >= 960 && m < 1320) return 'NEW_YORK';
  if (m >= 420 && m < 960) return 'LONDON';
  return 'OUT_OF_SESSION';
};

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
    if (!trigger || trigger.index !== index) continue;
    if (trigger.direction !== (spike.direction === 'BULLISH' ? 'BUY' : 'SELL')) continue;
    const breakout = breakouts.find((x) => x.index === spike.breakoutIndex && x.direction === spike.direction);
    const followThrough = ft.find((x) => x.breakoutIndex === spike.breakoutIndex && x.direction === spike.direction);
    if (!breakout || !followThrough) continue;
    return { visible, spike, breakout, followThrough, correction, trigger };
  }
  return null;
}

function outcomeStats(rows) {
  const finite = rows.filter((x) => Number.isFinite(x.r));
  const wins = finite.filter((x) => x.r > 0);
  const losses = finite.filter((x) => x.r <= 0);
  const grossWin = wins.reduce((s, x) => s + x.r, 0);
  const grossLoss = losses.reduce((s, x) => s + Math.abs(x.r), 0);
  return {
    n: finite.length,
    WR: finite.length ? wins.length / finite.length : null,
    avgR: finite.length ? finite.reduce((s, x) => s + x.r, 0) / finite.length : null,
    PF: grossLoss ? grossWin / grossLoss : null,
    totalR: finite.reduce((s, x) => s + x.r, 0),
  };
}

function rank(values) {
  const pairs = values.map((v, i) => ({ v, i })).filter((x) => Number.isFinite(x.v)).sort((a, b) => a.v - b.v);
  const out = Array(values.length).fill(null);
  let i = 0;
  while (i < pairs.length) {
    let j = i + 1;
    while (j < pairs.length && pairs[j].v === pairs[i].v) j++;
    const r = (i + 1 + j) / 2;
    for (let k = i; k < j; k++) out[pairs[k].i] = r;
    i = j;
  }
  return out;
}

function spearman(rows, feature, outcome = 'r') {
  const usable = rows.filter((x) => Number.isFinite(x[feature]) && Number.isFinite(x[outcome]));
  if (usable.length < 5) return null;
  const a = rank(usable.map((x) => x[feature]));
  const b = rank(usable.map((x) => x[outcome]));
  const ma = a.reduce((s, x) => s + x, 0) / a.length;
  const mb = b.reduce((s, x) => s + x, 0) / b.length;
  let num = 0, da = 0, db = 0;
  for (let i = 0; i < a.length; i++) {
    const xa = a[i] - ma, xb = b[i] - mb;
    num += xa * xb; da += xa * xa; db += xb * xb;
  }
  return da && db ? num / Math.sqrt(da * db) : null;
}

function featureDiagnostic(rows, feature) {
  const finite = rows.filter((x) => Number.isFinite(x[feature]) && Number.isFinite(x.r));
  const wins = finite.filter((x) => x.r > 0 && x.r < 5);
  const losses = finite.filter((x) => x.r < 0);
  const med = (xs) => {
    if (!xs.length) return null;
    const a = xs.map((x) => x[feature]).sort((m, n) => m - n);
    const mid = Math.floor(a.length / 2);
    return a.length % 2 ? a[mid] : (a[mid - 1] + a[mid]) / 2;
  };
  const winMedian = med(wins);
  const lossMedian = med(losses);
  return {
    n: finite.length,
    spearman: spearman(finite, feature),
    noExceptionalSpearman: spearman(finite.filter((x) => x.r < 5), feature),
    winMedianExcludingExceptional: winMedian,
    lossMedian: lossMedian,
    medianWinMinusLoss: Number.isFinite(winMedian) && Number.isFinite(lossMedian) ? winMedian - lossMedian : null,
  };
}

function segmentRows(rows) {
  const groups = {};
  for (const row of rows) {
    const key = `${row.direction}+${row.session}`;
    (groups[key] ??= []).push(row);
  }
  return groups;
}

function positiveContribution(rows) {
  const positive = rows.filter((x) => x.r > 0).map((x) => x.r).sort((a, b) => b - a);
  const total = positive.reduce((s, x) => s + x, 0);
  const top3 = positive.slice(0, 3).reduce((s, x) => s + x, 0);
  return { positiveTrades: positive.length, totalPositiveR: total, top3PositiveR: top3, top3Share: total > 0 ? top3 / total : null };
}

async function main() {
  const base = JSON.parse(await readFile(BASE, 'utf8'));
  const candles = (JSON.parse(await readFile(CANDLES, 'utf8')).candles ?? []);
  const targets = (base.trades ?? [])
    .map((t) => ({ entryIndex: Number(t.entryIndex), entryTime: t.entryTime, r: Number(t.rMultiple), direction: t.direction, result: t.result }))
    .filter((t) => Number.isInteger(t.entryIndex) && t.entryIndex < PRE && t.result !== 'AMBIGUOUS' && Number.isFinite(t.r) && (t.direction === 'BUY' || t.direction === 'SELL'));

  const rows = [];
  let replayMismatch = 0;
  let noReplay = 0;

  for (const t of targets) {
    const x = replayAt(candles, t.entryIndex);
    if (!x || x.trigger.timestamp !== t.entryTime || x.trigger.direction !== t.direction) {
      replayMismatch++;
      continue;
    }
    const { visible, spike, correction } = x;
    const triggerCandle = visible[t.entryIndex];
    const corr = visible.slice(correction.correctionStartIndex, correction.correctionExtremeIndex + 1);
    if (!corr.length) { noReplay++; continue; }

    const ranges = corr.map((c) => Math.max(0, c.high - c.low));
    const bodies = corr.map((c) => Math.abs(c.close - c.open));
    const upperWicks = corr.map((c) => Math.max(0, c.high - Math.max(c.open, c.close)));
    const lowerWicks = corr.map((c) => Math.max(0, Math.min(c.open, c.close) - c.low));
    const closeMoves = corr.slice(1).map((c, i) => Math.abs(c.close - corr[i].close));
    const pathLength = closeMoves.reduce((s, v) => s + v, 0);
    const netCloseMove = Math.abs(corr.at(-1).close - corr[0].close);
    const totalRange = ranges.reduce((s, v) => s + v, 0);
    const totalBody = bodies.reduce((s, v) => s + v, 0);
    const totalUpper = upperWicks.reduce((s, v) => s + v, 0);
    const totalLower = lowerWicks.reduce((s, v) => s + v, 0);
    const mid = Math.max(1, Math.floor(corr.length / 2));
    const firstHalf = corr.slice(0, mid);
    const secondHalf = corr.slice(mid);
    const directionSign = t.direction === 'BUY' ? 1 : -1;
    const adverse = (price) => directionSign * (price - spike.endPrice);
    const firstHalfAdverse = firstHalf.length ? Math.max(0, ...firstHalf.map((c) => adverse(t.direction === 'BUY' ? c.low : c.high))) : 0;
    const secondHalfAdverse = secondHalf.length ? Math.max(0, ...secondHalf.map((c) => adverse(t.direction === 'BUY' ? c.low : c.high))) : 0;
    const correctionSize = Math.max(0, adverse(correction.extremePrice));
    const correctionRange = Math.max(...corr.map((c) => c.high)) - Math.min(...corr.map((c) => c.low));
    const triggerRange = Math.max(0, triggerCandle.high - triggerCandle.low);
    const triggerBody = Math.abs(triggerCandle.close - triggerCandle.open);
    const reclaim = Math.max(0, directionSign * (triggerCandle.close - correction.extremePrice));
    const spikeSize = Math.abs(spike.size);

    rows.push({
      entryIndex: t.entryIndex,
      time: t.entryTime,
      split: t.entryIndex < DEV ? 'DEV' : 'VAL',
      direction: t.direction,
      session: sessionOf(t.entryTime),
      r: t.r,
      exceptional: t.r >= 5,
      correctionBars: corr.length,
      correctionToSpike: spikeSize > 0 ? correctionSize / spikeSize : null,
      pathEfficiency: pathLength > 0 ? netCloseMove / pathLength : null,
      bodyParticipation: totalRange > 0 ? totalBody / totalRange : null,
      upperWickShare: totalRange > 0 ? totalUpper / totalRange : null,
      lowerWickShare: totalRange > 0 ? totalLower / totalRange : null,
      secondHalfProgress: firstHalfAdverse > 0 ? secondHalfAdverse / Math.max(firstHalfAdverse, correctionSize) : null,
      triggerReclaimToRange: correctionRange > 0 ? reclaim / correctionRange : null,
      triggerBodyToRange: triggerRange > 0 ? triggerBody / triggerRange : null,
      triggerCloseLocation: triggerRange > 0 ? (t.direction === 'BUY' ? (triggerCandle.close - triggerCandle.low) / triggerRange : (triggerCandle.high - triggerCandle.close) / triggerRange) : null,
      triggerReclaimToCorrection: correctionSize > 0 ? reclaim / correctionSize : null,
    });
  }

  const FEATURES = [
    'correctionBars', 'correctionToSpike', 'pathEfficiency', 'bodyParticipation',
    'upperWickShare', 'lowerWickShare', 'secondHalfProgress',
    'triggerReclaimToRange', 'triggerBodyToRange', 'triggerCloseLocation', 'triggerReclaimToCorrection',
  ];

  const groups = segmentRows(rows);
  const segmentDiagnostics = Object.fromEntries(Object.entries(groups).sort().map(([key, group]) => [key, {
    outcome: outcomeStats(group),
    noExceptionalOutcome: outcomeStats(group.filter((x) => !x.exceptional)),
    positiveContribution: positiveContribution(group),
    features: Object.fromEntries(FEATURES.map((f) => [f, featureDiagnostic(group, f)])),
  }]));

  const allFeatureDiagnostics = Object.fromEntries(FEATURES.map((f) => [f, {
    ALL: featureDiagnostic(rows, f),
    DEV: featureDiagnostic(rows.filter((x) => x.split === 'DEV'), f),
    VAL: featureDiagnostic(rows.filter((x) => x.split === 'VAL'), f),
  }]));

  const result = {
    strategy: 'Strategy A / SP2L',
    mode: 'PHASE_12_PREENTRY_GEOMETRY_ROBUSTNESS',
    timeframe: '5m',
    scope: { baselinePre: targets.length, replayed: rows.length, dev: rows.filter((x) => x.split === 'DEV').length, val: rows.filter((x) => x.split === 'VAL').length, freshHoldoutExcluded: true, productionUntouched: true },
    integrity: { baselinePre: targets.length, replayMismatch, noReplay, deterministicRerunRequired: true, canonicalEntryTimestampRequired: true },
    methodology: {
      purpose: 'Audit whether already-defined pre-entry correction/trigger geometry associations survive across direction/session segments and DEV/VAL without creating a new trading rule.',
      features: FEATURES,
      noOptimization: true,
      noThresholdSearch: true,
      noNewTradingRules: true,
      noFreshHoldoutAccess: true,
      exceptionalDefinition: 'rMultiple >= 5',
      segmentDefinition: 'BUY/SELL × LONDON/NEW_YORK; OUT_OF_SESSION reported separately.',
      note: 'Existing geometry definitions are reused. BUY reclaim/location calculations are direction-aware; no thresholds are selected from outcomes.',
    },
    baseline: outcomeStats(rows),
    baselineNoExceptional: outcomeStats(rows.filter((x) => !x.exceptional)),
    positiveContribution: positiveContribution(rows),
    featureDiagnostics: allFeatureDiagnostics,
    segmentDiagnostics,
    cases: rows,
  };

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(result, null, 2));

  const fmt = (s) => `${s.n} avgR=${p(s.avgR)} PF=${s.PF == null ? '-' : p(s.PF)} WR=${s.WR == null ? '-' : p(s.WR * 100) + '%'}`;
  console.log(`PHASE_12_PREENTRY_GEOMETRY N=${rows.length} DEV=${result.scope.dev} VAL=${result.scope.val} FRESH=LOCKED`);
  console.log(`INTEGRITY baselinePre=${targets.length} replayed=${rows.length} mismatch=${replayMismatch} noReplay=${noReplay}`);
  console.log(`BASELINE ${fmt(result.baseline)} | NO_EX ${fmt(result.baselineNoExceptional)} | TOP3_POS_SHARE=${p(result.positiveContribution.top3Share)}`);
  console.log('=== SEGMENTS ===');
  for (const [key, d] of Object.entries(segmentDiagnostics)) console.log(`${key}: ${fmt(d.outcome)} | NO_EX ${fmt(d.noExceptionalOutcome)} | TOP3=${p(d.positiveContribution.top3Share)}`);
  console.log('=== FEATURE REPLICATION: ALL / DEV / VAL ===');
  for (const f of FEATURES) {
    const d = allFeatureDiagnostics[f];
    console.log(`${f}: ALL sp=${p(d.ALL.spearman)} noExSp=${p(d.ALL.noExceptionalSpearman)} delta=${p(d.ALL.medianWinMinusLoss)} | DEV sp=${p(d.DEV.spearman)} delta=${p(d.DEV.medianWinMinusLoss)} | VAL sp=${p(d.VAL.spearman)} delta=${p(d.VAL.medianWinMinusLoss)}`);
  }
  console.log(`REPORT=${resolve(OUT, '5m.json')}`);
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
}

await main();
