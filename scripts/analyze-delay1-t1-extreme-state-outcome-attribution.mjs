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
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT = resolve(ROOT, 'data/reports/strategy-a-t1-extreme-state-outcome-attribution');
const PRE = 10000;
const DEV = 6000;
const FRESH = 5000;
const BINS = [3, 4, 5];
const BO_LOOKBACK = 5;
const CTX = { emaPeriod: 60, roundStep: 50, roundDistance: 5, tradingSessions: [{ name: 'LONDON', startMinutes: 420, endMinutes: 960 }, { name: 'NEW_YORK', startMinutes: 780, endMinutes: 1320 }], avoidWindows: [] };
const finite = Number.isFinite;
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const pct = (n, d) => d ? n / d : null;
function edges(a, b) { a = a.filter(finite).sort((x, y) => x - y); if (!a.length) return []; return [...new Set(Array.from({ length: b - 1 }, (_, i) => { const p = (a.length - 1) * (i + 1) / b, l = Math.floor(p), h = Math.ceil(p); return a[l] + (a[h] - a[l]) * (p - l); }).filter(finite))]; }
const bin = (v, e) => finite(v) ? e.reduce((k, x) => k + (v > x ? 1 : 0), 0) : null;
function candidate(candles, index) {
  const v = candles.slice(0, index + 1); if (v.length < 60) return null;
  const bo = detectBreakout(v, BO_LOOKBACK), ft = detectFollowThrough(v, bo, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
  const sp = detectSpikeCandidates(v, bo, ft, { maxCandles: 8, minDirectionalFraction: .5, maxOverlapFraction: .8 });
  for (const spike of sp.candidates) {
    if (spike.endIndex >= index) continue;
    const cor = detectFirstCorrection(v, spike); if (!cor || cor.correctionExtremeIndex >= index || index - cor.correctionExtremeIndex !== 1) continue;
    const tr = detectEntryTrigger(v, cor); if (!tr || tr.index !== index) continue;
    const pr = projectLeg2(v, cor); if (!pr) continue;
    const inv = getInvalidationRule(cor), ema = buildEMAContext(v.map(c => c.close), CTX), loc = buildLocationContext(tr.entryPrice, CTX), ses = buildSessionContext(tr.timestamp, CTX);
    if (!ema || !scoreSetup(spike, { ema, location: loc, session: ses }).tradeAllowed) continue;
    const risk = Math.abs(tr.entryPrice - inv.invalidationLevel);
    if (!(risk > 0 && (tr.direction === 'BUY' ? pr.tp1 > tr.entryPrice : pr.tp1 < tr.entryPrice))) continue;
    return { entryIndex: index, direction: tr.direction, entry: tr.entryPrice, stopLoss: inv.invalidationLevel, tp1: pr.tp1, risk };
  }
  return null;
}
function adverseR(c, candle) { return Math.max(0, (c.direction === 'BUY' ? c.entry - candle.low : candle.high - c.entry) / c.risk); }
function stopHit(c, candle) { return c.direction === 'BUY' ? candle.low <= c.stopLoss : candle.high >= c.stopLoss; }
function path(c) {
  const first = c.candles[c.entryIndex + 1]; if (!first) return null;
  const t1Mae = adverseR(c, first), sameBarStop = stopHit(c, first), horizon = Math.min(c.entryIndex + 20, c.candles.length - 1);
  let mae20 = t1Mae, postT1Mfe = 0, postT1Stop = false;
  for (let j = c.entryIndex + 1; j <= horizon; j++) {
    const x = c.candles[j]; mae20 = Math.max(mae20, adverseR(c, x));
    if (j >= c.entryIndex + 2) {
      const mfe = c.direction === 'BUY' ? (x.high - c.entry) / c.risk : (c.entry - x.low) / c.risk;
      postT1Mfe = Math.max(postT1Mfe, mfe, 0); if (stopHit(c, x)) postT1Stop = true;
    }
  }
  return { t1Mae, mae20, sameBarStop, postT1Mfe, postT1Stop };
}
function attribution(rows, threshold) {
  const extreme = rows.filter(r => r.t1Mae >= threshold), control = rows.filter(r => r.t1Mae < threshold);
  const summarize = set => {
    const n = set.length, sameBarStop = set.filter(r => r.sameBarStop).length, finalStop = set.filter(r => r.y === -1).length;
    const finalPositive = set.filter(r => r.y > 0).length, recovered = set.filter(r => r.sameBarThreshold && r.y > -1).length;
    const recoveredPositive = set.filter(r => r.sameBarThreshold && r.y > 0).length;
    const thresholdBeforeStop = set.filter(r => r.sameBarThreshold && !r.sameBarStop).length;
    return { n, meanR: mean(set.map(r => r.y)), sameBarThresholdCount: set.filter(r => r.sameBarThreshold).length, sameBarThresholdPct: pct(set.filter(r => r.sameBarThreshold).length, n), sameBarStopCount: sameBarStop, sameBarStopPct: pct(sameBarStop, n), finalStopCount: finalStop, finalStopPct: pct(finalStop, n), finalPositiveCount: finalPositive, finalPositivePct: pct(finalPositive, n), thresholdHitButFinalAboveMinus1Count: recovered, thresholdHitButFinalAboveMinus1Pct: pct(recovered, n), thresholdHitAndFinalPositiveCount: recoveredPositive, thresholdHitAndFinalPositivePct: pct(recoveredPositive, n), thresholdHitWithoutSameBarStopCount: thresholdBeforeStop, thresholdHitWithoutSameBarStopPct: pct(thresholdBeforeStop, n), meanPostT1MFE: mean(set.map(r => r.postT1Mfe)) };
  };
  return { extreme: summarize(extreme), control: summarize(control), removedN: extreme.length };
}
async function rows(tf) {
  const raw = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8')), candles = raw.candles ?? raw;
  if (candles.length < PRE + FRESH) throw new Error(`${tf}: expected at least ${PRE + FRESH} candles, found ${candles.length}`);
  const base = JSON.parse(await readFile(resolve(BASE, `${tf}.json`), 'utf8')).trades ?? [];
  const map = new Map(base.filter(t => t.result !== 'AMBIGUOUS' && finite(Number(t.rMultiple))).map(t => [`${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`, t]));
  const out = [];
  for (let i = 0; i < candles.length; i++) {
    const c = candidate(candles, i); if (!c) continue;
    const key = `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`, t = map.get(key); if (!t) continue;
    const p = path({ ...c, candles }); if (!p) continue;
    out.push({ entryIndex: i, y: Number(t.rMultiple), result: t.result, t1Mae: p.t1Mae, mae20: p.mae20, sameBarStop: p.sameBarStop, postT1Mfe: p.postT1Mfe, postT1Stop: p.postT1Stop, sameBarThreshold: false });
  }
  return out;
}
function fmt(v) { return finite(v) ? v.toFixed(4) : 'NA'; }
function line(label, s) { return `${label}: N=${s.n} meanR=${fmt(s.meanR)} T1hit=${fmt(100*s.sameBarThresholdPct)}% sameBarSL=${fmt(100*s.sameBarStopPct)}% final-1R=${fmt(100*s.finalStopPct)}% positive=${fmt(100*s.finalPositivePct)}% recovered>-1R=${fmt(100*s.thresholdHitButFinalAboveMinus1Pct)}% recovered>0=${fmt(100*s.thresholdHitAndFinalPositivePct)}% noSameBarSL=${fmt(100*s.thresholdHitWithoutSameBarStopPct)}% postT1MFE=${fmt(s.meanPostT1MFE)}`; }
async function run(tf) {
  const all = await rows(tf), dev = all.filter(r => r.entryIndex < DEV), val = all.filter(r => r.entryIndex >= DEV && r.entryIndex < PRE), fresh = all.filter(r => r.entryIndex >= PRE && r.entryIndex < PRE + FRESH);
  const report = { strategy: 'Strategy A', mode: 'DELAY1_T1_EXTREME_STATE_OUTCOME_ATTRIBUTION', timeframe: tf, scope: { totalCandles: PRE + FRESH, devCandles: DEV, valCandles: PRE - DEV, freshHoldoutCandles: FRESH, delayExactly: 1 }, methodology: { thresholdSource: 'DEV quantile edge only', thresholds: { '3': 'P66.7', '4': 'P75', '5': 'P80' }, frozenFor: ['VAL', 'FRESH_HOLDOUT'], canonicalOutcome: 'baseline rMultiple/result joined by exact entry|direction|entry|stopLoss|tp1 key', sameBarStopDefinition: 'first post-entry candle breaches canonical stop', recoveryDefinition: 'T1 threshold hit and final canonical rMultiple > -1R', positiveRecoveryDefinition: 'T1 threshold hit and final canonical rMultiple > 0', intrabarOrderCaveat: true, diagnosticOnly: true, productionUntouched: true } };
  for (const b of BINS) {
    const e = edges(dev.map(r => r.t1Mae), b), threshold = e[e.length - 1];
    const annotate = r => ({ ...r, sameBarThreshold: r.t1Mae >= threshold });
    const d = dev.map(annotate), v = val.map(annotate), f = fresh.map(annotate);
    report[b] = { thresholdR: threshold, thresholdVsCanonicalStop: threshold <= 1 ? 'at_or_below_1R' : 'above_1R', dev: attribution(d, threshold), val: attribution(v, threshold), freshHoldout: attribution(f, threshold) };
  }
  await mkdir(OUT, { recursive: true }); await writeFile(resolve(OUT, `${tf}.json`), JSON.stringify({ ...report, counts: { all: all.length, dev: dev.length, val: val.length, freshHoldout: fresh.length } }, null, 2));
  console.log(`\n${tf}: n=${all.length} DEV=${dev.length} VAL=${val.length} FRESH=${fresh.length}`);
  for (const b of BINS) { const x = report[b]; console.log(`bins=${b} thresholdR=${fmt(x.thresholdR)} ${x.thresholdVsCanonicalStop}`); console.log('  DEV   ' + line('extreme', x.dev.extreme)); console.log('  VAL   ' + line('extreme', x.val.extreme)); console.log('  FRESH ' + line('extreme', x.freshHoldout.extreme)); }
}
for (const tf of ['1min', '5min']) await run(tf);
