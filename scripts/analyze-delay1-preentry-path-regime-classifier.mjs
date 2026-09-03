import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';
import { getInvalidationRule } from '../src/domain/strategy-a/Invalidation.js';
import { projectLeg2 } from '../src/domain/strategy-a/LegProjection.js';
import { buildEMAContext, buildLocationContext, buildSessionContext } from '../src/domain/strategy-a/Context.js';
import { scoreSetup } from '../src/domain/strategy-a/QualityScore.js';

const ROOT = resolve(process.cwd());
const BASE_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-delay1-preentry-path-regime-classifier');
const PRE = 10000, DEV = 6000, BLOCK = 2000, H20 = 20;
const BREAKOUT_LOOKBACK = 5, FT_MAX_BARS = 2, SPIKE_MAX_CANDLES = 8;
const SPIKE_MIN_DIRECTIONAL_FRACTION = 0.5, SPIKE_MAX_OVERLAP_FRACTION = 0.8;
const CONTEXT = { emaPeriod: 60, roundStep: 50, roundDistance: 5, tradingSessions: [{ name: 'LONDON', startMinutes: 420, endMinutes: 960 }, { name: 'NEW_YORK', startMinutes: 780, endMinutes: 1320 }], avoidWindows: [] };
const key = c => `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const median = a => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); const m = Math.floor(s.length / 2); return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
const pf = rs => { const w = rs.filter(x => x > 0), l = rs.filter(x => x < 0), gl = -l.reduce((a, b) => a + b, 0); return gl ? w.reduce((a, b) => a + b, 0) / gl : null; };

function build(candles, index) {
  const v = candles.slice(0, index + 1);
  if (v.length < Math.max(BREAKOUT_LOOKBACK + 2, CONTEXT.emaPeriod)) return [];
  const bo = detectBreakout(v, BREAKOUT_LOOKBACK);
  const ft = detectFollowThrough(v, bo, { maxBarsAfterBreakout: FT_MAX_BARS, requireCloseBeyondBrokenLevel: true });
  const sp = detectSpikeCandidates(v, bo, ft, { maxCandles: SPIKE_MAX_CANDLES, minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION, maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION });
  const out = [];
  for (const spike of sp.candidates) {
    if (spike.endIndex >= index) continue;
    const correction = detectFirstCorrection(v, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(v, correction);
    if (!trigger || trigger.index !== index) continue;
    if (correction.correctionExtremeIndex !== index - 1) continue;
    const projection = projectLeg2(v, correction);
    if (!projection) continue;
    const inv = getInvalidationRule(correction);
    const ema = buildEMAContext(v.map(c => c.close), CONTEXT);
    if (!ema) continue;
    const location = buildLocationContext(trigger.entryPrice, CONTEXT);
    const session = buildSessionContext(trigger.timestamp, CONTEXT);
    const quality = scoreSetup(spike, { ema, location, session });
    if (!quality.tradeAllowed) continue;
    const risk = Math.abs(trigger.entryPrice - inv.invalidationLevel);
    const reward = Math.abs(projection.tp1 - trigger.entryPrice);
    if (!(risk > 0 && reward > 0 && (trigger.direction === 'BUY' ? projection.tp1 > trigger.entryPrice : projection.tp1 < trigger.entryPrice))) continue;
    out.push({ entryIndex: index, entryTime: trigger.timestamp, direction: trigger.direction, entry: trigger.entryPrice, stopLoss: inv.invalidationLevel, tp1: projection.tp1, session: session.session, emaAligned: ema.aligned, nearRoundLevel: location.nearRoundLevel, qualityScore: quality.score, structureScore: spike.structureScore, overlapScore: spike.overlapScore, spike, correction });
  }
  return out;
}

function features(candles, c) {
  const i = c.entryIndex, cor = c.correction, sp = c.spike, risk = Math.abs(c.entry - c.stopLoss), imp = sp.size || 0, dir = c.direction === 'BUY' ? 1 : -1;
  const tc = candles[i], range = Math.max(0, tc.high - tc.low), body = Math.abs(tc.close - tc.open);
  const first = candles[cor.correctionStartIndex], firstRange = Math.max(0, first.high - first.low), firstBody = Math.abs(first.close - first.open);
  return {
    direction: c.direction,
    session: c.session,
    emaAligned: c.emaAligned,
    nearRoundLevel: c.nearRoundLevel,
    qualityScore: c.qualityScore,
    structureScore: c.structureScore,
    overlapScore: c.overlapScore,
    riskImpulse: imp ? risk / imp : null,
    correctionDepth: imp ? Math.abs(cor.extremePrice - sp.startPrice) / imp : null,
    correctionBars: cor.correctionExtremeIndex - cor.correctionStartIndex + 1,
    firstBodyRange: firstRange ? firstBody / firstRange : null,
    firstClosePos: firstRange ? (dir === 1 ? (first.close - first.low) / firstRange : (first.high - first.close) / firstRange) : null,
    triggerClosePos: range ? (dir === 1 ? (tc.close - tc.low) / range : (tc.high - tc.close) / range) : null,
    triggerBodyPos: range ? body / range : null,
    triggerOppositeWick: range ? (dir === 1 ? tc.high - tc.close : tc.close - tc.low) / range : null
  };
}

// Frozen heuristic. Thresholds are inherited from previously used descriptive bins;
// they are not optimized on this run or on VAL/fresh holdout.
function scorePreEntry(f) {
  let s = 0;
  if (f.triggerClosePos >= 0.75) s += 2; else if (f.triggerClosePos >= 0.50) s += 1;
  if (f.triggerBodyPos >= 0.25) s += 1;
  if (f.triggerOppositeWick <= 0.25) s += 1; else if (f.triggerOppositeWick > 0.50) s -= 1;
  if (f.firstClosePos >= 0.75) s += 1; else if (f.firstClosePos <= 0.25) s -= 1;
  if (f.riskImpulse != null && f.riskImpulse <= 0.25) s += 1; else if (f.riskImpulse != null && f.riskImpulse > 0.50) s -= 1;
  if (f.structureScore >= 0.65 && f.structureScore <= 0.85) s += 1; else if (f.structureScore > 0.85) s -= 1;
  if (f.overlapScore >= 0.40 && f.overlapScore <= 0.80) s += 1; else if (f.overlapScore > 0.80) s -= 1;
  if (f.nearRoundLevel === false) s += 1;
  if (f.emaAligned === true) s += 1;
  return s;
}

function scoreBand(s) { if (s <= 2) return 'HOSTILE_BIASED'; if (s <= 5) return 'NEUTRAL'; return 'CLEAN_BIASED'; }

function firstTouch(candles, r, threshold = 1) {
  const risk = Math.abs(r.entry - r.stopLoss); if (!(risk > 0)) return 'DEAD';
  const end = Math.min(candles.length - 1, r.entryIndex + H20);
  for (let i = r.entryIndex + 1; i <= end; i++) {
    const c = candles[i];
    const favorable = r.direction === 'BUY' ? c.high >= r.entry + threshold * risk : c.low <= r.entry - threshold * risk;
    const adverse = r.direction === 'BUY' ? c.low <= r.entry - threshold * risk : c.high >= r.entry + threshold * risk;
    if (favorable && adverse) return 'SAME_BAR_AMBIGUOUS';
    if (favorable) return 'CLEAN';
    if (adverse) return 'HOSTILE';
  }
  return 'DEAD';
}

function stats(rows) {
  const rs = rows.map(r => r.r).filter(Number.isFinite), un = rows.filter(r => r.regime === 'CLEAN' || r.regime === 'HOSTILE');
  const correct = un.filter(r => (r.predicted === 'CLEAN_BIASED' && r.regime === 'CLEAN') || (r.predicted === 'HOSTILE_BIASED' && r.regime === 'HOSTILE')).length;
  const actual = Object.fromEntries(['CLEAN','HOSTILE','DEAD','SAME_BAR_AMBIGUOUS'].map(k => [k, rows.filter(r => r.regime === k).length]));
  return { n: rows.length, avgR: mean(rs), PF: pf(rs), winRate: rs.length ? rs.filter(x => x > 0).length / rs.length : null, regimeRates: Object.fromEntries(Object.entries(actual).map(([k,v]) => [k, rows.length ? v / rows.length : 0])), unambiguousN: un.length, classifierCoverage: rows.length ? un.filter(r => r.predicted !== 'NEUTRAL').length / rows.length : 0, unambiguousDirectionalAccuracy: un.length ? correct / un.length : null };
}

function bucketStats(rows) {
  const bands = ['HOSTILE_BIASED','NEUTRAL','CLEAN_BIASED'];
  return Object.fromEntries(bands.map(b => {
    const g = rows.filter(r => r.predicted === b), rs = g.map(r => r.r), un = g.filter(r => r.regime === 'CLEAN' || r.regime === 'HOSTILE');
    return [b, { n: g.length, avgR: mean(rs), PF: pf(rs), actualCleanRate: un.length ? un.filter(r => r.regime === 'CLEAN').length / un.length : null, actualHostileRate: un.length ? un.filter(r => r.regime === 'HOSTILE').length / un.length : null, ambiguousRate: g.length ? g.filter(r => r.regime === 'SAME_BAR_AMBIGUOUS').length / g.length : 0 }];
  }));
}

function calibrate(dev) {
  const out = {};
  for (const band of ['HOSTILE_BIASED','NEUTRAL','CLEAN_BIASED']) {
    const g = dev.filter(r => r.predicted === band), un = g.filter(r => r.regime === 'CLEAN' || r.regime === 'HOSTILE');
    out[band] = { n: g.length, cleanProbability: un.length ? g.filter(r => r.regime === 'CLEAN').length / un.length : null, hostileProbability: un.length ? g.filter(r => r.regime === 'HOSTILE').length / un.length : null };
  }
  return out;
}

async function run(tf) {
  const candles = (JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8')).candles ?? []);
  const base = JSON.parse(await readFile(resolve(BASE_DIR, `${tf}.json`), 'utf8'));
  const cutoff = new Date(candles[PRE].timestamp), devCut = new Date(candles[DEV].timestamp);
  const canonical = new Map((base.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && new Date(t.entryTime) < cutoff).map(t => [key(t), t]));
  const rows = [];
  for (let i = 0; i < PRE; i++) {
    const cs = build(candles, i); if (!cs.length) continue;
    const c = cs[0], t = canonical.get(key(c)); if (!t) continue;
    const f = features(candles, c), score = scorePreEntry(f);
    rows.push({ entryIndex: i, entryTime: t.entryTime, r: Number(t.rMultiple), direction: t.direction, entry: Number(t.entry), stopLoss: Number(t.stopLoss), features: f, score, predicted: scoreBand(score), regime: firstTouch(candles, { entryIndex: i, direction: t.direction, entry: Number(t.entry), stopLoss: Number(t.stopLoss) }) });
  }
  const dev = rows.filter(r => new Date(r.entryTime) < devCut), val = rows.filter(r => new Date(r.entryTime) >= devCut && new Date(r.entryTime) < cutoff);
  const calibration = calibrate(dev);
  const windows = [];
  for (let start = 0; start < PRE; start += BLOCK) {
    const end = Math.min(PRE, start + BLOCK), label = start < DEV ? `DEV_${String(start / BLOCK + 1).padStart(2, '0')}` : `VAL_${String((start - DEV) / BLOCK + 1).padStart(2, '0')}`;
    const g = rows.filter(r => r.entryIndex >= start && r.entryIndex < end);
    windows.push({ label, stats: stats(g), bands: bucketStats(g) });
  }
  const report = { strategy: 'Strategy A', mode: 'DELAY1_PREENTRY_PATH_REGIME_CLASSIFIER', timeframe: tf, scope: { preHoldoutCandles: PRE, devCandles: DEV, valCandles: PRE - DEV, freshHoldoutExcluded: true, delayExactly: 1 }, methodology: { target: 'H20 first-touch regime at ±1R: CLEAN, HOSTILE, DEAD, SAME_BAR_AMBIGUOUS.', classifier: 'Frozen additive pre-entry score using existing entry/correction/context features. Score bands: <=2 HOSTILE_BIASED, 3-5 NEUTRAL, >=6 CLEAN_BIASED.', calibration: 'DEV-only empirical CLEAN/HOSTILE probabilities by frozen score band; mapping is not fitted on VAL.', features: ['triggerClosePos','triggerBodyPos','triggerOppositeWick','firstClosePos','riskImpulse','structureScore','overlapScore','nearRoundLevel','emaAligned'], noOptimization: true, noFreshHoldout: true, productionUntouched: true }, calibrationDEV: calibration, overall: { DEV: stats(dev), VAL: stats(val) }, bands: { DEV: bucketStats(dev), VAL: bucketStats(val) }, windows, decision: 'Diagnostic only. No production filter or rule change is authorized by this experiment.' };
  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${tf}.json`); await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`\n=== ${tf} DELAY1 PRE-ENTRY PATH REGIME CLASSIFIER ===`);
  console.log(`Overall DEV n=${report.overall.DEV.n} AvgR=${report.overall.DEV.avgR?.toFixed(3)} PF=${report.overall.DEV.PF?.toFixed(2) ?? 'n/a'} | VAL n=${report.overall.VAL.n} AvgR=${report.overall.VAL.avgR?.toFixed(3)} PF=${report.overall.VAL.PF?.toFixed(2) ?? 'n/a'}`);
  for (const label of ['DEV','VAL']) { console.log(`${label} bands:`); for (const [b,s] of Object.entries(report.bands[label])) console.log(`  ${b} n=${s.n} AvgR=${s.avgR?.toFixed(3) ?? 'n/a'} PF=${s.PF?.toFixed(2) ?? 'n/a'} clean=${s.actualCleanRate == null ? 'n/a' : (100*s.actualCleanRate).toFixed(1)+'%'} hostile=${s.actualHostileRate == null ? 'n/a' : (100*s.actualHostileRate).toFixed(1)+'%'} amb=${(100*s.ambiguousRate).toFixed(1)}%`); }
  console.log(`DEV calibration:`); for (const [b,s] of Object.entries(calibration)) console.log(`  ${b}: n=${s.n} P(CLEAN)=${s.cleanProbability == null ? 'n/a' : (100*s.cleanProbability).toFixed(1)+'%'} P(HOSTILE)=${s.hostileProbability == null ? 'n/a' : (100*s.hostileProbability).toFixed(1)+'%'}`);
  for (const w of windows) console.log(`${w.label} n=${w.stats.n} AvgR=${w.stats.avgR?.toFixed(3) ?? 'n/a'} PF=${w.stats.PF?.toFixed(2) ?? 'n/a'} clean/hostile/dead/same=${Object.values(w.stats.regimeRates).map(x => (100*x).toFixed(1)).join('/')}`);
  console.log(`Report -> ${out}`);
}
for (const tf of ['1min','5min']) await run(tf);
