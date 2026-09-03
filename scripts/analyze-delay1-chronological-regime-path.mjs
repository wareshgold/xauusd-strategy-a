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
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-delay1-chronological-regime-path');
const PRE = 10000;
const DEV = 6000;
const BLOCK = 2000;
const BREAKOUT_LOOKBACK = 5;
const FT_MAX_BARS = 2;
const SPIKE_MAX_CANDLES = 8;
const SPIKE_MIN_DIRECTIONAL_FRACTION = 0.5;
const SPIKE_MAX_OVERLAP_FRACTION = 0.8;
const HORIZONS = [1, 3, 5, 10, 20];
const THRESHOLDS = [0.5, 1, 2];
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

const key = c => `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const median = a => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); const m = Math.floor(s.length / 2); return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
const pf = rs => { const w = rs.filter(x => x > 0), l = rs.filter(x => x < 0), gl = -l.reduce((a, b) => a + b, 0); return gl ? w.reduce((a, b) => a + b, 0) / gl : null; };

function sessionOf(ts) {
  const d = new Date(ts), m = d.getUTCHours() * 60 + d.getUTCMinutes();
  if (m >= 420 && m < 960) return 'LONDON';
  if (m >= 780 && m < 1320) return 'NEW_YORK';
  return 'OUTSIDE';
}

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
    out.push({ entryIndex: index, entryTime: trigger.timestamp, direction: trigger.direction, entry: trigger.entryPrice, stopLoss: inv.invalidationLevel, tp1: projection.tp1, session: session.session, spike, correction, trigger, emaAligned: ema.aligned, nearRoundLevel: location.nearRoundLevel, qualityScore: quality.score, structureScore: spike.structureScore, overlapScore: spike.overlapScore });
  }
  return out;
}

function excursion(candles, r, horizon = 20) {
  const end = Math.min(candles.length - 1, r.entryIndex + horizon);
  const risk = Math.abs(r.entry - r.stopLoss);
  let mfe = 0, mae = 0, favorableFirst = Infinity, adverseFirst = Infinity;
  for (let i = r.entryIndex + 1; i <= end; i++) {
    const c = candles[i];
    const fav = r.direction === 'BUY' ? c.high - r.entry : r.entry - c.low;
    const adv = r.direction === 'BUY' ? r.entry - c.low : c.high - r.entry;
    mfe = Math.max(mfe, fav / risk);
    mae = Math.max(mae, adv / risk);
    if (fav > 0 && favorableFirst === Infinity) favorableFirst = i - r.entryIndex;
    if (adv > 0 && adverseFirst === Infinity) adverseFirst = i - r.entryIndex;
  }
  return { mfe, mae, favorableFirst, adverseFirst };
}

function thresholdEvent(candles, r, threshold, horizon) {
  const risk = Math.abs(r.entry - r.stopLoss);
  if (!(risk > 0)) return 'NONE';
  const end = Math.min(candles.length - 1, r.entryIndex + horizon);
  for (let i = r.entryIndex + 1; i <= end; i++) {
    const c = candles[i];
    const favorable = r.direction === 'BUY' ? c.high >= r.entry + threshold * risk : c.low <= r.entry - threshold * risk;
    const adverse = r.direction === 'BUY' ? c.low <= r.entry - threshold * risk : c.high >= r.entry + threshold * risk;
    if (favorable && adverse) return 'SAME_BAR';
    if (favorable) return 'FAVORABLE_FIRST';
    if (adverse) return 'ADVERSE_FIRST';
  }
  return 'NONE';
}

function path(candles, rows) {
  const out = {};
  for (const h of HORIZONS) {
    for (const th of THRESHOLDS) {
      const counts = { FAVORABLE_FIRST: 0, ADVERSE_FIRST: 0, SAME_BAR: 0, NONE: 0 };
      for (const r of rows) counts[thresholdEvent(candles, r, th, h)]++;
      const n = rows.length;
      out[`h${h}_pm${th}R`] = { n, favorableFirst: n ? counts.FAVORABLE_FIRST / n : 0, adverseFirst: n ? counts.ADVERSE_FIRST / n : 0, sameBar: n ? counts.SAME_BAR / n : 0, none: n ? counts.NONE / n : 0 };
    }
  }
  return out;
}

function stats(rows, candles) {
  const rs = rows.map(r => r.r).filter(Number.isFinite);
  const ex = rows.map(r => excursion(candles, r, 20));
  return {
    n: rs.length,
    avgR: mean(rs),
    PF: pf(rs),
    winRate: rs.length ? rs.filter(x => x > 0).length / rs.length : null,
    medianMFE: median(ex.map(x => x.mfe)),
    medianMAE: median(ex.map(x => x.mae)),
    favorableFirstRate: ex.length ? ex.filter(x => x.favorableFirst < x.adverseFirst).length / ex.length : null,
    adverseFirstRate: ex.length ? ex.filter(x => x.adverseFirst < x.favorableFirst).length / ex.length : null,
  };
}

function featureMedians(rows) {
  const numeric = ['structureScore', 'overlapScore', 'correctionBars', 'correctionDepth', 'riskImpulse', 'firstBodyRange', 'firstClosePos', 'triggerClosePos', 'triggerBodyPos', 'triggerOppositeWick', 'triggerRange', 'risk'];
  const out = {};
  for (const name of numeric) out[name] = median(rows.map(r => r.features[name]).filter(Number.isFinite));
  const counts = { BUY: 0, SELL: 0, LONDON: 0, NEW_YORK: 0, OUTSIDE: 0, nearRound: 0 };
  for (const r of rows) { counts[r.direction]++; counts[r.features.session]++; if (r.features.nearRoundLevel) counts.nearRound++; }
  out.directionMix = { BUY: rows.length ? counts.BUY / rows.length : 0, SELL: rows.length ? counts.SELL / rows.length : 0 };
  out.sessionMix = { LONDON: rows.length ? counts.LONDON / rows.length : 0, NEW_YORK: rows.length ? counts.NEW_YORK / rows.length : 0, OUTSIDE: rows.length ? counts.OUTSIDE / rows.length : 0 };
  out.nearRoundRate = rows.length ? counts.nearRound / rows.length : 0;
  return out;
}

function enrich(candles, c, t) {
  const i = c.entryIndex, cor = c.correction, sp = c.spike, dir = c.direction === 'BUY' ? 1 : -1;
  const risk = Math.abs(c.entry - c.stopLoss), imp = sp.size || 0;
  const cs = candles[cor.correctionStartIndex], cr = Math.max(0, cs.high - cs.low), cb = Math.abs(cs.close - cs.open);
  const tc = candles[i], tr = Math.max(0, tc.high - tc.low), tb = Math.abs(tc.close - tc.open);
  return {
    entryIndex: i, entryTime: t.entryTime, r: Number(t.rMultiple), direction: t.direction, entry: Number(t.entry), stopLoss: Number(t.stopLoss), tp1: Number(t.tp1),
    features: {
      session: c.session || sessionOf(c.entryTime), nearRoundLevel: c.nearRoundLevel, structureScore: c.structureScore, overlapScore: c.overlapScore,
      correctionBars: cor.correctionExtremeIndex - cor.correctionStartIndex + 1,
      correctionDepth: imp ? Math.abs(cor.extremePrice - sp.startPrice) / imp : null,
      riskImpulse: imp ? risk / imp : null,
      firstBodyRange: cr ? cb / cr : null,
      firstClosePos: cr ? (dir === 1 ? (cs.close - cs.low) / cr : (cs.high - cs.close) / cr) : null,
      triggerClosePos: tr ? (dir === 1 ? (tc.close - tc.low) / tr : (tc.high - tc.close) / tr) : null,
      triggerBodyPos: tr ? tb / tr : null,
      triggerOppositeWick: tr ? (dir === 1 ? (tc.high - tc.close) : (tc.close - tc.low)) / tr : null,
      triggerRange: tr, risk,
    },
  };
}

async function run(tf) {
  const candles = (JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8')).candles ?? []);
  const base = JSON.parse(await readFile(resolve(BASE_DIR, `${tf}.json`), 'utf8'));
  if (candles.length < PRE) throw new Error(`${tf}: expected at least ${PRE} pre-holdout candles`);
  const cutoff = new Date(candles[PRE].timestamp), devCut = new Date(candles[DEV].timestamp);
  const canonical = new Map((base.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && new Date(t.entryTime) < cutoff).map(t => [key({ entryIndex: t.entryIndex, direction: t.direction, entry: t.entry, stopLoss: t.stopLoss, tp1: t.tp1 }), t]));
  const rows = [];
  for (let i = 0; i < PRE; i++) {
    const cs = build(candles, i);
    if (!cs.length) continue;
    const c = cs[0];
    const t = canonical.get(key(c));
    if (!t) continue;
    if (c.entryIndex - c.correction.correctionExtremeIndex !== 1) continue;
    rows.push(enrich(candles, c, t));
  }
  const dev = rows.filter(r => new Date(r.entryTime) < devCut), val = rows.filter(r => new Date(r.entryTime) >= devCut && new Date(r.entryTime) < cutoff);
  const windows = [];
  for (let start = 0; start < PRE; start += BLOCK) {
    const end = Math.min(PRE, start + BLOCK);
    const label = start < DEV ? `DEV_${String(start / BLOCK + 1).padStart(2, '0')}` : `VAL_${String((start - DEV) / BLOCK + 1).padStart(2, '0')}`;
    const rs = rows.filter(r => r.entryIndex >= start && r.entryIndex < end);
    windows.push({ label, candleStart: start, candleEndExclusive: end, startTime: candles[start]?.timestamp ?? null, endTime: candles[end - 1]?.timestamp ?? null, stats: stats(rs, candles), featureMedians: featureMedians(rs), path: path(candles, rs) });
  }
  const report = {
    strategy: 'Strategy A', mode: 'DELAY1_CHRONOLOGICAL_REGIME_PATH', timeframe: tf,
    scope: { totalCandles: candles.length, preHoldoutCandles: PRE, devCandles: DEV, valCandles: PRE - DEV, blockCandles: BLOCK, delayExactly: 1, freshHoldoutExcluded: true },
    methodology: {
      purpose: 'Frozen chronological decomposition of Delay=1 to distinguish regime composition drift from post-entry path hostility.',
      windows: 'Five fixed chronological blocks of 2,000 candles: DEV_01..03 and VAL_01..02.',
      path: 'First post-entry touch of ±0.5R, ±1R, ±2R at horizons 1/3/5/10/20; SAME_BAR preserved as OHLC ambiguity.',
      features: 'Descriptive medians and direction/session composition only; no threshold optimization.',
      outcomeSource: 'Canonical baseline backtest; unresolved/AMBIGUOUS outcomes excluded.', noOptimization: true, noFreshHoldout: true, productionUntouched: true,
    },
    overall: { DEV: stats(dev, candles), VAL: stats(val, candles), joined: rows.length },
    windows,
    decision: 'Diagnostic only. No production filter, stop, delay rule, or fresh-holdout decision is authorized by this report.',
  };
  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${tf}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`\n=== ${tf} DELAY1 CHRONOLOGICAL REGIME/PATH ===`);
  console.log(`Overall DEV n=${report.overall.DEV.n} AvgR=${report.overall.DEV.avgR?.toFixed(3)} PF=${report.overall.DEV.PF?.toFixed(2) ?? 'n/a'} | VAL n=${report.overall.VAL.n} AvgR=${report.overall.VAL.avgR?.toFixed(3)} PF=${report.overall.VAL.PF?.toFixed(2) ?? 'n/a'}`);
  for (const w of windows) {
    const s = w.stats, f = w.featureMedians;
    console.log(`${w.label} n=${s.n} AvgR=${s.avgR?.toFixed(3)} PF=${s.PF?.toFixed(2) ?? 'n/a'} WR=${(100 * (s.winRate ?? 0)).toFixed(1)}% MFE/MAE=${s.medianMFE?.toFixed(2) ?? 'n/a'}/${s.medianMAE?.toFixed(2) ?? 'n/a'} F/A=${(100 * (s.favorableFirstRate ?? 0)).toFixed(0)}/${(100 * (s.adverseFirstRate ?? 0)).toFixed(0)}% BUY/SELL=${(100 * f.directionMix.BUY).toFixed(0)}/${(100 * f.directionMix.SELL).toFixed(0)} L/NY/O=${(100 * f.sessionMix.LONDON).toFixed(0)}/${(100 * f.sessionMix.NEW_YORK).toFixed(0)}/${(100 * f.sessionMix.OUTSIDE).toFixed(0)} nearRound=${(100 * f.nearRoundRate).toFixed(0)}%`);
    console.log(`  medians: structure=${f.structureScore?.toFixed(3) ?? 'n/a'} overlap=${f.overlapScore?.toFixed(3) ?? 'n/a'} corrBars=${f.correctionBars?.toFixed(1) ?? 'n/a'} corrDepth=${f.correctionDepth?.toFixed(3) ?? 'n/a'} riskImpulse=${f.riskImpulse?.toFixed(3) ?? 'n/a'} firstBody=${f.firstBodyRange?.toFixed(3) ?? 'n/a'} firstClose=${f.firstClosePos?.toFixed(3) ?? 'n/a'} triggerClose=${f.triggerClosePos?.toFixed(3) ?? 'n/a'} triggerBody=${f.triggerBodyPos?.toFixed(3) ?? 'n/a'} oppWick=${f.triggerOppositeWick?.toFixed(3) ?? 'n/a'}`);
    for (const h of HORIZONS) {
      const x = w.path[`h${h}_pm1R`];
      console.log(`  h${h} ±1R F/A/S/N=${(100*x.favorableFirst).toFixed(0)}/${(100*x.adverseFirst).toFixed(0)}/${(100*x.sameBar).toFixed(0)}/${(100*x.none).toFixed(0)}%`);
    }
  }
  console.log(`Report -> ${out}`);
}

await run('1min');
await run('5min');
