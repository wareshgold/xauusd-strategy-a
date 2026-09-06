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
const PATH_HORIZON = 500;
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
const DEV_END = WINDOWS.find(w => w.name === 'DEV_3').end;

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

function scanToCanonicalExit(candles, entryIndex, entryPrice, stopLoss, takeProfit, direction, result) {
  const risk = Math.abs(entryPrice - stopLoss);
  if (!Number.isFinite(risk) || risk <= 0 || !Number.isFinite(entryPrice) || !Number.isFinite(stopLoss) || !Number.isFinite(takeProfit)) return null;
  for (let j = entryIndex + 1; j <= Math.min(candles.length - 1, entryIndex + PATH_HORIZON); j++) {
    const candle = candles[j];
    const hitSL = direction === 'BUY' ? candle.low <= stopLoss : candle.high >= stopLoss;
    const hitTP = direction === 'BUY' ? candle.high >= takeProfit : candle.low <= takeProfit;
    if (hitSL && hitTP) return { exitIndex: j, exitReason: 'AMBIGUOUS_SAME_CANDLE', risk };
    if (hitSL) return { exitIndex: j, exitReason: 'SL', risk };
    if (hitTP) return { exitIndex: j, exitReason: 'TP1', risk };
  }
  return null;
}

function pathStats(candles, startIndex, endIndex, entryPrice, risk, direction) {
  let maeR = 0;
  let mfeR = 0;
  let reachedHalfAdverse = false;
  let reachedHalfFavorable = false;
  let reached1R = false;
  let reached2R = false;
  let firstHalfAdverse = null;
  let firstHalfFavorable = null;
  let first1R = null;
  let first2R = null;
  if (!Number.isFinite(risk) || risk <= 0) return null;
  for (let j = startIndex; j <= endIndex; j++) {
    const candle = candles[j];
    const adverse = direction === 'BUY' ? (entryPrice - candle.low) / risk : (candle.high - entryPrice) / risk;
    const favorable = direction === 'BUY' ? (candle.high - entryPrice) / risk : (entryPrice - candle.low) / risk;
    maeR = Math.max(maeR, adverse);
    mfeR = Math.max(mfeR, favorable);
    if (!reachedHalfAdverse && adverse >= 0.5) { reachedHalfAdverse = true; firstHalfAdverse = j - startIndex + 1; }
    if (!reachedHalfFavorable && favorable >= 0.5) { reachedHalfFavorable = true; firstHalfFavorable = j - startIndex + 1; }
    if (!reached1R && favorable >= 1) { reached1R = true; first1R = j - startIndex + 1; }
    if (!reached2R && favorable >= 2) { reached2R = true; first2R = j - startIndex + 1; }
  }
  return { maeR, mfeR, reachedHalfAdverse, reachedHalfFavorable, reached1R, reached2R, firstHalfAdverse, firstHalfFavorable, first1R, first2R };
}

function postExitStats(candles, exitIndex, entryPrice, risk, direction) {
  if (exitIndex >= candles.length - 1) return null;
  let favorableFromExitR = 0;
  let adverseFromExitR = 0;
  let continuation1R = null;
  let continuation2R = null;
  for (let j = exitIndex + 1; j <= Math.min(candles.length - 1, exitIndex + PATH_HORIZON); j++) {
    const candle = candles[j];
    const favorable = direction === 'BUY' ? (candle.high - entryPrice) / risk : (entryPrice - candle.low) / risk;
    const adverse = direction === 'BUY' ? (entryPrice - candle.low) / risk : (candle.high - entryPrice) / risk;
    favorableFromExitR = Math.max(favorableFromExitR, favorable);
    adverseFromExitR = Math.max(adverseFromExitR, adverse);
    if (continuation1R === null && favorable >= 1) continuation1R = j - exitIndex;
    if (continuation2R === null && favorable >= 2) continuation2R = j - exitIndex;
  }
  return { favorableFromExitR, adverseFromExitR, continuation1R, continuation2R };
}

const raw = (base.trades ?? []).filter(trade => {
  const entryIndex = Number(trade.entryIndex);
  return Number.isInteger(entryIndex) && entryIndex < PRE && trade.result !== 'AMBIGUOUS' && Number.isFinite(Number(trade.rMultiple)) && (trade.direction === 'BUY' || trade.direction === 'SELL');
});

let mismatch = 0;
let exitMismatch = 0;
const rows = [];
for (const trade of raw) {
  const entryIndex = Number(trade.entryIndex);
  const replayed = replay(candles, entryIndex);
  if (!replayed || replayed.trigger.timestamp !== trade.entryTime || replayed.trigger.direction !== trade.direction) {
    mismatch++;
    continue;
  }
  const entry = Number(trade.entry);
  const stopLoss = Number(trade.stopLoss);
  const tp1 = Number(trade.tp1);
  const exit = scanToCanonicalExit(candles, entryIndex, entry, stopLoss, tp1, trade.direction, trade.result);
  if (!exit || exit.exitReason === 'AMBIGUOUS_SAME_CANDLE') {
    exitMismatch++;
    continue;
  }
  const expectedReason = trade.result === 'TP1' ? 'TP1' : 'SL';
  if (exit.exitReason !== expectedReason) {
    exitMismatch++;
    continue;
  }
  const preEnd = exit.exitIndex;
  const post = postExitStats(candles, exit.exitIndex, entry, exit.risk, trade.direction);
  const pre = pathStats(candles, entryIndex + 1, preEnd, entry, exit.risk, trade.direction);
  if (!pre) { exitMismatch++; continue; }
  rows.push({
    entryIndex,
    entryTime: trade.entryTime,
    direction: trade.direction,
    session: session(trade.entryTime),
    split: entryIndex <= DEV_END ? 'DEV' : 'VAL',
    window: WINDOWS.find(w => entryIndex >= w.start && entryIndex <= w.end)?.name ?? 'UNKNOWN',
    r: Number(trade.rMultiple),
    outcome: Number(trade.rMultiple) > 0 ? 'WIN' : 'LOSS',
    result: trade.result,
    entry,
    stopLoss,
    tp1,
    risk: exit.risk,
    exitIndex: exit.exitIndex,
    exitBars: exit.exitIndex - entryIndex,
    exitReason: exit.exitReason,
    pre,
    post,
  });
}

const losses = rows.filter(x => x.outcome === 'LOSS');
const wins = rows.filter(x => x.outcome === 'WIN');
const splitRows = rows => ({ DEV: rows.filter(x => x.split === 'DEV').length, VAL: rows.filter(x => x.split === 'VAL').length });

const summarizePath = subset => ({
  n: subset.length,
  preExitMAE: median(subset.map(x => x.pre.maeR)),
  preExitMFE: median(subset.map(x => x.pre.mfeR)),
  preExitHalfAdv: subset.length ? subset.filter(x => x.pre.reachedHalfAdverse).length / subset.length : null,
  preExitHalfFav: subset.length ? subset.filter(x => x.pre.reachedHalfFavorable).length / subset.length : null,
  preExit1R: subset.length ? subset.filter(x => x.pre.reached1R).length / subset.length : null,
  preExit2R: subset.length ? subset.filter(x => x.pre.reached2R).length / subset.length : null,
  postExit1R: subset.length ? subset.filter(x => x.post?.continuation1R !== null).length / subset.length : null,
  postExit2R: subset.length ? subset.filter(x => x.post?.continuation2R !== null).length / subset.length : null,
  postExitFavorableMedian: median(subset.map(x => x.post?.favorableFromExitR)),
  exitBarsMedian: median(subset.map(x => x.exitBars)),
});

const result = {
  strategy: 'Strategy A / SP2L',
  mode: 'PHASE_18_PRE_EXIT_VS_POST_EXIT_PATH_ATTRIBUTION',
  timeframe: '5min',
  scope: {
    rawBaselinePre: raw.length,
    canonicalReplayed: rows.length,
    dev: rows.filter(x => x.split === 'DEV').length,
    val: rows.filter(x => x.split === 'VAL').length,
    freshHoldoutExcluded: true,
    productionUntouched: true,
  },
  integrity: {
    expectedCanonical: 210,
    rawBaselinePre: raw.length,
    canonicalReplayed: rows.length,
    replayMismatch: mismatch,
    exitMismatch,
    totalMismatch: mismatch + exitMismatch,
  },
  methodology: {
    purpose: 'Descriptive attribution of favorable/adverse path before versus after the canonical baseline exit; no optimization or rule selection.',
    pathHorizonBars: PATH_HORIZON,
    canonicalExit: 'First non-ambiguous hit of baseline stopLoss or tp1; exit reason must match baseline result (SL or TP1).',
    splitDefinition: 'DEV_1 + DEV_2 + DEV_3 = DEV; VAL_1 + VAL_2 = VAL.',
    noOptimization: true,
    noThresholdSearch: true,
    noNewTradingRules: true,
    noFreshHoldoutAccess: true,
  },
  overall: stats(rows),
  outcome: {
    losses: summarizePath(losses),
    wins: summarizePath(wins),
  },
  direction: {
    BUY: summarizePath(rows.filter(x => x.direction === 'BUY')),
    SELL: summarizePath(rows.filter(x => x.direction === 'SELL')),
  },
  exitReason: {
    SL: summarizePath(rows.filter(x => x.exitReason === 'SL')),
    TP1: summarizePath(rows.filter(x => x.exitReason === 'TP1')),
  },
  windows: Object.fromEntries(WINDOWS.map(w => [w.name, summarizePath(rows.filter(x => x.window === w.name))])),
  splitRows: splitRows(rows),
  cases: rows,
};

const out = resolve(ROOT, 'data/reports/strategy-a-phase18-pre-exit-vs-post-exit-path-attribution');
await mkdir(out, { recursive: true });
await writeFile(resolve(out, '5min.json'), JSON.stringify(result, null, 2));

console.log(`PHASE_18_PRE_EXIT_VS_POST_EXIT_PATH_ATTRIBUTION 5min N=${rows.length} DEV=${result.scope.dev} VAL=${result.scope.val} FRESH=LOCKED`);
console.log(`INTEGRITY expected=210 raw=${raw.length} actual=${rows.length} replayMismatch=${mismatch} exitMismatch=${exitMismatch}`);
console.log(`OVERALL N=${rows.length} avgR=${round(result.overall.avgR)} PF=${round(result.overall.PF)} WR=${pct(result.overall.WR)}% totalR=${round(result.overall.totalR)}`);
console.log(`LOSSES preExitMAE=${round(result.outcome.losses.preExitMAE)}R preExitMFE=${round(result.outcome.losses.preExitMFE)}R halfAdv=${pct(result.outcome.losses.preExitHalfAdv)}% halfFav=${pct(result.outcome.losses.preExitHalfFav)}% 1R=${pct(result.outcome.losses.preExit1R)}% 2R=${pct(result.outcome.losses.preExit2R)}% | postExit1R=${pct(result.outcome.losses.postExit1R)}% postExit2R=${pct(result.outcome.losses.postExit2R)}%`);
console.log(`WINS preExitMAE=${round(result.outcome.wins.preExitMAE)}R preExitMFE=${round(result.outcome.wins.preExitMFE)}R halfAdv=${pct(result.outcome.wins.preExitHalfAdv)}% halfFav=${pct(result.outcome.wins.preExitHalfFav)}% 1R=${pct(result.outcome.wins.preExit1R)}% 2R=${pct(result.outcome.wins.preExit2R)}% | postExit1R=${pct(result.outcome.wins.postExit1R)}% postExit2R=${pct(result.outcome.wins.postExit2R)}%`);
console.log('=== WINDOWS ===');
for (const [key, value] of Object.entries(result.windows)) console.log(`${key}: N=${value.n} preMAE=${round(value.preExitMAE)}R preMFE=${round(value.preExitMFE)}R halfAdv=${pct(value.preExitHalfAdv)}% halfFav=${pct(value.preExitHalfFav)}% 1R=${pct(value.preExit1R)}% post1R=${pct(value.postExit1R)}% post2R=${pct(value.postExit2R)}% exitBarsMed=${round(value.exitBarsMedian)}`);
console.log(`REPORT=${resolve(out, '5min.json')}`);
console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
