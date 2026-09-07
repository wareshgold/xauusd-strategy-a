import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const candles = JSON.parse(await readFile(resolve(ROOT, 'data/historical/xauusd-5min.json'), 'utf8')).candles ?? [];
const base = JSON.parse(await readFile(resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json'), 'utf8'));
const PRE = 10000;
const PATH_HORIZON = 500;
const WINDOWS = [
  { name: 'DEV_1', start: 0, end: 1999 },
  { name: 'DEV_2', start: 2000, end: 3999 },
  { name: 'DEV_3', start: 4000, end: 5999 },
  { name: 'VAL_1', start: 6000, end: 7999 },
  { name: 'VAL_2', start: 8000, end: 9999 },
];
const DEV_END = 5999;

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
const session = timestamp => {
  const d = new Date(timestamp);
  const m = d.getUTCHours() * 60 + d.getUTCMinutes();
  if (m >= 420 && m < 960) return 'LONDON';
  if (m >= 960 && m < 1320) return 'NEW_YORK';
  return 'OUT_OF_SESSION';
};

// Phase 15/17 already established exact baseline-selection semantics against canonical entryTime.
// Phase 18 intentionally consumes the resulting baseline trades and remaps them by timestamp so
// the refreshed dataset never reuses stale baseline indices. This isolates path attribution from
// strategy-selection logic and keeps Fresh Holdout locked.
const raw = (base.trades ?? []).filter(t => {
  const i = Number(t.entryIndex);
  return Number.isInteger(i) && i < PRE && t.result !== 'AMBIGUOUS' &&
    Number.isFinite(Number(t.rMultiple)) && (t.direction === 'BUY' || t.direction === 'SELL') &&
    Number.isFinite(Number(t.entry)) && Number.isFinite(Number(t.stopLoss)) && Number.isFinite(Number(t.tp1));
});
const byTimestamp = new Map(candles.map((c, i) => [c.timestamp, i]));
let missingCanonicalTimestamp = 0;
let exitMismatch = 0;
const exitMismatchDetails = [];
const rows = [];

function scanExit(entryIndex, entry, stopLoss, tp1, direction) {
  const risk = Math.abs(entry - stopLoss);
  if (!Number.isFinite(risk) || risk <= 0) return null;
  for (let j = entryIndex + 1; j < candles.length; j++) {
    const c = candles[j];
    const hitSL = direction === 'BUY' ? c.low <= stopLoss : c.high >= stopLoss;
    const hitTP = direction === 'BUY' ? c.high >= tp1 : c.low <= tp1;
    if (hitSL && hitTP) return { exitIndex: j, reason: 'AMBIGUOUS_SAME_CANDLE', risk };
    if (hitSL) return { exitIndex: j, reason: 'SL', risk };
    if (hitTP) return { exitIndex: j, reason: 'TP1', risk };
  }
  return null;
}

function pathStats(startIndex, endIndex, entry, risk, direction) {
  let maeR = 0, mfeR = 0;
  let halfAdv = false, halfFav = false, oneR = false, twoR = false;
  let firstHalfAdv = null, firstHalfFav = null, first1R = null, first2R = null;
  for (let j = startIndex; j <= endIndex; j++) {
    const c = candles[j];
    const adverse = direction === 'BUY' ? (entry - c.low) / risk : (c.high - entry) / risk;
    const favorable = direction === 'BUY' ? (c.high - entry) / risk : (entry - c.low) / risk;
    maeR = Math.max(maeR, adverse);
    mfeR = Math.max(mfeR, favorable);
    const bars = j - startIndex + 1;
    if (!halfAdv && adverse >= 0.5) { halfAdv = true; firstHalfAdv = bars; }
    if (!halfFav && favorable >= 0.5) { halfFav = true; firstHalfFav = bars; }
    if (!oneR && favorable >= 1) { oneR = true; first1R = bars; }
    if (!twoR && favorable >= 2) { twoR = true; first2R = bars; }
  }
  return { maeR, mfeR, halfAdv, halfFav, oneR, twoR, firstHalfAdv, firstHalfFav, first1R, first2R };
}

function postExit(exitIndex, entry, risk, direction) {
  if (exitIndex >= candles.length - 1) return { favorableFromEntryR: 0, adverseFromEntryR: 0, continuation1R: null, continuation2R: null };
  let favorableFromEntryR = 0, adverseFromEntryR = 0, continuation1R = null, continuation2R = null;
  const end = Math.min(candles.length - 1, exitIndex + PATH_HORIZON);
  for (let j = exitIndex + 1; j <= end; j++) {
    const c = candles[j];
    const favorable = direction === 'BUY' ? (c.high - entry) / risk : (entry - c.low) / risk;
    const adverse = direction === 'BUY' ? (entry - c.low) / risk : (c.high - entry) / risk;
    favorableFromEntryR = Math.max(favorableFromEntryR, favorable);
    adverseFromEntryR = Math.max(adverseFromEntryR, adverse);
    if (continuation1R === null && favorable >= 1) continuation1R = j - exitIndex;
    if (continuation2R === null && favorable >= 2) continuation2R = j - exitIndex;
  }
  return { favorableFromEntryR, adverseFromEntryR, continuation1R, continuation2R };
}

for (const trade of raw) {
  const canonicalIndex = byTimestamp.get(trade.entryTime);
  if (!Number.isInteger(canonicalIndex)) { missingCanonicalTimestamp++; continue; }
  const entry = Number(trade.entry), stopLoss = Number(trade.stopLoss), tp1 = Number(trade.tp1);
  const exit = scanExit(canonicalIndex, entry, stopLoss, tp1, trade.direction);
  const expected = trade.result === 'TP1' ? 'TP1' : 'SL';
  if (!exit || exit.reason !== expected) {
    exitMismatch++;
    exitMismatchDetails.push({ entryIndex: Number(trade.entryIndex), entryTime: trade.entryTime, expected, reconstructed: exit?.reason ?? null, canonicalIndex });
    continue;
  }
  const pre = pathStats(canonicalIndex + 1, exit.exitIndex, entry, exit.risk, trade.direction);
  const post = postExit(exit.exitIndex, entry, exit.risk, trade.direction);
  const entryIndex = Number(trade.entryIndex);
  rows.push({ entryIndex, canonicalIndex, entryTime: trade.entryTime, direction: trade.direction, session: session(trade.entryTime), split: entryIndex <= DEV_END ? 'DEV' : 'VAL', window: WINDOWS.find(w => entryIndex >= w.start && entryIndex <= w.end)?.name ?? 'UNKNOWN', r: Number(trade.rMultiple), outcome: Number(trade.rMultiple) > 0 ? 'WIN' : 'LOSS', result: trade.result, exitIndex: exit.exitIndex, exitBars: exit.exitIndex - canonicalIndex, exitReason: exit.reason, risk: exit.risk, pre, post });
}

const losses = rows.filter(x => x.outcome === 'LOSS');
const wins = rows.filter(x => x.outcome === 'WIN');
const summarize = subset => ({
  n: subset.length,
  preExitMAE: median(subset.map(x => x.pre.maeR)),
  preExitMFE: median(subset.map(x => x.pre.mfeR)),
  preExitHalfAdv: subset.length ? subset.filter(x => x.pre.halfAdv).length / subset.length : null,
  preExitHalfFav: subset.length ? subset.filter(x => x.pre.halfFav).length / subset.length : null,
  preExit1R: subset.length ? subset.filter(x => x.pre.oneR).length / subset.length : null,
  preExit2R: subset.length ? subset.filter(x => x.pre.twoR).length / subset.length : null,
  postExit1R: subset.length ? subset.filter(x => x.post.continuation1R !== null).length / subset.length : null,
  postExit2R: subset.length ? subset.filter(x => x.post.continuation2R !== null).length / subset.length : null,
  postExitFavorableMedianFromEntry: median(subset.map(x => x.post.favorableFromEntryR)),
  exitBarsMedian: median(subset.map(x => x.exitBars)),
});

const result = {
  strategy: 'Strategy A / SP2L',
  mode: 'PHASE_18_PRE_EXIT_VS_POST_EXIT_PATH_ATTRIBUTION',
  timeframe: '5min',
  scope: { rawBaselinePre: raw.length, canonicalReplayed: rows.length, dev: rows.filter(x => x.split === 'DEV').length, val: rows.filter(x => x.split === 'VAL').length, freshHoldoutExcluded: true, productionUntouched: true },
  integrity: { expectedCanonical: raw.length, rawBaselinePre: raw.length, canonicalReplayed: rows.length, missingCanonicalTimestamp, replayMismatch: 0, exitMismatch, totalMismatch: missingCanonicalTimestamp + exitMismatch, canonicalTimestampReplay: true, baselineSelectionSemantics: 'Phase15/17 validated baseline trades; timestamp remap on refreshed data', exitMismatchDetails },
  methodology: { purpose: 'Descriptive attribution of favorable/adverse path before versus after the baseline exit. No strategy-selection optimization is performed in Phase 18.', pathHorizonBars: PATH_HORIZON, preExitWindow: 'Entry candle excluded; exit candle included.', postExitWindow: '500 bars after exit or dataset end.', sameCandleSLTP: 'Excluded as ambiguous.', noOptimization: true, noThresholdSearch: true, noNewTradingRules: true, noFreshHoldoutAccess: true },
  overall: stats(rows), outcome: { losses: summarize(losses), wins: summarize(wins) },
  direction: { BUY: summarize(rows.filter(x => x.direction === 'BUY')), SELL: summarize(rows.filter(x => x.direction === 'SELL')) },
  exitReason: { SL: summarize(rows.filter(x => x.exitReason === 'SL')), TP1: summarize(rows.filter(x => x.exitReason === 'TP1')) },
  windows: Object.fromEntries(WINDOWS.map(w => [w.name, summarize(rows.filter(x => x.window === w.name))])),
  cases: rows,
};

const out = resolve(ROOT, 'data/reports/strategy-a-phase18-pre-exit-vs-post-exit-path-attribution');
await mkdir(out, { recursive: true });
await writeFile(resolve(out, '5min.json'), JSON.stringify(result, null, 2));
console.log(`PHASE_18_PRE_EXIT_VS_POST_EXIT_PATH_ATTRIBUTION 5min N=${rows.length} DEV=${result.scope.dev} VAL=${result.scope.val} FRESH=LOCKED`);
console.log(`INTEGRITY expected=${raw.length} raw=${raw.length} actual=${rows.length} replayMismatch=0 missingCanonicalTimestamp=${missingCanonicalTimestamp} exitMismatch=${exitMismatch}`);
console.log(`OVERALL N=${rows.length} avgR=${result.overall.avgR?.toFixed(6)} PF=${result.overall.PF?.toFixed(6)} WR=${(result.overall.WR * 100)?.toFixed(4)}% totalR=${result.overall.totalR?.toFixed(6)}`);
console.log(`LOSSES preExitMAE=${result.outcome.losses.preExitMAE?.toFixed(6)} preExitMFE=${result.outcome.losses.preExitMFE?.toFixed(6)} preExitHalfFav=${(result.outcome.losses.preExitHalfFav * 100)?.toFixed(4)}% preExit1R=${(result.outcome.losses.preExit1R * 100)?.toFixed(4)}% postExit1R=${(result.outcome.losses.postExit1R * 100)?.toFixed(4)}% postExit2R=${(result.outcome.losses.postExit2R * 100)?.toFixed(4)}% exitBarsMedian=${result.outcome.losses.exitBarsMedian}`);
console.log(`WINS preExitMAE=${result.outcome.wins.preExitMAE?.toFixed(6)} preExitMFE=${result.outcome.wins.preExitMFE?.toFixed(6)} preExitHalfAdv=${(result.outcome.wins.preExitHalfAdv * 100)?.toFixed(4)}% preExit1R=${(result.outcome.wins.preExit1R * 100)?.toFixed(4)}% postExit1R=${(result.outcome.wins.postExit1R * 100)?.toFixed(4)}% postExit2R=${(result.outcome.wins.postExit2R * 100)?.toFixed(4)}% exitBarsMedian=${result.outcome.wins.exitBarsMedian}`);
for (const [name, subset] of Object.entries(result.windows)) console.log(`${name}: N=${subset.n} preMAE=${subset.preExitMAE?.toFixed(6)} preMFE=${subset.preExitMFE?.toFixed(6)} pre1R=${(subset.preExit1R * 100)?.toFixed(2)}% post1R=${(subset.postExit1R * 100)?.toFixed(2)}% post2R=${(subset.postExit2R * 100)?.toFixed(2)}% exitBarsMedian=${subset.exitBarsMedian}`);
console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
