import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';
import { getInvalidationRule } from '../src/domain/strategy-a/Invalidation.js';
import { projectLeg2 } from '../src/domain/strategy-a/LegProjection.js';
import { buildEMAContext, buildLocationContext, buildSessionContext } from '../src/domain/strategy-a/Context.js';
import { scoreSetup } from '../src/domain/strategy-a/QualityScore.js';

const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const candles = JSON.parse(await readFile(resolve(ROOT, 'data/historical/xauusd-5min.json'), 'utf8')).candles ?? [];
const base = JSON.parse(await readFile(resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json'), 'utf8'));
const PRE = 10000;
const DEV = 6000;
const WINDOWS = [
  { name: 'DEV_1', start: 0, end: 1999 },
  { name: 'DEV_2', start: 2000, end: 3999 },
  { name: 'DEV_3', start: 4000, end: 5999 },
  { name: 'VAL_1', start: 6000, end: 7999 },
  { name: 'VAL_2', start: 8000, end: 9999 },
];
const CFG = {
  breakoutLookback: 5,
  followThrough: { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true },
  spike: { maxCandles: 8, minDirectionalFraction: 0.5, maxOverlapFraction: 0.8 },
};
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
const FEATURES = [
  'breakoutToFollowThrough','spikeBars','spikeSizeR','spikeStructureScore','spikeOverlapScore',
  'correctionBars','correctionSizeR','correctionToSpike','correctionDelay','correctionEfficiency',
  'entryTriggerReclaimR','entryTriggerBodyR','entryTriggerCloseLocation','entryTriggerUpperWickShare','entryTriggerLowerWickShare',
];
const FAMILIES = {
  impulse_quality: ['spikeSizeR','spikeStructureScore','spikeOverlapScore','spikeBars','breakoutToFollowThrough'],
  correction_quality: ['correctionSizeR','correctionToSpike','correctionBars','correctionEfficiency','correctionDelay'],
  trigger_quality: ['entryTriggerReclaimR','entryTriggerBodyR','entryTriggerCloseLocation','entryTriggerUpperWickShare','entryTriggerLowerWickShare'],
};

const mean = values => { const v = values.filter(Number.isFinite); return v.length ? v.reduce((s, x) => s + x, 0) / v.length : null; };
const sd = values => { const v = values.filter(Number.isFinite); if (v.length < 2) return null; const m = mean(v); return Math.sqrt(v.reduce((s, x) => s + (x - m) ** 2, 0) / (v.length - 1)); };
const median = values => { const v = values.filter(Number.isFinite).sort((a, b) => a - b); if (!v.length) return null; const m = Math.floor(v.length / 2); return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2; };
const rank = values => { const pairs = values.map((v, i) => ({ v, i })).filter(x => Number.isFinite(x.v)).sort((a, b) => a.v - b.v); const out = Array(values.length).fill(null); let i = 0; while (i < pairs.length) { let j = i + 1; while (j < pairs.length && pairs[j].v === pairs[i].v) j++; const r = (i + 1 + j) / 2; for (let k = i; k < j; k++) out[pairs[k].i] = r; i = j; } return out; };
const auc = (a, b) => { const x = a.filter(Number.isFinite), y = b.filter(Number.isFinite); if (!x.length || !y.length) return null; let w = 0, t = 0; for (const i of x) for (const j of y) { if (i > j) w++; else if (i === j) t++; } return (w + 0.5 * t) / (x.length * y.length); };
const stats = rows => { const n = rows.length, totalR = rows.reduce((s, x) => s + x.r, 0), wins = rows.filter(x => x.r > 0), losses = rows.filter(x => x.r <= 0), gw = wins.reduce((s, x) => s + x.r, 0), gl = -losses.reduce((s, x) => s + x.r, 0); return { n, avgR: n ? totalR / n : null, PF: gl ? gw / gl : null, WR: n ? wins.length / n : null, totalR }; };
const sessionOf = ts => { const d = new Date(ts), m = d.getUTCHours() * 60 + d.getUTCMinutes(); if (m >= 960 && m < 1320) return 'NEW_YORK'; if (m >= 420 && m < 960) return 'LONDON'; return 'OUT_OF_SESSION'; };

function replay(index) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < 60) return null;
  const bo = detectBreakout(visible, CFG.breakoutLookback);
  const ft = detectFollowThrough(visible, bo, CFG.followThrough);
  const sp = detectSpikeCandidates(visible, bo, ft, CFG.spike);
  const candidates = [];
  for (const s of sp.candidates) {
    if (s.endIndex >= index) continue;
    const co = detectFirstCorrection(visible, s);
    if (!co || co.correctionExtremeIndex >= index) continue;
    const tr = detectEntryTrigger(visible, co);
    if (!tr || tr.index !== index) continue;
    const b = bo.find(x => x.index === s.breakoutIndex && x.direction === s.direction);
    const f = ft.find(x => x.breakoutIndex === s.breakoutIndex && x.direction === s.direction);
    if (!b || !f) continue;
    const projection = projectLeg2(visible, co);
    const invalidation = getInvalidationRule(co);
    const ema = buildEMAContext(visible.map(x => x.close), CONTEXT);
    if (!projection || !ema) continue;
    const location = buildLocationContext(tr.entryPrice, CONTEXT);
    const session = buildSessionContext(tr.timestamp, CONTEXT);
    const quality = scoreSetup(s, { ema, location, session });
    if (!quality.tradeAllowed) continue;
    const risk = Math.abs(tr.entryPrice - invalidation.invalidationLevel);
    const reward = Math.abs(projection.tp1 - tr.entryPrice);
    const target = tr.direction === 'BUY' ? projection.tp1 > tr.entryPrice : projection.tp1 < tr.entryPrice;
    if (risk <= 0 || reward <= 0 || !target) continue;
    candidates.push({ visible, spike: s, breakout: b, followThrough: f, correction: co, trigger: tr, projection, invalidation, quality, risk, reward });
  }
  return candidates[0] ?? null;
}

function features(risk, x) {
  const { spike: s, correction: co, trigger: tr, breakout: b, followThrough: f } = x;
  const spikeBars = s.endIndex - s.startIndex + 1;
  const correctionBars = co.correctionExtremeIndex - s.endIndex;
  const spikeSizeR = Math.abs(s.endPrice - s.startPrice) / risk;
  const correctionSizeR = Math.abs(co.extremePrice - s.endPrice) / risk;
  const correctionToSpike = spikeSizeR > 0 ? correctionSizeR / spikeSizeR : null;
  const correctionEfficiency = correctionBars > 0 ? correctionSizeR / correctionBars : null;
  const c = candles[tr.index];
  const range = Math.max(0, Number(c.high) - Number(c.low));
  const body = Math.abs(Number(c.close) - Number(c.open));
  const triggerCloseLocation = range ? (tr.direction === 'BUY' ? (Number(c.close) - Number(c.low)) / range : (Number(c.high) - Number(c.close)) / range) : null;
  const upper = range ? (Number(c.high) - Math.max(Number(c.open), Number(c.close))) / range : null;
  const lower = range ? (Math.min(Number(c.open), Number(c.close)) - Number(c.low)) / range : null;
  return {
    breakoutToFollowThrough: f.index - b.index,
    spikeBars,
    spikeSizeR,
    spikeStructureScore: s.structureScore,
    spikeOverlapScore: s.overlapScore,
    correctionBars,
    correctionSizeR,
    correctionToSpike,
    correctionDelay: correctionBars,
    correctionEfficiency,
    entryTriggerReclaimR: Math.abs(tr.entryPrice - co.extremePrice) / risk,
    entryTriggerBodyR: body / risk,
    entryTriggerCloseLocation: triggerCloseLocation,
    entryTriggerUpperWickShare: upper,
    entryTriggerLowerWickShare: lower,
  };
}

function familyScores(rows) {
  const out = {};
  for (const [name, keys] of Object.entries(FAMILIES)) {
    const ranks = Object.fromEntries(keys.map(k => [k, rank(rows.map(x => x.features[k]))]));
    out[name] = rows.map((_, i) => { const vals = keys.map(k => ranks[k][i]).filter(Number.isFinite); return vals.length && rows.length > 1 ? mean(vals.map(v => (v - 1) / (rows.length - 1))) : null; });
  }
  return out;
}

function summarize(rows) {
  if (!rows.length) return { n: 0, stats: stats(rows), families: Object.fromEntries(Object.keys(FAMILIES).map(k => [k, { targetN: 0, nonTargetN: 0 }])) };
  const scores = familyScores(rows);
  const result = { n: rows.length, stats: stats(rows), families: {} };
  for (const name of Object.keys(FAMILIES)) {
    const wins = rows.map((x, i) => x.r > 0 ? scores[name][i] : null).filter(Number.isFinite);
    const losses = rows.map((x, i) => x.r <= 0 ? scores[name][i] : null).filter(Number.isFinite);
    const wm = mean(wins), lm = mean(losses), ws = sd(wins), ls = sd(losses);
    const pooled = ws !== null && ls !== null && wins.length + losses.length > 2 ? Math.sqrt(((wins.length - 1) * ws ** 2 + (losses.length - 1) * ls ** 2) / (wins.length + losses.length - 2)) : null;
    result.families[name] = { targetN: wins.length, nonTargetN: losses.length, targetMeanRank: wm, nonTargetMeanRank: lm, delta: wm !== null && lm !== null ? wm - lm : null, standardizedDelta: pooled ? (wm - lm) / pooled : null, aucTargetGreater: auc(wins, losses), targetMedianRank: median(wins), nonTargetMedianRank: median(losses) };
  }
  return result;
}

function subgroup(rows, field, values) { return Object.fromEntries(values.map(v => { const g = rows.filter(x => x[field] === v); return [v, summarize(g)]; })); }

const raw = (base.trades ?? []).filter(t => {
  const i = Number(t.entryIndex);
  return Number.isInteger(i) && i < PRE && t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && (t.direction === 'BUY' || t.direction === 'SELL') && typeof t.entryTime === 'string' && t.entryTime;
});
const byTimestamp = new Map();
for (let i = 0; i < candles.length; i++) {
  const ts = candles[i]?.timestamp;
  if (!ts) throw new Error(`PHASE23 missing canonical timestamp at candle ${i}`);
  if (byTimestamp.has(ts)) throw new Error(`PHASE23 duplicate canonical timestamp ${ts}`);
  byTimestamp.set(ts, i);
}

let replayMismatch = 0, missingCanonicalTimestamp = 0, rows = [];
for (const t of raw) {
  const i = byTimestamp.get(t.entryTime);
  if (!Number.isInteger(i)) { missingCanonicalTimestamp++; continue; }
  const x = replay(i);
  if (!x || x.trigger.timestamp !== t.entryTime || x.trigger.direction !== t.direction) { replayMismatch++; continue; }
  const risk = Math.abs(Number(t.entry) - Number(t.stopLoss));
  if (!Number.isFinite(risk) || risk <= 0) { replayMismatch++; continue; }
  rows.push({
    entryIndex: i,
    baselineEntryIndex: Number(t.entryIndex),
    entryTime: t.entryTime,
    direction: t.direction,
    session: sessionOf(t.entryTime),
    split: Number(t.entryIndex) < DEV ? 'DEV' : 'VAL',
    window: WINDOWS.find(w => Number(t.entryIndex) >= w.start && Number(t.entryIndex) <= w.end)?.name ?? 'UNKNOWN',
    r: Number(t.rMultiple),
    outcome: Number(t.rMultiple) > 0 ? 'WIN' : 'LOSS',
    features: features(risk, x),
  });
}
if (missingCanonicalTimestamp || replayMismatch) throw new Error(`PHASE23 canonical replay integrity failure: missingTimestamp=${missingCanonicalTimestamp} replayMismatch=${replayMismatch}`);

const result = {
  strategy: 'Strategy A / SP2L',
  mode: 'PHASE_23_PREENTRY_SETUP_QUALITY_STATE_AUDIT',
  timeframe: '5min',
  scope: { rawBaselinePre: raw.length, canonicalReplayed: rows.length, dev: rows.filter(x => x.split === 'DEV').length, val: rows.filter(x => x.split === 'VAL').length, freshHoldoutExcluded: true, productionUntouched: true },
  integrity: { expectedCanonical: raw.length, rawBaselinePre: raw.length, canonicalReplayed: rows.length, replayMismatch, missingCanonicalTimestamp, canonicalTimestampReplay: true, exactBaselineSelectionSemantics: true },
  methodology: {
    purpose: 'Descriptive audit of deterministic setup-quality information available at or before canonical entry, testing whether fixed impulse, correction, and trigger families separate winners from losers across time, direction, and session.',
    families: FAMILIES,
    compression: 'Within each evaluated population, each feature is percentile-ranked and each family score is the unweighted mean member rank.',
    futureLeakageGuard: 'Only candles at or before canonical entry are used for features; trade outcome is label only.',
    exactBaselineSemantics: 'Breakout -> FollowThrough -> Spike -> Correction -> Trigger -> Projection/Invalidation/Context/Quality -> first trade-allowed positive-RR candidate.',
    noOptimization: true,
    noThresholdSearch: true,
    noNewTradingRules: true,
    noFreshHoldoutAccess: true,
  },
  overall: stats(rows),
  allSetupQuality: summarize(rows),
  temporalRobustness: subgroup(rows, 'window', WINDOWS.map(x => x.name)),
  directionRobustness: subgroup(rows, 'direction', ['BUY', 'SELL']),
  sessionRobustness: subgroup(rows, 'session', ['LONDON', 'NEW_YORK', 'OUT_OF_SESSION']),
};

const out = resolve(ROOT, 'data/reports/strategy-a-phase23-preentry-setup-quality-state-audit');
await mkdir(out, { recursive: true });
await writeFile(resolve(out, '5min.json'), JSON.stringify(result, null, 2));
console.log(`PHASE_23_PREENTRY_SETUP_QUALITY_STATE_AUDIT 5min N=${rows.length} DEV=${rows.filter(x => x.split === 'DEV').length} VAL=${rows.filter(x => x.split === 'VAL').length} FRESH=LOCKED`);
console.log(`INTEGRITY expected=${raw.length} raw=${raw.length} actual=${rows.length} replayMismatch=${replayMismatch} missingCanonicalTimestamp=${missingCanonicalTimestamp}`);
console.log(`OVERALL N=${rows.length} avgR=${result.overall.avgR?.toFixed(6)} PF=${result.overall.PF?.toFixed(6)} WR=${(result.overall.WR * 100)?.toFixed(4)}% totalR=${result.overall.totalR?.toFixed(6)}`);
for (const [family, s] of Object.entries(result.allSetupQuality.families)) console.log(`FAMILY ${family}: WIN_N=${s.targetN} LOSS_N=${s.nonTargetN} winRank=${s.targetMeanRank?.toFixed(4)} lossRank=${s.nonTargetMeanRank?.toFixed(4)} stdDelta=${s.standardizedDelta?.toFixed(4)} auc=${s.aucTargetGreater?.toFixed(4)} delta=${s.delta?.toFixed(4)}`);
for (const [k, v] of Object.entries(result.temporalRobustness)) console.log(`WINDOW ${k}: N=${v.stats.n} avgR=${v.stats.avgR?.toFixed(4)} PF=${v.stats.PF?.toFixed(4)} IMPULSE=${v.families.impulse_quality.standardizedDelta?.toFixed(4)} CORRECTION=${v.families.correction_quality.standardizedDelta?.toFixed(4)} TRIGGER=${v.families.trigger_quality.standardizedDelta?.toFixed(4)}`);
for (const [k, v] of Object.entries(result.directionRobustness)) console.log(`DIRECTION ${k}: N=${v.stats.n} avgR=${v.stats.avgR?.toFixed(4)} PF=${v.stats.PF?.toFixed(4)} IMPULSE=${v.families.impulse_quality.standardizedDelta?.toFixed(4)} CORRECTION=${v.families.correction_quality.standardizedDelta?.toFixed(4)} TRIGGER=${v.families.trigger_quality.standardizedDelta?.toFixed(4)}`);
for (const [k, v] of Object.entries(result.sessionRobustness)) console.log(`SESSION ${k}: N=${v.stats.n} avgR=${v.stats.avgR?.toFixed(4)} PF=${v.stats.PF?.toFixed(4)} IMPULSE=${v.families.impulse_quality.standardizedDelta?.toFixed(4)} CORRECTION=${v.families.correction_quality.standardizedDelta?.toFixed(4)} TRIGGER=${v.families.trigger_quality.standardizedDelta?.toFixed(4)}`);
console.log(`REPORT=${resolve(out, '5min.json')}`);
console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
