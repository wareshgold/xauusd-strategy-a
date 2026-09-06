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
const POST_HORIZON = 500;
const CFG = { breakoutLookback: 5, followThrough: { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true }, spike: { maxCandles: 8, minDirectionalFraction: 0.5, maxOverlapFraction: 0.8 } };
const WINDOWS = [
  { name: 'DEV_1', start: 0, end: 1999 }, { name: 'DEV_2', start: 2000, end: 3999 }, { name: 'DEV_3', start: 4000, end: 5999 },
  { name: 'VAL_1', start: 6000, end: 7999 }, { name: 'VAL_2', start: 8000, end: 9999 },
];
const DEV_END = 5999;
const FAMILIES = {
  directional_displacement: ['exitVsEntryR', 'recentNetMoveR', 'exitSignedBodyToRange'],
  exit_candle_intensity: ['exitRangeR', 'exitBodyR', 'exitCloseLocation', 'exitUpperWickShare', 'exitLowerWickShare'],
  prior_bar_expansion: ['previousRangeR'],
};
const FEATURE_NAMES = Object.values(FAMILIES).flat();
const mean = values => { const v = values.filter(Number.isFinite); return v.length ? v.reduce((s, x) => s + x, 0) / v.length : null; };
const sd = values => { const v = values.filter(Number.isFinite); if (v.length < 2) return null; const m = mean(v); return Math.sqrt(v.reduce((s, x) => s + (x - m) ** 2, 0) / (v.length - 1)); };
const median = values => { const v = values.filter(Number.isFinite).sort((a, b) => a - b); if (!v.length) return null; const m = Math.floor(v.length / 2); return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2; };
const stats = rows => { const n = rows.length, totalR = rows.reduce((s, x) => s + x.r, 0), wins = rows.filter(x => x.r > 0), losses = rows.filter(x => x.r <= 0), gw = wins.reduce((s, x) => s + x.r, 0), gl = -losses.reduce((s, x) => s + x.r, 0); return { n, avgR: n ? totalR / n : null, PF: gl ? gw / gl : null, WR: n ? wins.length / n : null, totalR }; };
const pct = rows => rows.length ? rows.filter(Boolean).length / rows.length : null;
const rank = values => { const pairs = values.map((v, i) => ({ v, i })).filter(x => Number.isFinite(x.v)).sort((a, b) => a.v - b.v); const out = Array(values.length).fill(null); let i = 0; while (i < pairs.length) { let j = i + 1; while (j < pairs.length && pairs[j].v === pairs[i].v) j++; const r = (i + 1 + j) / 2; for (let k = i; k < j; k++) out[pairs[k].i] = r; i = j; } return out; };
function percentileRanks(rows, key) { const values = rows.map(x => x.features[key]); const rs = rank(values); const n = rows.length; return rs.map(r => Number.isFinite(r) && n > 1 ? (r - 1) / (n - 1) : null); }
function auc(target, non) { const a = target.filter(Number.isFinite), b = non.filter(Number.isFinite); if (!a.length || !b.length) return null; let wins = 0, ties = 0; for (const x of a) for (const y of b) { if (x > y) wins++; else if (x === y) ties++; } return (wins + 0.5 * ties) / (a.length * b.length); }
function session(ts) { const d = new Date(ts), m = d.getUTCHours() * 60 + d.getUTCMinutes(); if (m >= 420 && m < 960) return 'LONDON'; if (m >= 960 && m < 1320) return 'NEW_YORK'; return 'OUT_OF_SESSION'; }
function replay(entryIndex) { const view = candles.slice(0, entryIndex + 1); if (view.length < 60) return null; const bo = detectBreakout(view, CFG.breakoutLookback), ft = detectFollowThrough(view, bo, CFG.followThrough), sp = detectSpikeCandidates(view, bo, ft, CFG.spike); for (const s of sp.candidates) { if (s.endIndex >= entryIndex) continue; const co = detectFirstCorrection(view, s); if (!co || co.correctionExtremeIndex >= entryIndex) continue; const tr = detectEntryTrigger(view, co); if (!tr || tr.index !== entryIndex) continue; const b = bo.find(x => x.index === s.breakoutIndex && x.direction === s.direction), f = ft.find(x => x.breakoutIndex === s.breakoutIndex && x.direction === s.direction); if (b && f) return { s, co, tr, b, f }; } return null; }
function canonicalExit(entryIndex, entry, sl, tp, direction) { const risk = Math.abs(entry - sl); if (!Number.isFinite(risk) || risk <= 0) return null; for (let j = entryIndex + 1; j < candles.length; j++) { const c = candles[j], hitSL = direction === 'BUY' ? c.low <= sl : c.high >= sl, hitTP = direction === 'BUY' ? c.high >= tp : c.low <= tp; if (hitSL && hitTP) return { index: j, reason: 'AMBIGUOUS', risk }; if (hitSL) return { index: j, reason: 'SL', risk }; if (hitTP) return { index: j, reason: 'TP1', risk }; } return null; }
function exitFeatures(entryIndex, exitIndex, entry, risk) { const c = candles[exitIndex], p = candles[Math.max(entryIndex, exitIndex - 1)], range = Math.max(0, Number(c.high) - Number(c.low)), body = Math.abs(Number(c.close) - Number(c.open)); const closeLoc = range ? (Number(c.close) - Number(c.low)) / range : null; const upper = range ? (Number(c.high) - Math.max(Number(c.open), Number(c.close))) / range : null; const lower = range ? (Math.min(Number(c.open), Number(c.close)) - Number(c.low)) / range : null; const signedBody = range ? (Number(c.close) - Number(c.open)) / range : null; const prevRange = Math.max(0, Number(p.high) - Number(p.low)); const recentStart = Math.max(entryIndex, exitIndex - 3); let netMove = 0, pathRange = 0, absMove = 0; for (let j = recentStart + 1; j <= exitIndex; j++) { const a = candles[j - 1], b = candles[j], d = Number(b.close) - Number(a.close); netMove += d; absMove += Math.abs(d); pathRange += Math.max(0, Number(b.high) - Number(b.low)); } const exitVsEntry = (Number(c.close) - entry) / risk; return { exitBars: exitIndex - entryIndex, exitRangeR: range / risk, exitBodyR: body / risk, exitCloseLocation: closeLoc, exitUpperWickShare: upper, exitLowerWickShare: lower, exitSignedBodyToRange: signedBody, previousRangeR: prevRange / risk, recentNetMoveR: netMove / risk, recentPathEfficiency: absMove ? Math.abs(netMove) / absMove : null, recentRangeR: pathRange / risk, exitVsEntryR: exitVsEntry, exitVsEntryAbsR: Math.abs(exitVsEntry) }; }
function postContinuation(exitIndex, entry, risk, direction) { let mfe = 0; for (let j = exitIndex + 1; j <= Math.min(candles.length - 1, exitIndex + POST_HORIZON); j++) { const c = candles[j], fav = direction === 'BUY' ? (c.high - entry) / risk : (entry - c.low) / risk; mfe = Math.max(mfe, fav); } return { mfeR: mfe, hasPost1: mfe >= 1 }; }
function familyScore(rows, features) { const ranks = Object.fromEntries(features.map(k => [k, percentileRanks(rows, k)])); return rows.map((_, i) => { const vals = features.map(k => ranks[k][i]).filter(Number.isFinite); return vals.length ? mean(vals) : null; }); }
function summarizeGroup(rows) { const target = rows.filter(x => x.post.hasPost1), non = rows.filter(x => !x.post.hasPost1); const families = Object.fromEntries(Object.entries(FAMILIES).map(([name, features]) => { const scores = familyScore(rows, features); const targetScores = [], nonScores = []; rows.forEach((_, i) => (rows[i].post.hasPost1 ? targetScores : nonScores).push(scores[i])); const tm = mean(targetScores), nm = mean(nonScores), ts = sd(targetScores), ns = sd(nonScores), pooled = ts !== null && ns !== null ? Math.sqrt(((targetScores.filter(Number.isFinite).length - 1) * ts ** 2 + (nonScores.filter(Number.isFinite).length - 1) * ns ** 2) / Math.max(1, targetScores.filter(Number.isFinite).length + nonScores.filter(Number.isFinite).length - 2)) : null; return [name, { features, targetMeanRank: tm, nonTargetMeanRank: nm, delta: tm !== null && nm !== null ? tm - nm : null, standardizedDelta: pooled ? (tm - nm) / pooled : null, aucTargetGreater: auc(targetScores, nonScores), targetMedianRank: median(targetScores), nonTargetMedianRank: median(nonScores) }]; })); return { n: rows.length, continuation1R: pct(rows.map(x => x.post.hasPost1)), targetN: target.length, nonTargetN: non.length, families }; }
function subgroup(rows, field, values) { return Object.fromEntries(values.map(v => { const g = rows.filter(x => x[field] === v); return [v, summarizeGroup(g)]; })); }
const raw = (base.trades ?? []).filter(t => { const i = Number(t.entryIndex); return Number.isInteger(i) && i < PRE && t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && (t.direction === 'BUY' || t.direction === 'SELL'); });
let replayMismatch = 0, exitMismatch = 0; const rows = [];
for (const t of raw) { const i = Number(t.entryIndex), r = replay(i); if (!r || r.tr.timestamp !== t.entryTime || r.tr.direction !== t.direction) { replayMismatch++; continue; } const entry = Number(t.entry), sl = Number(t.stopLoss), tp = Number(t.tp1), ex = canonicalExit(i, entry, sl, tp, t.direction), expected = t.result === 'TP1' ? 'TP1' : 'SL'; if (!ex || ex.reason !== expected) { exitMismatch++; continue; } rows.push({ entryIndex: i, entryTime: t.entryTime, direction: t.direction, session: session(t.entryTime), split: i <= DEV_END ? 'DEV' : 'VAL', window: WINDOWS.find(w => i >= w.start && i <= w.end)?.name ?? 'UNKNOWN', r: Number(t.rMultiple), outcome: Number(t.rMultiple) > 0 ? 'WIN' : 'LOSS', features: exitFeatures(i, ex.index, entry, ex.risk), post: postContinuation(ex.index, entry, ex.risk, t.direction) }); }
const losses = rows.filter(x => x.outcome === 'LOSS');
const familyOverall = summarizeGroup(losses);
const result = {
  strategy: 'Strategy A / SP2L', mode: 'PHASE_22_EXIT_STATE_COMPRESSION_TEMPORAL_ROBUSTNESS', timeframe: '5min',
  scope: { rawBaselinePre: raw.length, canonicalReplayed: rows.length, dev: rows.filter(x => x.split === 'DEV').length, val: rows.filter(x => x.split === 'VAL').length, freshHoldoutExcluded: true, productionUntouched: true },
  integrity: { expectedCanonical: 210, rawBaselinePre: raw.length, canonicalReplayed: rows.length, replayMismatch, exitMismatch, totalMismatch: replayMismatch + exitMismatch },
  methodology: {
    purpose: 'Descriptive audit of compressed exit-state feature families and their temporal robustness. Features are compressed into fixed conceptual families using within-group percentile ranks; no optimized thresholds or trading rules are produced.',
    label: 'Loss with post-exit MFE >=1R within 500 bars.',
    families: FAMILIES,
    compression: 'For each fixed subgroup, each feature is converted to a percentile rank among losses in that subgroup; family score is the unweighted mean rank of its member features.',
    futureLeakageGuard: 'Post-exit continuation is retrospective label only; no future candle enters any exit-state feature or family score.',
    noOptimization: true, noThresholdSearch: true, noNewTradingRules: true, noFreshHoldoutAccess: true,
  },
  overall: stats(rows),
  lossPopulation: { n: losses.length, ...familyOverall },
  temporalRobustness: subgroup(losses, 'window', WINDOWS.map(x => x.name)),
  directionRobustness: subgroup(losses, 'direction', ['BUY', 'SELL']),
  sessionRobustness: subgroup(losses, 'session', ['LONDON', 'NEW_YORK', 'OUT_OF_SESSION']),
};
const out = resolve(ROOT, 'data/reports/strategy-a-phase22-exit-state-compression-temporal-robustness');
await mkdir(out, { recursive: true });
await writeFile(resolve(out, '5min.json'), JSON.stringify(result, null, 2));
console.log(`PHASE_22_EXIT_STATE_COMPRESSION_TEMPORAL_ROBUSTNESS 5min N=${rows.length} DEV=${rows.filter(x => x.split === 'DEV').length} VAL=${rows.filter(x => x.split === 'VAL').length} FRESH=LOCKED`);
console.log(`INTEGRITY expected=210 raw=${raw.length} actual=${rows.length} replayMismatch=${replayMismatch} exitMismatch=${exitMismatch}`);
console.log(`OVERALL N=${rows.length} avgR=${result.overall.avgR?.toFixed(6)} PF=${result.overall.PF?.toFixed(6)} WR=${(result.overall.WR * 100)?.toFixed(4)}% totalR=${result.overall.totalR?.toFixed(6)}`);
console.log(`LOSSES N=${losses.length} CONT_GE_1R=${familyOverall.targetN} share=${(familyOverall.continuation1R * 100).toFixed(4)}% NO_CONT=${familyOverall.nonTargetN}`);
for (const [family, s] of Object.entries(familyOverall.families)) console.log(`FAMILY ${family}: targetRank=${s.targetMeanRank?.toFixed(4)} nonTargetRank=${s.nonTargetMeanRank?.toFixed(4)} stdDelta=${s.standardizedDelta?.toFixed(4)} auc=${s.aucTargetGreater?.toFixed(4)} delta=${s.delta?.toFixed(4)}`);
for (const [k, v] of Object.entries(result.temporalRobustness)) console.log(`WINDOW ${k}: N=${v.n} continuation1R=${(v.continuation1R * 100).toFixed(2)}% DISP_STD=${v.families.directional_displacement.standardizedDelta?.toFixed(4)} INTENSITY_STD=${v.families.exit_candle_intensity.standardizedDelta?.toFixed(4)} PRIOR_STD=${v.families.prior_bar_expansion.standardizedDelta?.toFixed(4)}`);
for (const [k, v] of Object.entries(result.directionRobustness)) console.log(`DIRECTION ${k}: N=${v.n} continuation1R=${(v.continuation1R * 100).toFixed(2)}% DISP_STD=${v.families.directional_displacement.standardizedDelta?.toFixed(4)} INTENSITY_STD=${v.families.exit_candle_intensity.standardizedDelta?.toFixed(4)} PRIOR_STD=${v.families.prior_bar_expansion.standardizedDelta?.toFixed(4)}`);
for (const [k, v] of Object.entries(result.sessionRobustness)) console.log(`SESSION ${k}: N=${v.n} continuation1R=${(v.continuation1R * 100).toFixed(2)}% DISP_STD=${v.families.directional_displacement.standardizedDelta?.toFixed(4)} INTENSITY_STD=${v.families.exit_candle_intensity.standardizedDelta?.toFixed(4)} PRIOR_STD=${v.families.prior_bar_expansion.standardizedDelta?.toFixed(4)}`);
console.log(`REPORT=${resolve(out, '5min.json')}`);
console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
