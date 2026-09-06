import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';

const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const candles = JSON.parse(await readFile(resolve(ROOT, 'data/historical/xauusd-5min.json'), 'utf8')).candles ?? [];
const base = JSON.parse(await readFile(resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json'), 'utf8'));
const PRE = 10000;
const DEV = 5000;
const CFG = {
  breakoutLookback: 5,
  followThrough: { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true },
  spike: { maxCandles: 8, minDirectionalFraction: 0.5, maxOverlapFraction: 0.8 },
};
const WINDOWS = [
  { name: 'DEV_1', start: 0, end: 1999 },
  { name: 'DEV_2', start: 2000, end: 3999 },
  { name: 'DEV_3', start: 4000, end: 5999 },
  { name: 'VAL_1', start: 6000, end: 7999 },
  { name: 'VAL_2', start: 8000, end: 9999 },
];

const round = x => Number.isFinite(x) ? Number(x.toFixed(6)) : null;
const pct = x => Number.isFinite(x) ? Number((x * 100).toFixed(4)) : null;
const median = values => {
  const v = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!v.length) return null;
  const m = Math.floor(v.length / 2);
  return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2;
};
const stats = rows => {
  const n = rows.length;
  const totalR = rows.reduce((s, x) => s + x.r, 0);
  const wins = rows.filter(x => x.r > 0);
  const losses = rows.filter(x => x.r <= 0);
  const grossWin = wins.reduce((s, x) => s + x.r, 0);
  const grossLoss = -losses.reduce((s, x) => s + x.r, 0);
  return { n, avgR: n ? totalR / n : null, PF: grossLoss ? grossWin / grossLoss : null, WR: n ? wins.length / n : null, totalR };
};
const bucket = (rows, key) => Object.fromEntries(
  [...new Set(rows.map(x => x[key]))].sort().map(value => [value, stats(rows.filter(x => x[key] === value))])
);
const consecutiveLosses = rows => {
  let current = 0;
  let max = 0;
  for (const row of rows) {
    if (row.r <= 0) {
      current++;
      max = Math.max(max, current);
    } else {
      current = 0;
    }
  }
  return max;
};

function session(timestamp) {
  const d = new Date(timestamp);
  const minutes = d.getUTCHours() * 60 + d.getUTCMinutes();
  if (minutes >= 420 && minutes < 960) return 'LONDON';
  if (minutes >= 960 && minutes < 1320) return 'NEW_YORK';
  return 'OUT_OF_SESSION';
}

function replay(candles, entryIndex) {
  const view = candles.slice(0, entryIndex + 1);
  if (view.length < 60) return null;
  const breakouts = detectBreakout(view, CFG.breakoutLookback);
  const followThrough = detectFollowThrough(view, breakouts, CFG.followThrough);
  const spikes = detectSpikeCandidates(view, breakouts, followThrough, CFG.spike);
  for (const spike of spikes.candidates) {
    if (spike.endIndex >= entryIndex) continue;
    const correction = detectFirstCorrection(view, spike);
    if (!correction || correction.correctionExtremeIndex >= entryIndex) continue;
    const trigger = detectEntryTrigger(view, correction);
    if (!trigger || trigger.index !== entryIndex) continue;
    const breakout = breakouts.find(x => x.index === spike.breakoutIndex && x.direction === spike.direction);
    const follow = followThrough.find(x => x.breakoutIndex === spike.breakoutIndex && x.direction === spike.direction);
    if (breakout && follow) return { spike, correction, trigger, breakout, follow };
  }
  return null;
}

function path(candles, entryIndex, entryPrice, stopLoss, takeProfit, direction) {
  let maeR = 0;
  let mfeR = 0;
  let firstHalfAdverse = null;
  let firstHalfFavorable = null;
  let first1R = null;
  let hitSL = null;
  let hitTP = null;
  const risk = Math.abs(entryPrice - stopLoss);
  for (let j = entryIndex + 1; j <= Math.min(candles.length - 1, entryIndex + 500); j++) {
    const candle = candles[j];
    const adverse = direction === 'BUY' ? (entryPrice - candle.low) / risk : (candle.high - entryPrice) / risk;
    const favorable = direction === 'BUY' ? (candle.high - entryPrice) / risk : (entryPrice - candle.low) / risk;
    maeR = Math.max(maeR, adverse);
    mfeR = Math.max(mfeR, favorable);
    if (firstHalfAdverse === null && adverse >= 0.5) firstHalfAdverse = j - entryIndex;
    if (firstHalfFavorable === null && favorable >= 0.5) firstHalfFavorable = j - entryIndex;
    if (first1R === null && favorable >= 1) first1R = j - entryIndex;
    if (hitSL === null && (direction === 'BUY' ? candle.low <= stopLoss : candle.high >= stopLoss)) hitSL = j - entryIndex;
    if (hitTP === null && (direction === 'BUY' ? candle.high >= takeProfit : candle.low <= takeProfit)) hitTP = j - entryIndex;
    if (hitSL !== null && hitTP !== null) break;
  }
  return { maeR, mfeR, firstHalfAdverse, firstHalfFavorable, first1R, hitSL, hitTP };
}

const raw = (base.trades ?? []).filter(trade => {
  const entryIndex = Number(trade.entryIndex);
  return Number.isInteger(entryIndex) && entryIndex < PRE && trade.result !== 'AMBIGUOUS' && Number.isFinite(Number(trade.rMultiple)) && (trade.direction === 'BUY' || trade.direction === 'SELL');
});

let mismatch = 0;
const rows = [];
for (const trade of raw) {
  const entryIndex = Number(trade.entryIndex);
  const replayed = replay(candles, entryIndex);
  if (!replayed || replayed.trigger.timestamp !== trade.entryTime || replayed.trigger.direction !== trade.direction) {
    mismatch++;
    continue;
  }
  const pathResult = path(candles, entryIndex, Number(trade.entryPrice), Number(trade.stopLoss), Number(trade.takeProfit1), trade.direction);
  const r = Number(trade.rMultiple);
  rows.push({
    entryIndex,
    entryTime: trade.entryTime,
    direction: trade.direction,
    session: session(trade.entryTime),
    split: entryIndex < DEV ? 'DEV' : 'VAL',
    window: WINDOWS.find(w => entryIndex >= w.start && entryIndex <= w.end)?.name ?? 'UNKNOWN',
    r,
    exceptional: r >= 5,
    maeR: pathResult.maeR,
    mfeR: pathResult.mfeR,
    firstHalfAdverse: pathResult.firstHalfAdverse,
    firstHalfFavorable: pathResult.firstHalfFavorable,
    first1R: pathResult.first1R,
    hitSL: pathResult.hitSL,
    hitTP: pathResult.hitTP,
    outcome: r > 0 ? 'WIN' : 'LOSS',
  });
}

const losses = rows.filter(x => x.r <= 0);
const wins = rows.filter(x => x.r > 0);
const buckets = {
  direction: bucket(rows, 'direction'),
  session: bucket(rows, 'session'),
  outcome: bucket(rows, 'outcome'),
  window: bucket(rows, 'window'),
  split: bucket(rows, 'split'),
};
const failureModes = {
  losses: stats(losses),
  wins: stats(wins),
  lossMAE: {
    medianR: median(losses.map(x => x.maeR)),
    p50: losses.length ? losses.filter(x => x.maeR >= 0.5).length / losses.length : null,
    p75: losses.length ? losses.filter(x => x.maeR >= 0.75).length / losses.length : null,
    p90: losses.length ? losses.filter(x => x.maeR >= 0.9).length / losses.length : null,
  },
  lossMFE: {
    medianR: median(losses.map(x => x.mfeR)),
    reachedHalf: losses.length ? losses.filter(x => x.mfeR >= 0.5).length / losses.length : null,
    reached1R: losses.length ? losses.filter(x => x.mfeR >= 1).length / losses.length : null,
    reached2R: losses.length ? losses.filter(x => x.mfeR >= 2).length / losses.length : null,
  },
  winsMAE: { medianR: median(wins.map(x => x.maeR)) },
  winsMFE: { medianR: median(wins.map(x => x.mfeR)) },
  pathTiming: {
    lossReachedHalfAdverse: losses.length ? losses.filter(x => x.firstHalfAdverse !== null).length / losses.length : null,
    lossReachedHalfFavorable: losses.length ? losses.filter(x => x.firstHalfFavorable !== null).length / losses.length : null,
    lossReached1R: losses.length ? losses.filter(x => x.first1R !== null).length / losses.length : null,
    winReached1R: wins.length ? wins.filter(x => x.first1R !== null).length / wins.length : null,
    winHitSL: wins.length ? wins.filter(x => x.hitSL !== null).length / wins.length : null,
    winHitTP: wins.length ? wins.filter(x => x.hitTP !== null).length / wins.length : null,
  },
  consecutiveLosses: consecutiveLosses(rows),
};

const windowFailure = Object.fromEntries(WINDOWS.map(w => {
  const windowRows = rows.filter(x => x.window === w.name);
  const windowLosses = windowRows.filter(x => x.r <= 0);
  const windowWins = windowRows.filter(x => x.r > 0);
  return [w.name, {
    overall: stats(windowRows),
    losses: stats(windowLosses),
    wins: stats(windowWins),
    lossMAEmedianR: median(windowLosses.map(x => x.maeR)),
    lossMFEmedianR: median(windowLosses.map(x => x.mfeR)),
    lossReachedHalfAdverse: windowLosses.length ? windowLosses.filter(x => x.firstHalfAdverse !== null).length / windowLosses.length : null,
    lossReachedHalfFavorable: windowLosses.length ? windowLosses.filter(x => x.firstHalfFavorable !== null).length / windowLosses.length : null,
    lossReached1R: windowLosses.length ? windowLosses.filter(x => x.first1R !== null).length / windowLosses.length : null,
    maxConsecutiveLosses: consecutiveLosses(windowRows),
  }];
}));

const result = {
  strategy: 'Strategy A / SP2L',
  mode: 'PHASE_17_BASELINE_FAILURE_DECOMPOSITION',
  timeframe: '5min',
  scope: {
    rawBaselinePre: raw.length,
    canonicalReplayed: rows.length,
    dev: rows.filter(x => x.split === 'DEV').length,
    val: rows.filter(x => x.split === 'VAL').length,
    freshHoldoutExcluded: true,
    productionUntouched: true,
  },
  integrity: { expectedCanonical: 210, rawBaselinePre: raw.length, canonicalReplayed: rows.length, mismatch },
  methodology: {
    purpose: 'Descriptive decomposition of baseline trade failures and path behavior; identify common mechanical failure modes without optimizing or selecting thresholds.',
    pathHorizonBars: 500,
    metrics: ['MAE in R', 'MFE in R', 'time-to-0.5R adverse', 'time-to-0.5R favorable', 'time-to-1R favorable', 'SL/TP path hits', 'fixed chronological windows', 'direction/session splits', 'maximum consecutive losses'],
    noOptimization: true,
    noThresholdSearch: true,
    noNewTradingRules: true,
    noFreshHoldoutAccess: true,
  },
  overall: stats(rows),
  buckets,
  failureModes,
  windowFailure,
  cases: rows,
};

const out = resolve(ROOT, 'data/reports/strategy-a-phase17-baseline-failure-decomposition');
await mkdir(out, { recursive: true });
await writeFile(resolve(out, '5min.json'), JSON.stringify(result, null, 2));
const fmt = s => `N=${s.n} avgR=${round(s.avgR)} PF=${round(s.PF)} WR=${pct(s.WR)}% totalR=${round(s.totalR)}`;
console.log(`PHASE_17_BASELINE_FAILURE_DECOMPOSITION 5min N=${rows.length} DEV=${rows.filter(x => x.split === 'DEV').length} VAL=${rows.filter(x => x.split === 'VAL').length} FRESH=LOCKED`);
console.log(`INTEGRITY expected=210 raw=${raw.length} actual=${rows.length} mismatch=${mismatch}`);
console.log(`OVERALL ${fmt(result.overall)}`);
console.log(`LOSSES ${fmt(failureModes.losses)} | WINS ${fmt(failureModes.wins)}`);
console.log(`MAE losses median=${round(failureModes.lossMAE.medianR)}R >=0.5R=${pct(failureModes.lossMAE.p50)}% >=0.75R=${pct(failureModes.lossMAE.p75)}% >=0.9R=${pct(failureModes.lossMAE.p90)}%`);
console.log(`MFE losses median=${round(failureModes.lossMFE.medianR)}R reached0.5R=${pct(failureModes.lossMFE.reachedHalf)}% reached1R=${pct(failureModes.lossMFE.reached1R)}% reached2R=${pct(failureModes.lossMFE.reached2R)}%`);
console.log(`PATH losses: halfAdv=${pct(failureModes.pathTiming.lossReachedHalfAdverse)}% halfFav=${pct(failureModes.pathTiming.lossReachedHalfFavorable)}% 1R=${pct(failureModes.pathTiming.lossReached1R)}% | wins: 1R=${pct(failureModes.pathTiming.winReached1R)}%`);
console.log(`MAX_CONSECUTIVE_LOSSES=${failureModes.consecutiveLosses}`);
console.log('=== WINDOWS ===');
for (const [key, value] of Object.entries(windowFailure)) console.log(`${key}: ${fmt(value.overall)} lossMAE=${round(value.lossMAEmedianR)}R lossMFE=${round(value.lossMFEmedianR)}R lossHalfAdv=${pct(value.lossReachedHalfAdverse)}% lossHalfFav=${pct(value.lossReachedHalfFavorable)}% loss1R=${pct(value.lossReached1R)}% maxLossStreak=${value.maxConsecutiveLosses}`);
console.log(`REPORT=${resolve(out, '5min.json')}`);
console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
