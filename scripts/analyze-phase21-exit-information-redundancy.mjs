import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const PRE = 10000;
const POST_HORIZON = 500;
const WINDOWS = [
  { name: 'DEV_1', start: 0, end: 1999 },
  { name: 'DEV_2', start: 2000, end: 3999 },
  { name: 'DEV_3', start: 4000, end: 5999 },
  { name: 'VAL_1', start: 6000, end: 7999 },
  { name: 'VAL_2', start: 8000, end: 9999 },
];
const FEATURE_NAMES = [
  'exitBars', 'exitRangeR', 'exitBodyR', 'exitCloseLocation',
  'exitUpperWickShare', 'exitLowerWickShare', 'exitSignedBodyToRange',
  'previousRangeR', 'recentNetMoveR', 'recentPathEfficiency', 'recentRangeR',
  'exitVsEntryR', 'exitVsEntryAbsR',
];
const FEATURE_FAMILIES = {
  exit_timing: ['exitBars'],
  exit_candle_intensity: ['exitRangeR', 'exitBodyR', 'exitSignedBodyToRange', 'exitCloseLocation', 'exitUpperWickShare', 'exitLowerWickShare'],
  recent_path: ['previousRangeR', 'recentNetMoveR', 'recentPathEfficiency', 'recentRangeR'],
  displacement_from_entry: ['exitVsEntryR', 'exitVsEntryAbsR'],
};

const candles = (JSON.parse(await readFile(resolve(ROOT, 'data/historical/xauusd-5min.json'), 'utf8')).candles ?? []);
const base = JSON.parse(await readFile(resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json'), 'utf8'));

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
const sd = values => {
  const v = values.filter(Number.isFinite);
  if (v.length < 2) return null;
  const m = mean(v);
  return Math.sqrt(v.reduce((s, x) => s + (x - m) ** 2, 0) / (v.length - 1));
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
const rank = values => {
  const pairs = values.map((v, i) => ({ v, i })).filter(x => Number.isFinite(x.v)).sort((a, b) => a.v - b.v);
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
};
function spearman(a, b) {
  const pairs = [];
  for (let i = 0; i < a.length; i++) if (Number.isFinite(a[i]) && Number.isFinite(b[i])) pairs.push([a[i], b[i]]);
  if (pairs.length < 3) return null;
  const ra = rank(pairs.map(x => x[0]));
  const rb = rank(pairs.map(x => x[1]));
  const ma = mean(ra), mb = mean(rb);
  let num = 0, da = 0, db = 0;
  for (let i = 0; i < ra.length; i++) {
    const xa = ra[i] - ma, xb = rb[i] - mb;
    num += xa * xb; da += xa * xa; db += xb * xb;
  }
  return da && db ? num / Math.sqrt(da * db) : null;
}
function auc(target, nonTarget) {
  const a = target.filter(Number.isFinite), b = nonTarget.filter(Number.isFinite);
  if (!a.length || !b.length) return null;
  let wins = 0, ties = 0;
  for (const x of a) for (const y of b) {
    if (x > y) wins++;
    else if (x === y) ties++;
  }
  return (wins + ties * 0.5) / (a.length * b.length);
}
function session(ts) {
  const d = new Date(ts);
  const m = d.getUTCHours() * 60 + d.getUTCMinutes();
  if (m >= 420 && m < 960) return 'LONDON';
  if (m >= 960 && m < 1320) return 'NEW_YORK';
  return 'OUT_OF_SESSION';
}
function canonicalExit(entryIndex, entry, sl, tp, direction) {
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
function exitFeatures(entryIndex, exitIndex, entry, risk, direction) {
  const c = candles[exitIndex];
  const p = candles[Math.max(entryIndex, exitIndex - 1)];
  const range = Math.max(0, Number(c.high) - Number(c.low));
  const body = Math.abs(Number(c.close) - Number(c.open));
  const closeLocation = range ? (Number(c.close) - Number(c.low)) / range : null;
  const upperWickShare = range ? (Number(c.high) - Math.max(Number(c.open), Number(c.close))) / range : null;
  const lowerWickShare = range ? (Math.min(Number(c.open), Number(c.close)) - Number(c.low)) / range : null;
  const signedBodyToRange = range ? (Number(c.close) - Number(c.open)) / range : null;
  const previousRange = Math.max(0, Number(p.high) - Number(p.low));
  const recentStart = Math.max(entryIndex, exitIndex - 3);
  let netMove = 0, pathRange = 0, absMove = 0;
  for (let j = recentStart + 1; j <= exitIndex; j++) {
    const a = candles[j - 1], b = candles[j];
    const d = Number(b.close) - Number(a.close);
    netMove += d;
    absMove += Math.abs(d);
    pathRange += Math.max(0, Number(b.high) - Number(b.low));
  }
  const exitVsEntryR = (Number(c.close) - entry) / risk;
  return {
    exitBars: exitIndex - entryIndex,
    exitRangeR: range / risk,
    exitBodyR: body / risk,
    exitCloseLocation: closeLocation,
    exitUpperWickShare: upperWickShare,
    exitLowerWickShare: lowerWickShare,
    exitSignedBodyToRange: signedBodyToRange,
    previousRangeR: previousRange / risk,
    recentNetMoveR: netMove / risk,
    recentPathEfficiency: absMove ? Math.abs(netMove) / absMove : null,
    recentRangeR: pathRange / risk,
    exitVsEntryR,
    exitVsEntryAbsR: Math.abs(exitVsEntryR),
    directionalClose: direction === 'BUY' ? Number(c.close) > Number(c.open) : Number(c.close) < Number(c.open),
  };
}
function postContinuation(exitIndex, exitPrice, risk, direction) {
  let mfeR = 0, maeR = 0, tHalf = null, t1 = null, t2 = null;
  for (let j = exitIndex + 1; j <= Math.min(candles.length - 1, exitIndex + POST_HORIZON); j++) {
    const c = candles[j];
    const favorable = direction === 'BUY' ? (c.high - exitPrice) / risk : (exitPrice - c.low) / risk;
    const adverse = direction === 'BUY' ? (exitPrice - c.low) / risk : (c.high - exitPrice) / risk;
    mfeR = Math.max(mfeR, favorable);
    maeR = Math.max(maeR, adverse);
    if (tHalf === null && favorable >= 0.5) tHalf = j - exitIndex;
    if (t1 === null && favorable >= 1) t1 = j - exitIndex;
    if (t2 === null && favorable >= 2) t2 = j - exitIndex;
  }
  return { mfeR, maeR, tHalf, t1, t2, hasPost1: mfeR >= 1 };
}

const raw = (base.trades ?? []).filter(t => {
  const i = Number(t.entryIndex);
  return Number.isInteger(i) && i < PRE && t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && (t.direction === 'BUY' || t.direction === 'SELL');
});
let replayMismatch = 0, exitMismatch = 0;
const rows = [];
for (const t of raw) {
  const i = Number(t.entryIndex);
  const refreshedIndex = candles.findIndex(c => c.timestamp === t.entryTime);
  if (refreshedIndex < 0 || candles[refreshedIndex].timestamp !== t.entryTime) { replayMismatch++; continue; }
  if (candles[refreshedIndex].timestamp !== t.entryTime) { replayMismatch++; continue; }
  const entry = Number(t.entry), sl = Number(t.stopLoss), tp = Number(t.tp1);
  const ex = canonicalExit(refreshedIndex, entry, sl, tp, t.direction);
  const expected = t.result === 'TP1' ? 'TP1' : 'SL';
  if (!ex || ex.reason !== expected) { exitMismatch++; continue; }
  const features = exitFeatures(refreshedIndex, ex.index, entry, ex.risk, t.direction);
  const post = postContinuation(ex.index, expected === 'TP1' ? tp : sl, ex.risk, t.direction);
  rows.push({ entryIndex: i, entryTime: t.entryTime, direction: t.direction, session: session(t.entryTime), split: i <= 5999 ? 'DEV' : 'VAL', window: WINDOWS.find(w => i >= w.start && i <= w.end)?.name ?? 'UNKNOWN', r: Number(t.rMultiple), outcome: Number(t.rMultiple) > 0 ? 'WIN' : 'LOSS', exitReason: ex.reason, features, post });
}

const losses = rows.filter(x => x.outcome === 'LOSS');
const target = losses.filter(x => x.post.hasPost1);
const nonTarget = losses.filter(x => !x.post.hasPost1);
const featureTargetStats = Object.fromEntries(FEATURE_NAMES.map(k => {
  const a = target.map(x => x.features[k]);
  const b = nonTarget.map(x => x.features[k]);
  const am = mean(a), bm = mean(b), as = sd(a), bs = sd(b);
  const na = a.filter(Number.isFinite).length, nb = b.filter(Number.isFinite).length;
  const pooled = as !== null && bs !== null && na + nb > 2 ? Math.sqrt(((na - 1) * as ** 2 + (nb - 1) * bs ** 2) / (na + nb - 2)) : null;
  return [k, { targetMean: am, nonTargetMean: bm, delta: am !== null && bm !== null ? am - bm : null, targetMedian: median(a), nonTargetMedian: median(b), standardizedDelta: pooled ? (am - bm) / pooled : null, aucTargetGreater: auc(a, b) }];
}));
const pairwise = [];
for (let i = 0; i < FEATURE_NAMES.length; i++) for (let j = i + 1; j < FEATURE_NAMES.length; j++) {
  const r = spearman(rows.map(x => x.features[FEATURE_NAMES[i]]), rows.map(x => x.features[FEATURE_NAMES[j]]));
  if (r !== null) pairwise.push({ a: FEATURE_NAMES[i], b: FEATURE_NAMES[j], spearman: r });
}
pairwise.sort((a, b) => Math.abs(b.spearman) - Math.abs(a.spearman));
const familySummary = Object.fromEntries(Object.entries(FEATURE_FAMILIES).map(([family, features]) => [family, {
  features,
  targetEffects: features.map(f => ({ feature: f, ...featureTargetStats[f] })),
  withinFamilyCorrelations: pairwise.filter(p => features.includes(p.a) && features.includes(p.b)).slice(0, 10),
}]));
function breakdown(field, values) {
  return Object.fromEntries(values.map(v => {
    const a = losses.filter(x => x[field] === v);
    return [v, { n: a.length, continuation1R: pct(a.map(x => x.post.hasPost1)) }];
  }));
}

const result = {
  strategy: 'Strategy A / SP2L',
  mode: 'PHASE_21_EXIT_INFORMATION_REDUNDANCY',
  timeframe: '5min',
  scope: { rawBaselinePre: raw.length, canonicalReplayed: rows.length, dev: rows.filter(x => x.split === 'DEV').length, val: rows.filter(x => x.split === 'VAL').length, freshHoldoutExcluded: true, productionUntouched: true },
  integrity: { expectedCanonical: raw.length, rawBaselinePre: raw.length, canonicalReplayed: rows.length, replayMismatch, exitMismatch, totalMismatch: replayMismatch + exitMismatch },
  methodology: {
    purpose: 'Descriptive redundancy audit of information available at canonical exit. Measures whether exit-time features carry distinct information beyond one another when retrospectively separating losses by post-exit continuation.',
    label: 'Loss with future post-exit MFE >=1R within 500 bars.',
    featuresUseOnlyExitTimeInformation: true,
    futureLeakageGuard: 'Post-exit continuation is a retrospective label only; no future candle enters any exit feature.',
    noOptimization: true,
    noThresholdSearch: true,
    noNewTradingRules: true,
    noFreshHoldoutAccess: true,
  },
  overall: stats(rows),
  losses: { n: losses.length, continuation1R: target.length, continuation1RShare: losses.length ? target.length / losses.length : null, nonContinuation1R: nonTarget.length, featureTargetStats, pairwiseFeatureCorrelations: pairwise, familySummary },
  direction: breakdown('direction', ['BUY', 'SELL']),
  session: breakdown('session', ['LONDON', 'NEW_YORK', 'OUT_OF_SESSION']),
  window: breakdown('window', WINDOWS.map(x => x.name)),
};

const out = resolve(ROOT, 'data/reports/strategy-a-phase21-exit-information-redundancy');
await mkdir(out, { recursive: true });
await writeFile(resolve(out, '5min.json'), JSON.stringify(result, null, 2));
console.log(`PHASE_21_EXIT_INFORMATION_REDUNDANCY 5min N=${rows.length} DEV=${rows.filter(x => x.split === 'DEV').length} VAL=${rows.filter(x => x.split === 'VAL').length} FRESH=LOCKED`);
console.log(`INTEGRITY expected=${raw.length} raw=${raw.length} actual=${rows.length} replayMismatch=${replayMismatch} exitMismatch=${exitMismatch}`);
console.log(`OVERALL N=${rows.length} avgR=${result.overall.avgR?.toFixed(6)} PF=${result.overall.PF?.toFixed(6)} WR=${(result.overall.WR * 100)?.toFixed(4)}% totalR=${result.overall.totalR?.toFixed(6)}`);
console.log(`LOSSES N=${losses.length} CONT_GE_1R=${target.length} share=${(result.losses.continuation1RShare * 100).toFixed(4)}% NO_CONT=${nonTarget.length}`);
for (const k of FEATURE_NAMES) { const s = featureTargetStats[k]; console.log(`FEATURE ${k}: stdDelta=${s.standardizedDelta?.toFixed(4)} auc=${s.aucTargetGreater?.toFixed(4)} delta=${s.delta?.toFixed(6)}`); }
console.log('TOP_FEATURE_CORRELATIONS');
for (const p of pairwise.slice(0, 12)) console.log(`CORR ${p.a} ~ ${p.b}: spearman=${p.spearman.toFixed(4)}`);
for (const [k, v] of Object.entries(result.direction)) console.log(`DIRECTION ${k}: N=${v.n} continuation1R=${(v.continuation1R * 100).toFixed(2)}%`);
for (const [k, v] of Object.entries(result.session)) console.log(`SESSION ${k}: N=${v.n} continuation1R=${(v.continuation1R * 100).toFixed(2)}%`);
for (const [k, v] of Object.entries(result.window)) console.log(`WINDOW ${k}: N=${v.n} continuation1R=${(v.continuation1R * 100).toFixed(2)}%`);
console.log(`REPORT=${resolve(out, '5min.json')}`);
console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
