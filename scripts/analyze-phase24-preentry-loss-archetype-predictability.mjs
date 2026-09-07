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
const DEV_END = 5999;
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
const FAMILIES = {
  impulse_quality: ['spikeSizeR', 'spikeStructureScore', 'spikeOverlapScore', 'spikeBars', 'breakoutToFollowThrough'],
  correction_quality: ['correctionSizeR', 'correctionToSpike', 'correctionBars', 'correctionDelay', 'correctionEfficiency'],
  trigger_quality: ['entryTriggerReclaimR', 'entryTriggerBodyR', 'entryTriggerCloseLocation', 'entryTriggerUpperWickShare', 'entryTriggerLowerWickShare'],
};
const ARCS = [
  'LOSS_A_NO_PRE_FAVORABLE',
  'LOSS_B_PRE_0_5_TO_LT_1R',
  'LOSS_C_PRE_1_TO_LT_2R',
  'LOSS_D_PRE_GE_2R',
];

const mean = values => { const v = values.filter(Number.isFinite); return v.length ? v.reduce((s, x) => s + x, 0) / v.length : null; };
const sd = values => { const v = values.filter(Number.isFinite); if (v.length < 2) return null; const m = mean(v); return Math.sqrt(v.reduce((s, x) => s + (x - m) ** 2, 0) / (v.length - 1)); };
const median = values => { const v = values.filter(Number.isFinite).sort((a, b) => a - b); if (!v.length) return null; const m = Math.floor(v.length / 2); return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2; };
const rank = values => { const pairs = values.map((v, i) => ({ v, i })).filter(x => Number.isFinite(x.v)).sort((a, b) => a.v - b.v); const out = Array(values.length).fill(null); let i = 0; while (i < pairs.length) { let j = i + 1; while (j < pairs.length && pairs[j].v === pairs[i].v) j++; const r = (i + 1 + j) / 2; for (let k = i; k < j; k++) out[pairs[k].i] = r; i = j; } return out; };
const auc = (a, b) => { const x = a.filter(Number.isFinite), y = b.filter(Number.isFinite); if (!x.length || !y.length) return null; let w = 0, ties = 0; for (const i of x) for (const j of y) { if (i > j) w++; else if (i === j) ties++; } return (w + 0.5 * ties) / (x.length * y.length); };
const sessionOf = ts => { const d = new Date(ts), m = d.getUTCHours() * 60 + d.getUTCMinutes(); if (m >= 960 && m < 1320) return 'NEW_YORK'; if (m >= 420 && m < 960) return 'LONDON'; return 'OUT_OF_SESSION'; };
const stats = rows => { const n = rows.length, totalR = rows.reduce((s, x) => s + x.r, 0), wins = rows.filter(x => x.r > 0), losses = rows.filter(x => x.r <= 0), gw = wins.reduce((s, x) => s + x.r, 0), gl = -losses.reduce((s, x) => s + x.r, 0); return { n, avgR: n ? totalR / n : null, PF: gl ? gw / gl : null, WR: n ? wins.length / n : null, totalR }; };

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
    candidates.push({ spike: s, breakout: b, followThrough: f, correction: co, trigger: tr, projection, invalidation, risk });
  }
  return candidates[0] ?? null;
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

function preExitMFE(entryIndex, exitIndex, entry, risk, direction) {
  let mfe = 0;
  for (let j = entryIndex + 1; j <= exitIndex; j++) {
    const c = candles[j];
    const fav = direction === 'BUY' ? (c.high - entry) / risk : (entry - c.low) / risk;
    mfe = Math.max(mfe, fav);
  }
  return mfe;
}

function archetype(mfe) {
  if (mfe < 0.5) return 'LOSS_A_NO_PRE_FAVORABLE';
  if (mfe < 1) return 'LOSS_B_PRE_0_5_TO_LT_1R';
  if (mfe < 2) return 'LOSS_C_PRE_1_TO_LT_2R';
  return 'LOSS_D_PRE_GE_2R';
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
  const closeLocation = range ? (tr.direction === 'BUY' ? (Number(c.close) - Number(c.low)) / range : (Number(c.high) - Number(c.close)) / range) : null;
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
    entryTriggerCloseLocation: closeLocation,
    entryTriggerUpperWickShare: upper,
    entryTriggerLowerWickShare: lower,
  };
}

function familyScores(rows) {
  const out = {};
  for (const [name, keys] of Object.entries(FAMILIES)) {
    const ranks = Object.fromEntries(keys.map(k => [k, rank(rows.map(x => x.features[k]))]));
    out[name] = rows.map((_, i) => {
      const vals = keys.map(k => ranks[k][i]).filter(Number.isFinite);
      return vals.length && rows.length > 1 ? mean(vals.map(v => (v - 1) / (rows.length - 1))) : null;
    });
  }
  return out;
}

function familyAudit(rows) {
  const scores = familyScores(rows);
  const out = {};
  for (const family of Object.keys(FAMILIES)) {
    const perArc = {};
    for (const arc of ARCS) {
      const target = rows.map((x, i) => x.archetype === arc ? scores[family][i] : null).filter(Number.isFinite);
      const rest = rows.map((x, i) => x.archetype !== arc ? scores[family][i] : null).filter(Number.isFinite);
      const tm = mean(target), rm = mean(rest), ts = sd(target), rs = sd(rest);
      const pooled = ts !== null && rs !== null && target.length + rest.length > 2 ? Math.sqrt(((target.length - 1) * ts ** 2 + (rest.length - 1) * rs ** 2) / (target.length + rest.length - 2)) : null;
      perArc[arc] = {
        n: target.length,
        meanRank: tm,
        medianRank: median(target),
        restMeanRank: rm,
        deltaVsRest: tm !== null && rm !== null ? tm - rm : null,
        standardizedDeltaVsRest: pooled ? (tm - rm) / pooled : null,
        aucVsRest: auc(target, rest),
      };
    }
    out[family] = perArc;
  }
  return out;
}

function countsBy(rows, field, values) {
  return Object.fromEntries(values.map(v => [v, Object.fromEntries(ARCS.map(a => [a, rows.filter(x => x[field] === v && x.archetype === a).length]))]));
}

const raw = (base.trades ?? []).filter(t => {
  const i = Number(t.entryIndex);
  return Number.isInteger(i) && i < PRE && t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && (t.direction === 'BUY' || t.direction === 'SELL') && typeof t.entryTime === 'string' && t.entryTime && Number.isFinite(Number(t.entry)) && Number.isFinite(Number(t.stopLoss)) && Number.isFinite(Number(t.tp1));
});

const byTimestamp = new Map();
for (let i = 0; i < candles.length; i++) {
  const ts = candles[i]?.timestamp;
  if (!ts) throw new Error(`PHASE24 missing canonical timestamp at candle ${i}`);
  if (byTimestamp.has(ts)) throw new Error(`PHASE24 duplicate canonical timestamp ${ts}`);
  byTimestamp.set(ts, i);
}

let missingCanonicalTimestamp = 0;
let replayMismatch = 0;
let exitMismatch = 0;
const rows = [];
const mismatchDetails = [];

for (const t of raw) {
  const canonicalIndex = byTimestamp.get(t.entryTime);
  if (!Number.isInteger(canonicalIndex)) { missingCanonicalTimestamp++; continue; }
  const x = replay(canonicalIndex);
  if (!x || x.trigger.timestamp !== t.entryTime || x.trigger.direction !== t.direction) {
    replayMismatch++;
    mismatchDetails.push({ type: 'REPLAY', entryIndex: Number(t.entryIndex), entryTime: t.entryTime, direction: t.direction });
    continue;
  }
  const entry = Number(t.entry);
  const sl = Number(t.stopLoss);
  const tp = Number(t.tp1);
  const risk = Math.abs(entry - sl);
  if (!Number.isFinite(risk) || risk <= 0) { replayMismatch++; continue; }
  const ex = scanExit(canonicalIndex, entry, sl, tp, t.direction);
  const expected = t.result === 'TP1' ? 'TP1' : 'SL';
  if (!ex || ex.reason !== expected) {
    exitMismatch++;
    mismatchDetails.push({ type: 'EXIT', entryIndex: Number(t.entryIndex), entryTime: t.entryTime, expected, reconstructed: ex?.reason ?? null });
    continue;
  }
  const isLoss = Number(t.rMultiple) <= 0;
  const mfe = isLoss ? preExitMFE(canonicalIndex, ex.index, entry, risk, t.direction) : null;
  rows.push({
    entryIndex: canonicalIndex,
    baselineEntryIndex: Number(t.entryIndex),
    entryTime: t.entryTime,
    direction: t.direction,
    session: sessionOf(t.entryTime),
    split: Number(t.entryIndex) <= DEV_END ? 'DEV' : 'VAL',
    window: WINDOWS.find(w => Number(t.entryIndex) >= w.start && Number(t.entryIndex) <= w.end)?.name ?? 'UNKNOWN',
    r: Number(t.rMultiple),
    outcome: isLoss ? 'LOSS' : 'WIN',
    archetype: isLoss ? archetype(mfe) : null,
    preExitMFE: mfe,
    features: features(risk, x),
  });
}

if (missingCanonicalTimestamp || replayMismatch || exitMismatch) {
  throw new Error(`PHASE24 canonical integrity failure: missingTimestamp=${missingCanonicalTimestamp} replayMismatch=${replayMismatch} exitMismatch=${exitMismatch}`);
}

const losses = rows.filter(x => x.outcome === 'LOSS');
const devLosses = losses.filter(x => x.split === 'DEV');
const valLosses = losses.filter(x => x.split === 'VAL');
const familyAuditOverall = familyAudit(losses);

const result = {
  strategy: 'Strategy A / SP2L',
  mode: 'PHASE_24_PREENTRY_LOSS_ARCHETYPE_PREDICTABILITY',
  timeframe: '5min',
  scope: {
    rawBaselinePre: raw.length,
    canonicalReplayed: rows.length,
    losses: losses.length,
    dev: rows.filter(x => x.split === 'DEV').length,
    val: rows.filter(x => x.split === 'VAL').length,
    freshHoldoutExcluded: true,
    productionUntouched: true,
  },
  integrity: {
    expectedCanonical: raw.length,
    rawBaselinePre: raw.length,
    canonicalReplayed: rows.length,
    replayMismatch,
    missingCanonicalTimestamp,
    exitMismatch,
    canonicalTimestampReplay: true,
    exactBaselineSelectionSemantics: true,
    exactBaselineExitSemantics: true,
  },
  methodology: {
    purpose: 'Descriptive audit of whether deterministic pre-entry setup information separates the four already-defined loss-path archetypes A/B/C/D.',
    archetypeBasis: 'Only losing baseline trades are labeled after the fact by pre-exit MFE: A <0.5R, B 0.5R-<1R, C 1R-<2R, D >=2R.',
    featureGuard: 'All predictor features use only candles available at or before canonical entry. Post-entry MFE is used only as the loss-archetype label and never as a predictor.',
    families: FAMILIES,
    compression: 'Within the complete loss population, each feature is percentile-ranked and each family score is the unweighted mean of member ranks.',
    validation: 'Family archetype means, median ranks, standardized deltas and one-vs-rest AUC are reported descriptively; DEV/VAL, direction and session counts test temporal/context stability.',
    noOptimization: true,
    noThresholdSearch: true,
    noNewTradingRules: true,
    noFreshHoldoutAccess: true,
  },
  overall: stats(rows),
  lossPopulation: {
    n: losses.length,
    byArchetype: Object.fromEntries(ARCS.map(a => {
      const rs = losses.filter(x => x.archetype === a);
      return [a, { n: rs.length, shareOfLosses: losses.length ? rs.length / losses.length : null, medianPreExitMFE: median(rs.map(x => x.preExitMFE)) }];
    })),
  },
  familyAudit: familyAuditOverall,
  temporalCounts: {
    DEV: Object.fromEntries(ARCS.map(a => [a, devLosses.filter(x => x.archetype === a).length])),
    VAL: Object.fromEntries(ARCS.map(a => [a, valLosses.filter(x => x.archetype === a).length])),
    windows: countsBy(losses, 'window', WINDOWS.map(w => w.name)),
  },
  directionCounts: countsBy(losses, 'direction', ['BUY', 'SELL']),
  sessionCounts: countsBy(losses, 'session', ['LONDON', 'NEW_YORK', 'OUT_OF_SESSION']),
  cases: losses,
  mismatchDetails,
};

const out = resolve(ROOT, 'data/reports/strategy-a-phase24-preentry-loss-archetype-predictability');
await mkdir(out, { recursive: true });
await writeFile(resolve(out, '5min.json'), JSON.stringify(result, null, 2));

console.log(`PHASE_24_PREENTRY_LOSS_ARCHETYPE_PREDICTABILITY 5min N=${rows.length} LOSSES=${losses.length} DEV=${devLosses.length} VAL=${valLosses.length} FRESH=LOCKED`);
console.log(`INTEGRITY expected=${raw.length} raw=${raw.length} actual=${rows.length} replayMismatch=${replayMismatch} missingCanonicalTimestamp=${missingCanonicalTimestamp} exitMismatch=${exitMismatch}`);
console.log(`OVERALL N=${rows.length} avgR=${result.overall.avgR?.toFixed(6)} PF=${result.overall.PF?.toFixed(6)} WR=${(result.overall.WR * 100)?.toFixed(4)}% totalR=${result.overall.totalR?.toFixed(6)}`);
for (const a of ARCS) {
  const s = result.lossPopulation.byArchetype[a];
  console.log(`ARCHETYPE ${a}: N=${s.n} share=${(s.shareOfLosses * 100).toFixed(2)}% medianPreMFE=${s.medianPreExitMFE?.toFixed(3)}R`);
}
for (const [family, arcs] of Object.entries(familyAuditOverall)) {
  console.log(`FAMILY ${family}: ${ARCS.map(a => `${a}[N=${arcs[a].n},mean=${arcs[a].meanRank?.toFixed(4)},vsRest=${arcs[a].standardizedDeltaVsRest?.toFixed(4)},auc=${arcs[a].aucVsRest?.toFixed(4)}]`).join(' ')}`);
}
for (const [w, counts] of Object.entries(result.temporalCounts.windows)) console.log(`WINDOW ${w}: ${ARCS.map(a => `${a}=${counts[a]}`).join(' ')}`);
for (const [d, counts] of Object.entries(result.directionCounts)) console.log(`DIRECTION ${d}: ${ARCS.map(a => `${a}=${counts[a]}`).join(' ')}`);
for (const [s, counts] of Object.entries(result.sessionCounts)) console.log(`SESSION ${s}: ${ARCS.map(a => `${a}=${counts[a]}`).join(' ')}`);
console.log(`REPORT=${resolve(out, '5min.json')}`);
console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
