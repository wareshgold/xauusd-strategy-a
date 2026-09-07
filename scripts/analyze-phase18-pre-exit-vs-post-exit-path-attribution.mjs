import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';
import { getInvalidationRule } from '../src/domain/strategy-a/InvalidationRule.js';
import { projectLeg2 } from '../src/domain/strategy-a/LegProjection.js';
import { buildEMAContext } from '../src/domain/context/EMAContext.js';
import { buildLocationContext } from '../src/domain/context/LocationContext.js';
import { buildSessionContext } from '../src/domain/context/SessionContext.js';
import { scoreSetup } from '../src/domain/quality/QualityScore.js';

const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const candles = JSON.parse(await readFile(resolve(ROOT, 'data/historical/xauusd-5min.json'), 'utf8')).candles ?? [];
const base = JSON.parse(await readFile(resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json'), 'utf8'));
const PRE = 10000;
const PATH_HORIZON = 500;
const CFG = {
  breakoutLookback: 5,
  followThrough: { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true },
  spike: { maxCandles: 8, minDirectionalFraction: 0.5, maxOverlapFraction: 0.8 },
  ema: { period: 60 },
  location: { roundStep: 50, roundDistance: 5 },
  session: { londonStartUtcMinute: 420, londonEndUtcMinute: 960, newYorkStartUtcMinute: 780, newYorkEndUtcMinute: 1320, avoidWindowsUtc: [] },
};
const WINDOWS = [
  { name: 'DEV_1', start: 0, end: 1999 }, { name: 'DEV_2', start: 2000, end: 3999 }, { name: 'DEV_3', start: 4000, end: 5999 },
  { name: 'VAL_1', start: 6000, end: 7999 }, { name: 'VAL_2', start: 8000, end: 9999 },
];
const DEV_END = WINDOWS.find(w => w.name === 'DEV_3').end;
const median = values => { const v = values.filter(Number.isFinite).sort((a, b) => a - b); if (!v.length) return null; const m = Math.floor(v.length / 2); return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2; };
const stats = rows => { const n = rows.length; const totalR = rows.reduce((s, x) => s + x.r, 0); const wins = rows.filter(x => x.r > 0); const losses = rows.filter(x => x.r <= 0); const grossWin = wins.reduce((s, x) => s + x.r, 0); const grossLoss = -losses.reduce((s, x) => s + x.r, 0); return { n, avgR: n ? totalR / n : null, PF: grossLoss ? grossWin / grossLoss : null, WR: n ? wins.length / n : null, totalR }; };
function session(timestamp) { const d = new Date(timestamp); const minutes = d.getUTCHours() * 60 + d.getUTCMinutes(); if (minutes >= 420 && minutes < 960) return 'LONDON'; if (minutes >= 960 && minutes < 1320) return 'NEW_YORK'; return 'OUT_OF_SESSION'; }
function replayExact(candles, entryIndex) {
  const view = candles.slice(0, entryIndex + 1); if (view.length < 60) return null;
  const breakouts = detectBreakout(view, CFG.breakoutLookback); const followThrough = detectFollowThrough(view, breakouts, CFG.followThrough); const spikes = detectSpikeCandidates(view, breakouts, followThrough, CFG.spike);
  for (const spike of spikes.candidates) {
    if (spike.endIndex >= entryIndex) continue; const correction = detectFirstCorrection(view, spike); if (!correction || correction.correctionExtremeIndex >= entryIndex) continue;
    const trigger = detectEntryTrigger(view, correction); if (!trigger || trigger.index !== entryIndex) continue;
    const breakout = breakouts.find(x => x.index === spike.breakoutIndex && x.direction === spike.direction); const follow = followThrough.find(x => x.breakoutIndex === spike.breakoutIndex && x.direction === spike.direction); if (!breakout || !follow) continue;
    const projection = projectLeg2(view, correction, trigger); const invalidation = getInvalidationRule(view, correction, trigger); const emaContext = buildEMAContext(view, trigger.index, CFG.ema); const locationContext = buildLocationContext(view, trigger.index, CFG.location); const sessionContext = buildSessionContext(trigger.timestamp, CFG.session);
    const quality = scoreSetup({ structure: spike, breakout, followThrough: follow, correction, trigger, projection, invalidation, emaContext, locationContext, sessionContext }); if (!quality.tradeAllowed) continue;
    const entry = Number(trigger.entryPrice); const stopLoss = Number(invalidation.stopLoss); const takeProfit = Number(projection.tp1); const risk = Math.abs(entry - stopLoss); const reward = Math.abs(takeProfit - entry); const targetIsDirectional = trigger.direction === 'BUY' ? takeProfit > entry : takeProfit < entry;
    if (!Number.isFinite(risk) || risk <= 0 || !Number.isFinite(reward) || reward <= 0 || !targetIsDirectional) continue;
    return { spike, correction, trigger, breakout, follow, projection, invalidation, emaContext, locationContext, sessionContext, quality };
  }
  return null;
}
function scanToCanonicalExit(candles, entryIndex, entryPrice, stopLoss, takeProfit, direction) {
  const risk = Math.abs(entryPrice - stopLoss); if (!Number.isFinite(risk) || risk <= 0 || !Number.isFinite(entryPrice) || !Number.isFinite(stopLoss) || !Number.isFinite(takeProfit)) return null;
  for (let j = entryIndex + 1; j < candles.length; j++) { const candle = candles[j]; const hitSL = direction === 'BUY' ? candle.low <= stopLoss : candle.high >= stopLoss; const hitTP = direction === 'BUY' ? candle.high >= takeProfit : candle.low <= takeProfit; if (hitSL && hitTP) return { exitIndex: j, exitReason: 'AMBIGUOUS_SAME_CANDLE', risk }; if (hitSL) return { exitIndex: j, exitReason: 'SL', risk }; if (hitTP) return { exitIndex: j, exitReason: 'TP1', risk }; }
  return null;
}
function pathStats(candles, startIndex, endIndex, entryPrice, risk, direction) {
  let maeR = 0, mfeR = 0, reachedHalfAdverse = false, reachedHalfFavorable = false, reached1R = false, reached2R = false, firstHalfAdverse = null, firstHalfFavorable = null, first1R = null, first2R = null;
  if (!Number.isFinite(risk) || risk <= 0) return null;
  for (let j = startIndex; j <= endIndex; j++) { const candle = candles[j]; const adverse = direction === 'BUY' ? (entryPrice - candle.low) / risk : (candle.high - entryPrice) / risk; const favorable = direction === 'BUY' ? (candle.high - entryPrice) / risk : (entryPrice - candle.low) / risk; maeR = Math.max(maeR, adverse); mfeR = Math.max(mfeR, favorable); if (!reachedHalfAdverse && adverse >= 0.5) { reachedHalfAdverse = true; firstHalfAdverse = j - startIndex + 1; } if (!reachedHalfFavorable && favorable >= 0.5) { reachedHalfFavorable = true; firstHalfFavorable = j - startIndex + 1; } if (!reached1R && favorable >= 1) { reached1R = true; first1R = j - startIndex + 1; } if (!reached2R && favorable >= 2) { reached2R = true; first2R = j - startIndex + 1; } }
  return { maeR, mfeR, reachedHalfAdverse, reachedHalfFavorable, reached1R, reached2R, firstHalfAdverse, firstHalfFavorable, first1R, first2R };
}
function postExitStats(candles, exitIndex, entryPrice, risk, direction) {
  if (exitIndex >= candles.length - 1) return null; let favorableFromEntryR = 0, adverseFromEntryR = 0, continuation1R = null, continuation2R = null;
  for (let j = exitIndex + 1; j <= Math.min(candles.length - 1, exitIndex + PATH_HORIZON); j++) { const candle = candles[j]; const favorable = direction === 'BUY' ? (candle.high - entryPrice) / risk : (entryPrice - candle.low) / risk; const adverse = direction === 'BUY' ? (entryPrice - candle.low) / risk : (candle.high - entryPrice) / risk; favorableFromEntryR = Math.max(favorableFromEntryR, favorable); adverseFromEntryR = Math.max(adverseFromEntryR, adverse); if (continuation1R === null && favorable >= 1) continuation1R = j - exitIndex; if (continuation2R === null && favorable >= 2) continuation2R = j - exitIndex; }
  return { favorableFromEntryR, adverseFromEntryR, continuation1R, continuation2R };
}
const raw = (base.trades ?? []).filter(trade => { const entryIndex = Number(trade.entryIndex); return Number.isInteger(entryIndex) && entryIndex < PRE && trade.result !== 'AMBIGUOUS' && Number.isFinite(Number(trade.rMultiple)) && (trade.direction === 'BUY' || trade.direction === 'SELL'); });
const refreshedByTimestamp = new Map(candles.map((c, i) => [c.timestamp, i])); let replayMismatch = 0, missingCanonicalTimestamp = 0, exitMismatch = 0; const exitMismatchDetails = []; const rows = [];
for (const trade of raw) {
  const canonicalIndex = refreshedByTimestamp.get(trade.entryTime); if (!Number.isInteger(canonicalIndex)) { missingCanonicalTimestamp++; continue; }
  const replayed = replayExact(candles, canonicalIndex); if (!replayed || replayed.trigger.timestamp !== trade.entryTime || replayed.trigger.direction !== trade.direction) { replayMismatch++; continue; }
  const entry = Number(trade.entry), stopLoss = Number(trade.stopLoss), tp1 = Number(trade.tp1); const exit = scanToCanonicalExit(candles, canonicalIndex, entry, stopLoss, tp1, trade.direction); const expectedReason = trade.result === 'TP1' ? 'TP1' : 'SL';
  if (!exit || exit.exitReason === 'AMBIGUOUS_SAME_CANDLE' || exit.exitReason !== expectedReason) { exitMismatch++; exitMismatchDetails.push({ entryIndex: Number(trade.entryIndex), canonicalIndex, entryTime: trade.entryTime, direction: trade.direction, expectedReason, reconstructed: exit?.exitReason ?? null, reconstructedExitIndex: exit?.exitIndex ?? null, baselineR: Number(trade.rMultiple) }); continue; }
  const pre = pathStats(candles, canonicalIndex + 1, exit.exitIndex, entry, exit.risk, trade.direction); if (!pre) { exitMismatch++; continue; }
  const post = postExitStats(candles, exit.exitIndex, entry, exit.risk, trade.direction);
  rows.push({ entryIndex: Number(trade.entryIndex), canonicalIndex, entryTime: trade.entryTime, direction: trade.direction, session: session(trade.entryTime), split: Number(trade.entryIndex) <= DEV_END ? 'DEV' : 'VAL', window: WINDOWS.find(w => Number(trade.entryIndex) >= w.start && Number(trade.entryIndex) <= w.end)?.name ?? 'UNKNOWN', r: Number(trade.rMultiple), outcome: Number(trade.rMultiple) > 0 ? 'WIN' : 'LOSS', result: trade.result, entry, stopLoss, tp1, risk: exit.risk, exitIndex: exit.exitIndex, exitBars: exit.exitIndex - canonicalIndex, exitReason: exit.exitReason, pre, post });
}
const losses = rows.filter(x => x.outcome === 'LOSS'); const wins = rows.filter(x => x.outcome === 'WIN');
const summarizePath = subset => ({ n: subset.length, preExitMAE: median(subset.map(x => x.pre.maeR)), preExitMFE: median(subset.map(x => x.pre.mfeR)), preExitHalfAdv: subset.length ? subset.filter(x => x.pre.reachedHalfAdverse).length / subset.length : null, preExitHalfFav: subset.length ? subset.filter(x => x.pre.reachedHalfFavorable).length / subset.length : null, preExit1R: subset.length ? subset.filter(x => x.pre.reached1R).length / subset.length : null, preExit2R: subset.length ? subset.filter(x => x.pre.reached2R).length / subset.length : null, postExit1R: subset.length ? subset.filter(x => x.post?.continuation1R !== null).length / subset.length : null, postExit2R: subset.length ? subset.filter(x => x.post?.continuation2R !== null).length / subset.length : null, postExitFavorableMedianFromEntry: median(subset.map(x => x.post?.favorableFromEntryR)), exitBarsMedian: median(subset.map(x => x.exitBars)) });
const subsets = { losses, wins, BUY: rows.filter(x => x.direction === 'BUY'), SELL: rows.filter(x => x.direction === 'SELL'), SL: rows.filter(x => x.exitReason === 'SL'), TP1: rows.filter(x => x.exitReason === 'TP1') };
const result = { strategy: 'Strategy A / SP2L', mode: 'PHASE_18_PRE_EXIT_VS_POST_EXIT_PATH_ATTRIBUTION', timeframe: '5min', scope: { rawBaselinePre: raw.length, canonicalReplayed: rows.length, dev: rows.filter(x => x.split === 'DEV').length, val: rows.filter(x => x.split === 'VAL').length, freshHoldoutExcluded: true, productionUntouched: true }, integrity: { expectedCanonical: raw.length, rawBaselinePre: raw.length, canonicalReplayed: rows.length, missingCanonicalTimestamp, replayMismatch, exitMismatch, totalMismatch: missingCanonicalTimestamp + replayMismatch + exitMismatch, exitMismatchDetails }, methodology: { purpose: 'Descriptive attribution of favorable/adverse path before versus after the canonical baseline exit; no optimization or rule selection.', pathHorizonBars: PATH_HORIZON, canonicalExit: 'Exact BacktestEngine semantics: first SL+TP same-candle is AMBIGUOUS, otherwise first SL/TP.', noOptimization: true, noThresholdSearch: true, noNewTradingRules: true, noFreshHoldoutAccess: true }, overall: stats(rows), outcome: { losses: summarizePath(losses), wins: summarizePath(wins) }, direction: { BUY: summarizePath(subsets.BUY), SELL: summarizePath(subsets.SELL) }, exitReason: { SL: summarizePath(subsets.SL), TP1: summarizePath(subsets.TP1) }, windows: Object.fromEntries(WINDOWS.map(w => [w.name, summarizePath(rows.filter(x => x.window === w.name))])), cases: rows };
const out = resolve(ROOT, 'data/reports/strategy-a-phase18-pre-exit-vs-post-exit-path-attribution'); await mkdir(out, { recursive: true }); await writeFile(resolve(out, '5min.json'), JSON.stringify(result, null, 2));
console.log(`PHASE_18_PRE_EXIT_VS_POST_EXIT_PATH_ATTRIBUTION 5min N=${rows.length} DEV=${result.scope.dev} VAL=${result.scope.val} FRESH=LOCKED`);
console.log(`INTEGRITY expected=${raw.length} raw=${raw.length} actual=${rows.length} replayMismatch=${replayMismatch} missingCanonicalTimestamp=${missingCanonicalTimestamp} exitMismatch=${exitMismatch}`);
console.log(`OVERALL N=${rows.length} avgR=${result.overall.avgR?.toFixed(6)} PF=${result.overall.PF?.toFixed(6)} WR=${(result.overall.WR * 100)?.toFixed(4)}% totalR=${result.overall.totalR?.toFixed(6)}`);
console.log(`LOSSES preExitMAE=${result.outcome.losses.preExitMAE?.toFixed(6)} preExitMFE=${result.outcome.losses.preExitMFE?.toFixed(6)} preExitHalfFav=${(result.outcome.losses.preExitHalfFav * 100)?.toFixed(4)}% preExit1R=${(result.outcome.losses.preExit1R * 100)?.toFixed(4)}% postExit1R=${(result.outcome.losses.postExit1R * 100)?.toFixed(4)}% postExit2R=${(result.outcome.losses.postExit2R * 100)?.toFixed(4)}% exitBarsMedian=${result.outcome.losses.exitBarsMedian}`);
console.log(`WINS preExitMAE=${result.outcome.wins.preExitMAE?.toFixed(6)} preExitMFE=${result.outcome.wins.preExitMFE?.toFixed(6)} preExitHalfAdv=${(result.outcome.wins.preExitHalfAdv * 100)?.toFixed(4)}% preExit1R=${(result.outcome.wins.preExit1R * 100)?.toFixed(4)}% postExit1R=${(result.outcome.wins.postExit1R * 100)?.toFixed(4)}% postExit2R=${(result.outcome.wins.postExit2R * 100)?.toFixed(4)}% exitBarsMedian=${result.outcome.wins.exitBarsMedian}`);
for (const [name, subset] of Object.entries(result.windows)) console.log(`${name}: N=${subset.n} preMAE=${subset.preExitMAE?.toFixed(6)} preMFE=${subset.preExitMFE?.toFixed(6)} pre1R=${(subset.preExit1R * 100)?.toFixed(2)}% post1R=${(subset.postExit1R * 100)?.toFixed(2)}% post2R=${(subset.postExit2R * 100)?.toFixed(2)}% exitBarsMedian=${subset.exitBarsMedian}`);
console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
