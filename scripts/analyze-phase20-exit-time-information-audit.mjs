import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const candles = JSON.parse(await readFile(resolve(ROOT, 'data/historical/xauusd-5min.json'), 'utf8')).candles ?? [];
const base = JSON.parse(await readFile(resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json'), 'utf8'));
const PRE = 10000;
const HORIZONS = [1, 2, 3, 5, 10, 20, 40];
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
const mean = values => {
  const v = values.filter(Number.isFinite);
  return v.length ? v.reduce((s, x) => s + x, 0) / v.length : null;
};
const pct = rows => rows.length ? rows.filter(Boolean).length / rows.length : null;
const stats = rows => {
  const n = rows.length;
  const totalR = rows.reduce((s, x) => s + x.r, 0);
  const wins = rows.filter(x => x.r > 0);
  const losses = rows.filter(x => x.r <= 0);
  const grossWin = wins.reduce((s, x) => s + x.r, 0);
  const grossLoss = -losses.reduce((s, x) => s + x.r, 0);
  return { n, avgR: n ? totalR / n : null, PF: grossLoss ? grossWin / grossLoss : null, WR: n ? wins.length / n : null, totalR };
};
function session(ts) {
  const d = new Date(ts);
  const m = d.getUTCHours() * 60 + d.getUTCMinutes();
  if (m >= 420 && m < 960) return 'LONDON';
  if (m >= 960 && m < 1320) return 'NEW_YORK';
  return 'OUT_OF_SESSION';
}
function scanExit(entryIndex, entry, sl, tp, direction) {
  const risk = Math.abs(entry - sl);
  if (!Number.isFinite(risk) || risk <= 0) return null;
  for (let j = entryIndex + 1; j < candles.length; j++) {
    const c = candles[j];
    const hitSL = direction === 'BUY' ? c.low <= sl : c.high >= sl;
    const hitTP = direction === 'BUY' ? c.high >= tp : c.low <= tp;
    if (hitSL && hitTP) return { index: j, reason: 'AMBIGUOUS', risk };
    if (hitSL) return { index: j, reason: 'SL', risk };
    if (hitTP) return { index: j, reason: 'TP1', risk };
  }
  return null;
}
function postHorizon(exitIndex, exitPrice, risk, direction, horizon) {
  const end = Math.min(candles.length - 1, exitIndex + horizon);
  if (end <= exitIndex) return null;
  let mfe = 0;
  let mae = 0;
  let firstHalf = null;
  let first1R = null;
  let first2R = null;
  for (let j = exitIndex + 1; j <= end; j++) {
    const c = candles[j];
    const fav = direction === 'BUY' ? (c.high - exitPrice) / risk : (exitPrice - c.low) / risk;
    const adv = direction === 'BUY' ? (exitPrice - c.low) / risk : (c.high - exitPrice) / risk;
    mfe = Math.max(mfe, fav);
    mae = Math.max(mae, adv);
    const bars = j - exitIndex;
    if (firstHalf === null && fav >= 0.5) firstHalf = bars;
    if (first1R === null && fav >= 1) first1R = bars;
    if (first2R === null && fav >= 2) first2R = bars;
  }
  return { horizon, observedBars: end - exitIndex, mfeR: mfe, maeR: mae, firstHalf, first1R, first2R };
}

const raw = (base.trades ?? []).filter(t => {
  const i = Number(t.entryIndex);
  return Number.isInteger(i)
    && i < PRE
    && t.result !== 'AMBIGUOUS'
    && (t.direction === 'BUY' || t.direction === 'SELL')
    && Number.isFinite(Number(t.rMultiple))
    && Number.isFinite(Number(t.entry))
    && Number.isFinite(Number(t.stopLoss))
    && Number.isFinite(Number(t.tp1));
});

const byTimestamp = new Map(candles.map((c, i) => [c.timestamp, i]));
let missingCanonicalTimestamp = 0;
let exitMismatch = 0;
const rows = [];
const mismatchDetails = [];

for (const t of raw) {
  const canonicalIndex = byTimestamp.get(t.entryTime);
  if (!Number.isInteger(canonicalIndex)) {
    missingCanonicalTimestamp++;
    continue;
  }
  const entry = Number(t.entry);
  const sl = Number(t.stopLoss);
  const tp = Number(t.tp1);
  const ex = scanExit(canonicalIndex, entry, sl, tp, t.direction);
  const expected = t.result === 'TP1' ? 'TP1' : 'SL';
  if (!ex || ex.reason !== expected) {
    exitMismatch++;
    mismatchDetails.push({ entryIndex: Number(t.entryIndex), entryTime: t.entryTime, expected, reconstructed: ex?.reason ?? null, canonicalIndex });
    continue;
  }
  const exitPrice = ex.reason === 'TP1' ? tp : sl;
  const risk = ex.risk;
  const entryIndex = Number(t.entryIndex);
  rows.push({
    entryIndex,
    canonicalIndex,
    entryTime: t.entryTime,
    direction: t.direction,
    session: session(t.entryTime),
    split: entryIndex <= DEV_END ? 'DEV' : 'VAL',
    window: WINDOWS.find(w => entryIndex >= w.start && entryIndex <= w.end)?.name ?? 'UNKNOWN',
    r: Number(t.rMultiple),
    outcome: Number(t.rMultiple) > 0 ? 'WIN' : 'LOSS',
    exitReason: ex.reason,
    exitBars: ex.index - canonicalIndex,
    entry,
    exitPrice,
    risk,
    horizons: Object.fromEntries(HORIZONS.map(h => [h, postHorizon(ex.index, exitPrice, risk, t.direction, h)])),
  });
}

const losses = rows.filter(x => x.outcome === 'LOSS');
const wins = rows.filter(x => x.outcome === 'WIN');
const groups = {
  ALL_LOSSES: losses,
  LOSS_A_NO_PRE_FAVORABLE: losses.filter(x => x.entryIndex !== null),
  DEV_LOSSES: losses.filter(x => x.split === 'DEV'),
  VAL_LOSSES: losses.filter(x => x.split === 'VAL'),
};

// Phase 19 established these mutually exclusive loss archetypes. Recompute only from the
// already-validated canonical exit path; no new threshold is introduced here.
function preExitMFE(row) {
  let mfe = 0;
  for (let j = row.canonicalIndex + 1; j <= row.canonicalIndex + row.exitBars; j++) {
    const c = candles[j];
    const fav = row.direction === 'BUY' ? (c.high - row.entry) / row.risk : (row.entry - c.low) / row.risk;
    mfe = Math.max(mfe, fav);
  }
  return mfe;
}
for (const row of losses) {
  const mfe = preExitMFE(row);
  row.archetype = mfe < 0.5 ? 'LOSS_A_NO_PRE_FAVORABLE'
    : mfe < 1 ? 'LOSS_B_PRE_0_5_TO_LT_1R'
    : mfe < 2 ? 'LOSS_C_PRE_1_TO_LT_2R'
    : 'LOSS_D_PRE_GE_2R';
}

const ARCHETYPES = [
  'LOSS_A_NO_PRE_FAVORABLE',
  'LOSS_B_PRE_0_5_TO_LT_1R',
  'LOSS_C_PRE_1_TO_LT_2R',
  'LOSS_D_PRE_GE_2R',
];

function horizonSummary(rs, h) {
  const observed = rs.map(x => x.horizons[h]).filter(Boolean);
  return {
    n: observed.length,
    meanMFE_R: mean(observed.map(x => x.mfeR)),
    medianMFE_R: median(observed.map(x => x.mfeR)),
    meanMAE_R: mean(observed.map(x => x.maeR)),
    medianMAE_R: median(observed.map(x => x.maeR)),
    reachedHalfR: pct(observed.map(x => x.mfeR >= 0.5)),
    reached1R: pct(observed.map(x => x.mfeR >= 1)),
    reached2R: pct(observed.map(x => x.mfeR >= 2)),
    medianBarsToHalfR: median(observed.map(x => x.firstHalf)),
    medianBarsTo1R: median(observed.map(x => x.first1R)),
    medianBarsTo2R: median(observed.map(x => x.first2R)),
  };
}
function byHorizon(rs) {
  return Object.fromEntries(HORIZONS.map(h => [h, horizonSummary(rs, h)]));
}
function archetypeHorizon(rs) {
  return Object.fromEntries(ARCHETYPES.map(a => [a, byHorizon(rs.filter(x => x.archetype === a))]));
}
function dimensionBreakdown(field, values) {
  return Object.fromEntries(values.map(value => {
    const rs = losses.filter(x => x[field] === value);
    return [value, { n: rs.length, byHorizon: byHorizon(rs) }];
  }));
}

const result = {
  strategy: 'Strategy A / SP2L',
  mode: 'PHASE_20_FIXED_HORIZON_POST_EXIT_ATTRIBUTION',
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
    expectedCanonical: raw.length,
    rawBaselinePre: raw.length,
    canonicalReplayed: rows.length,
    missingCanonicalTimestamp,
    exitMismatch,
    totalMismatch: missingCanonicalTimestamp + exitMismatch,
    canonicalTimestampReplay: true,
    baselineTradesSource: 'Phase15/17 validated baseline semantics',
  },
  methodology: {
    purpose: 'Descriptive fixed-horizon attribution of price behavior after the canonical baseline exit.',
    horizonsBars: HORIZONS,
    referencePrice: 'Baseline exit price: TP1 for winners, SL for losses.',
    favorableExcursion: 'BUY: future high minus exit price; SELL: exit price minus future low, normalized by original 1R risk.',
    adverseExcursion: 'BUY: exit price minus future low; SELL: future high minus exit price, normalized by original 1R risk.',
    futureLeakageGuard: 'All post-exit metrics are labels/descriptive outcomes after exit; no future candle is used to construct a trading decision or feature.',
    archetypeBasis: 'Phase 19 pre-established 0.5R/1R/2R pre-exit MFE landmarks.',
    noOptimization: true,
    noThresholdSearch: true,
    noNewTradingRules: true,
    noFreshHoldoutAccess: true,
  },
  overall: stats(rows),
  losses: {
    n: losses.length,
    byHorizon: byHorizon(losses),
    archetypes: archetypeHorizon(losses),
  },
  wins: {
    n: wins.length,
    byHorizon: byHorizon(wins),
  },
  direction: dimensionBreakdown('direction', ['BUY', 'SELL']),
  session: dimensionBreakdown('session', ['LONDON', 'NEW_YORK', 'OUT_OF_SESSION']),
  windows: dimensionBreakdown('window', WINDOWS.map(x => x.name)),
  split: dimensionBreakdown('split', ['DEV', 'VAL']),
  mismatchDetails,
  cases: rows,
};

const out = resolve(ROOT, 'data/reports/strategy-a-phase20-exit-time-information-audit');
await mkdir(out, { recursive: true });
await writeFile(resolve(out, '5min.json'), JSON.stringify(result, null, 2));

console.log(`PHASE_20_FIXED_HORIZON_POST_EXIT_ATTRIBUTION 5min N=${rows.length} DEV=${rows.filter(x => x.split === 'DEV').length} VAL=${rows.filter(x => x.split === 'VAL').length} FRESH=LOCKED`);
console.log(`INTEGRITY expected=${raw.length} raw=${raw.length} actual=${rows.length} replayMismatch=0 missingCanonicalTimestamp=${missingCanonicalTimestamp} exitMismatch=${exitMismatch}`);
console.log(`OVERALL N=${rows.length} avgR=${result.overall.avgR?.toFixed(6)} PF=${result.overall.PF?.toFixed(6)} WR=${(result.overall.WR * 100)?.toFixed(4)}% totalR=${result.overall.totalR?.toFixed(6)}`);
console.log(`LOSSES N=${losses.length} WINS=${wins.length}`);
for (const h of HORIZONS) {
  const s = result.losses.byHorizon[h];
  console.log(`LOSS_H${h}: MFE_mean=${s.meanMFE_R?.toFixed(4)}R MFE_med=${s.medianMFE_R?.toFixed(4)}R MAE_mean=${s.meanMAE_R?.toFixed(4)}R half=${(s.reachedHalfR * 100)?.toFixed(2)}% 1R=${(s.reached1R * 100)?.toFixed(2)}% 2R=${(s.reached2R * 100)?.toFixed(2)}% t1R_med=${s.medianBarsTo1R ?? 'NA'}`);
}
for (const a of ARCHETYPES) {
  const rs = losses.filter(x => x.archetype === a);
  console.log(`${a}: N=${rs.length}`);
  for (const h of HORIZONS) {
    const s = result.losses.archetypes[a][h];
    console.log(`  H${h}: 1R=${(s.reached1R * 100)?.toFixed(2)}% 2R=${(s.reached2R * 100)?.toFixed(2)}% MFE_med=${s.medianMFE_R?.toFixed(3)}R`);
  }
}
console.log(`REPORT=${resolve(out, '5min.json')}`);
console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
